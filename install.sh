#!/bin/bash

# Sky-Net Panel Auto-Installer
# Optimized for Ubuntu 24.04 LTS
# Version: 2026-03-30

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "   ███████╗██╗  ██╗██╗   ██╗      ███╗   ██╗███████╗████████╗"
echo "   ██╔════╝██║ ██╔╝╚██╗ ██╔╝      ████╗  ██║██╔════╝╚══██╔══╝"
echo "   ███████╗█████╔╝  ╚████╔╝ █████╗██╔██╗ ██║█████╗     ██║   "
echo "   ╚════██║██╔═██╗   ╚██╔╝  ╚════╝██║╚██╗██║██╔══╝     ██║   "
echo "   ███████║██║  ██╗   ██║         ██║ ╚████║███████╗   ██║   "
echo "   ╚══════╝╚═╝  ╚═╝   ╚═╝         ╚═╝  ╚═══╝╚══════╝   ╚═╝   "
echo -e "${NC}"
echo -e "${BLUE}Sky-Net VPN Panel Installer — Ubuntu 24.04 LTS${NC}"
echo ""

# ─── Root Check ───────────────────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}This script must be run as root.${NC}"
    exit 1
fi

# ─── Detect IPs ───────────────────────────────────────────────────────────────
LOCAL_IP=$(ip route get 8.8.8.8 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' | head -1)
LOCAL_IP=${LOCAL_IP:-$(hostname -I | awk '{print $1}')}

EXT_IP=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null || \
         curl -s --max-time 5 https://ifconfig.me 2>/dev/null || \
         echo "")

echo -e "${BLUE}Detected: Local IP=${LOCAL_IP}  External IP=${EXT_IP:-NOT DETECTED}${NC}"
echo ""

# ─── Interactive / Non-interactive Port Input ──────────────────────────────────
IS_INTERACTIVE=0
if [ -t 0 ] && [ -t 1 ]; then IS_INTERACTIVE=1; fi

safe_prompt() {
    local prompt_msg=$1 var_name=$2 default_val=$3 input_val=""
    if [ "$IS_INTERACTIVE" -eq 1 ]; then
        read -rp "$(echo -e "${BLUE}${prompt_msg}${NC}")" input_val
        eval "$var_name=\"${input_val:-$default_val}\""
    elif [ -c /dev/tty ]; then
        if read -rp "$(echo -e "${BLUE}${prompt_msg}${NC}")" input_val </dev/tty; then
            eval "$var_name=\"${input_val:-$default_val}\""
        else
            eval "$var_name=\"$default_val\""
        fi
    else
        eval "$var_name=\"$default_val\""
    fi
}

while true; do
    safe_prompt "HTTP Panel Port [default 4467]: " PANEL_PORT 4467
    safe_prompt "HTTPS Panel Port [default 4466]: " PANEL_HTTPS_PORT 4466

    VALID=1
    [[ "$PANEL_PORT" == "$PANEL_HTTPS_PORT" ]] && { echo -e "${RED}Error: HTTP and HTTPS ports must differ.${NC}"; VALID=0; }
    ! [[ "$PANEL_PORT" =~ ^[0-9]+$ ]] || [ "$PANEL_PORT" -lt 1024 ] || [ "$PANEL_PORT" -gt 65535 ] && { echo -e "${RED}Error: HTTP port must be 1024–65535.${NC}"; VALID=0; }
    ! [[ "$PANEL_HTTPS_PORT" =~ ^[0-9]+$ ]] || [ "$PANEL_HTTPS_PORT" -lt 1024 ] || [ "$PANEL_HTTPS_PORT" -gt 65535 ] && { echo -e "${RED}Error: HTTPS port must be 1024–65535.${NC}"; VALID=0; }
    [ "$VALID" -eq 1 ] && break
    if [ "$IS_INTERACTIVE" -eq 0 ] && ! [ -c /dev/tty ]; then
        echo -e "${RED}Validation failed in non-interactive mode. Using defaults.${NC}"
        PANEL_PORT=4467; PANEL_HTTPS_PORT=4466; break
    fi
done

safe_prompt "Confirm/override External IP [${EXT_IP}]: " USER_EXT_IP "${EXT_IP}"
EXT_IP=$(echo "${USER_EXT_IP:-$EXT_IP}" | tr -cd '0-9.a-fA-F:')

if [ -z "$EXT_IP" ]; then
    echo -e "${YELLOW}WARNING: No External IP detected. Using Local IP for configs.${NC}"
    EXT_IP="$LOCAL_IP"
fi

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo -e "  HTTP Port:    ${BLUE}${PANEL_PORT}${NC}"
echo -e "  HTTPS Port:   ${BLUE}${PANEL_HTTPS_PORT}${NC}"
echo -e "  Local IP:     ${BLUE}${LOCAL_IP}${NC}"
echo -e "  External IP:  ${BLUE}${EXT_IP}${NC}"
echo ""

