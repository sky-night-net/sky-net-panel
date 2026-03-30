"""
Sky-Net Protocol Adapters
─────────────────────────
Базовый класс и фабрика для протокольных адаптеров.
Каждый адаптер умеет: install, generate configs, add/remove clients, get traffic.
"""

import subprocess
import ipaddress
import json
import os
import logging

log = logging.getLogger("sky-net.adapters")


class ProtocolAdapter:
    """Базовый класс для всех VPN-адаптеров."""

    PROTOCOL_NAME = "base"
    REQUIRED_BINARIES = []

    def __init__(self, db_conn=None):
        self.db = db_conn

    def check_binaries(self, binaries: list):
        """Проверка наличия необходимых программ в системе."""
        for b in binaries:
            if subprocess.run(["which", b], capture_output=True).returncode != 0:
                raise Exception(f"Программа '{b}' не найдена. Установите её для работы протокола {self.PROTOCOL_NAME}.")

    def check_and_install(self, server_ip: str):
        """Проверить наличие бинарников, если нет - запустить install."""
        try:
            self.check_binaries(self.REQUIRED_BINARIES)
        except Exception as e:
            log.info(f"[{self.PROTOCOL_NAME}] Binaries missing, attempting install: {e}")
            self.install(server_ip)
            self.check_binaries(self.REQUIRED_BINARIES)

    def install(self, server_ip: str):
        """Установить необходимые пакеты/контейнеры на сервере."""
        raise NotImplementedError

    def generate_keypair(self) -> dict:
        """Сгенерировать пару ключей (приватный/публичный)."""
        raise NotImplementedError

    def generate_server_config(self, inbound: dict) -> str:
        """Создать файл конфигурации сервера."""
        raise NotImplementedError

    def generate_client_config(self, client: dict, inbound: dict) -> str:
        """Создать конфиг клиента (.conf или .ovpn)."""
        raise NotImplementedError

    def add_client(self, client: dict, inbound: dict) -> bool:
        """Добавить клиента в работающий VPN."""
        raise NotImplementedError

    def remove_client(self, client: dict, inbound: dict) -> bool:
        """Удалить клиента."""
        raise NotImplementedError

    def toggle_client(self, client: dict, inbound: dict, enable: bool) -> bool:
        """Включить/выключить клиента."""
        raise NotImplementedError

    def get_traffic(self, inbound: dict) -> list:
        """Получить список {public_key/username, tx, rx} для всех клиентов."""
        raise NotImplementedError

    def start(self, inbound: dict) -> bool:
        """Запустить VPN-интерфейс."""
        raise NotImplementedError

    def stop(self, inbound: dict) -> bool:
        """Остановить VPN-интерфейс."""
        raise NotImplementedError

    def restart(self, inbound: dict) -> bool:
        """Перезапустить VPN-интерфейс."""
        self.stop(inbound)
        return self.start(inbound)

    def is_running(self, inbound: dict) -> bool:
        """Проверка, запущен ли интерфейс/сервис."""
        raise NotImplementedError

    def _run(self, cmd: list, check: bool = True) -> str:
        """Выполнить shell-команду и вернуть stdout."""
        log.info(f"[{self.PROTOCOL_NAME}] exec: {' '.join(str(c) for c in cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            log.error(f"[{self.PROTOCOL_NAME}] failed: {e.cmd} | err: {e.stderr}")
            raise Exception(f"Ошибка команды: {e.stderr or str(e)}")

    def _get_external_iface(self) -> str:
        """Определить внешний сетевой интерфейс (с маршрутом по умолчанию)."""
        try:
            res = subprocess.run(
                ["ip", "route", "get", "8.8.8.8"],
                capture_output=True, text=True
            )
            if res.returncode == 0 and res.stdout:
                parts = res.stdout.split()
                if "dev" in parts:
                    idx = parts.index("dev")
                    if idx + 1 < len(parts):
                        iface = parts[idx + 1]
                        # Exclude loopback and virtual interfaces
                        if iface not in ("lo", "docker0"):
                            return iface

            # Fallback: parse default route
            res2 = subprocess.run(
                ["ip", "-4", "route", "show", "default"],
                capture_output=True, text=True
            )
            if res2.returncode == 0 and res2.stdout:
                parts = res2.stdout.split()
                if "dev" in parts:
                    idx = parts.index("dev")
                    if idx + 1 < len(parts):
                        return parts[idx + 1]
        except Exception:
            pass
        return "eth0"

    @staticmethod
    def _normalize_subnet(subnet: str) -> str:
        """Convert any IP/prefix (e.g. 10.8.0.1/24) to network address (10.8.0.0/24)."""
        try:
            return str(ipaddress.ip_network(subnet, strict=False))
        except Exception:
            return subnet

    def _setup_nat(self, subnet: str):
        """Настроить NAT (MASQUERADE) и пересылку (FORWARD) для указанной подсети.
        Rules are applied both at runtime (iptables) AND persistently (ufw before.rules).
        Duplicate rules are NOT added.
        """
        # Always use network address, not host address
        subnet = self._normalize_subnet(subnet)
        iface = self._get_external_iface()
        log.info(f"[{self.PROTOCOL_NAME}] Setting up NAT for {subnet} via {iface}")
        try:
            # Enable IP Forwarding
            subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False,
                           capture_output=True)

            # FORWARD rule for this subnet — check before adding (no duplicates)
            fwd_check = subprocess.run(
                ["iptables", "-C", "FORWARD", "-s", subnet, "-j", "ACCEPT"],
                capture_output=True
            )
            if fwd_check.returncode != 0:
                self._run(["iptables", "-I", "FORWARD", "1", "-s", subnet, "-j", "ACCEPT"], check=False)

            # RELATED,ESTABLISHED — always ensure it's there (idempotent via check)
            fwd_est_check = subprocess.run(
                ["iptables", "-C", "FORWARD", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"],
                capture_output=True
            )
            if fwd_est_check.returncode != 0:
                self._run(["iptables", "-I", "FORWARD", "1", "-m", "state",
                           "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"], check=False)

            # NAT rule — check before adding (no duplicates)
            nat_check = subprocess.run(
                ["iptables", "-t", "nat", "-C", "POSTROUTING", "-s", subnet, "-o", iface, "-j", "MASQUERADE"],
                capture_output=True
            )
            if nat_check.returncode != 0:
                self._run(["iptables", "-t", "nat", "-A", "POSTROUTING",
                           "-s", subnet, "-o", iface, "-j", "MASQUERADE"], check=False)

            # UFW Route Allowance
            if subprocess.run(["which", "ufw"], capture_output=True).returncode == 0:
                self._run(["ufw", "route", "allow", "from", subnet, "to", "any"], check=False)
                self._run(["ufw", "default", "allow", "routed"], check=False)

            # TCP MSS Clamping — subnet-specific (no duplicates via check)
            mss_check = subprocess.run(
                ["iptables", "-t", "mangle", "-C", "FORWARD", "-p", "tcp",
                 "--tcp-flags", "SYN,RST", "SYN", "-s", subnet,
                 "-j", "TCPMSS", "--set-mss", "1350"],
                capture_output=True
            )
            if mss_check.returncode != 0:
                self._run(["iptables", "-t", "mangle", "-I", "FORWARD", "1",
                           "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN",
                           "-s", subnet, "-j", "TCPMSS", "--set-mss", "1350"], check=False)

            # Persistent NAT
            self._persist_nat_rule(subnet, iface)

        except Exception as e:
            log.error(f"[{self.PROTOCOL_NAME}] NAT setup error: {e}")

    def _allow_port(self, port: int, proto: str = "udp"):
        """Open inbound port in UFW and Iptables."""
        log.info(f"[{self.PROTOCOL_NAME}] Opening port {port}/{proto} in firewall")
        try:
            # Iptables rule (runtime)
            self._run(["iptables", "-I", "INPUT", "1", "-p", proto, "--dport", str(port), "-j", "ACCEPT"], check=False)
            # UFW rule (persistent)
            if subprocess.run(["which", "ufw"], capture_output=True).returncode == 0:
                self._run(["ufw", "allow", f"{port}/{proto}"], check=False)
        except Exception as e:
            log.warning(f"[{self.PROTOCOL_NAME}] Failed to allow port {port}: {e}")

    def _deny_port(self, port: int, proto: str = "udp"):
        """Remove inbound port from UFW and Iptables."""
        log.info(f"[{self.PROTOCOL_NAME}] Closing port {port}/{proto} in firewall")
        try:
            subprocess.run(["iptables", "-D", "INPUT", "-p", proto, "--dport", str(port), "-j", "ACCEPT"],
                           capture_output=True, check=False)
            if subprocess.run(["which", "ufw"], capture_output=True).returncode == 0:
                self._run(["ufw", "delete", "allow", f"{port}/{proto}"], check=False)
        except Exception:
            pass

    def _persist_nat_rule(self, subnet: str, iface: str):
        """Add a NAT MASQUERADE rule to /etc/ufw/before.rules for persistence across reboots.
        Uses tagged blocks for idempotent updates. Only writes to the *nat table section.
        """
        before_rules = "/etc/ufw/before.rules"
        subnet = self._normalize_subnet(subnet)
        tag_start = f"# SKYNET-NAT-{subnet}"
        tag_end = f"# SKYNET-NAT-{subnet}-END"

        # The NAT-only block (no *filter here — UFW manages that via 'ufw route allow')
        nat_block = (
            f"\n{tag_start}\n"
            f"*nat\n"
            f":POSTROUTING ACCEPT [0:0]\n"
            f"-A POSTROUTING -s {subnet} -o {iface} -j MASQUERADE\n"
            f"COMMIT\n"
            f"{tag_end}\n"
        )

        try:
            if not os.path.exists(before_rules):
                log.warning(f"[{self.PROTOCOL_NAME}] {before_rules} not found, skipping persistence.")
                return

            with open(before_rules, "r") as f:
                content = f.read()

            # Don't duplicate
            if tag_start in content:
                log.info(f"[{self.PROTOCOL_NAME}] NAT rule for {subnet} already in {before_rules}")
                return

            # Insert the *nat block BEFORE the first *filter line (UFW's structure)
            # This ensures the nat table is processed correctly by iptables-restore
            if "*filter" in content:
                insert_pos = content.find("*filter")
                new_content = content[:insert_pos] + nat_block + "\n" + content[insert_pos:]
            else:
                # Append at end as fallback
                new_content = content + nat_block

            with open(before_rules, "w") as f:
                f.write(new_content)
            log.info(f"[{self.PROTOCOL_NAME}] Persistent NAT written to {before_rules} for {subnet}")
        except Exception as e:
            log.warning(f"[{self.PROTOCOL_NAME}] Failed to persist NAT rule: {e}")

    def _cleanup_nat(self, subnet: str):
        """Удалить правила NAT и FORWARD для указанной подсети."""
        subnet = self._normalize_subnet(subnet)
        iface = self._get_external_iface()
        log.info(f"[{self.PROTOCOL_NAME}] Cleaning up NAT for {subnet}")
        try:
            # Remove FORWARD rules (loop to catch duplicates)
            for _ in range(5):
                r = subprocess.run(
                    ["iptables", "-D", "FORWARD", "-s", subnet, "-j", "ACCEPT"],
                    capture_output=True
                )
                if r.returncode != 0:
                    break

            # Remove NAT rules (loop to catch duplicates)
            for _ in range(5):
                r = subprocess.run(
                    ["iptables", "-t", "nat", "-D", "POSTROUTING",
                     "-s", subnet, "-o", iface, "-j", "MASQUERADE"],
                    capture_output=True
                )
                if r.returncode != 0:
                    break

            # Remove MSS clamping
            for _ in range(5):
                r = subprocess.run(
                    ["iptables", "-t", "mangle", "-D", "FORWARD", "-p", "tcp",
                     "--tcp-flags", "SYN,RST", "SYN", "-s", subnet,
                     "-j", "TCPMSS", "--set-mss", "1350"],
                    capture_output=True
                )
                if r.returncode != 0:
                    break

            # UFW Cleanup
            if subprocess.run(["which", "ufw"], capture_output=True).returncode == 0:
                subprocess.run(
                    ["ufw", "route", "delete", "allow", "from", subnet, "to", "any"],
                    capture_output=True
                )

            # Remove persistent NAT rule from before.rules
            self._remove_persist_nat_rule(subnet)
        except Exception as e:
            log.debug(f"[{self.PROTOCOL_NAME}] NAT cleanup error (expected if rules gone): {e}")

    def _remove_persist_nat_rule(self, subnet: str):
        """Remove the tagged NAT block from /etc/ufw/before.rules."""
        before_rules = "/etc/ufw/before.rules"
        subnet = self._normalize_subnet(subnet)
        tag_start = f"# SKYNET-NAT-{subnet}"
        tag_end = f"# SKYNET-NAT-{subnet}-END"
        try:
            if not os.path.exists(before_rules):
                return
            with open(before_rules, "r") as f:
                content = f.read()

            if tag_start not in content:
                return

            new_lines = []
            skip = False
            for line in content.splitlines(keepends=True):
                if tag_start in line and tag_end not in line:
                    skip = True
                    continue
                if tag_end in line:
                    skip = False
                    continue
                if not skip:
                    new_lines.append(line)

            with open(before_rules, "w") as f:
                f.writelines(new_lines)
            log.info(f"[{self.PROTOCOL_NAME}] Removed persistent NAT for {subnet}")
        except Exception as e:
            log.warning(f"[{self.PROTOCOL_NAME}] Failed to remove persistent NAT rule: {e}")


class AdapterFactory:
    """Фабрика адаптеров — возвращает экземпляр по имени протокола."""

    _registry: dict = {}

    @classmethod
    def register(cls, protocol_name: str, adapter_class):
        cls._registry[protocol_name] = adapter_class

    @classmethod
    def get(cls, protocol_name: str, db_conn=None) -> ProtocolAdapter:
        adapter_class = cls._registry.get(protocol_name)
        if not adapter_class:
            raise ValueError(f"Unknown protocol: {protocol_name}. "
                             f"Available: {list(cls._registry.keys())}")
        return adapter_class(db_conn)

    @classmethod
    def available_protocols(cls) -> list:
        return list(cls._registry.keys())
