#!/usr/bin/env python3
"""
Sky-Net v1.0 — Universal VPN Control Panel
───────────────────────────────────────────
Поддерживаемые протоколы: AmneziaWG v1, AmneziaWG v2, OpenVPN+XOR
"""

import json, os, time, threading, logging, sqlite3, hashlib, secrets, functools
from datetime import datetime
from flask import (Flask, jsonify, request, Response, redirect,
                   render_template_string, session, send_file, abort)
from flask_cors import CORS
from collections import deque
import urllib.request

# Импорт адаптеров
from adapters import AdapterFactory
from adapters.amneziawg_v1 import AmneziaWGv1Adapter
from adapters.amneziawg_v2 import AmneziaWGv2Adapter
from adapters.openvpn_xor import OpenVPNXORAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("sky-net")

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SKYNET_SECRET", secrets.token_hex(32))

PORT = int(os.getenv("SKYNET_PORT", "9090"))
DB_FILE = os.getenv("SKYNET_DB", "sky_net.db")
POLL_SEC = int(os.getenv("POLL_INTERVAL", "15"))

# ─── Database ────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

# ─── Auth Decorator ──────────────────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/panel/api/"):
                return jsonify({"success": False, "msg": "Unauthorized"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

# ─── API: System Management (Setup) ──────────────────────────────────────────

@app.route("/panel/api/system/setupService", methods=["POST"])
@login_required
def api_system_setup_service():
    """Создание и активация системного юнита skynet.service."""
    import subprocess
    script_path = os.path.abspath(__file__)
    work_dir = os.path.dirname(script_path)
    user = os.getenv("USER", "root")

    service_content = f"""[Unit]
Description=Sky-Net Universal VPN Panel
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={work_dir}
ExecStart=/usr/bin/python3 {script_path}
Restart=always
RestartSec=5
Environment=SKYNET_PORT={PORT}
Environment=SKYNET_DB={DB_FILE}
Environment=SKYNET_EXT_IP={get_public_ip()}

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/skynet.service"
    try:
        if os.getuid() != 0:
            return jsonify({"success": False, "msg": "Нужны права root"}), 403

        with open(service_path, "w") as f:
            f.write(service_content)

        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "skynet.service"], check=True)
        return jsonify({"success": True, "msg": "Сервис skynet.service установлен и включен в автозагрузку"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route("/panel/api/system/installFail2Ban", methods=["POST"])
@login_required
def api_system_install_fail2ban():
    """Установка и базовая защита панели через Fail2Ban."""
    import subprocess
    if os.getuid() != 0: return jsonify({"success": False, "msg": "Нужны права root"}), 403
    try:
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "fail2ban"], check=True)
        # Настройка jail для SSH и панели (упрощенно)
        jail_conf = """[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5

[skynet]
enabled = true
port = 9090
filter = nosmtp
logpath = /var/log/auth.log
maxretry = 10
"""
        with open("/etc/fail2ban/jail.local", "w") as f:
            f.write(jail_conf)
        subprocess.run(["systemctl", "restart", "fail2ban"], check=True)
        return jsonify({"success": True, "msg": "Fail2Ban установлен и настроен (jail.local)"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route("/panel/api/system/issueSSL", methods=["POST"])
@login_required
def api_system_issue_ssl():
    """Автоматизация SSL через acme.sh."""
    import subprocess
    data = request.json
    domain = data.get("domain")
    email = data.get("email", "admin@sky-net.io")
    if not domain: return jsonify({"success": False, "msg": "Домен обязателен"}), 400
    if os.getuid() != 0: return jsonify({"success": False, "msg": "Нужны права root"}), 403
    try:
        # Установка acme.sh если нет
        if not os.path.exists("/root/.acme.sh/acme.sh"):
            subprocess.run(["curl", "https://get.acme.sh", "|", "sh", "-s", "email=" + email], shell=True, check=True)
        
        # Выпуск (требует открытого 80 порта или DNS)
        cmd = [f"/root/.acme.sh/acme.sh", "--issue", "-d", domain, "--standalone"]
        subprocess.run(cmd, check=True)
        return jsonify({"success": True, "msg": f"Сертификат для {domain} выпущен"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route("/panel/api/db/backup", methods=["POST"])
@login_required
def api_db_backup():
    """Создание бэкапа базы данных."""
    import shutil
    try:
        backup_name = f"{DB_FILE}.bak_{int(time.time())}"
        shutil.copy2(DB_FILE, backup_name)
        return jsonify({"success": True, "msg": f"Бэкап создан: {backup_name}"})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

def get_public_ip():
    env_ip = os.getenv("SKYNET_EXT_IP")
    if env_ip: return env_ip
    try:
        url = 'https://api.ipify.org'
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.64.1'})
        return urllib.request.urlopen(req, timeout=5).read().decode('utf-8').strip()
    except:
        return ""

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS inbounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                protocol TEXT NOT NULL,
                remark TEXT DEFAULT '',
                port INTEGER NOT NULL,
                listen TEXT DEFAULT '0.0.0.0',
                enable INTEGER DEFAULT 1,
                settings TEXT DEFAULT '{}',
                obfuscation TEXT DEFAULT '{}',
                up INTEGER DEFAULT 0,
                down INTEGER DEFAULT 0,
                total_limit INTEGER DEFAULT 0,
                expiry_time INTEGER DEFAULT 0,
                created_at INTEGER
            );
            CREATE TABLE IF NOT EXISTS client_traffics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inbound_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                public_key TEXT DEFAULT '',
                private_key TEXT DEFAULT '',
                preshared_key TEXT DEFAULT '',
                allowed_ips TEXT DEFAULT '10.8.0.2/32',
                enable INTEGER DEFAULT 1,
                up INTEGER DEFAULT 0,
                down INTEGER DEFAULT 0,
                total_limit INTEGER DEFAULT 0,
                expiry_time INTEGER DEFAULT 0,
                last_online INTEGER DEFAULT 0,
                FOREIGN KEY(inbound_id) REFERENCES inbounds(id) ON DELETE CASCADE,
                UNIQUE(inbound_id, username)
            );
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS traffic_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER,
                up INTEGER DEFAULT 0,
                down INTEGER DEFAULT 0
            );
        """)
        # Default admin
        existing = db.execute("SELECT id FROM users LIMIT 1").fetchone()
        if not existing:
            pwd_hash = hashlib.sha256("admin".encode()).hexdigest()
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", pwd_hash))
        
        # Default settings
        detect_ip = get_public_ip()
        defaults = {
            "panel_port": str(PORT),
            "web_base_path": "",
            "session_timeout": "3600",
            "fail2ban_enabled": "false",
            "server_ip": detect_ip
        }
        for k, v in defaults.items():
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
        
        # Override with env var if present
        env_ip = os.getenv("SKYNET_EXT_IP")
        if env_ip:
            db.execute("UPDATE settings SET value=? WHERE key='server_ip'", (env_ip,))
        db.commit()
    log.info("Database initialized")

# ─── Auth ────────────────────────────────────────────────────────────────────

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/panel/api/"):
                return jsonify({"success": False, "msg": "Unauthorized"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form if request.form else request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                              (username, pwd_hash)).fetchone()
        if user:
            session["logged_in"] = True
            session["username"] = username
            return redirect("/")
        return render_template_string(LOGIN_HTML, error="Неверный логин или пароль")
    return render_template_string(LOGIN_HTML, error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ─── API: Inbounds ───────────────────────────────────────────────────────────

@app.route("/panel/api/inbounds/list")
@login_required
def api_inbounds_list():
    with get_db() as db:
        rows = db.execute("SELECT * FROM inbounds ORDER BY id").fetchall()
        inbounds = [dict(r) for r in rows]
        for ib in inbounds:
            clients = db.execute(
                "SELECT * FROM client_traffics WHERE inbound_id=?", (ib["id"],)
            ).fetchall()
            ib["clients"] = [dict(c) for c in clients]
    return jsonify({"success": True, "obj": inbounds})

@app.route("/panel/api/inbounds/add", methods=["POST"])
@login_required
def api_inbound_add():
    data = request.get_json(silent=True) or {}
    protocol = data.get("protocol", "amneziawg_v1")
    remark = data.get("remark", f"VPN-{int(time.time())}")
    port = int(data.get("port", 51820))
    obfuscation = json.dumps(data.get("obfuscation", {}))

    adapter = AdapterFactory.get(protocol)
    # Get server IP from settings or detect it
    with get_db() as db:
        res = db.execute("SELECT value FROM settings WHERE key='server_ip'").fetchone()
        server_ip = res["value"] if res and res["value"] else get_public_ip()
        if server_ip and (not res or not res["value"]):
             db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('server_ip', ?)", (server_ip,))
             db.commit()

    # Ensure binaries are installed
    try:
        adapter.check_and_install(server_ip)
    except Exception as e:
        log.error(f"Failed to ensure binaries for {protocol}: {e}")
        return jsonify({"success": False, "msg": f"Ошибка подготовки протокола: {e}"}), 500

    keys = {"private_key": "", "public_key": "", "server_ip": server_ip, "address": "10.8.0.1/24",
            "dns": "1.1.1.1, 8.8.8.8", "mtu": 1420}
    try:
        kp = adapter.generate_keypair()
        keys["private_key"] = kp.get("private_key", "")
        keys["public_key"] = kp.get("public_key", "")
    except Exception as e:
        log.warning(f"Keypair generation skipped: {e}")
    settings_dict = data.get("settings", {})
    if not isinstance(settings_dict, dict):
        settings_dict = {}
    settings = json.dumps({**keys, **settings_dict})

    with get_db() as db:
        db.execute(
            "INSERT INTO inbounds (protocol,remark,port,settings,obfuscation,created_at) "
            "VALUES (?,?,?,?,?,?)",
            (protocol, remark, port, settings, obfuscation, int(time.time()))
        )
        db.commit()
    
    # Auto-allow port in UFW
    import subprocess
    try:
        subprocess.run(["ufw", "allow", f"{port}/{'tcp' if 'openvpn' in protocol else 'udp'}"], check=False)
    except: pass

    return jsonify({"success": True, "msg": "Inbound создан"})

@app.route("/panel/api/inbounds/del/<int:ib_id>", methods=["POST"])
@login_required
def api_inbound_del(ib_id):
    with get_db() as db:
        ib = db.execute("SELECT port, protocol FROM inbounds WHERE id=?", (ib_id,)).fetchone()
        if ib:
             # Auto-delete port in UFW
             import subprocess
             try:
                 subprocess.run(["ufw", "delete", "allow", f"{ib['port']}/{'tcp' if 'openvpn' in ib['protocol'] else 'udp'}"], check=False)
             except: pass
        db.execute("DELETE FROM inbounds WHERE id=?", (ib_id,))
        db.commit()
    return jsonify({"success": True})

@app.route("/panel/api/inbounds/toggle/<int:ib_id>", methods=["POST"])
@login_required
def api_inbound_toggle(ib_id):
    with get_db() as db:
        row = db.execute("SELECT enable FROM inbounds WHERE id=?", (ib_id,)).fetchone()
        if not row:
            return jsonify({"success": False}), 404
        new_state = 0 if row["enable"] else 1
        db.execute("UPDATE inbounds SET enable=? WHERE id=?", (new_state, ib_id))
        db.commit()
    return jsonify({"success": True, "enable": new_state})

# ─── API: Clients ────────────────────────────────────────────────────────────

@app.route("/panel/api/inbounds/addClient", methods=["POST"])
@login_required
def api_client_add():
    data = request.get_json(silent=True) or {}
    inbound_id = int(data.get("inbound_id", 0))
    username = data.get("username", f"user-{int(time.time())}")
    total_limit = int(data.get("total_limit", 0))
    expiry_time = int(data.get("expiry_time", 0))

    with get_db() as db:
        ib = db.execute("SELECT * FROM inbounds WHERE id=?", (inbound_id,)).fetchone()
        if not ib:
            return jsonify({"success": False, "msg": "Inbound не найден"}), 404

        # Определить следующий IP
        existing = db.execute(
            "SELECT allowed_ips FROM client_traffics WHERE inbound_id=? ORDER BY id DESC LIMIT 1",
            (inbound_id,)
        ).fetchone()
        if existing:
            last_ip = existing["allowed_ips"].split("/")[0]
            parts = last_ip.split(".")
            parts[3] = str(int(parts[3]) + 1)
            next_ip = ".".join(parts) + "/32"
        else:
            next_ip = "10.8.0.2/32"

        # Генерация ключей
        adapter = AdapterFactory.get(ib["protocol"])
        keys = {}
        try:
            keys = adapter.generate_keypair()
        except Exception:
            pass

        db.execute(
            "INSERT INTO client_traffics "
            "(inbound_id,username,public_key,private_key,preshared_key,allowed_ips,"
            "total_limit,expiry_time) VALUES (?,?,?,?,?,?,?,?)",
            (inbound_id, username, keys.get("public_key", ""),
             keys.get("private_key", ""), keys.get("preshared_key", ""),
             next_ip, total_limit, expiry_time)
        )
        db.commit()
    return jsonify({"success": True, "msg": f"Клиент {username} добавлен"})

@app.route("/panel/api/inbounds/delClient/<int:client_id>", methods=["POST"])
@login_required
def api_client_del(client_id):
    with get_db() as db:
        db.execute("DELETE FROM client_traffics WHERE id=?", (client_id,))
        db.commit()
    return jsonify({"success": True})

@app.route("/panel/api/inbounds/toggleClient/<int:client_id>", methods=["POST"])
@login_required
def api_client_toggle(client_id):
    with get_db() as db:
        row = db.execute("SELECT enable FROM client_traffics WHERE id=?", (client_id,)).fetchone()
        if not row:
            return jsonify({"success": False}), 404
        new = 0 if row["enable"] else 1
        db.execute("UPDATE client_traffics SET enable=? WHERE id=?", (new, client_id))
        db.commit()
    return jsonify({"success": True, "enable": new})

@app.route("/panel/api/inbounds/resetClientTraffic/<int:client_id>", methods=["POST"])
@login_required
def api_client_reset_traffic(client_id):
    with get_db() as db:
        db.execute("UPDATE client_traffics SET up=0, down=0 WHERE id=?", (client_id,))
        db.commit()
    return jsonify({"success": True})

@app.route("/panel/api/inbounds/clientConfig/<int:client_id>")
@login_required
def api_client_config(client_id):
    with get_db() as db:
        client = db.execute("SELECT * FROM client_traffics WHERE id=?", (client_id,)).fetchone()
        if not client:
            return jsonify({"success": False}), 404
        ib = db.execute("SELECT * FROM inbounds WHERE id=?", (client["inbound_id"],)).fetchone()
        if not ib:
            return jsonify({"success": False}), 404
    adapter = AdapterFactory.get(ib["protocol"])
    config_text = adapter.generate_client_config(dict(client), dict(ib))
    return jsonify({"success": True, "config": config_text})

# ─── API: Server Status ─────────────────────────────────────────────────────

@app.route("/server/status")
@login_required
def api_server_status():
    import platform
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        uptime = int(time.time() - psutil.boot_time())
        net = psutil.net_io_counters()
        return jsonify({
            "cpu": cpu, "mem_percent": mem.percent,
            "mem_used": mem.used, "mem_total": mem.total,
            "disk_percent": disk.percent, "disk_used": disk.used, "disk_total": disk.total,
            "uptime": uptime, "net_sent": net.bytes_sent, "net_recv": net.bytes_recv,
            "hostname": platform.node(),
            "os_version": f"{platform.system()} {platform.release()}"
        })
    except ImportError:
        return jsonify({"cpu": 0, "mem_percent": 0, "uptime": 0, "error": "psutil not installed"})

# ─── API: Settings ───────────────────────────────────────────────────────────

@app.route("/panel/api/settings", methods=["GET", "POST"])
@login_required
def api_settings():
    with get_db() as db:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            for k, v in data.items():
                db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
            db.commit()
            return jsonify({"success": True})
        rows = db.execute("SELECT key, value FROM settings").fetchall()
    return jsonify({"success": True, "obj": {r["key"]: r["value"] for r in rows}})

@app.route("/panel/api/settings/updateUser", methods=["POST"])
@login_required
def api_update_user():
    data = request.get_json(silent=True) or {}
    old_pass = data.get("old_password", "")
    new_user = data.get("new_username", "")
    new_pass = data.get("new_password", "")
    old_hash = hashlib.sha256(old_pass.encode()).hexdigest()
    with get_db() as db:
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (session.get("username"), old_hash)).fetchone()
        if not user:
            return jsonify({"success": False, "msg": "Неверный старый пароль"}), 403
        new_hash = hashlib.sha256(new_pass.encode()).hexdigest()
        db.execute("UPDATE users SET username=?, password=? WHERE id=?",
                   (new_user, new_hash, user["id"]))
        db.commit()
    session["username"] = new_user
    return jsonify({"success": True})

@app.route("/panel/api/db/export")
@login_required
def api_db_export():
    return send_file(DB_FILE, as_attachment=True, download_name="sky_net_backup.db")

@app.route("/panel/api/db/import", methods=["POST"])
@login_required
def api_db_import():
    f = request.files.get("file")
    if not f:
        return jsonify({"success": False, "msg": "No file"}), 400
    import shutil
    backup_path = DB_FILE + ".bak"
    shutil.copy2(DB_FILE, backup_path)
    f.save(DB_FILE)
    init_db()
    return jsonify({"success": True, "msg": "Database imported"})

# ─── API: Firewall (UFW) ────────────────────────────────────────────────────

@app.route("/panel/api/firewall/status")
@login_required
def api_firewall_status():
    import subprocess
    r = subprocess.run(["ufw", "status", "numbered"], capture_output=True, text=True)
    lines = r.stdout.strip().split("\n") if r.returncode == 0 else []
    active = any("Status: active" in l for l in lines)
    rules = []
    for l in lines:
        l = l.strip()
        if l.startswith("["):
            rules.append(l)
    return jsonify({"success": True, "active": active, "rules": rules, "raw": r.stdout})

@app.route("/panel/api/firewall/toggle", methods=["POST"])
@login_required
def api_firewall_toggle():
    import subprocess
    data = request.get_json(silent=True) or {}
    action = "enable" if data.get("enable") else "disable"
    r = subprocess.run(["ufw", "--force", action], capture_output=True, text=True)
    return jsonify({"success": r.returncode == 0, "output": r.stdout + r.stderr})

@app.route("/panel/api/firewall/addRule", methods=["POST"])
@login_required
def api_firewall_add_rule():
    import subprocess
    data = request.get_json(silent=True) or {}
    port = data.get("port", "")
    proto = data.get("proto", "")
    action = data.get("action", "allow")
    from_ip = data.get("from_ip", "any")
    cmd = ["ufw", action]
    if from_ip and from_ip != "any":
        cmd += ["from", from_ip]
    cmd += ["to", "any", "port", str(port)]
    if proto:
        cmd += ["proto", proto]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return jsonify({"success": r.returncode == 0, "output": r.stdout + r.stderr})

@app.route("/panel/api/firewall/delRule", methods=["POST"])
@login_required
def api_firewall_del_rule():
    import subprocess
    data = request.get_json(silent=True) or {}
    rule_num = data.get("rule_num", "")
    r = subprocess.run(["ufw", "--force", "delete", str(rule_num)],
                       capture_output=True, text=True)
    return jsonify({"success": r.returncode == 0, "output": r.stdout + r.stderr})

# ─── API: Network & System ──────────────────────────────────────────────────

@app.route("/panel/api/system/network")
@login_required
def api_system_network():
    try:
        import psutil
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        interfaces = []
        for name, addr_list in addrs.items():
            iface = {"name": name, "addresses": [], "is_up": False, "speed": 0}
            if name in stats:
                iface["is_up"] = stats[name].isup
                iface["speed"] = stats[name].speed
            for a in addr_list:
                if a.family.name == "AF_INET":
                    iface["addresses"].append({"ip": a.address, "netmask": a.netmask, "type": "IPv4"})
                elif a.family.name == "AF_INET6":
                    iface["addresses"].append({"ip": a.address, "type": "IPv6"})
            interfaces.append(iface)
        return jsonify({"success": True, "interfaces": interfaces})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/panel/api/system/services")
@login_required
def api_system_services():
    import subprocess
    r = subprocess.run(
        ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--plain"],
        capture_output=True, text=True
    )
    services: list[dict[str, str]] = []
    for line in r.stdout.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 5:
            services.append({
                "name": parts[0], 
                "status": parts[2], 
                "description": " ".join(parts[4:])
            })
    return jsonify({"success": True, "services": services[:30]})

@app.route("/panel/api/system/logs")
@login_required
def api_system_logs():
    import subprocess
    lines = int(request.args.get("lines", 50))
    unit = request.args.get("unit", "")
    cmd = ["journalctl", "-n", str(lines), "--no-pager", "-o", "short"]
    if unit:
        cmd += ["-u", unit]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return jsonify({"success": True, "logs": r.stdout})

@app.route("/panel/api/system/hostname", methods=["GET", "POST"])
@login_required
def api_system_hostname():
    import subprocess
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        new_name = data.get("hostname", "")
        if new_name:
            subprocess.run(["hostnamectl", "set-hostname", new_name],
                           capture_output=True, text=True)
            return jsonify({"success": True})
        return jsonify({"success": False}), 400
    r = subprocess.run(["hostname"], capture_output=True, text=True)
    return jsonify({"success": True, "hostname": r.stdout.strip()})

@app.route("/panel/api/system/dns", methods=["GET", "POST"])
@login_required
def api_system_dns():
    dns_file = "/etc/resolv.conf"
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        servers = data.get("servers", [])
        try:
            with open(dns_file, "w") as f:
                for s in servers:
                    f.write(f"nameserver {s}\n")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    try:
        with open(dns_file) as f:
            lines = [l.strip().split()[1] for l in f if l.strip().startswith("nameserver")]
        return jsonify({"success": True, "servers": lines})
    except Exception as e:
        return jsonify({"success": False, "servers": [], "error": str(e)})

@app.route("/panel/api/system/timezone", methods=["GET", "POST"])
@login_required
def api_system_timezone():
    import subprocess
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        tz = data.get("timezone", "")
        if tz:
            subprocess.run(["timedatectl", "set-timezone", tz], capture_output=True, text=True)
            return jsonify({"success": True})
        return jsonify({"success": False}), 400
    r = subprocess.run(["timedatectl", "show", "--property=Timezone", "--value"],
                       capture_output=True, text=True)
    return jsonify({"success": True, "timezone": r.stdout.strip()})

# ─── Traffic History ─────────────────────────────────────────────────────────

traffic_history = {"up": deque([0]*60, maxlen=60), "down": deque([0]*60, maxlen=60)}

@app.route("/panel/api/trafficHistory")
@login_required
def api_traffic_history():
    return jsonify({"up": list(traffic_history["up"]), "down": list(traffic_history["down"])})

# ─── Pages (HTML rendered from templates/main.html) ──────────────────────────

@app.route("/")
@login_required
def page_dashboard():
    return render_template_string(MAIN_HTML, page="dashboard")

@app.route("/inbounds")
@login_required
def page_inbounds():
    return render_template_string(MAIN_HTML, page="inbounds")

@app.route("/clients")
@login_required
def page_clients():
    return render_template_string(MAIN_HTML, page="clients")

@app.route("/settings")
@login_required
def page_settings():
    return render_template_string(MAIN_HTML, page="settings")

@app.route("/firewall")
@login_required
def page_firewall():
    return render_template_string(MAIN_HTML, page="firewall")

@app.route("/system")
@login_required
def page_system():
    return render_template_string(MAIN_HTML, page="system")

@app.route("/logs")
@login_required
def page_logs():
    return render_template_string(MAIN_HTML, page="logs")

# ─── HTML Templates (embedded) ──────────────────────────────────────────────
# Will be defined in templates file and imported
from templates_html import LOGIN_HTML, MAIN_HTML

# ─── Background Poller ──────────────────────────────────────────────────────

def poll_traffic():
    while True:
        try:
            with get_db() as db:
                total_up = 0
                total_down = 0
                inbounds = db.execute("SELECT * FROM inbounds WHERE enable=1").fetchall()
                for ib in inbounds:
                    try:
                        adapter = AdapterFactory.get(ib["protocol"])
                        stats = adapter.get_traffic(dict(ib))
                        for s in stats:
                            key_field = "public_key" if "public_key" in s else "username"
                            client = db.execute(
                                f"SELECT * FROM client_traffics WHERE inbound_id=? AND {key_field}=?",
                                (ib["id"], s[key_field])
                            ).fetchone()
                            if client:
                                db.execute(
                                    "UPDATE client_traffics SET up=?, down=?, last_online=? WHERE id=?",
                                    (s.get("tx", 0), s.get("rx", 0), int(time.time()), client["id"])
                                )
                                tx = s.get("tx", 0)
                                rx = s.get("rx", 0)
                                if isinstance(tx, (int, float)):
                                    total_up += int(tx)
                                if isinstance(rx, (int, float)):
                                    total_down += int(rx)
                                # Traffic limit enforcement
                                if client["total_limit"] > 0:
                                    used = s.get("tx", 0) + s.get("rx", 0)
                                    if used >= client["total_limit"] and client["enable"]:
                                        db.execute("UPDATE client_traffics SET enable=0 WHERE id=?",
                                                   (client["id"],))
                                        adapter.toggle_client(dict(client), dict(ib), False)
                                        log.info(f"Client {client['username']} disabled (limit reached)")
                    except Exception as e:
                        log.debug(f"Poll error for inbound {ib['id']}: {e}")
                traffic_history["up"].append(total_up)
                traffic_history["down"].append(total_down)
                db.commit()
        except Exception as e:
            log.error(f"Poll error: {e}")
        time.sleep(POLL_SEC)

# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    t = threading.Thread(target=poll_traffic, daemon=True)
    t.start()
    log.info(f"Sky-Net started on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
