"""
AmneziaWG v2 Adapter
─────────────────────
Расширение v1 с поддержкой:
  S3, S4       — паддинг Cookie- и Data-сообщений
  I1–I5        — Custom Protocol Signature пакеты
  H1-H4        — теперь поддерживают диапазоны (e.g. "123-456")

Формат CPS-пакетов (I1-I5):
  <b 0xHEX>  — статические байты
  <r SIZE>   — случайные байты
  <rd SIZE>  — случайные цифры
  <rc SIZE>  — случайные буквы
  <t>        — UNIX timestamp (4 байта)
"""

import json
from .amneziawg_v1 import AmneziaWGv1Adapter, DEFAULT_AWG_V1_OBFUSCATION
from . import AdapterFactory

# Расширенные дефолты для v2
DEFAULT_AWG_V2_OBFUSCATION = {
    **DEFAULT_AWG_V1_OBFUSCATION,
    "S3": 69,
    "S4": 69,
    "H1": "5-2147483647",   # Диапазонный формат
    "H2": "5-2147483647",
    "H3": "5-2147483647",
    "H4": "5-2147483647",
    "I1": "",  # Пусто = не используется
    "I2": "",
    "I3": "",
    "I4": "",
    "I5": "",
}


class AmneziaWGv2Adapter(AmneziaWGv1Adapter):
    PROTOCOL_NAME = "amneziawg_v2"
    REQUIRED_BINARIES = ["awg", "awg-quick"]

    def generate_server_config(self, inbound: dict) -> str:
        """Генерация серверного конфига с v2-параметрами."""
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))

        # Merge v2 defaults
        for k, v in DEFAULT_AWG_V2_OBFUSCATION.items():
            obfs.setdefault(k, v)

        private_key = settings.get("private_key", "")
        address = settings.get("address", "10.8.0.1/24")
        mtu = settings.get("mtu", 1420)
        port = inbound.get("port", 51820)

        # Detect default interface
        import subprocess
        try:
            iface_out = subprocess.check_output("ip route get 8.8.8.8 | grep dev | awk '{print $5}'", shell=True).decode().strip()
            if not iface_out: iface_out = "ens18" 
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
            "# AmneziaWG v2 Obfuscation Parameters",
            f"S1 = {obfs['S1']}",
            f"S2 = {obfs['S2']}",
            f"S3 = {obfs['S3']}",
            f"S4 = {obfs['S4']}",
            f"H1 = {obfs['H1']}",
            f"H2 = {obfs['H2']}",
            f"H3 = {obfs['H3']}",
            f"H4 = {obfs['H4']}",
        ]

        # Добавить CPS-пакеты (I1-I5) если заданы
        for i_key in ["I1", "I2", "I3", "I4", "I5"]:
            val = obfs.get(i_key, "")
            if val:
                lines.append(f"{i_key} = {val}")

        # Peer-секции
        clients = settings.get("clients", [])
        for c in clients:
            if not c.get("enabled", True):
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
        """Клиентский конфиг AWG v2 — добавляем S3, S4, I1-I5."""
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))

        for k, v in DEFAULT_AWG_V2_OBFUSCATION.items():
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
            "# AmneziaWG v2 Obfuscation",
            f"Jc = {obfs.get('Jc', 5)}",
            f"Jmin = {obfs.get('Jmin', 50)}",
            f"Jmax = {obfs.get('Jmax', 1000)}",
            f"S1 = {obfs['S1']}",
            f"S2 = {obfs['S2']}",
            f"S3 = {obfs['S3']}",
            f"S4 = {obfs['S4']}",
            f"H1 = {obfs['H1']}",
            f"H2 = {obfs['H2']}",
            f"H3 = {obfs['H3']}",
            f"H4 = {obfs['H4']}",
        ]

        # CPS packets
        for i_key in ["I1", "I2", "I3", "I4", "I5"]:
            val = obfs.get(i_key, "")
            if val:
                lines.append(f"{i_key} = {val}")

        lines += [
            "",
            "[Peer]",
            f"PublicKey = {server_pub}",
            f"PresharedKey = {client.get('preshared_key', '')}",
            f"Endpoint = {server_ip}:{port}",
            "AllowedIPs = 0.0.0.0/0, ::/0",
            "PersistentKeepalive = 25",
        ]
        return "\n".join(lines) + "\n"


# Регистрация
AdapterFactory.register("amneziawg_v2", AmneziaWGv2Adapter)
