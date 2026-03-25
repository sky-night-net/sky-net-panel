#!/bin/bash

# Sky-Net Panel Uninstaller
# Use with caution! Removes all panel files and services.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}=== Sky-Net VPN Panel Uninstallation ===${NC}"
echo -e "${RED}WARNING: This will remove all Sky-Net files, database, and service.${NC}"
read -p "Are you sure you want to continue? (y/n) " -n 1 -r < /dev/tty
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Stop and Disable Service
echo -e "${BLUE}Stopping skynet service...${NC}"
systemctl stop skynet.service || true
systemctl disable skynet.service || true
rm -f /etc/systemd/system/skynet.service
systemctl daemon-reload

# Remove Files
INSTALL_DIR="/opt/sky-net"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${BLUE}Removing files from $INSTALL_DIR...${NC}"
    rm -rf "$INSTALL_DIR"
else
    echo -e "${BLUE}Directory $INSTALL_DIR not found.${NC}"
fi

# Note: We do NOT remove system dependencies (python, openvpn, amneziawg)
# to avoid breaking other services. You can remove them manually if needed.

echo -e "${GREEN}=== Uninstallation Complete! ===${NC}"
