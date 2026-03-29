#!/bin/bash

# Sky-Net Panel Auto-Installer
# Optimized for Ubuntu 24.04 LTS (Update 2026-03-29 17:45)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Non-Interactive Detection ---
IS_INTERACTIVE=0
if [ -t 0 ] && [ -t 1 ]; then
    IS_INTERACTIVE=1
fi

# Detect Local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
# Detect External IP
EXT_IP=$(curl -s ifconfig.me || echo "unknown")

# --- Input Validation ---

# Function to safely read with timeout and default
safe_prompt() {
    local prompt_msg=$1
    local var_name=$2
    local default_val=$3
    local input_val=""

    if [ "$IS_INTERACTIVE" -eq 1 ]; then
        read -p "$(echo -e "${BLUE}${prompt_msg}${NC}")" input_val
        eval "$var_name=\"${input_val:-$default_val}\""
    elif [ -c /dev/tty ]; then
        # Try to read from TTY even if stdin is a pipe
        if read -p "$(echo -e "${BLUE}${prompt_msg}${NC}")" input_val < /dev/tty; then
            eval "$var_name=\"${input_val:-$default_val}\""
        else
            eval "$var_name=\"$default_val\""
        fi
    else
        eval "$var_name=\"$default_val\""
    fi
}

while true; do
    safe_prompt "Enter HTTP Panel Port [default 4467]: " PANEL_PORT 4467
    safe_prompt "Enter HTTPS Panel Port [default 4466]: " PANEL_HTTPS_PORT 4466

    # Validation
    VALID=1
    if [[ "$PANEL_PORT" == "$PANEL_HTTPS_PORT" ]]; then
        echo -e "${RED}Error: HTTP and HTTPS ports cannot be the same ($PANEL_PORT).${NC}"
        VALID=0
    fi
    if ! [[ "$PANEL_PORT" =~ ^[0-9]+$ ]] || [ "$PANEL_PORT" -lt 1024 ] || [ "$PANEL_PORT" -gt 65535 ]; then
        echo -e "${RED}Error: HTTP port must be between 1024 and 65535.${NC}"
        VALID=0
    fi
    if ! [[ "$PANEL_HTTPS_PORT" =~ ^[0-9]+$ ]] || [ "$PANEL_HTTPS_PORT" -lt 1024 ] || [ "$PANEL_HTTPS_PORT" -gt 65535 ]; then
        echo -e "${RED}Error: HTTPS port must be between 1024 and 65535.${NC}"
        VALID=0
    fi

    if [ "$VALID" -eq 1 ]; then
        break
    else
        if [ "$IS_INTERACTIVE" -eq 0 ] && ! [ -c /dev/tty ]; then
            echo -e "${RED}Critical: Validation failed in non-interactive mode. Aborting.${NC}"
            exit 1
        fi
        # If interactive, loop back for retry
    fi
done

# IPs
safe_prompt "Confirm Local IP [$LOCAL_IP]: " USER_LOCAL_IP "$LOCAL_IP"
LOCAL_IP=$(echo "${USER_LOCAL_IP:-$LOCAL_IP}" | tr -cd '0-9.a-fA-F:')

while true; do
    safe_prompt "Confirm External IP [$EXT_IP]: " USER_EXT_IP "$EXT_IP"
    EXT_IP=$(echo "$USER_EXT_IP" | tr -cd '0-9.a-fA-F:')
    
    if [ -z "$EXT_IP" ] || [ "$EXT_IP" == "unknown" ]; then
        echo -e "${RED}Error: Invalid External IP address.${NC}"
        if [ "$IS_INTERACTIVE" -eq 0 ] && ! [ -c /dev/tty ]; then exit 1; fi
        continue
    fi
    break
done

echo -e "${BLUE}Using HTTP Port: $PANEL_PORT, HTTPS Port: $PANEL_HTTPS_PORT, Local IP: $LOCAL_IP, External IP: $EXT_IP${NC}"

# Update system
echo -e "${BLUE}Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# ─── Pre-Installation Cleanup ────────────────────────────────────────────────
echo -e "${BLUE}Performing pre-installation cleanup...${NC}"
# 1. Stop all VPN containers
echo -e "${YELLOW}Stopping all Sky-Net containers...${NC}"
set +e
docker ps -a --format '{{.Names}}' | grep -E '^skynet_|^openvpn_xor_' | xargs -r docker rm -f
set -e

