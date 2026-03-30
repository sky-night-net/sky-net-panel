"""
Sky-Net Protocol Adapters
─────────────────────────
Базовый класс и фабрика для протокольных адаптеров.
Каждый адаптер умеет: install, generate configs, add/remove clients, get traffic.
"""

import subprocess
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
            # Second check after install
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
        log.info(f"[{self.PROTOCOL_NAME}] exec: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            log.error(f"[{self.PROTOCOL_NAME}] failed: {e.cmd} | err: {e.stderr}")
            raise Exception(f"Ошибка команды: {e.stderr or str(e)}")

    def _get_external_iface(self) -> str:
        """Определить внешний сетевой интерфейс (с маршрутом по умолчанию)."""
        try:
            res = self._run(["ip", "route", "get", "8.8.8.8"], check=False)
            if not res:
                res = self._run(["ip", "-4", "route", "show", "default"], check=False)
            if not res: return "eth0"
            
            # Typical output: "8.8.8.8 via 192.168.1.1 dev ens18 src 192.168.1.2 uid 1000"
            parts = res.split()
            if "dev" in parts:
                idx = parts.index("dev")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
            return "eth0"
        except:
            return "eth0"

    def _setup_nat(self, subnet: str):
        """Настроить NAT (MASQUERADE) и пересылку (FORWARD) для указанной подсети.
        Rules are applied both at runtime (iptables) AND persistently (ufw before.rules).
        """
        iface = self._get_external_iface()
        log.info(f"[{self.PROTOCOL_NAME}] Setting up NAT for {subnet} via {iface}")
        try:
            # Enable IP Forwarding
            self._run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)

            # FORWARD rules (Insert at top to bypass UFW if needed)
            self._run(["iptables", "-I", "FORWARD", "-s", subnet, "-j", "ACCEPT"], check=False)
            self._run(["iptables", "-I", "FORWARD", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"], check=False)

            # NAT rule (append if not exists)
            check_cmd = ["iptables", "-t", "nat", "-C", "POSTROUTING", "-s", subnet, "-o", iface, "-j", "MASQUERADE"]
            res = subprocess.run(check_cmd, capture_output=True)
            if res.returncode != 0:
                self._run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-s", subnet, "-o", iface, "-j", "MASQUERADE"], check=False)

            # UFW Route Allowance (if UFW exists)
            res_ufw = subprocess.run(["which", "ufw"], capture_output=True)
            if res_ufw.returncode == 0:
                self._run(["ufw", "route", "allow", "from", subnet, "to", "any"], check=False)
                # Ensure global default forward policy is ALLOW for VPN to work
                # On Ubuntu 24.04, UFW might default 'routed' to 'drop'
                self._run(["ufw", "default", "allow", "routed"], check=False)

            # TCP MSS Clamping to avoid MTU issues (Crucial for mobile networks)
            self._run(["iptables", "-t", "mangle", "-I", "FORWARD", "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN", "-j", "TCPMSS", "--clamp-mss-to-pmtu"], check=False)
            self._run(["iptables", "-t", "mangle", "-I", "FORWARD", "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN", "-s", subnet, "-j", "TCPMSS", "--set-mss", "1350"], check=False)

            # ─── Persistent NAT: write to /etc/ufw/before.rules ─────
            self._persist_nat_rule(subnet, iface)
        except Exception as e:
            log.error(f"[{self.PROTOCOL_NAME}] NAT setup error: {e}")

    def _persist_nat_rule(self, subnet: str, iface: str):
        """Add a NAT MASQUERADE rule and FORWARD allows to /etc/ufw/before.rules for persistence."""
        before_rules = "/etc/ufw/before.rules"
        tag = f"# SKYNET-NAT-{subnet}"
        nat_block = [
            f"{tag}",
            f"*nat",
            f":POSTROUTING ACCEPT [0:0]",
            f"-A POSTROUTING -s {subnet} -o {iface} -j MASQUERADE",
            f"COMMIT",
            f"*filter",
            f":ufw-before-forward - [0:0]",
            f"-A ufw-before-forward -s {subnet} -j ACCEPT",
            f"-A ufw-before-forward -d {subnet} -j ACCEPT",
            f"COMMIT",
            f"{tag}-END\n"
        ]
        try:
            if not os.path.exists(before_rules):
                return
            with open(before_rules, "r") as f:
                content = f.read()
            
            if tag in content:
                return
            
            # Smart insertion: find the first line that is NOT a comment and insert BEFORE it
            lines = content.split('\n')
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('#'):
                    insert_idx = i
                    break
            
            # Insert at the top of the file (after comments) for maximum reliability
            new_content = lines[:insert_idx] + nat_block + lines[insert_idx:]
            with open(before_rules, "w") as f:
                f.write('\n'.join(new_content))
            log.info(f"[{self.PROTOCOL_NAME}] Persistent NAT written to {before_rules} for {subnet}")
        except Exception as e:
            log.warning(f"[{self.PROTOCOL_NAME}] Failed to persist NAT rule: {e}")

    def _cleanup_nat(self, subnet: str):
        """Удалить правила NAT и FORWARD для указанной подсети."""
        iface = self._get_external_iface()
        log.info(f"[{self.PROTOCOL_NAME}] Cleaning up NAT for {subnet}")
        try:
            self._run(["iptables", "-D", "FORWARD", "-s", subnet, "-j", "ACCEPT"], check=False)
            self._run(["iptables", "-t", "nat", "-D", "POSTROUTING", "-s", subnet, "-o", iface, "-j", "MASQUERADE"], check=False)
            self._run(["iptables", "-D", "INPUT", "-s", subnet, "-j", "ACCEPT"], check=False)

            # UFW Cleanup
            res_ufw = subprocess.run(["which", "ufw"], capture_output=True)
            if res_ufw.returncode == 0:
                self._run(["ufw", "route", "delete", "allow", "from", subnet, "to", "any"], check=False)

            # Remove persistent NAT rule from before.rules
            self._remove_persist_nat_rule(subnet)
        except Exception as e:
            log.debug(f"[{self.PROTOCOL_NAME}] NAT cleanup error (expected if rules gone): {e}")

    def _remove_persist_nat_rule(self, subnet: str):
        """Remove the tagged NAT block from /etc/ufw/before.rules."""
        before_rules = "/etc/ufw/before.rules"
        tag_start = f"# SKYNET-NAT-{subnet}"
        tag_end = f"{tag_start}-END"
        try:
            if not os.path.exists(before_rules):
                return
            with open(before_rules, "r") as f:
                lines = f.readlines()
            # Filter out the tagged block
            new_lines = []
            skip = False
            for line in lines:
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
