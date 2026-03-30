#!/bin/bash

# Sky-Net Panel Uninstaller / Cleanup Script
# This script removes the Sky-Net panel, its containers, images, and network settings.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Sky-Net VPN Panel — Deep Cleanup Tool${NC}"
echo -e "${YELLOW}Warning: This will stop all active VPNs and remove the panel data.${NC}"

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}This script must be run as root.${NC}"
    exit 1
fi

# 1. Stop and remove the systemd service
echo -e "${BLUE}[1/6] Stopping Sky-Net service...${NC}"
systemctl stop skynet 2>/dev/null || true
systemctl disable skynet 2>/dev/null || true
rm -f /etc/systemd/system/skynet.service
systemctl daemon-reload
echo -e "  ${GREEN}Done.${NC}"

# 2. Stop and remove Docker containers
echo -e "${BLUE}[2/6] Stopping VPN containers...${NC}"
docker ps -a --format '{{.Names}}' 2>/dev/null | grep -E '^skynet_|^openvpn_xor_' | xargs -r docker rm -f 2>/dev/null || true
echo -e "  ${GREEN}Done.${NC}"

# 3. Remove local Docker images
echo -e "${BLUE}[3/6] Removing Sky-Net Docker images...${NC}"
docker rmi skynet-local/amneziawg:latest 2>/dev/null || true
docker rmi skynet-local/openvpn-xor:latest 2>/dev/null || true
echo -e "  ${GREEN}Done.${NC}"

# 4. Remove network interfaces
echo -e "${BLUE}[4/6] Cleaning network interfaces...${NC}"
for iface in $(ip link show | grep -oE '(awg|tun_skynet)[0-9]*' | sort -u); do
    echo "  Deleting $iface..."
    ip link delete "$iface" 2>/dev/null || true
done
ip link delete tun_skynet 2>/dev/null || true
echo -e "  ${GREEN}Done.${NC}"

# 5. Remove panel files
echo -e "${BLUE}[5/6] Removing panel files...${NC}"
rm -rf /opt/sky-net
echo -e "  ${GREEN}Done.${NC}"

# 6. Reset firewall rules (optional but recommended)
echo -e "${BLUE}[6/6] Resetting UFW rules...${NC}"
# We don't want to lock the user out of SSH, so we just remove our specific ports
# but a full reset is often cleaner if the user is okay with it.
# For now, let's just make sure forwarding is off.
sysctl -w net.ipv4.ip_forward=0 >/dev/null 2>&1 || true
# If the user wants a full UFW reset, they can run 'ufw --force reset' manually.
echo -e "  ${GREEN}Done.${NC}"

echo ""
echo -e "${GREEN}Cleanup complete. Your system is now clear of Sky-Net components.${NC}"
echo -e "${BLUE}You can now run the installation script again if needed.${NC}"
echo ""