# ─── Pre-Installation Cleanup ─────────────────────────────────────────────────
echo -e "${BLUE}[1/7] Pre-installation cleanup...${NC}"
set +e
# Stop all Sky-Net containers
docker ps -a --format '{{.Names}}' 2>/dev/null | grep -E '^skynet_|^openvpn_xor_' | xargs -r docker rm -f 2>/dev/null
# Remove leftover VPN interfaces
for iface in $(ip link show 2>/dev/null | grep -oE '(awg|tun_skynet)[0-9]*' | sort -u); do
    ip link delete "$iface" 2>/dev/null && echo "  Removed interface: $iface"
done
ip link delete tun_skynet 2>/dev/null || true
set -e
echo -e "  ${GREEN}Done.${NC}"

# ─── Install Dependencies ─────────────────────────────────────────────────────
echo -e "${BLUE}[5/7] Installing dependencies...${NC}"
export DEBIAN_FRONTEND=noninteractive

# Robustness: Fix existing broken state and sync repositories
dpkg --configure -a 2>/dev/null || true
apt-get clean
apt-get update -y
apt-get autoremove -y
# Optional: upgrade core packages to resolve dependency trees
apt-get upgrade -y

# Prepare repositories
apt-get install -y software-properties-common
add-apt-repository universe -y
apt-get update -y

# Install core dependencies
echo -e "  Installing system tools..."
apt-get install -y git curl sqlite3 ufw easy-rsa wireguard-tools gunicorn fail2ban

echo -e "  Installing Python environment..."
apt-get install -y python3 python3-pip python3-venv

# ─── Docker ───────────────────────────────────────────────────────────────────
echo -e "${BLUE}[3/7] Installing Docker...${NC}"
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker --now
else
    echo -e "  ${GREEN}Docker already installed: $(docker --version)${NC}"
fi

# Fix Docker DNS resolution (Common issue on Ubuntu 24.04)
echo -e "  ${BLUE}Checking Docker DNS configuration...${NC}"
mkdir -p /etc/docker
if [ ! -f /etc/docker/daemon.json ] || ! grep -q "dns" /etc/docker/daemon.json; then
    echo -e "  ${YELLOW}Force-configuring Docker DNS (8.8.8.8)...${NC}"
    echo '{"dns": ["8.8.8.8", "1.1.1.1"]}' > /etc/docker/daemon.json
    systemctl restart docker
fi

# ─── Getting Source Code ────────────────────────────────────────────────────────
echo -e "${BLUE}[4/7] Cloning Sky-Net panel repository...${NC}"
rm -rf /opt/sky-net
git clone https://github.com/sky-night-net/sky-net-panel.git /opt/sky-net

# ─── Local Docker Builds ──────────────────────────────────────────────────────
echo -e "${BLUE}[5/7] Building autonomous Docker images (This may take 3-5 minutes)...${NC}"

# Temporary swap to prevent OOM on 512MB VPS during compilation
if [ $(free -m | awk '/^Mem:/{print $2}') -lt 1500 ] && [ $(free -m | awk '/^Swap:/{print $2}') -eq 0 ]; then
    echo -e "  ${YELLOW}Low RAM detected. Creating temporary 1GB SWAP...${NC}"
    fallocate -l 1G /tmp/skynet_swap || dd if=/dev/zero of=/tmp/skynet_swap bs=1M count=1024 >/dev/null 2>&1
    chmod 600 /tmp/skynet_swap
    mkswap /tmp/skynet_swap >/dev/null 2>&1
    swapon /tmp/skynet_swap >/dev/null 2>&1
fi

# Ensure we FAIL if build fails, don't just continue. Using --network=host to inherit host DNS (failsafe).
docker build --network=host --no-cache -t skynet-local/amneziawg:latest /opt/sky-net/docker/amneziawg || { echo -e "  ${RED}Failed to build AWG. Aborting.${NC}"; exit 1; }
docker build --network=host --no-cache -t skynet-local/openvpn-xor:latest /opt/sky-net/docker/openvpn-xor || { echo -e "  ${RED}Failed to build OpenVPN-XOR. Aborting.${NC}"; exit 1; }

# Remove temporary swap
if [ -f /tmp/skynet_swap ]; then
    echo -e "  ${YELLOW}Removing temporary SWAP...${NC}"
    swapoff /tmp/skynet_swap 2>/dev/null || true
    rm -f /tmp/skynet_swap
fi

echo -e "  ${GREEN}Done.${NC}"

# ─── IP Forwarding & Firewall ─────────────────────────────────────────────────
echo -e "${BLUE}[6/7] Configuring IP forwarding and firewall...${NC}"

# Enable immediately
modprobe tun 2>/dev/null || true
modprobe amneziawg 2>/dev/null || true
sysctl -w net.ipv4.ip_forward=1 >/dev/null
sysctl -w net.ipv6.conf.all.forwarding=1 >/dev/null 2>&1 || true
sysctl -p /etc/sysctl.conf >/dev/null 2>&1 || true

# Persist in sysctl.conf
sed -i '/^#*net.ipv4.ip_forward/d' /etc/sysctl.conf
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Persist in UFW sysctl
if [ -f /etc/ufw/sysctl.conf ]; then
    sed -i '/^#*net\/ipv4\/ip_forward/d' /etc/ufw/sysctl.conf
    echo "net/ipv4/ip_forward=1" >> /etc/ufw/sysctl.conf