# 2. Cleanup all network interfaces
echo -e "${YELLOW}Removing leftover network interfaces...${NC}"
set +e
for iface in $(ip link show | grep -E 'awg|tun_skynet' | awk -F': ' '{print $2}' | sed 's/@.*//'); do
    ip link delete "$iface" 2>/dev/null
done
ip addr flush dev tun_skynet 2>/dev/null
ip link delete dev tun_skynet 2>/dev/null
set -e
echo "Done."

# ─── Install Core Dependencies ──────────────────────────────────────────────
echo -e "${BLUE}Installing Python and system tools...${NC}"
apt-get install -y python3 python3-pip python3-flask python3-flask-cors python3-psutil \
  sqlite3 curl git ufw fail2ban certbot

# VPN Keys and Cert Tools (OpenVPN utilizes easy-rsa on the host)
echo -e "${BLUE}Installing VPN Key Utilities...${NC}"
apt-get install -y easy-rsa wireguard-tools

# Install Docker (required for all VPN protocols: AmneziaWG, OpenVPN XOR)
if ! [ -x "$(command -v docker)" ]; then
  echo -e "${BLUE}Docker not found. Installing Docker...${NC}"
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
fi

# Pre-pull required images for OOTB speed
echo -e "${BLUE}Pre-pulling Docker images (AmneziaWG, OpenVPN XOR)...${NC}"
docker pull amneziavpn/amnezia-wg || true
docker pull amneziavpn/amneziawg-go || true
docker pull lawtancool/docker-openvpn-xor || true
docker pull amnezia-awg2 || true

# Enable IP Forwarding persistently
echo -e "${BLUE}Enabling IP Forwarding...${NC}"
sysctl -w net.ipv4.ip_forward=1
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf || echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sed -i 's/#net\/ipv4\/ip_forward=1/net\/ipv4\/ip_forward=1/' /etc/ufw/sysctl.conf || true
grep -q "net/ipv4/ip_forward=1" /etc/ufw/sysctl.conf || echo "net/ipv4/ip_forward=1" >> /etc/ufw/sysctl.conf

# ─── Setup Sky-Net Directory and Source Code ───────────────────────────────
echo -e "${BLUE}Setting up Sky-Net at /opt/sky-net...${NC}"
rm -rf /opt/sky-net
git clone https://github.com/sky-night-net/sky-net-panel.git /opt/sky-net
cd /opt/sky-net

# Initialize database if not exists
if [ ! -f sky_net.db ]; then
    echo -e "${BLUE}Initializing database...${NC}"
    sqlite3 sky_net.db < schema.sql
fi

# Update settings with ports and IPs
sqlite3 sky_net.db "UPDATE settings SET value='$PANEL_PORT' WHERE key='panel_port';"
sqlite3 sky_net.db "UPDATE settings SET value='$PANEL_HTTPS_PORT' WHERE key='panel_https_port';"
sqlite3 sky_net.db "UPDATE settings SET value='$LOCAL_IP' WHERE key='local_ip';"
sqlite3 sky_net.db "UPDATE settings SET value='$EXT_IP' WHERE key='external_ip';"

# ─── Setup Firewall ─────────────────────────────────────────────────────────
echo -e "${BLUE}Configuring UFW firewall...${NC}"
ufw allow 22/tcp || true
ufw allow "$PANEL_PORT"/tcp || true
ufw allow "$PANEL_HTTPS_PORT"/tcp || true
# OpenVPN and AmneziaWG ports (defaults)
ufw allow 1194/udp || true
ufw allow 51820/udp || true
ufw allow 51821/udp || true
ufw allow 51822/udp || true

# CRITICAL: Allow forwarded/routed traffic for VPN
ufw default allow routed || true
ufw --force enable || true

# ─── Create Systemd Service ────────────────────────────────────────────────
echo -e "${BLUE}Creating skynet systemd service...${NC}"
cat > /etc/systemd/system/skynet.service <<EOF
[Unit]
Description=Sky-Net VPN Panel
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sky-net
ExecStart=/usr/bin/python3 sky_net.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skynet
systemctl restart skynet

echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo -e "${GREEN}Sky-Net is now running and ready to use.${NC}"
echo -e "HTTPS Address: ${BLUE}https://$EXT_IP:$PANEL_HTTPS_PORT${NC}"
echo -e "HTTP Address:  ${BLUE}http://$EXT_IP:$PANEL_PORT${NC}"
echo -e "Local Address: ${BLUE}http://$LOCAL_IP:$PANEL_PORT${NC}"
echo -e "Default login: ${YELLOW}admin / admin${NC}"
