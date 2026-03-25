# Sky-Net VPN Panel

Universal VPN management dashboard for Ubuntu 24.04 LTS.
Supports: **AmneziaWG (v1/v2)** and **OpenVPN (XOR patch)**.

## Quick Install

Run this command on your Ubuntu server as root:

```bash
curl -sSL https://raw.githubusercontent.com/sky-night-net/sky-net-panel/main/install.sh | sudo bash
```

## Uninstall

To completely remove the panel from your server:

```bash
curl -sSL https://raw.githubusercontent.com/sky-night-net/sky-net-panel/main/uninstall.sh | sudo bash
```

## Features
- **Premium Design**: Sleek dark interface, no emojis, purely professional.
- **System Reliability**: Built-in Fail2Ban, SSL (acme.sh), Systemd service, and DB Backups.
- **Protocol Agnostic**: Modular adapter system for easy extension.
- **Security**: Local-first SQLite with WAL mode, UFW integration.

## Default Credentials
- **Username**: `admin`
- **Password**: `admin`

## 📋 System Requirements
- **OS**: Ubuntu 22.04 / 24.04 LTS (x86_64 / ARM64)
- **CPU**: 1 Core (min), 2+ recommended for multiple inbounds
- **RAM**: 1 GB (min), 2 GB recommended
- **Disk**: 10 GB free space
- **Network**: Public IPv4 address, ports 22 and Panel Port must be open

## 🚀 One-Line Installation
:
1. Clone the repo: `git clone https://github.com/sky-night-net/sky-net-panel.git /opt/sky-net`
2. Install dependencies: `apt install python3-flask python3-psutil python3-flask-cors`
3. Run the panel: `python3 sky_net.py`