fi

# ─── UFW Firewall ─────────────────────────────────────────────────────────────
ufw --force reset 2>/dev/null || true
ufw default deny incoming
ufw default allow outgoing
ufw default allow routed          # CRITICAL: allows VPN traffic forwarding
ufw allow 22/tcp    comment 'SSH'
ufw allow "${PANEL_PORT}/tcp"     comment 'Sky-Net HTTP'
ufw allow "${PANEL_HTTPS_PORT}/tcp" comment 'Sky-Net HTTPS'
# Default VPN ports (can be customized per-server in the panel)
ufw allow 1194/udp  comment 'OpenVPN XOR default'
ufw allow 51820/udp comment 'AmneziaWG default'
ufw allow 51821/udp comment 'AmneziaWG alt'
ufw allow 51822/udp comment 'AmneziaWG alt 2'

# Docker interacts badly with UFW; ensure forwarding isn't blocked by UFW
# UFW FORWARD policy must be ACCEPT (handled by 'ufw default allow routed')
ufw --force enable

echo -e "  ${GREEN}Firewall configured.${NC}"

# ─── Sky-Net Source Code ──────────────────────────────────────────────────────
echo -e "${BLUE}[7/7] Setting up Sky-Net panel...${NC}"
if [ -d /opt/sky-net/.git ]; then
    echo -e "  Updating existing installation..."
    cd /opt/sky-net
    git pull origin main || true
else
    echo -e "  Cloning repository..."
    rm -rf /opt/sky-net
    git clone https://github.com/sky-night-net/sky-net-panel.git /opt/sky-net
    cd /opt/sky-net
fi

# Install Python dependencies into a Virtual Environment (Crucial for Ubuntu 24.04)
echo -e "  Setting up Python Virtual Environment..."
python3 -m venv /opt/sky-net/venv
/opt/sky-net/venv/bin/pip install --upgrade pip
/opt/sky-net/venv/bin/pip install flask flask-cors psutil gunicorn

# Initialize database
if [ ! -f /opt/sky-net/sky_net.db ]; then
    echo -e "  Initializing database..."
    sqlite3 /opt/sky-net/sky_net.db < /opt/sky-net/schema.sql 2>/dev/null || true
fi

# Write settings to DB (always update to reflect current install values)
sqlite3 /opt/sky-net/sky_net.db "
INSERT OR IGNORE INTO settings (key, value) VALUES ('panel_port', '${PANEL_PORT}');
INSERT OR IGNORE INTO settings (key, value) VALUES ('panel_port_https', '${PANEL_HTTPS_PORT}');
INSERT OR IGNORE INTO settings (key, value) VALUES ('server_ip', '${EXT_IP}');
INSERT OR IGNORE INTO settings (key, value) VALUES ('local_ip', '${LOCAL_IP}');
INSERT OR IGNORE INTO settings (key, value) VALUES ('public_ip_override', '${EXT_IP}');
UPDATE settings SET value='${PANEL_PORT}' WHERE key='panel_port';
UPDATE settings SET value='${PANEL_HTTPS_PORT}' WHERE key='panel_port_https';
UPDATE settings SET value='${EXT_IP}' WHERE key='server_ip';
UPDATE settings SET value='${EXT_IP}' WHERE key='public_ip_override';
UPDATE settings SET value='${LOCAL_IP}' WHERE key='local_ip';
" 2>/dev/null || true

# ─── Systemd Service ──────────────────────────────────────────────────────────
echo -e "${BLUE}[8/8] Creating systemd service...${NC}"
cat > /etc/systemd/system/skynet.service <<EOF
[Unit]
Description=Sky-Net VPN Panel
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sky-net
Environment=PYTHONPATH=/opt/sky-net
Environment=SKYNET_PORT=${PANEL_PORT}
Environment=SKYNET_HTTPS_PORT=${PANEL_HTTPS_PORT}
ExecStart=/opt/sky-net/venv/bin/gunicorn --bind 0.0.0.0:${PANEL_PORT} --workers 1 --worker-class sync --timeout 120 --graceful-timeout 30 sky_net:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skynet

# Stop existing if running
systemctl stop skynet 2>/dev/null || true
sleep 2
systemctl start skynet

echo ""
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Sky-Net Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Panel (HTTP):   ${BLUE}http://${EXT_IP}:${PANEL_PORT}${NC}"
echo -e "  Panel (HTTPS):  ${BLUE}https://${EXT_IP}:${PANEL_HTTPS_PORT}${NC}"
echo -e "  Local access:   ${BLUE}http://${LOCAL_IP}:${PANEL_PORT}${NC}"
echo ""
echo -e "  Default login:  ${YELLOW}admin / admin${NC}"
echo -e "  ${RED}Change the password immediately after first login!${NC}"
echo ""
echo -e "  Service:    systemctl status skynet"
echo -e "  Logs:       journalctl -u skynet -f"
echo ""
