"""
AmneziaWG v1 (Legacy) Adapter
──────────────────────────────
Управляет WireGuard-интерфейсами с параметрами обфускации:
  Jc, Jmin, Jmax — мусорные пакеты (только клиент)
  S1, S2          — паддинг хендшейка (сервер + клиент)
  H1, H2, H3, H4 — фиксированные заголовки пакетов (сервер + клиент)

Используемые утилиты на сервере:
  - awg (amneziawg-tools) — управление интерфейсом
  - awg-quick             — быстрый запуск/остановка
  - awg genkey / pubkey   — генерация ключей
"""

import json
import os
import ipaddress
import logging
import subprocess
import re
from . import ProtocolAdapter, AdapterFactory

log = logging.getLogger(__name__)

# Дефолтные параметры обфускации AWG v1
DEFAULT_AWG_V1_OBFUSCATION = {
    "Jc": 5,
    "Jmin": 50,
    "Jmax": 1000,
    "S1": 69,
    "S2": 115,
    "H1": 924883749,
    "H2": 16843009,
    "H3": 305419896,
    "H4": 878082202,
}


class AmneziaWGv1Adapter(ProtocolAdapter):
    PROTOCOL_NAME = "amneziawg_v1"
    REQUIRED_BINARIES = ["docker"]
    INTERFACE_PREFIX = "awg"
    CONFIG_DIR = "/etc/amnezia/amneziawg"

    def __init__(self, db_conn=None):
        super().__init__(db_conn)

    def install(self, server_ip: str):
        log.info(f"[{self.PROTOCOL_NAME}] Checking AmneziaWG Docker images...")
        self._run(["docker", "pull", "amneziavpn/amnezia-wg:latest"])
        self._run(["docker", "pull", "amneziavpn/amneziawg-go:latest"])

    def generate_keypair(self) -> dict:
        # Use native wg tool (installed via wireguard-tools on host) for instant/safe keygen
        # AmneziaWG curve25519 keys are 100% mathematically identical to WireGuard keys
        priv = self._run(["wg", "genkey"])
        
        import subprocess
        proc = subprocess.run(["wg", "pubkey"], input=priv + "\n", capture_output=True, text=True, check=True)
        pub = proc.stdout.strip()
        
        psk = self._run(["wg", "genpsk"])
        return {"private_key": priv, "public_key": pub, "preshared_key": psk}

    def _iface_name(self, inbound: dict) -> str:
        return f"{self.INTERFACE_PREFIX}{inbound['id']}"

    def _config_path(self, inbound: dict) -> str:
        iface = self._iface_name(inbound)
        return f"{self.CONFIG_DIR}/{iface}.conf"

    def generate_server_config(self, inbound: dict) -> str:
        """Генерация серверного awgN.conf файла."""
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))

        # Merge defaults
        for k, v in DEFAULT_AWG_V1_OBFUSCATION.items():
            obfs.setdefault(k, v)

        private_key = settings.get("private_key", "")
        address = settings.get("address", "10.8.0.1/24")
        mtu = settings.get("mtu", 1420)
        port = inbound.get("port", 51820)

        lines = [
            "[Interface]",
            f"PrivateKey = {private_key}",
            f"Address = {address}",
            f"ListenPort = {port}",
            f"MTU = {mtu}",
            "# NAT and Forwarding are managed by the panel's central routing engine",
            "",
            "# AmneziaWG v1 Obfuscation Parameters",
            f"S1 = {obfs['S1']}",
            f"S2 = {obfs['S2']}",
            f"H1 = {obfs['H1']}",
            f"H2 = {obfs['H2']}",
            f"H3 = {obfs['H3']}",
            f"H4 = {obfs['H4']}",
        ]

        # Добавить Peer-секции клиентов
        clients = settings.get("clients", [])
        for c in clients:
            if not c.get("enable", True): continue
            lines.append("")
            lines.append(f"# Client: {c.get('username', 'unknown')}")
            lines.append("[Peer]")
            lines.append(f"PublicKey = {c['public_key']}")
            if c.get("preshared_key"):
                lines.append(f"PresharedKey = {c['preshared_key']}")
            lines.append(f"AllowedIPs = {c.get('allowed_ips', '10.8.0.2/32')}")

        return "\n".join(lines)

    def generate_client_config(self, client: dict, inbound: dict) -> str:
        """Генерация клиентского .conf файла."""
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))

        for k, v in DEFAULT_AWG_V1_OBFUSCATION.items():
            obfs.setdefault(k, v)

        server_pub = settings.get("public_key", "")
        server_ip = settings.get("server_ip", "0.0.0.0")
        port = inbound.get("port", 51820)
        dns = settings.get("dns", "1.1.1.1, 8.8.8.8")
        mtu = settings.get("mtu", 1420)

        lines = [
            "[Interface]",
            f"PrivateKey = {client.get('private_key', '')}",
            f"Address = {client.get('allowed_ips', '10.8.0.2/32')}",
            f"DNS = {dns}",
            f"MTU = {mtu}",
            "",
            "# AmneziaWG v1 Obfuscation (Junk packets: client-only)",
            f"Jc = {obfs['Jc']}",
            f"Jmin = {obfs['Jmin']}",
            f"Jmax = {obfs['Jmax']}",
            f"S1 = {obfs['S1']}",
            f"S2 = {obfs['S2']}",
            f"H1 = {obfs['H1']}",
            f"H2 = {obfs['H2']}",
            f"H3 = {obfs['H3']}",
            f"H4 = {obfs['H4']}",
            "",
            "[Peer]",
            f"PublicKey = {server_pub}",
            f"PresharedKey = {client.get('preshared_key', '')}",
            f"Endpoint = {server_ip}:{port}",
            "AllowedIPs = 0.0.0.0/0, ::/0",
            "PersistentKeepalive = 25",
        ]
        return "\n".join(lines)

    def add_client(self, client: dict, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        self.check_binaries(["docker"])
        
        allowed_ips = client.get("allowed_ips", "10.8.0.2/32")
        
        if client.get("preshared_key"):
            psk_file = os.path.join(self.CONFIG_DIR, f"psk_{client['username']}.key")
            with open(psk_file, 'w') as f:
                f.write(client['preshared_key'] + '\n')
            try:
                self._run(["docker", "exec", container_name, "awg", "set", iface, "peer", client["public_key"], 
                          "allowed-ips", allowed_ips, 
                          "preshared-key", f"/etc/amnezia/amneziawg/psk_{client['username']}.key"])
            finally:
                if os.path.exists(psk_file): os.remove(psk_file)
        else:
            self._run(["docker", "exec", container_name, "awg", "set", iface, "peer", client["public_key"], "allowed-ips", allowed_ips])
            
        return True

    def remove_client(self, client: dict, inbound: dict) -> bool:
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        iface = self._iface_name(inbound)
        self._run(["docker", "exec", container_name, "awg", "set", iface, "peer", client["public_key"], "remove"])
        return True

    def toggle_client(self, client: dict, inbound: dict, enable: bool) -> bool:
        return self.add_client(client, inbound) if enable else self.remove_client(client, inbound)

    def get_traffic(self, inbound: dict) -> list:
        iface = self._iface_name(inbound)
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        
        try:
            dump = self._run(["docker", "exec", container_name, "awg", "show", iface, "dump"])
            lines = dump.split('\n')
            clients = []
            for line in lines[1:]: # Первая строка - инфо об интерфейсе
                parts = line.strip().split('\t')
                if len(parts) >= 6:
                    clients.append({
                        "public_key": parts[0],
                        "preshared_key": parts[1] if parts[1] != "(none)" else "",
                        "endpoint": parts[2] if parts[2] != "(none)" else "",
                        "allowed_ips": parts[3],
                        "rx": int(parts[5].strip()),
                        "tx": int(parts[6].strip()),
                        "last_handshake": int(parts[4].strip())
                    })
            return clients
        except: return []

    def start(self, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        conf = self._config_path(inbound)
        with open(conf, "w") as f: f.write(self.generate_server_config(inbound))
        
        settings = json.loads(inbound.get("settings", "{}"))
        subnet = settings.get("address", "10.8.0.0/24")
        if "/" not in subnet: subnet = "10.8.0.0/24" # safety
        try:
            net = ipaddress.ip_network(subnet, strict=False)
            subnet = str(net)
            server_ip = str(list(net.hosts())[0]) # usually .1
        except: server_ip = "10.8.0.1"

        # PROACTIVE CLEANUP: Check for conflicting interfaces or IPs on host
        log.info(f"[{self.PROTOCOL_NAME}] Checking for host conflicts (iface: {iface}, ip: {server_ip})")
        try:
            # Check if interface already exists
            res = subprocess.run(["ip", "link", "show", iface], capture_output=True, text=True)
            if res.returncode == 0:
                log.warning(f"[{self.PROTOCOL_NAME}] Interface {iface} already exists on host. Deleting...")
                subprocess.run(["ip", "link", "delete", iface], check=False)

            # Check if IP is already assigned to ANY interface
            res = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True)
            if server_ip in res.stdout:
                log.warning(f"[{self.PROTOCOL_NAME}] IP {server_ip} already assigned on host. Finding and deleting interface...")
                # Find which interface has this IP
                match = re.search(r'inet\s+' + re.escape(server_ip) + r'.*?dev\s+([a-zA-Z0-9_\-]+)', res.stdout)
                if match:
                    conflicting_iface = match.group(1)
                    log.warning(f"[{self.PROTOCOL_NAME}] Deleting conflicting interface {conflicting_iface}")
                    subprocess.run(["ip", "link", "delete", conflicting_iface], check=False)
        except Exception as e:
            log.error(f"[{self.PROTOCOL_NAME}] Conflict resolution failed: {e}")

        self.stop(inbound)

        log.info(f"[{self.PROTOCOL_NAME}] Starting Docker container {container_name}")
        # Use official AmneziaWG images. AWG-GO is more compatible with newer kernels.
        img = "amneziavpn/amneziawg-go:latest"

        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--restart", "unless-stopped",
            "--network", "host",
            "--cap-add", "NET_ADMIN",
            "--device", "/dev/net/tun",
            "-v", f"{self.CONFIG_DIR}:/etc/amnezia/amneziawg",
            "--entrypoint", "sh",
            img,
            "-c", f"awg-quick up /etc/amnezia/amneziawg/{iface}.conf && tail -f /dev/null"
        ]
        self._run(cmd)
        self._setup_nat(subnet)
        return True

    def stop(self, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        try:
            settings = json.loads(inbound.get("settings", "{}"))
            subnet = settings.get("address", "10.8.0.0/24")
            self._cleanup_nat(subnet)
            self._run(["docker", "rm", "-f", container_name], check=False)
            # Since we use --network host, the interface might persist on host. Cleanup if possible.
            subprocess.run(["ip", "link", "delete", iface], check=False)
        except: pass
        return True

    def is_running(self, inbound: dict) -> bool:
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        try:
            res = self._run(["docker", "inspect", "-f", "{{.State.Running}}", container_name], check=False)
            return res.strip() == "true"
        except:
            return False

AdapterFactory.register("amneziawg_v1", AmneziaWGv1Adapter)
