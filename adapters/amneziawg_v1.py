"""
AmneziaWG v1 (Legacy) Adapter
──────────────────────────────
Управляет WireGuard-интерфейсами с параметрами обфускации:
  Jc, Jmin, Jmax — мусорные пакеты (только клиент)
  S1, S2          — паддинг хендшейка (сервер + клиент)
  H1, H2, H3, H4 — фиксированные заголовки пакетов (сервер + клиент)

Используемые образы:
  - amneziavpn/amneziawg-go:latest — содержит awg + awg-quick (AmneziaWG бинарники)
  - amneziavpn/amnezia-wg:latest   — только wg-quick (стандартный WireGuard, НЕ AWG)
"""

import json
import os
import time
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

# Образ с AmneziaWG бинарниками (awg-quick is in /usr/bin/)
AWG_DOCKER_IMAGE = "skynet-local/amneziawg:latest"


class AmneziaWGv1Adapter(ProtocolAdapter):
    PROTOCOL_NAME = "amneziawg_v1"
    REQUIRED_BINARIES = ["docker"]
    INTERFACE_PREFIX = "awg"
    CONFIG_DIR = "/etc/amnezia/amneziawg"

    def __init__(self, db_conn=None):
        super().__init__(db_conn)

    def install(self, server_ip: str):
        log.info(f"[{self.PROTOCOL_NAME}] Checking autonomous AmneziaWG Docker image...")
        # Image is built during install.sh, but just in case:
        res = subprocess.run(["docker", "images", "-q", AWG_DOCKER_IMAGE], capture_output=True, text=True)
        if not res.stdout.strip():
            log.warning(f"[{self.PROTOCOL_NAME}] Image {AWG_DOCKER_IMAGE} not found. Attempting local build...")
            self._run(["docker", "build", "-t", AWG_DOCKER_IMAGE, "/opt/sky-net/docker/amneziawg"], check=False)

    def generate_keypair(self) -> dict:
        """Generate keys using the AWG binary inside a temporary Docker container."""
        try:
            # 1. Private Key
            priv = self._run(["docker", "run", "--rm", AWG_DOCKER_IMAGE, "awg", "genkey"])
            # 2. Public Key (pipe private key into pubkey)
            pub_proc = subprocess.run(
                ["docker", "run", "--rm", "-i", AWG_DOCKER_IMAGE, "awg", "pubkey"],
                input=priv + "\n", capture_output=True, text=True, check=True
            )
            pub = pub_proc.stdout.strip()
            # 3. Preshared Key
            psk = self._run(["docker", "run", "--rm", AWG_DOCKER_IMAGE, "awg", "genpsk"])
            
            return {"private_key": priv, "public_key": pub, "preshared_key": psk}
        except Exception as e:
            log.error(f"[{self.PROTOCOL_NAME}] Docker-based keygen failed: {e}")
            # Fallback to host 'wg' if available
            try:
                priv = self._run(["wg", "genkey"])
                pub = subprocess.run(["wg", "pubkey"], input=priv+"\n", capture_output=True, text=True).stdout.strip()
                psk = self._run(["wg", "genpsk"])
                return {"private_key": priv, "public_key": pub, "preshared_key": psk}
            except Exception:
                raise Exception(f"Key generation failed (Docker and Host): {e}")

    def _iface_name(self, inbound: dict) -> str:
        return f"{self.INTERFACE_PREFIX}{inbound['id']}"

    def _config_path(self, inbound: dict) -> str:
        iface = self._iface_name(inbound)
        return f"{self.CONFIG_DIR}/{iface}.conf"

    def generate_server_config(self, inbound: dict) -> str:
        """Генерация серверного awgN.conf файла."""
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))

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
            "",
            "# AmneziaWG v1 Obfuscation Parameters",
            f"S1 = {obfs['S1']}",
            f"S2 = {obfs['S2']}",
            f"H1 = {obfs['H1']}",
            f"H2 = {obfs['H2']}",
            f"H3 = {obfs['H3']}",
            f"H4 = {obfs['H4']}",
        ]

        clients = settings.get("clients", [])
        for c in clients:
            if not c.get("enable", True):
                continue
            lines.append("")
            lines.append(f"# Client: {c.get('username', 'unknown')}")
            lines.append("[Peer]")
            lines.append(f"PublicKey = {c['public_key']}")
            if c.get("preshared_key"):
                lines.append(f"PresharedKey = {c['preshared_key']}")
            lines.append(f"AllowedIPs = {c.get('allowed_ips', '10.8.0.2/32')}")

        return "\n".join(lines) + "\n"

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

        # Client address: use the /32 address but present as /24 in interface
        client_addr = client.get('allowed_ips', '10.8.0.2/32')
        # Convert 10.8.0.2/32 -> 10.8.0.2/24 for client interface
        try:
            client_net = ipaddress.ip_interface(client_addr)
            # Get the full network
            full_net = ipaddress.ip_network(client_addr.replace("/32", "/24"), strict=False)
            client_interface_addr = f"{client_net.ip}/{full_net.prefixlen}"
        except Exception:
            client_interface_addr = client_addr

        lines = [
            "[Interface]",
            f"PrivateKey = {client.get('private_key', '')}",
            f"Address = {client_interface_addr}",
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
        return "\n".join(lines) + "\n"

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
                self._run(["docker", "exec", container_name, "awg", "set", iface,
                           "peer", client["public_key"],
                           "allowed-ips", allowed_ips,
                           "preshared-key", f"/etc/amnezia/amneziawg/psk_{client['username']}.key"])
            finally:
                if os.path.exists(psk_file):
                    os.remove(psk_file)
        else:
            self._run(["docker", "exec", container_name, "awg", "set", iface,
                       "peer", client["public_key"], "allowed-ips", allowed_ips])

        # Also update the persistent config
        conf_path = self._config_path(inbound)
        if os.path.exists(conf_path):
            self._run(["docker", "exec", container_name, "awg", "saveconfig", iface], check=False)

        return True

    def remove_client(self, client: dict, inbound: dict) -> bool:
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        iface = self._iface_name(inbound)
        self._run(["docker", "exec", container_name, "awg", "set", iface,
                   "peer", client["public_key"], "remove"])
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
            for line in lines[1:]:  # First line is interface info
                parts = line.strip().split('\t')
                if len(parts) >= 7:
                    try:
                        clients.append({
                            "public_key": parts[0],
                            "preshared_key": parts[1] if parts[1] != "(none)" else "",
                            "endpoint": parts[2] if parts[2] != "(none)" else "",
                            "allowed_ips": parts[3],
                            "last_handshake": int(parts[4]),
                            "rx": int(parts[5]),
                            "tx": int(parts[6]),
                        })
                    except (ValueError, IndexError):
                        continue
            return clients
        except Exception:
            return []

    def start(self, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        os.makedirs(self.CONFIG_DIR, exist_ok=True)

        # Write server config
        conf = self._config_path(inbound)
        with open(conf, "w") as f:
            f.write(self.generate_server_config(inbound))

        # Get subnet (always use network address, not host address)
        settings = json.loads(inbound.get("settings", "{}"))
        address = settings.get("address", "10.8.0.0/24")
        try:
            net = ipaddress.ip_network(address, strict=False)
            subnet = str(net)
        except Exception:
            subnet = "10.8.0.0/24"

        # PROACTIVE CLEANUP: Remove stale containers and interfaces
        log.info(f"[{self.PROTOCOL_NAME}] Stopping any stale instance of {container_name}")
        self.stop(inbound)

        # Also check if interface somehow persists after stop
        res = subprocess.run(["ip", "link", "show", iface], capture_output=True, text=True)
        if res.returncode == 0:
            log.warning(f"[{self.PROTOCOL_NAME}] Interface {iface} still exists after stop, forcing delete...")
            subprocess.run(["ip", "link", "delete", iface], capture_output=True, check=False)

        log.info(f"[{self.PROTOCOL_NAME}] Starting container {container_name} with image {AWG_DOCKER_IMAGE}")
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--restart", "unless-stopped",
            "--network", "host",
            "--cap-add", "NET_ADMIN",
            "--device", "/dev/net/tun",
            "-v", f"{self.CONFIG_DIR}:/etc/amnezia/amneziawg",
            "--entrypoint", "/bin/bash",
            AWG_DOCKER_IMAGE,
            "-c",
            f"awg-quick up /etc/amnezia/amneziawg/{iface}.conf && tail -f /dev/null"
        ]
        self._run(cmd)
        self._setup_nat(subnet)

        # Wait for container to be ready
        log.info(f"[{self.PROTOCOL_NAME}] Waiting for interface {iface} to come up...")
        for _ in range(10):
            res = subprocess.run(["docker", "exec", container_name, "awg", "show", iface], capture_output=True)
            if res.returncode == 0:
                log.info(f"[{self.PROTOCOL_NAME}] Interface {iface} is UP")
                return True
            time.sleep(1)
        
        log.error(f"[{self.PROTOCOL_NAME}] Interface {iface} failed to come up within 10s")
        return True # Still return True to avoid stopping the server setup, but log error

    def stop(self, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        try:
            settings = json.loads(inbound.get("settings", "{}"))
            address = settings.get("address", "10.8.0.0/24")
            subnet = self._normalize_subnet(address)
            self._cleanup_nat(subnet)
            subprocess.run(["docker", "rm", "-f", container_name],
                           capture_output=True, check=False)
            # Interface cleanup (docker --network host leaves interfaces on host)
            subprocess.run(["ip", "link", "delete", iface],
                           capture_output=True, check=False)
        except Exception:
            pass
        return True

    def is_running(self, inbound: dict) -> bool:
        container_name = f"skynet_{inbound['protocol']}_{inbound['id']}"
        try:
            res = subprocess.run(
                ["docker", "inspect", "-f", "{{.State.Running}}", container_name],
                capture_output=True, text=True
            )
            return res.stdout.strip() == "true"
        except Exception:
            return False


AdapterFactory.register("amneziawg_v1", AmneziaWGv1Adapter)
