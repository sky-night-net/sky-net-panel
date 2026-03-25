"""
OpenVPN + XOR Patch (Tunnelblick) Adapter
──────────────────────────────────────────
Управляет OpenVPN-сервером с XOR-обфускацией.
Обфускация: `scramble obfuscate <password>` в server.conf и .ovpn клиентах.

Требования на сервере:
  - openvpn (собранный с XOR-патчем) ИЛИ Docker: jeff47/openvpn-xor
  - easyrsa (для PKI: генерация CA, сертификатов, ключей)

Файлы:
  - /etc/openvpn/server.conf     — серверный конфиг
  - /etc/openvpn/easy-rsa/       — PKI инфраструктура
  - /var/log/openvpn/status.log  — статус клиентов (для трафика)
"""

import json
import os
import re
import time
import subprocess
import logging
from datetime import datetime
from . import ProtocolAdapter, AdapterFactory


class OpenVPNXORAdapter(ProtocolAdapter):
    PROTOCOL_NAME = "openvpn_xor"
    REQUIRED_BINARIES = ["openvpn", "make-cadir"]
    CONFIG_DIR = "/etc/openvpn"
    EASYRSA_DIR = "/etc/openvpn/easy-rsa"
    STATUS_LOG = "/var/log/openvpn/status.log"

    def __init__(self, db_conn=None):
        super().__init__(db_conn)

    def install(self, server_ip: str):
        """Установить OpenVPN с XOR-патчем."""
        self._run(["apt-get", "update"])
        self._run(["apt-get", "install", "-y", "openvpn", "easy-rsa"])

    def generate_keypair(self) -> dict:
        """Инициализировать PKI (если нужно) и вернуть пути к CA."""
        self.check_binaries(["openvpn", "make-cadir"])
        if not os.path.exists(f"{self.EASYRSA_DIR}/pki"):
            # Clean up if partially exists
            self._run(["rm", "-rf", self.EASYRSA_DIR])
            os.makedirs(os.path.dirname(self.EASYRSA_DIR), exist_ok=True)
            self._run(["make-cadir", self.EASYRSA_DIR])
            # Easy-RSA init logic
            self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && ./easyrsa init-pki"])
            # Workaround for build-ca nopass in some easy-rsa versions
            self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && EASYRSA_BATCH=1 ./easyrsa build-ca nopass"])
            self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && EASYRSA_BATCH=1 ./easyrsa build-server-full server nopass"])
            self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && ./easyrsa gen-dh"])
            self._run(["openvpn", "--genkey", "--secret", f"{self.EASYRSA_DIR}/pki/ta.key"])
        
        return {
            "ca": f"{self.EASYRSA_DIR}/pki/ca.crt",
            "cert": f"{self.EASYRSA_DIR}/pki/issued/server.crt",
            "key": f"{self.EASYRSA_DIR}/pki/private/server.key",
            "dh": f"{self.EASYRSA_DIR}/pki/dh.pem",
            "ta": f"{self.EASYRSA_DIR}/pki/ta.key",
        }

    def generate_server_config(self, inbound: dict) -> str:
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))
        port = inbound.get("port", 1194)
        scramble_password = obfs.get("scramble_password", "")
        proto = settings.get("proto", "udp")
        cipher = settings.get("cipher", "AES-256-GCM")

        return f"""port {port}
proto {proto}
dev tun
ca {self.EASYRSA_DIR}/pki/ca.crt
cert {self.EASYRSA_DIR}/pki/issued/server.crt
key {self.EASYRSA_DIR}/pki/private/server.key
dh {self.EASYRSA_DIR}/pki/dh.pem
tls-auth {self.EASYRSA_DIR}/pki/ta.key 0
server 10.9.0.0 255.255.255.0
ifconfig-pool-persist ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 1.1.1.1"
keepalive 10 120
cipher {cipher}
persist-key
persist-tun
status {self.STATUS_LOG} 10
verb 3
{"scramble obfuscate " + scramble_password if scramble_password else ""}
"""

    def generate_client_config(self, client: dict, inbound: dict) -> str:
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))
        port = inbound.get("port", 1194)
        server_ip = settings.get("server_ip", "0.0.0.0")
        scramble_password = obfs.get("scramble_password", "")

        def r(p): 
            try: return open(p).read().strip()
            except: return ""

        return f"""client
dev tun
proto {settings.get('proto','udp')}
remote {server_ip} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher {settings.get('cipher','AES-256-GCM')}
key-direction 1
{"scramble obfuscate " + scramble_password if scramble_password else ""}
<ca>
{r(self.EASYRSA_DIR+'/pki/ca.crt')}
</ca>
<cert>
{r(self.EASYRSA_DIR+'/pki/issued/'+client['username']+'.crt')}
</cert>
<key>
{r(self.EASYRSA_DIR+'/pki/private/'+client['username']+'.key')}
</key>
<tls-auth>
{r(self.EASYRSA_DIR+'/pki/ta.key')}
</tls-auth>
"""

    def add_client(self, client: dict, inbound: dict) -> bool:
        self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && ./easyrsa --batch build-client-full {client['username']} nopass"])
        return True

    def remove_client(self, client: dict, inbound: dict) -> bool:
        self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && ./easyrsa --batch revoke {client['username']}"])
        self._run(["bash", "-c", f"cd {self.EASYRSA_DIR} && ./easyrsa gen-crl"])
        return True

    def toggle_client(self, client: dict, inbound: dict, enable: bool) -> bool:
        return self.add_client(client, inbound) if enable else self.remove_client(client, inbound)

    def get_traffic(self, inbound: dict) -> list:
        if not os.path.exists(self.STATUS_LOG): return []
        clients = []
        try:
            with open(self.STATUS_LOG) as f:
                content = f.read()
                # Simple parser for OpenVPN status log
                for line in content.split("\n"):
                    if "," in line and "." in line: # Common Name, Real Address, ...
                        parts = line.split(",")
                        if len(parts) >= 5 and parts[0] != "Common Name":
                            try:
                                # Connected Since is typically 'Wed Mar 25 10:40:00 2026'
                                # OpenVPN format: %a %b %d %H:%M:%S %Y
                                ts = int(datetime.strptime(parts[4], "%a %b %d %H:%M:%S %Y").timestamp())
                            except: ts = int(time.time())
                            clients.append({"username": parts[0], "rx": int(parts[2]), "tx": int(parts[3]), "last_handshake": ts})
        except: pass
        return clients

    def start(self, inbound: dict) -> bool:
        conf_path = f"{self.CONFIG_DIR}/server_{inbound['id']}.conf"
        with open(conf_path, "w") as f: f.write(self.generate_server_config(inbound))
        self._run(["systemctl", "start", f"openvpn@server_{inbound['id']}"])
        return True

    def stop(self, inbound: dict) -> bool:
        try: self._run(["systemctl", "stop", f"openvpn@server_{inbound['id']}"])
        except: pass
        return True

    def is_running(self, inbound: dict) -> bool:
        try:
            res = self._run(["systemctl", "is-active", f"openvpn@server_{inbound['id']}"])
            return res == "active"
        except: return False

AdapterFactory.register("openvpn_xor", OpenVPNXORAdapter)


# Регистрация
AdapterFactory.register("openvpn_xor", OpenVPNXORAdapter)
