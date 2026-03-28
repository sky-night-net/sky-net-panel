#!/bin/bash

# Sky-Net Panel Auto-Installer
# Optimized for Ubuntu 24.04 LTS (Update 2026-03-28 11:15)

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

# --- Input Validation ---
while true; do
  echo -n -e "${BLUE}Enter HTTP Panel Port [default 4467]: ${NC}"
  read PANEL_PORT < /dev/tty
  PANEL_PORT=${PANEL_PORT:-4467}

  echo -n -e "${BLUE}Enter HTTPS Panel Port [default 4466]: ${NC}"
  read PANEL_HTTPS_PORT < /dev/tty
  PANEL_HTTPS_PORT=${PANEL_HTTPS_PORT:-4466}

  if [[ "$PANEL_PORT" == "$PANEL_HTTPS_PORT" ]]; then
    echo -e "${RED}Error: HTTP and HTTPS ports cannot be the same ($PANEL_PORT).${NC}"
    continue
  fi
  if ! [[ "$PANEL_PORT" =~ ^[0-9]+$ ]] || [ "$PANEL_PORT" -lt 1024 ] || [ "$PANEL_PORT" -gt 65535 ]; then
    echo -e "${RED}Error: HTTP port must be between 1024 and 65535.${NC}"
    continue
  fi
  if ! [[ "$PANEL_HTTPS_PORT" =~ ^[0-9]+$ ]] || [ "$PANEL_HTTPS_PORT" -lt 1024 ] || [ "$PANEL_HTTPS_PORT" -gt 65535 ]; then
    echo -e "${RED}Error: HTTPS port must be between 1024 and 65535.${NC}"
    continue
  fi
  break
done

echo -n -e "${BLUE}Confirm Local IP [$LOCAL_IP]: ${NC}"
read USER_LOCAL_IP < /dev/tty
LOCAL_IP=${USER_LOCAL_IP:-$LOCAL_IP}
# Sanitize Local IP
LOCAL_IP=$(echo "$LOCAL_IP" | tr -cd '0-9.a-fA-F:')

while true; do
  echo -n -e "${BLUE}Confirm External IP [$EXT_IP]: ${NC}"
  read USER_EXT_IP < /dev/tty
  USER_EXT_IP=${USER_EXT_IP:-$EXT_IP}
  # Sanitize: Strip any non-ASCII characters (e.g. Cyrillic typos)
  EXT_IP=$(echo "$USER_EXT_IP" | tr -cd '0-9.a-fA-F:')
  
  if [ -z "$EXT_IP" ]; then
    echo -e "${RED}Error: Invalid External IP address.${NC}"
    continue
  fi
  break
done

echo -e "${BLUE}Using HTTP Port: $PANEL_PORT, HTTPS Port: $PANEL_HTTPS_PORT, Local IP: $LOCAL_IP, External IP: $EXT_IP${NC}"

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
apt-get install -y linux-headers-generic amneziawg amneziawg-dkms amneziawg-tools amneziawg-go wireguard-tools || echo "AmneziaWG installation from PPA failed"
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
ufw allow $PANEL_HTTPS_PORT/tcp
# CRITICAL: Allow forwarded/routed traffic for VPN
ufw default allow routed
sed -i 's/DEFAULT_FORWARD_POLICY="DROP"/DEFAULT_FORWARD_POLICY="ACCEPT"/' /etc/default/ufw
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
Environment=SKYNET_HTTPS_PORT=$PANEL_HTTPS_PORT
Environment=SKYNET_EXT_IP=$EXT_IP

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable skynet.service
systemctl start skynet.service

echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo -e "${GREEN}Sky-Net is now running and ready to use.${NC}"
echo -e "HTTPS Address: https://$EXT_IP:$PANEL_HTTPS_PORT"
echo -e "HTTP Address:  http://$EXT_IP:$PANEL_PORT"
echo -e "Local Address: http://$LOCAL_IP:$PANEL_PORT"
echo -e "Default login: ${BLUE}admin / admin${NC}"
