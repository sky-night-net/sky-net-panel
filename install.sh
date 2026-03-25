#!/bin/bash

# Sky-Net Panel Auto-Installer
# Optimized for Ubuntu 24.04 LTS

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Sky-Net VPN Panel Installation ===${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root${NC}"
  exit 1
fi

# Update system
echo -e "${BLUE}Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install Core Dependencies
echo -e "${BLUE}Installing Python and system tools...${NC}"
apt-get install -y python3 python3-pip python3-flask python3-flask-cors python3-psutil \
  sqlite3 curl git ufw fail2ban certbot

# Install VPN Dependencies
echo -e "${BLUE}Installing VPN protocols (AmneziaWG, OpenVPN)...${NC}"
# AmneziaWG (using PPA or direct binary depending on version)
add-apt-repository ppa:amnezia/ppa -y || true
apt-get update
apt-get install -y amneziawg wireguard-tools || echo "AmneziaWG PPA failed, please install manually"

# OpenVPN + EasyRSA
apt-get install -y openvpn easy-rsa

# Setup Sky-Net Directory
INSTALL_DIR="/opt/sky-net"
echo -e "${BLUE}Setting up directory: ${INSTALL_DIR}${NC}"
mkdir -p $INSTALL_DIR
# Assuming we are in the repo or downloading it
# cp -r . $INSTALL_DIR

# Initializing DB (will be done by python script)

# Setup Firewall
echo -e "${BLUE}Configuring UFW...${NC}"
ufw allow 22/tcp
ufw allow 9090/tcp
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

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skynet.service

echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo -e "Panel is available at: http://$(curl -s ifconfig.me):9090"
echo -e "Default login: admin / admin"
echo -e "Run 'systemctl start skynet' to launch the panel."
