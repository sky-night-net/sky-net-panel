# Sky-Net VPN Panel

Universal VPN management dashboard for Ubuntu 24.04 LTS.
Supports: **AmneziaWG (v1/v2)** and **OpenVPN (XOR patch)**.

## Quick Install

Run this command on your Ubuntu server as root:

```bash
curl -sSL https://raw.githubusercontent.com/sky-night-net/sky-net-panel/main/install.sh | sudo bash
```

## Features
- **Premium Design**: Sleek dark interface, no emojis, purely professional.
- **System Reliability**: Built-in Fail2Ban, SSL (acme.sh), Systemd service, and DB Backups.
- **Protocol Agnostic**: Modular adapter system for easy extension.
- **Security**: Local-first SQLite with WAL mode, UFW integration.

## Default Credentials
- **Username**: `admin`
- **Password**: `admin`

## Manual Setup
If you prefer manual installation:
1. Clone the repo: `git clone https://github.com/USER/sky-net.git /opt/sky-net`
2. Install dependencies: `apt install python3-flask python3-psutil python3-flask-cors`
3. Run the panel: `python3 sky_net.py`
