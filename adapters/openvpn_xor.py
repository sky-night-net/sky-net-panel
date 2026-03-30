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
import ipaddress
from datetime import datetime
from . import ProtocolAdapter, AdapterFactory
log = logging.getLogger(__name__)


class OpenVPNXORAdapter(ProtocolAdapter):
    PROTOCOL_NAME = "openvpn_xor"
    REQUIRED_BINARIES = ["openvpn", "make-cadir"]
    CONFIG_DIR = "/etc/openvpn"
    EASYRSA_DIR = "/etc/openvpn/easy-rsa"
    STATUS_LOG = "/var/log/openvpn/status.log"
    BYPASS_ROUTES = """
route 95.85.96.0 255.255.224.0 net_gateway
route 95.85.100.0 255.255.252.0 net_gateway
route 95.85.104.0 255.255.255.0 net_gateway
route 217.174.224.0 255.255.240.0 net_gateway
route 185.69.184.0 255.255.255.0 net_gateway
route 185.69.185.0 255.255.255.0 net_gateway
route 185.69.186.0 255.255.255.0 net_gateway
route 185.69.187.0 255.255.255.0 net_gateway
route 185.246.72.0 255.255.255.0 net_gateway
route 93.171.220.0 255.255.252.0 net_gateway
route 103.220.0.0 255.255.252.0 net_gateway
route 119.235.112.0 255.255.240.0 net_gateway
route 177.93.143.0 255.255.255.0 net_gateway
route 216.250.8.0 255.255.248.0 net_gateway
route 91.202.232.0 255.255.255.0 net_gateway
route 93.171.174.0 255.255.255.0 net_gateway
route 94.102.176.0 255.255.240.0 net_gateway
route 103.209.230.0 255.255.255.0 net_gateway
route 104.28.13.97 255.255.255.255 net_gateway
route 104.28.13.98 255.255.255.254 net_gateway
route 104.28.38.186 255.255.255.254 net_gateway
route 154.30.29.0 255.255.255.192 net_gateway
route 172.225.137.112 255.255.255.240 net_gateway
route 172.225.200.224 255.255.255.240 net_gateway
route 172.225.224.48 255.255.255.240 net_gateway
route 185.69.184.0 255.255.252.0 net_gateway
route 185.246.72.0 255.255.252.0 net_gateway
route 217.8.117.0 255.255.255.0 net_gateway
route 94.200.128.0 255.255.224.0 net_gateway
route 94.200.0.0 255.248.0.0 net_gateway
route 95.85.116.0 255.255.255.0 net_gateway
route 95.85.112.0 255.255.255.0 net_gateway
"""

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
        cipher = settings.get("cipher", "AES-256-CBC")

        address_full = settings.get("address", "10.9.0.0/24")
        address = address_full.split("/")[0]
        netmask = "255.255.255.0" # Assuming /24 for now, or we can calculate
        if "/" in address_full:
            # Simple CIDR to Netmask conversion for common /24
            if "/24" in address_full: netmask = "255.255.255.0"
        
        # OpenVPN needs the network address (e.g. 10.9.0.0)
        net_parts = address.split(".")
        net_parts[3] = "0"
        network = ".".join(net_parts)

        return f"""port {port}
proto {proto}4
dev tun
ca {self.EASYRSA_DIR}/pki/ca.crt
cert {self.EASYRSA_DIR}/pki/issued/server.crt
key {self.EASYRSA_DIR}/pki/private/server.key
dh {self.EASYRSA_DIR}/pki/dh.pem
tls-auth {self.EASYRSA_DIR}/pki/ta.key 0
server {network} {netmask}
ifconfig-pool-persist ipp.txt
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 1.1.1.1"
push "dhcp-option DNS 8.8.8.8"
keepalive 10 120
topology subnet
data-ciphers {cipher}:AES-256-GCM:AES-128-GCM
cipher {cipher}
auth SHA256
explicit-exit-notify 1
tls-version-min 1.2
persist-key
persist-tun
status {self.STATUS_LOG} 10
verb 3
mssfix 1350
{"scramble obfuscate " + scramble_password if scramble_password else ""}
"""

    def generate_client_config(self, client: dict, inbound: dict) -> str:
        settings = json.loads(inbound.get("settings", "{}"))
        obfs = json.loads(inbound.get("obfuscation", "{}"))
        port = inbound.get("port", 1194)
        server_ip = settings.get("server_ip", "0.0.0.0")
        scramble_password = obfs.get("scramble_password", "")

        def r(p): 
            try:
                content = open(p).read().strip()
                # Remove verbose certificate info if any
                if "-----BEGIN CERTIFICATE-----" in content:
                    idx = content.find("-----BEGIN CERTIFICATE-----")
                    return content[idx:]
                return content
            except: return ""

        bypass = self.BYPASS_ROUTES if obfs.get("bypass_routes") else ""

        return f"""client
dev tun
proto {settings.get('proto','udp')}
remote {server_ip} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
data-ciphers {settings.get('cipher','AES-256-CBC')}:AES-256-GCM:AES-128-GCM
cipher {settings.get('cipher','AES-256-CBC')}
auth SHA256
auth-nocache
tls-client
tls-version-min 1.2
key-direction 1
explicit-exit-notify
ignore-unknown-option block-outside-dns
setenv opt block-outside-dns
verb 3
mssfix 1350
{"scramble obfuscate " + scramble_password if scramble_password else ""}
{bypass}
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
        
        iface = "tun_skynet"
        container_name = f"skynet_openvpn_xor_{inbound['id']}"
        
        # Stop existing if any
        self.stop(inbound)
        
        settings = json.loads(inbound.get("settings", "{}"))
        address_full = settings.get("address", "10.9.0.0/24")
        try:
            net = ipaddress.ip_network(address_full, strict=False)
            server_ip = str(list(net.hosts())[0])
        except: server_ip = "10.9.0.1"

        log.info(f"[{self.PROTOCOL_NAME}] Checking for host conflicts (iface: {iface}, ip: {server_ip})")
        try:
            # Check if interface already exists
            res = subprocess.run(["ip", "link", "show", iface], capture_output=True, text=True)
            if res.returncode == 0:
                log.warning(f"[{self.PROTOCOL_NAME}] Interface {iface} already exists on host. Deleting...")
                subprocess.run(["ip", "link", "delete", iface], check=False)

            # Check if IP is already assigned
            res = subprocess.run(["ip", "addr", "show"], capture_output=True, text=True)
            if server_ip in res.stdout:
                log.warning(f"[{self.PROTOCOL_NAME}] IP {server_ip} already assigned on host. Finding and deleting interface...")
                match = re.search(r'inet\s+' + re.escape(server_ip) + r'.*?dev\s+([a-zA-Z0-9_\-]+)', res.stdout)
                if match:
                    conflicting_iface = match.group(1)
                    subprocess.run(["ip", "link", "delete", conflicting_iface], check=False)
        except Exception as e:
            log.error(f"[{self.PROTOCOL_NAME}] Conflict resolution failed: {e}")

        # Stop existing if any
        self.stop(inbound)
        
        # We need to map the config directory and make sure logging exists
        os.makedirs("/var/log/openvpn", exist_ok=True)
        
        # Start Docker container with XOR patched binary in HOST network mode 
        cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "--restart", "unless-stopped",
            "--network", "host",
            "--cap-add", "NET_ADMIN",
            "--device", "/dev/net/tun",
            "-v", f"{self.CONFIG_DIR}:/etc/openvpn",
            "-v", "/var/log/openvpn:/var/log/openvpn",
            "lawtancool/docker-openvpn-xor:latest",
            "openvpn", "--config", f"/etc/openvpn/server_{inbound['id']}.conf",
            "--dev", iface 
        ]
        
        self._run(cmd)
        self._setup_nat(address_full)
        
        # Apply MSS clamping on the host too for good measure
        self._run(["iptables", "-t", "mangle", "-I", "FORWARD", "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN", "-s", address_full, "-j", "TCPMSS", "--set-mss", "1350"], check=False)
        
        return True

    def stop(self, inbound: dict) -> bool:
        iface = "tun_skynet"
        container_name = f"skynet_openvpn_xor_{inbound['id']}"
        try:
            settings = json.loads(inbound.get("settings", "{}"))
            address_full = settings.get("address", "10.9.0.0/24")
            
            self._run(["docker", "rm", "-f", container_name], check=False)
            self._cleanup_nat(address_full)

            # Cleanup host interface if it persists
            subprocess.run(["ip", "link", "delete", iface], check=False)

            # Remove UFW/iptables rules added during start
            try:
                res_ufw = subprocess.run(["which", "ufw"], capture_output=True)
                if res_ufw.returncode == 0:
                    subnet = address_full
                    self._run(["ufw", "route", "delete", "allow", "from", subnet, "to", "any"], check=False)
                    self._run(["iptables", "-D", "INPUT", "-s", subnet, "-j", "ACCEPT"], check=False)
                    self._run(["iptables", "-t", "mangle", "-D", "FORWARD", "-p", "tcp", "--tcp-flags", "SYN,RST", "SYN", "-s", subnet, "-j", "TCPMSS", "--set-mss", "1350"], check=False)
            except: pass

        except: pass
        return True

    def is_running(self, inbound: dict) -> bool:
        container_name = f"skynet_openvpn_xor_{inbound['id']}"
        try:
            res = self._run(["docker", "inspect", "-f", "{{.State.Running}}", container_name], check=False)
            return res.strip() == "true"
        except: return False

# Регистрация
AdapterFactory.register("openvpn_xor", OpenVPNXORAdapter)
