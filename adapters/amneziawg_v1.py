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
from . import ProtocolAdapter, AdapterFactory

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
    REQUIRED_BINARIES = ["awg", "awg-quick"]
    INTERFACE_PREFIX = "awg"
    CONFIG_DIR = "/etc/amnezia/amneziawg"

    def __init__(self, db_conn=None):
        super().__init__(db_conn)

    def generate_keypair(self) -> dict:
        """Генерация PrivateKey + PublicKey через awg."""
        # Try finding awg in common paths
        awg_bin = "awg"
        for p in ["/usr/bin/awg", "/usr/local/bin/awg"]:
            if os.path.exists(p):
                awg_bin = p
                break
        
        priv = self._run([awg_bin, "genkey"])
        # Use subprocess directly to avoid shell injection and handle stdin properly
        import subprocess
        # Some versions of awg pubkey require the newline
        proc = subprocess.run([awg_bin, "pubkey"], input=priv + "\n", capture_output=True, text=True, check=True)
        pub = proc.stdout.strip()
        psk = self._run([awg_bin, "genpsk"])
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

        # Detect default interface
        import subprocess
        try:
            iface_out = subprocess.check_output("ip route get 8.8.8.8 | grep dev | awk '{print $5}'", shell=True).decode().strip()
            if not iface_out: iface_out = "ens18" # fallback
        except: iface_out = "ens18"

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
        return "\n".join(lines) + "\n"

    def add_client(self, client: dict, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        self.check_binaries(["awg"])
        
        allowed_ips = client.get("allowed_ips", "10.8.0.2/32")
        # Full command to set everything at once
        cmd = ["awg", "set", iface, "peer", client["public_key"], "allowed-ips", allowed_ips]
        
        if client.get("preshared_key"):
            # Use a temporary file for the PSK to avoid shell complexities
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
                tf.write(client['preshared_key'] + '\n')
                tf_path = tf.name
            try:
                self._run(["awg", "set", iface, "peer", client["public_key"], 
                          "allowed-ips", allowed_ips, 
                          "preshared-key", tf_path])
            finally:
                if os.path.exists(tf_path): os.remove(tf_path)
        else:
            self._run(cmd)
        return True

    def remove_client(self, client: dict, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        self._run(["awg", "set", iface, "peer", client["public_key"], "remove"])
        return True

    def toggle_client(self, client: dict, inbound: dict, enable: bool) -> bool:
        return self.add_client(client, inbound) if enable else self.remove_client(client, inbound)

    def get_traffic(self, inbound: dict) -> list:
        iface = self._iface_name(inbound)
        try:
            # Using 'dump' to get rx, tx AND latest handshake
            output = self._run(["awg", "show", iface, "dump"])
            clients = []
            for line in output.split("\n"):
                if not line.strip(): continue
                parts = line.split("\t")
                # Dump format: public_key [preshared_key] endpoint allowed_ips latest_handshake rx tx persistent_keepalive
                # But headers might be different. Let's check part count.
                # WG dump for peer: public_key  psk  endpoint  allowed_ips  latest_handshake  rx  tx  keepalive
                if len(parts) >= 8:
                    clients.append({
                        "public_key": parts[0].strip(),
                        "rx": int(parts[5].strip()),
                        "tx": int(parts[4].strip()), # Correcting tx/rx based on dump order
                        "last_handshake": int(parts[4].strip())
                    })
            return clients
        except: return []

    def start(self, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        conf = self._config_path(inbound)
        with open(conf, "w") as f: f.write(self.generate_server_config(inbound))
        
        # Centralized Routing Setup
        settings = json.loads(inbound.get("settings", "{}"))
        subnet = settings.get("address", "10.8.0.0/24")
        if "/" not in subnet: subnet = "10.8.0.0/24" # safety
        # Ensure it's a network address, not an IP
        try:
            net = ipaddress.ip_network(subnet, strict=False)
            subnet = str(net)
        except: pass

        # Ensure interface is down before starting
        try:
            self._run(["awg-quick", "down", conf])
        except: pass

        self._run(["awg-quick", "up", conf])
        self._setup_nat(subnet)
        
        return True

    def stop(self, inbound: dict) -> bool:
        try:
            settings = json.loads(inbound.get("settings", "{}"))
            subnet = settings.get("address", "10.8.0.0/24")
            self._run(["awg-quick", "down", self._config_path(inbound)])
            self._cleanup_nat(subnet)
        except: pass
        return True

    def is_running(self, inbound: dict) -> bool:
        try:
            self._run(["awg", "show", self._iface_name(inbound)])
            return True
        except: return False

    def install(self, server_ip: str):
        # Попытка установки через PPA
        self._run(["bash", "-c", "DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:amnezia/ppa -y || true"])
        self._run(["apt-get", "update"])
        try:
            self._run(["apt-get", "install", "-y", "amneziawg", "amneziawg-tools"])
        except:
            # Fallback to manual build if PPA fails
            log.info(f"[{self.PROTOCOL_NAME}] PPA install failed, building from source...")
            self._run(["apt-get", "install", "-y", "git", "golang", "make"])
            if not os.path.exists("/usr/bin/awg"):
                self._run(["git", "clone", "https://github.com/amnezia-vpn/amneziawg-tools.git", "/tmp/awg-tools"])
                self._run(["make", "-C", "/tmp/awg-tools/src"])
                self._run(["cp", "/tmp/awg-tools/src/wg", "/usr/bin/awg"])
                self._run(["cp", "/tmp/awg-tools/src/wg-quick/linux.bash", "/usr/bin/awg-quick"])
                self._run(["chmod", "+x", "/usr/bin/awg", "/usr/bin/awg-quick"])

AdapterFactory.register("amneziawg_v1", AmneziaWGv1Adapter)
