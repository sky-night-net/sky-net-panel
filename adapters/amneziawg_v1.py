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
        self.check_binaries(["awg"])
        priv = self._run(["awg", "genkey"])
        pub = self._run(["bash", "-c", f"echo '{priv}' | awg pubkey"])
        psk = self._run(["awg", "genpsk"])
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
            f"PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o {iface_out} -j MASQUERADE",
            f"PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o {iface_out} -j MASQUERADE",
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
        cmd = ["awg", "set", iface, "peer", client["public_key"], "allowed-ips", client.get("allowed_ips", "10.8.0.2/32")]
        if client.get("preshared_key"):
            # Для PSK используем временный файл или echo так как _run не поддерживает stdin напрямую в текущем виде
            self._run(["bash", "-c", f"echo '{client['preshared_key']}' > /tmp/psk_{iface} && awg set {iface} peer {client['public_key']} preshared-key /tmp/psk_{iface} && rm /tmp/psk_{iface}"])
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
            output = self._run(["awg", "show", iface, "transfer"])
            clients = []
            for line in output.split("\n"):
                if not line.strip(): continue
                parts = line.split("\t")
                if len(parts) >= 3:
                    clients.append({"public_key": parts[0].strip(), "rx": int(parts[1].strip()), "tx": int(parts[2].strip())})
            return clients
        except: return []

    def start(self, inbound: dict) -> bool:
        iface = self._iface_name(inbound)
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        conf = self._config_path(inbound)
        with open(conf, "w") as f: f.write(self.generate_server_config(inbound))
        self._run(["awg-quick", "up", conf])
        return True

    def stop(self, inbound: dict) -> bool:
        try: self._run(["awg-quick", "down", self._config_path(inbound)])
        except: pass
        return True

    def is_running(self, inbound: dict) -> bool:
        try:
            self._run(["awg", "show", self._iface_name(inbound)])
            return True
        except: return False

    def install(self, server_ip: str):
        # Реализация установки уже была, просто приводим к стилю
        self._run(["apt-get", "update"])
        self._run(["apt-get", "install", "-y", "git", "golang", "make"])
        if not os.path.exists("/usr/local/bin/awg"):
            self._run(["git", "clone", "https://github.com/amnezia-vpn/amneziawg-tools.git", "/tmp/awg-tools"])
            self._run(["make", "-C", "/tmp/awg-tools/src"])
            self._run(["cp", "/tmp/awg-tools/src/wg", "/usr/local/bin/awg"])
            self._run(["cp", "/tmp/awg-tools/src/wg-quick/linux.bash", "/usr/local/bin/awg-quick"])
            self._run(["chmod", "+x", "/usr/local/bin/awg", "/usr/local/bin/awg-quick"])

AdapterFactory.register("amneziawg_v1", AmneziaWGv1Adapter)
