#!/bin/bash

# Sky-Net Panel Auto-Installer
# Optimized for Ubuntu 24.04 LTS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# ─── Configuration ──────────────────────────────────────────────────────────

# Detect Local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
# Detect External IP
EXT_IP=$(curl -s ifconfig.me || echo "unknown")

echo -n -e "${BLUE}Enter Panel Port [default 9090]: ${NC}"
read PANEL_PORT < /dev/tty
PANEL_PORT=${PANEL_PORT:-9090}

echo -n -e "${BLUE}Confirm Local IP [$LOCAL_IP]: ${NC}"
read USER_LOCAL_IP < /dev/tty
LOCAL_IP=${USER_LOCAL_IP:-$LOCAL_IP}

echo -n -e "${BLUE}Confirm External IP [$EXT_IP]: ${NC}"
read USER_EXT_IP < /dev/tty
EXT_IP=${USER_EXT_IP:-$EXT_IP}

echo -e "${BLUE}Using Port: $PANEL_PORT, Local IP: $LOCAL_IP, External IP: $EXT_IP${NC}"

# ─── Installation ──────────────────────────────────────────────────────────

# Update system
echo -e "${BLUE}Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install Core Dependencies
echo -e "${BLUE}Installing Python and system tools...${NC}"
apt-get install -y python3 python3-pip python3-flask python3-flask-cors python3-psutil \
  sqlite3 curl git ufw fail2ban certbot

# Install VPN Dependencies
echo -e "${BLUE}Installing VPN protocols (AmneziaWG, OpenVPN, Docker)...${NC}"
# Use non-interactive for PPA
DEBIAN_FRONTEND=noninteractive add-apt-repository ppa:amnezia/ppa -y || true
apt-get update
# AmneziaWG-tools is usually needed for awg-quick
apt-get install -y amneziawg amneziawg-tools wireguard-tools || echo "AmneziaWG installation from PPA failed"
apt-get install -y openvpn easy-rsa

# Install Docker (needed for OpenVPN XOR)
if ! [ -x "$(command -v docker)" ]; then
  echo -e "${BLUE}Docker not found. Installing Docker...${NC}"
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
fi

# Enable IP Forwarding persistently
echo -e "${BLUE}Enabling IP Forwarding...${NC}"
sysctl -w net.ipv4.ip_forward=1
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf || echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Setup Sky-Net Directory and Source Code
INSTALL_DIR="/opt/sky-net"
echo -e "${BLUE}Downloading Sky-Net source code...${NC}"
rm -rf $INSTALL_DIR
git clone https://github.com/sky-night-net/sky-net-panel.git $INSTALL_DIR
cd $INSTALL_DIR

# Setup Firewall
echo -e "${BLUE}Configuring UFW...${NC}"
ufw allow 22/tcp
ufw allow $PANEL_PORT/tcp
ufw --force enable

# Create Systemd Service
echo -e "${BLUE}Creating systemd service...${NC}"
cat > /etc/systemd/system/skynet.service <<EOF
[Unit]
Description=Sky-Net Universal VPN Panel
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/sky_net.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=SKYNET_PORT=$PANEL_PORT
Environment=SKYNET_EXT_IP=$EXT_IP

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skynet.service

echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo -e "Panel is available at: http://$EXT_IP:$PANEL_PORT"
echo -e "Local Address: http://$LOCAL_IP:$PANEL_PORT"
echo -e "Default login: admin / admin"
echo -e "Run 'systemctl start skynet' to launch the panel."
