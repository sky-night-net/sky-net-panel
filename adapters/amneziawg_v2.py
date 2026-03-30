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
import ipaddress
from .amneziawg_v1 import AmneziaWGv1Adapter, DEFAULT_AWG_V1_OBFUSCATION
from . import AdapterFactory

# Расширенные дефолты для v2
DEFAULT_AWG_V2_OBFUSCATION = {
    **DEFAULT_AWG_V1_OBFUSCATION,
    "S3": 69,
    "S4": 69,
    "H1": "10000000-20000000",
    "H2": "20000001-30000000",
    "H3": "30000001-40000000",
    "H4": "40000001-50000000",
    "I1": "<b 0xabcd010000010000000000000562656c657402746d0000010001>",
    "I2": "<b 0x1234010000010000000000000573706565640562656c6574026d650000010001>",
    "I3": "",
    "I4": "",
    "I5": "",
}


class AmneziaWGv2Adapter(AmneziaWGv1Adapter):
    PROTOCOL_NAME = "amneziawg_v2"
    REQUIRED_BINARIES = ["docker", "wg"]

    def generate_server_config(self, inbound: dict) -> str:
        """Генерация серверного конфига с v2-параметрами."""
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))

        for k, v in DEFAULT_AWG_V2_OBFUSCATION.items():
            obfs.setdefault(k, v)

        private_key = settings.get("private_key", "")
        address = settings.get("address", "10.10.0.1/24")
        mtu = settings.get("mtu", 1420)
        port = inbound.get("port", 51820)

        lines = [
            "[Interface]",
            f"PrivateKey = {private_key}",
            f"Address = {address}",
            f"ListenPort = {port}",
            f"MTU = {mtu}",
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

        for i_key in ["I1", "I2", "I3", "I4", "I5"]:
            val = obfs.get(i_key, "")
            if val:
                lines.append(f"{i_key} = {val}")

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
            lines.append(f"AllowedIPs = {c.get('allowed_ips', '10.10.0.2/32')}")

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

        # Client address: convert /32 to /24 for the Interface section
        client_addr = client.get('allowed_ips', '10.10.0.2/32')
        try:
            client_net = ipaddress.ip_interface(client_addr)
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


AdapterFactory.register("amneziawg_v2", AmneziaWGv2Adapter)
