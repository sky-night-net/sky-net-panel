#!/usr/bin/env python3
"""
Sky-Net v1.0 — Universal VPN Control Panel
───────────────────────────────────────────
Поддерживаемые протоколы: AmneziaWG v1, AmneziaWG v2, OpenVPN+XOR
"""

import json, os, time, threading, logging, sqlite3, hashlib, secrets, functools, subprocess, re, socket, ipaddress
import psutil
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
CORS(app, supports_credentials=True)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(SCRIPT_DIR, "sky_net.db")
DB_FILE = os.getenv("SKYNET_DB", DEFAULT_DB)

# ─── Database ────────────────────────────────────────────────────────────────
import contextlib

@contextlib.contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()

def check_schema():
    with get_db() as db:
        # Ensure firewall_rules table exists
        db.execute("""
            CREATE TABLE IF NOT EXISTS firewall_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 100,
                action TEXT DEFAULT 'allow',
                protocol TEXT DEFAULT 'any',
                src_ip TEXT DEFAULT 'any',
                src_port TEXT DEFAULT 'any',
                dst_ip TEXT DEFAULT 'any',
                dst_port TEXT DEFAULT 'any',
                interface TEXT DEFAULT 'any',
                comment TEXT DEFAULT ''
            )
        """)
        
        # Check for missing columns and add them if necessary
        res = db.execute("PRAGMA table_info(firewall_rules)").fetchall()
        cols = [r["name"] for r in res]
        if "interface" not in cols:
            db.execute("ALTER TABLE firewall_rules ADD COLUMN interface TEXT DEFAULT 'any'")
        if "schedule" not in cols:
            db.execute("ALTER TABLE firewall_rules ADD COLUMN schedule TEXT DEFAULT 'always'")
        db.commit()

# Call schema check on startup
check_schema()

# ─── Persistent Secret Key ───────────────────────────────────────────────────
def get_secret_key():
    with get_db() as db:
        # Check if settings table exists first
        db.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL, value TEXT DEFAULT '')")
        res = db.execute("SELECT value FROM settings WHERE key='secret_key'").fetchone()
        if res and res[0]:
            return res[0]
        else:
            new_key = secrets.token_hex(32)
            db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('secret_key', ?)", (new_key,))
            db.commit()
            return new_key

app.secret_key = get_secret_key()
# Load Port Settings with Collision Protection
# Priority: 1. Database settings, 2. Environment variables, 3. Hardcoded defaults
DEFAULT_HTTP_PORT = 4467
DEFAULT_HTTPS_PORT = 4466

PORT = int(os.getenv("SKYNET_PORT", str(DEFAULT_HTTP_PORT)))
HTTPS_PORT = int(os.getenv("SKYNET_HTTPS_PORT", str(DEFAULT_HTTPS_PORT)))

with get_db() as db:
    p1 = db.execute("SELECT value FROM settings WHERE key='panel_port'").fetchone()
    if p1 and p1[0].isdigit():
        PORT = int(p1[0])
    p2 = db.execute("SELECT value FROM settings WHERE key='panel_port_https'").fetchone()
    if p2 and p2[0].isdigit():
        HTTPS_PORT = int(p2[0])

# Prevent collision: If ports are same, shift the HTTP port
if PORT == HTTPS_PORT:
    log.warning(f"Port collision detected ({PORT}). Resolving...")
    if HTTPS_PORT == 4466: PORT = 4467
    else: PORT = HTTPS_PORT + 1
    log.info(f"Resolved collision: HTTP={PORT}, HTTPS={HTTPS_PORT}")

# Persistence: Save to DB if missing (crucial for clean installs)
with get_db() as db:
    r1 = db.execute("SELECT 1 FROM settings WHERE key='panel_port'").fetchone()
    if not r1:
        db.execute("INSERT INTO settings (key, value) VALUES ('panel_port', ?)", (str(PORT),))
    r2 = db.execute("SELECT 1 FROM settings WHERE key='panel_port_https'").fetchone()
    if not r2:
        db.execute("INSERT INTO settings (key, value) VALUES ('panel_port_https', ?)", (str(HTTPS_PORT),))
    
    # Also persist server_ip if available in ENV or detected, but missing in DB
    r3 = db.execute("SELECT 1 FROM settings WHERE key='server_ip'").fetchone()
    if not r3:
        # Check for old key 'panel_ext_ip' for backward compat
        old_r = db.execute("SELECT value FROM settings WHERE key='panel_ext_ip'").fetchone()
        if old_r:
            db.execute("INSERT INTO settings (key, value) VALUES ('server_ip', ?)", (old_r[0],))
        else:
            env_ip = os.getenv("SKYNET_EXT_IP") or get_public_ip()
            if env_ip:
                db.execute("INSERT INTO settings (key, value) VALUES ('server_ip', ?)", (env_ip,))
    db.commit()
POLL_SEC = int(os.getenv("POLL_INTERVAL", "15"))

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

@app.route("/panel/api/system/cmd", methods=["POST"])
@login_required
def api_system_cmd():
    """Выполнение команд оболочки через Web CLI."""
    import subprocess
    data = request.get_json(force=True, silent=True) or {}
    cmd = data.get("cmd", "")
    if not cmd: return jsonify({"success": False, "output": "Empty command"})
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = result.stdout
        if result.stderr:
            out = (out + "\n" + result.stderr).strip() if out else result.stderr.strip()
        if not out:
            out = "(done, exit code: {})".format(result.returncode)
        return jsonify({"success": True, "output": out.strip()})
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "output": "Command timed out (30s)."})
    except Exception as e:
        return jsonify({"success": False, "output": str(e)})

@app.route("/panel/api/system/start_ttyd", methods=["POST"])
@login_required
def api_start_ttyd():
    """Запуск Web SSH (ttyd) на порту 7681."""
    import subprocess, socket
    if os.getuid() != 0: return jsonify({"success": False, "msg": "Root privileges required."})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        in_use = s.connect_ex(('localhost', 7681)) == 0
    if in_use: return jsonify({"success": True, "port": 7681})
    try:
        res = subprocess.run(["which", "ttyd"], capture_output=True, text=True)
        ttyd_path = res.stdout.strip()
        if not ttyd_path:
            import urllib.request
            ttyd_path = "/usr/local/bin/ttyd"
            try:
                urllib.request.urlretrieve("https://github.com/tsl0922/ttyd/releases/download/1.7.3/ttyd.x86_64", ttyd_path)
                os.chmod(ttyd_path, 0o755)
            except Exception as dl_err:
                return jsonify({"success": False, "msg": f"Failed to download ttyd: {dl_err}"})
                
        subprocess.Popen([ttyd_path, "-p", "7681", "-W", "bash"])
        return jsonify({"success": True, "port": 7681})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route("/panel/api/system/logs/download", methods=["GET"])
@login_required
def api_system_logs_download():
    """Скачать журнал событий (.txt)."""
    import subprocess
    unit = request.args.get("unit", "skynet")
    try:
        res = subprocess.run(["journalctl", "-u", unit, "--no-pager"], capture_output=True, text=True)
        return Response(res.stdout, mimetype="text/plain", headers={"Content-disposition": f"attachment; filename={unit}_logs.txt"})
    except Exception as e:
        return str(e), 500

@app.route("/panel/api/system/logs/settings", methods=["POST"])
@login_required
def api_system_logs_settings():
    """Управление хранением журнала."""
    import subprocess
    if os.getuid() != 0: return jsonify({"success": False, "msg": "Root privileges required."})
    data = request.json
    retention = data.get("retention", "")
    try:
        if retention:
            # Vacuum older logs immediately
            subprocess.run(["journalctl", f"--vacuum-time={retention}"], check=True)
        return jsonify({"success": True, "msg": "Log settings applied."})
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

@app.route("/panel/api/system/save-public-ip", methods=["POST"])
@login_required
def api_system_save_public_ip():
    data = request.json
    val = data.get("value", "").strip()
    with get_db() as db:
        db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('public_ip_override', ?)", (val,))
        # Also sync to 'server_ip' for immediate effect in new inbounds
        if val:
            db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('server_ip', ?)", (val,))
        db.commit()
    return jsonify({"success": True})

@app.route("/panel/api/system/settings", methods=["GET"])
@login_required
def api_system_get_settings():
    with get_db() as db:
        res = db.execute("SELECT key, value FROM settings").fetchall()
        return jsonify({r["key"]: r["value"] for r in res})


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
            CREATE TABLE IF NOT EXISTS firewall_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enabled INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 100,
                action TEXT NOT NULL,
                protocol TEXT DEFAULT 'any',
                src_ip TEXT DEFAULT 'any',
                src_port TEXT DEFAULT 'any',
                dst_ip TEXT DEFAULT 'any',
                dst_port TEXT DEFAULT 'any',
                interface TEXT DEFAULT 'any',
                comment TEXT DEFAULT ''
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
            "server_ip": detect_ip,
            "ntp_servers": "pool.ntp.org"
        }
        for k, v in defaults.items():
            db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
            
        # Seed failsafe firewall rules if empty
        fw_count = db.execute("SELECT COUNT(id) FROM firewall_rules").fetchone()[0]
        if fw_count == 0:
            safe_rules = [
                (1, 10, 'allow', 'tcp', 'any', 'any', 'any', '22', 'any', 'SSH Failsafe'),
                (1, 20, 'allow', 'tcp', 'any', 'any', 'any', str(PORT), 'any', 'Panel HTTP Failsafe')
            ]
            db.executemany("INSERT INTO firewall_rules (enabled, priority, action, protocol, src_ip, src_port, dst_ip, dst_port, interface, comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", safe_rules)
            db.commit()
        
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
        log.info(f"API List: Found {len(inbounds)} inbounds in DB")
        for ib in inbounds:
            clients = db.execute(
                "SELECT * FROM client_traffics WHERE inbound_id=?", (ib["id"],)
            ).fetchall()
            ib["clients"] = [dict(c) for c in clients]
            log.info(f"Inbound {ib['id']} ({ib['protocol']}): {len(ib['clients'])} clients")
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
        
        # Fallback to current request host if still empty (likely local network)
        if not server_ip:
            server_ip = request.host.split(':')[0]
            
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
        new_ib = db.execute("SELECT * FROM inbounds WHERE id=last_insert_rowid()").fetchone()
        if new_ib:
            try:
                ib_dict = enrich_inbound_with_clients(db, dict(new_ib))
                adapter.start(ib_dict)
            except Exception as e: log.error(f"Failed to start inbound: {e}")
    
    # Auto-allow port in UFW AND register in firewall_rules DB
    import subprocess
    try:
        proto_cfg = "tcp" if "openvpn" in protocol else "udp"
        subprocess.run(["ufw", "allow", f"{port}/{proto_cfg}"], check=False)
        # Also register in DB so _apply_firewall_rules() preserves it
        with get_db() as db:
            existing = db.execute(
                "SELECT id FROM firewall_rules WHERE dst_port=? AND protocol=? AND comment LIKE 'VPN:%'",
                (str(port), proto_cfg)
            ).fetchone()
            if not existing:
                max_prio = db.execute("SELECT COALESCE(MAX(priority),0) FROM firewall_rules").fetchone()[0]
                db.execute(
                    "INSERT INTO firewall_rules (enabled,priority,action,protocol,src_ip,src_port,dst_ip,dst_port,interface,comment) "
                    "VALUES (1,?,?,?,?,?,?,?,?,?)",
                    (max_prio + 10, "allow", proto_cfg, "any", "any", "any", str(port), "any", f"VPN: {remark}")
                )
                db.commit()
    except Exception as e:
        log.warning(f"Auto-register VPN port rule failed: {e}")

    return jsonify({"success": True, "msg": "Inbound создан"})

@app.route("/panel/api/inbounds/del/<int:ib_id>", methods=["POST"])
@login_required
def api_inbound_del(ib_id):
    with get_db() as db:
        ib = db.execute("SELECT * FROM inbounds WHERE id=?", (ib_id,)).fetchone()
        if ib:
             proto_cfg = 'tcp' if 'openvpn' in ib['protocol'] else 'udp'
             port = ib['port']
             # Auto-delete port in UFW
             import subprocess
             try:
                 subprocess.run(["ufw", "delete", "allow", f"{port}/{proto_cfg}"], check=False)
             except: pass
             # Also remove from firewall_rules DB
             try:
                 db.execute(
                     "DELETE FROM firewall_rules WHERE dst_port=? AND protocol=? AND comment LIKE 'VPN:%'",
                     (str(port), proto_cfg)
                 )
             except: pass
             try: AdapterFactory.get(ib["protocol"]).stop(dict(ib))
             except Exception as e: log.error(f"Failed to stop inbound {ib_id}: {e}")
        db.execute("DELETE FROM inbounds WHERE id=?", (ib_id,))
        db.commit()
    return jsonify({"success": True})

@app.route("/panel/api/inbounds/toggle/<int:ib_id>", methods=["POST"])
@login_required
def api_inbound_toggle(ib_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM inbounds WHERE id=?", (ib_id,)).fetchone()
        if not row:
            return jsonify({"success": False}), 404
        new_state = 0 if row["enable"] else 1
        db.execute("UPDATE inbounds SET enable=? WHERE id=?", (new_state, ib_id))
        db.commit()
        ib = db.execute("SELECT * FROM inbounds WHERE id=?", (ib_id,)).fetchone()
        if ib:
            try:
                adapter = AdapterFactory.get(ib["protocol"])
                port = ib.get("port")
                proto = "udp" if "wg" in ib["protocol"] or "openvpn" in ib["protocol"] else "tcp"
                
                if new_state:
                    # Auto-allow port in UFW
                    subprocess.run(["ufw", "allow", f"{port}/{proto}"], capture_output=True)
                    
                    ib_dict = enrich_inbound_with_clients(db, dict(ib))
                    adapter.start(ib_dict)
                else:
                    # Auto-delete port in UFW (optional, but cleaner)
                    subprocess.run(["ufw", "delete", "allow", f"{port}/{proto}"], capture_output=True)
                    
                    adapter.stop(dict(ib))
            except Exception as e: log.error(f"Toggle error: {e}")
    return jsonify({"success": True, "enable": new_state})

@app.route("/panel/api/inbounds/logs/<int:ib_id>")
@login_required
def api_inbound_logs(ib_id):
    with get_db() as db:
        ib = db.execute("SELECT * FROM inbounds WHERE id=?", (ib_id,)).fetchone()
        if not ib: return jsonify({"success": False, "msg": "Inbound not found"}), 404
        
        protocol = ib["protocol"]
        output = ""
        try:
            if protocol == "openvpn_xor":
                # Get Docker logs
                container_name = f"openvpn_xor_{ib_id}"
                r = subprocess.run(["docker", "logs", "--tail", "100", container_name], capture_output=True, text=True)
                output = r.stdout + r.stderr
            else:
                # Get Journalctl logs for AmneziaWG (assuming it runs under systemd if it had a unit)
                # Or we can check if it's running via wg-quick
                unit = f"awg-quick@{ib['name']}"
                r = subprocess.run(["journalctl", "-u", unit, "--no-pager", "-n", "100"], capture_output=True, text=True)
                output = r.stdout + r.stderr
                
            if not output: output = "(No logs found)"
            return jsonify({"success": True, "logs": output})
        except Exception as e:
            return jsonify({"success": False, "msg": str(e)})

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
        if ib["enable"]:
            try:
                client = db.execute("SELECT * FROM client_traffics WHERE id=last_insert_rowid()").fetchone()
                AdapterFactory.get(ib["protocol"]).add_client(dict(client), dict(ib))
            except Exception as e: log.error(f"Failed to add client to running iface: {e}")
    return jsonify({"success": True, "msg": f"Клиент {username} добавлен"})

@app.route("/panel/api/inbounds/delClient/<int:client_id>", methods=["POST"])
@login_required
def api_client_del(client_id):
    with get_db() as db:
        client = db.execute("SELECT * FROM client_traffics WHERE id=?", (client_id,)).fetchone()
        if client:
            ib = db.execute("SELECT * FROM inbounds WHERE id=?", (client["inbound_id"],)).fetchone()
            if ib and ib["enable"]:
                try: AdapterFactory.get(ib["protocol"]).remove_client(dict(client), dict(ib))
                except Exception as e: log.error(f"Failed to remove client from running iface: {e}")
        db.execute("DELETE FROM client_traffics WHERE id=?", (client_id,))
        db.commit()
    return jsonify({"success": True})

@app.route("/panel/api/inbounds/toggleClient/<int:client_id>", methods=["POST"])
@login_required
def api_client_toggle(client_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM client_traffics WHERE id=?", (client_id,)).fetchone()
        if not row:
            return jsonify({"success": False}), 404
        new = 0 if row["enable"] else 1
        db.execute("UPDATE client_traffics SET enable=? WHERE id=?", (new, client_id))
        db.commit()
        ib = db.execute("SELECT * FROM inbounds WHERE id=?", (row["inbound_id"],)).fetchone()
        if ib and ib["enable"]:
             client = db.execute("SELECT * FROM client_traffics WHERE id=?", (client_id,)).fetchone()
             try: AdapterFactory.get(ib["protocol"]).toggle_client(dict(client), dict(ib), bool(new))
             except Exception as e: log.error(f"Failed to toggle client: {e}")
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

@app.route("/panel/api/server/status")
@login_required
def api_server_status():
    import platform
    public_ip = get_public_ip() or "--"

    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        uptime = int(time.time() - psutil.boot_time())
        net = psutil.net_io_counters()
        net_faces = psutil.net_io_counters(pernic=True)
        ifaces_traffic = {}
        for nic, st in net_faces.items():
            ifaces_traffic[nic] = {"bytes_sent": st.bytes_sent, "bytes_recv": st.bytes_recv}
        
        load1, load5, load15 = os.getloadavg()
        
        # Check HTTPS status
        https_status = "Отключен"
        with get_db() as db:
            s_mode = db.execute("SELECT value FROM settings WHERE key='ssl_mode'").fetchone()
            if s_mode and s_mode[0] != "off":
                https_status = "Активен"

        try:
            current_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd="/opt/sky-net").decode().strip()
            panel_version = f"v3.0 ({current_hash})"
        except Exception:
            panel_version = "v3.0"

        return jsonify({
            "cpu": cpu, "mem_percent": mem.percent,
            "mem_used": mem.used, "mem_total": mem.total,
            "disk_percent": disk.percent, "disk_used": disk.used, "disk_total": disk.total,
            "uptime": uptime, "net_sent": net.bytes_sent, "net_recv": net.bytes_recv,
            "interfaces": ifaces_traffic,
            "hostname": platform.node(),
            "os_version": f"{platform.system()} {platform.release()}",
            "public_ip": public_ip,
            "load_avg": f"{load1:.2f}  {load5:.2f}  {load15:.2f}",
            "panel_version": panel_version,
            "https_status": https_status,
            "panel_port": PORT,
            "panel_port_https": HTTPS_PORT,
            "server_time": int(time.time())
        })
    except Exception as e:
        log.error(f"Error in api_server_status: {e}")
        return jsonify({
            "cpu": 0, "mem_percent": 0, "disk_percent": 0,
            "uptime": 0, "public_ip": public_ip, "error": str(e)
        })

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

# ─── API: Full System Backup & Restore ────────────────────────────────────────

@app.route("/panel/api/system/ssl-status", methods=["GET"])
@login_required
def api_system_ssl_status():
    with get_db() as db:
        mode = db.execute("SELECT value FROM settings WHERE key='ssl_mode'").fetchone()
        cert = db.execute("SELECT value FROM settings WHERE key='ssl_cert'").fetchone()
        key = db.execute("SELECT value FROM settings WHERE key='ssl_key'").fetchone()
        domain = db.execute("SELECT value FROM settings WHERE key='panel_domain'").fetchone()
    
    mode = mode[0] if mode else "off"
    cert_path = cert[0] if cert else ""
    key_path = key[0] if key else ""
    domain_val = domain[0] if domain else ""
    
    active = False
    if mode != "off" and cert_path and key_path:
        if os.path.exists(cert_path) and os.path.exists(key_path):
            active = True
            
    return jsonify({
        "mode": mode,
        "domain": domain_val,
        "active": active,
        "cert_path": cert_path,
        "key_path": key_path
    })

@app.route("/panel/api/system/backup")
@login_required
def api_system_backup():
    """Create a full ZIP backup: DB + VPN configs + panel settings."""
    import zipfile, tempfile, shutil
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"skynet_backup_{ts}.zip"
    tmp_path = os.path.join(tempfile.gettempdir(), backup_name)
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Database
            if os.path.exists(DB_FILE):
                zf.write(DB_FILE, "sky_net.db")
            # OpenVPN configs
            for cfg_dir in ["/etc/openvpn", "/etc/wireguard"]:
                if os.path.isdir(cfg_dir):
                    for root, dirs, files in os.walk(cfg_dir):
                        for fname in files:
                            fp = os.path.join(root, fname)
                            zf.write(fp, fp.lstrip("/"))
            # Panel PKI (EasyRSA keys)
            pki_dir = "/etc/openvpn/pki"
            if os.path.isdir(pki_dir):
                for root, dirs, files in os.walk(pki_dir):
                    for fname in files:
                        fp = os.path.join(root, fname)
                        zf.write(fp, fp.lstrip("/"))
        return send_file(tmp_path, as_attachment=True, download_name=backup_name,
                         mimetype="application/zip")
    except Exception as e:
        log.error(f"Backup failed: {e}")
        return jsonify({"success": False, "msg": str(e)}), 500

@app.route("/panel/api/system/restore", methods=["POST"])
@login_required
def api_system_restore():
    """Restore from a ZIP backup file."""
    import zipfile, shutil, tempfile
    f = request.files.get("file")
    if not f or not f.filename.endswith(".zip"):
        return jsonify({"success": False, "msg": "Загрузите файл .zip"}), 400
    tmp_path = os.path.join(tempfile.gettempdir(), "skynet_restore.zip")
    f.save(tmp_path)
    try:
        # Backup current DB before restoring
        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, DB_FILE + ".pre_restore_bak")
        with zipfile.ZipFile(tmp_path, "r") as zf:
            names = zf.namelist()
            # Extract DB
            if "sky_net.db" in names:
                zf.extract("sky_net.db", os.path.dirname(DB_FILE) or ".")
            # Extract configs to root (they have full paths like etc/openvpn/...)
            for name in names:
                if name.startswith("etc/"):
                    zf.extract(name, "/")
        # Restart service to apply restored config
        def _restart():
            import time; time.sleep(1)
            subprocess.Popen(["systemctl", "restart", "skynet"])
        threading.Thread(target=_restart, daemon=True).start()
        return jsonify({"success": True, "msg": "Восстановление завершено. Панель перезапускается..."})
    except Exception as e:
        log.error(f"Restore failed: {e}")
        return jsonify({"success": False, "msg": str(e)}), 500


# ─── API: Firewall (UFW & SQLite) ──────────────────────────────────────────

@app.route("/panel/api/firewall")
@login_required
def api_firewall_get():
    import subprocess
    import psutil
    
    # Get global UFW status
    try:
        r = subprocess.run(["ufw", "status"], capture_output=True, text=True)
        active = "Status: active" in r.stdout
    except FileNotFoundError:
        active = False

    # Get clean interfaces
    ifaces = [name for name in psutil.net_if_addrs().keys() if name != 'lo']
    
    # Get all rules ordered by priority
    with get_db() as db:
        rules = db.execute("SELECT * FROM firewall_rules ORDER BY priority ASC").fetchall()
        
    return jsonify({
        "success": True,
        "active": active,
        "interfaces": ifaces,
        "rules": [dict(r) for r in rules]
    })

def _apply_firewall_rules():
    """Apply firewall rules from DB to UFW WITHOUT resetting (preserves iptables NAT)."""
    import subprocess
    import re
    try:
        # ─── Step 1: Delete existing UFW rules (in reverse to keep numbering stable) ─
        # This approach preserves iptables -t nat rules (MASQUERADE etc.)
        result = subprocess.run(["ufw", "status", "numbered"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            # Extract rule numbers in reverse order
            rule_nums = []
            for line in lines:
                m = re.match(r'^\[\s*(\d+)\]', line)
                if m:
                    rule_nums.append(int(m.group(1)))
            # Delete in reverse order so numbering stays correct
            for num in sorted(rule_nums, reverse=True):
                subprocess.run(["ufw", "--force", "delete", str(num)], capture_output=True)

        # ─── Step 2: Set defaults ────────────────────────────────────
        subprocess.run(["ufw", "default", "deny", "incoming"], capture_output=True)
        subprocess.run(["ufw", "default", "allow", "outgoing"], capture_output=True)
        subprocess.run(["ufw", "default", "allow", "routed"], capture_output=True)

        # ─── Step 3: Safety Failsafes (Always Allow) ─────────────────
        subprocess.run(["ufw", "allow", "22/tcp"], capture_output=True)
        subprocess.run(["ufw", "allow", f"{PORT}/tcp"], capture_output=True)
        subprocess.run(["ufw", "allow", f"{HTTPS_PORT}/tcp"], capture_output=True)

        # ─── Step 4: Apply all DB rules ──────────────────────────────
        with get_db() as db:
            rules = db.execute("SELECT * FROM firewall_rules WHERE enabled=1 ORDER BY priority ASC").fetchall()

        for rule in rules:
            # Skip if already covered by failsafe
            if rule["dst_port"] in [str(22), str(PORT), str(HTTPS_PORT)] and rule["action"] == "allow":
                continue

            action = rule["action"].lower()
            if action not in ["allow", "deny", "reject"]: action = "allow"

            is_route = "FWD" in (rule["comment"] or "")

            cmd = ["ufw"]
            if is_route: cmd.append("route")
            cmd.append(action)

            if rule["interface"] and rule["interface"] != "any":
                if is_route:
                    cmd += ["on", rule["interface"]]
                else:
                    cmd += ["in", "on", rule["interface"]]

            if rule["protocol"] and rule["protocol"] != "any":
                cmd += ["proto", rule["protocol"]]

            cmd += ["from", rule["src_ip"] if rule["src_ip"] else "any"]
            if rule["src_port"] and rule["src_port"] != "any":
                cmd += ["port", str(rule["src_port"])]

            cmd += ["to", rule["dst_ip"] if rule["dst_ip"] else "any"]
            if rule["dst_port"] and rule["dst_port"] != "any":
                cmd += ["port", str(rule["dst_port"])]

            subprocess.run(cmd, capture_output=True)

        # ─── Step 5: Re-apply NAT for all running VPN inbounds ──────
        # This ensures MASQUERADE rules are restored after UFW changes
        with get_db() as db:
            inbounds = db.execute("SELECT * FROM inbounds WHERE enable=1").fetchall()
        for ib in inbounds:
            try:
                import json as _json
                settings = _json.loads(ib["settings"] or "{}")
                subnet = settings.get("address", "10.8.0.0/24")
                import ipaddress
                net = ipaddress.ip_network(subnet, strict=False)
                subnet = str(net)
                adapter = AdapterFactory.get(ib["protocol"])
                adapter._setup_nat(subnet)
            except Exception as e:
                log.warning(f"NAT re-apply for inbound {ib['id']}: {e}")

        subprocess.run(["ufw", "--force", "enable"], capture_output=True)
        return True
    except Exception as e:
        log.error(f"Firewall apply failed: {e}")
        return False

@app.route("/panel/api/firewall/toggle", methods=["POST"])
@login_required
def api_firewall_toggle():
    import subprocess
    data = request.get_json(silent=True) or {}
    action = "enable" if data.get("enable") else "disable"
    r = subprocess.run(["ufw", "--force", action], capture_output=True, text=True)
    return jsonify({"success": r.returncode == 0, "output": r.stdout + r.stderr})

@app.route("/panel/api/firewall/apply", methods=["POST"])
@login_required
def api_firewall_apply():
    success = _apply_firewall_rules()
    return jsonify({"success": success, "msg": "Правила успешно применены!" if success else "Ошибка применения"})

@app.route("/panel/api/firewall/save", methods=["POST"])
@login_required
def api_firewall_save():
    data = request.get_json(silent=True) or {}
    rid = data.get("id", None)
    enabled = int(data.get("enabled", 1))
    priority = int(data.get("priority", 100))
    action = data.get("action", "allow")
    proto = data.get("protocol", "any")
    src_ip = data.get("src_ip", "any")
    src_port = data.get("src_port", "any")
    dst_ip = data.get("dst_ip", "any")
    dst_port = data.get("dst_port", "any")
    interface = data.get("interface", "any")
    schedule = data.get("schedule", "always")
    comment = data.get("comment", "")
    
    with get_db() as db:
        if rid:
            db.execute("""
                UPDATE firewall_rules 
                SET enabled=?, priority=?, action=?, protocol=?, src_ip=?, src_port=?, dst_ip=?, dst_port=?, interface=?, schedule=?, comment=?
                WHERE id=?
            """, (enabled, priority, action, proto, src_ip, src_port, dst_ip, dst_port, interface, schedule, comment, rid))
        else:
            db.execute("""
                INSERT INTO firewall_rules (enabled, priority, action, protocol, src_ip, src_port, dst_ip, dst_port, interface, schedule, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (enabled, priority, action, proto, src_ip, src_port, dst_ip, dst_port, interface, schedule, comment))
        db.commit()
    
    _apply_firewall_rules()
    return jsonify({"success": True, "msg": "Правило сохранено и применено"})

@app.route("/panel/api/firewall/delete", methods=["POST"])
@login_required
def api_firewall_delete():
    data = request.get_json(silent=True) or {}
    rid = data.get("id")
    if not rid: return jsonify({"success": False, "msg": "ID не указан"})
    
    with get_db() as db:
        db.execute("DELETE FROM firewall_rules WHERE id=?", (rid,))
        db.commit()
    _apply_firewall_rules()
    return jsonify({"success": True, "msg": "Правило удалено"})

@app.route("/panel/api/firewall/sync", methods=["POST"])
@login_required
def api_firewall_sync():
    import subprocess
    import re
    # Ensure schema is up-to-date before sync
    check_schema()
    try:
        r = subprocess.run(["ufw", "status"], capture_output=True, text=True)
        if r.returncode != 0:
            return jsonify({"success": False, "msg": "UFW не доступен"})
            
        lines = r.stdout.splitlines()
        imported = []
        
        for line in lines:
            line = line.strip()
            # Skip headers and non-rule lines
            if not line or any(line.startswith(x) for x in ['To', '--', 'Status', 'Logging', 'Default', 'New']):
                continue
            
            if '(v6)' in line: continue
            
            # Regex to capture target, action, direction, source
            # Supports numbered: [ 1] 22/tcp ALLOW Anywhere
            # Supports verbose: 22/tcp ALLOW IN Anywhere
            # Direction (3rd group) is now optional
            m = re.match(r'^(?:\[\s*\d+\]\s+)?(.+?)\s+(ALLOW|DENY|REJECT)\s+(IN|FWD|OUT)?\s*(.*)', line, re.IGNORECASE)
            if not m: continue
            
            target_raw = m.group(1).strip()
            action = m.group(2).lower()
            direction = (m.group(3) or "IN").upper()
            source_raw = (m.group(4) or "").strip()
            
            dst_port, proto, src_ip, dst_ip, iface = "any", "any", "any", "any", "any"
            
            # Detect interface "on [iface]" in target or source
            if " on " in target_raw:
                parts = target_raw.split(" on ", 1)
                target_raw = parts[0].strip()
                iface = parts[1].strip()
            elif " on " in source_raw:
                parts = source_raw.split(" on ", 1)
                source_raw = parts[0].strip()
                iface = parts[1].strip()
            
            target_raw, source_raw = target_raw.strip(), source_raw.strip()

            # Parse target port/proto (e.g. 22/tcp)
            if "/" in target_raw:
                dst_port, proto = target_raw.split("/", 1)
            elif target_raw.lower() not in ["anywhere", "any"]:
                # If it consists of digits, it's a port
                if target_raw.isdigit():
                    dst_port = target_raw
                else:
                    dst_ip = target_raw

            if source_raw.lower() not in ["anywhere", "any", ""]:
                src_ip = source_raw
            
            comment = f"Imported {direction}"
            if direction == "FWD": 
                comment = f"FWD: {src_ip} -> {dst_ip}"
            elif dst_port != "any":
                comment = f"Port: {dst_port}/{proto}"
            
            imported.append({
                "action": action, "proto": proto, "src_ip": src_ip, "src_port": "any",
                "dst_ip": dst_ip, "dst_port": dst_port, "iface": iface, "comment": comment
            })
            
        with get_db() as db:
            db.execute("DELETE FROM firewall_rules")
            for i, rule in enumerate(imported):
                db.execute("""
                    INSERT INTO firewall_rules (enabled, priority, action, protocol, src_ip, src_port, dst_ip, dst_port, interface, schedule, comment)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, 'always', ?)
                """, ((i+1)*10, rule["action"], rule["proto"], rule["src_ip"], rule["src_port"], rule["dst_ip"], rule["dst_port"], rule["iface"], rule["comment"]))
            db.commit()
            
        return jsonify({"success": True, "msg": f"Импортировано {len(imported)} правил"})
    except Exception as e:
        log.error(f"Sync failed: {e}")
        return jsonify({"success": False, "msg": str(e)})


# ─── API: Network & System ──────────────────────────────────────────────────

@app.route("/panel/api/system/network")
@login_required
def api_system_network():
    try:
        import psutil
        import socket
        
        # Get active inbound IDs to filter "ghost" interfaces
        valid_ifaces = []
        with get_db() as db:
            inbounds = db.execute("SELECT id, protocol FROM inbounds").fetchall()
            for ib in inbounds:
                if "amneziawg" in ib['protocol']:
                    valid_ifaces.append(f"awg{ib['id']}")
                elif "openvpn_xor" in ib['protocol']:
                    valid_ifaces.append("tun_skynet")

        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        interfaces = []
        for name, addr_list in addrs.items():
            # FILTER: Hide ghost VPN interfaces (starting with awg or tun_skynet) 
            # if they are not active in the database.
            is_vpn_prefix = name.startswith("awg") or name.startswith("tun_skynet")
            if is_vpn_prefix and name not in valid_ifaces:
                continue
                
            iface = {"name": name, "addresses": [], "mac": "--", "is_up": False, "speed": 0}
            if name in stats:
                iface["is_up"] = stats[name].isup
                iface["speed"] = stats[name].speed
            for a in addr_list:
                if a.family == socket.AF_INET:
                    iface["addresses"].append({"ip": a.address, "netmask": a.netmask, "type": "IPv4"})
                elif a.family == socket.AF_INET6:
                    iface["addresses"].append({"ip": a.address, "type": "IPv6"})
                elif getattr(a.family, "name", "") == "AF_LINK" or a.family == 17: # AF_PACKET
                    iface["mac"] = a.address
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

@app.route("/panel/api/system/ntp", methods=["GET", "POST"])
@login_required
def api_system_ntp():
    import subprocess
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        servers = data.get("servers", "").strip()
        with get_db() as db:
            db.execute("UPDATE settings SET value=? WHERE key='ntp_servers'", (servers,))
            db.commit()
            
        # Update systemd-timesyncd
        conf_path = "/etc/systemd/timesyncd.conf"
        try:
            if os.path.exists(conf_path):
                with open(conf_path, "r") as f:
                    lines = f.readlines()
                with open(conf_path, "w") as f:
                    for line in lines:
                        if line.startswith("NTP=") or line.startswith("#NTP="):
                            f.write(f"NTP={servers}\n")
                        else:
                            f.write(line)
            subprocess.run(["systemctl", "restart", "systemd-timesyncd"], capture_output=True)
            return jsonify({"success": True, "msg": "NTP серверы обновлены"})
        except Exception as e:
            return jsonify({"success": False, "msg": str(e)})

    # GET response
    with get_db() as db:
        row = db.execute("SELECT value FROM settings WHERE key='ntp_servers'").fetchone()
    return jsonify({"success": True, "servers": row["value"] if row else ""})


# ─── API: System Time (Live Clock) ──────────────────────────────────────────

@app.route("/panel/api/system/time")
@login_required
def api_system_time():
    import datetime as dt
    import zoneinfo
    try:
        r = subprocess.run(["timedatectl", "show", "--property=Timezone", "--value"],
                           capture_output=True, text=True)
        tz_name = r.stdout.strip() or "UTC"
        tz = zoneinfo.ZoneInfo(tz_name)
        now = dt.datetime.now(tz)
        return jsonify({
            "success": True,
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timezone": tz_name,
            "utc_offset": now.strftime("%z")
        })
    except Exception as e:
        return jsonify({"success": False, "time": str(dt.datetime.utcnow())[:19], "timezone": "UTC"})

# ─── API: Credentials Change ─────────────────────────────────────────────────

@app.route("/panel/api/system/change-credentials", methods=["POST"])
@login_required
def api_change_credentials():
    data = request.get_json(silent=True) or {}
    new_login = data.get("login", "").strip()
    new_pass = data.get("password", "").strip()
    if not new_login or not new_pass:
        return jsonify({"success": False, "msg": "Логин и пароль не могут быть пустыми"}), 400
    if len(new_pass) < 6:
        return jsonify({"success": False, "msg": "Пароль должен быть минимум 6 символов"}), 400
    pw_hash = hashlib.sha256(new_pass.encode()).hexdigest()
    with get_db() as db:
        db.execute("UPDATE users SET username=?, password=? WHERE id=1", (new_login, pw_hash))
        db.commit()
    session.clear()
    return jsonify({"success": True, "msg": "Данные обновлены. Войдите заново."})

# ─── API: Panel Port Change ───────────────────────────────────────────────────

@app.route("/panel/api/system/change-port", methods=["POST"])
@login_required
def api_change_port():
    data = request.get_json(silent=True) or {}
    new_port = int(data.get("port", PORT))
    new_port_https = int(data.get("port_https", HTTPS_PORT))
    
    if (new_port < 1024 or new_port > 65535) or (new_port_https < 1024 or new_port_https > 65535):
        return jsonify({"success": False, "msg": "Порты должны быть от 1024 до 65535"}), 400
    if new_port == new_port_https:
        return jsonify({"success": False, "msg": "Порты HTTP и HTTPS должны различаться"}), 400
        
    old_port = PORT
    old_port_https = HTTPS_PORT
    
    # Step 1: Open new ports in UFW FIRST to avoid lockout
    subprocess.run(["ufw", "allow", f"{new_port}/tcp"], capture_output=True)
    subprocess.run(["ufw", "allow", f"{new_port_https}/tcp"], capture_output=True)
    
    # Step 2: Save new ports to DB settings
    with get_db() as db:
        db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('panel_port', ?)", (str(new_port),))
        db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('panel_port_https', ?)", (str(new_port_https),))
        
        # Also update firewall_rules DB so rules survive apply/sync
        # Remove old panel port rules
        db.execute("DELETE FROM firewall_rules WHERE comment LIKE '%Panel HTTP%' OR comment LIKE '%Panel HTTPS%'")
        max_prio = db.execute("SELECT COALESCE(MAX(priority),0) FROM firewall_rules").fetchone()[0]
        db.execute(
            "INSERT INTO firewall_rules (enabled,priority,action,protocol,src_ip,src_port,dst_ip,dst_port,interface,comment) "
            "VALUES (1,?,?,?,?,?,?,?,?,?)",
            (max_prio + 10, "allow", "tcp", "any", "any", "any", str(new_port), "any", "Panel HTTP Failsafe")
        )
        db.execute(
            "INSERT INTO firewall_rules (enabled,priority,action,protocol,src_ip,src_port,dst_ip,dst_port,interface,comment) "
            "VALUES (1,?,?,?,?,?,?,?,?,?)",
            (max_prio + 20, "allow", "tcp", "any", "any", "any", str(new_port_https), "any", "Panel HTTPS Failsafe")
        )
        db.commit()
        
    # Step 3: Close old ports in UFW (only if different)
    if new_port != old_port:
        subprocess.run(["ufw", "delete", "allow", f"{old_port}/tcp"], capture_output=True)
    if new_port_https != old_port_https:
        subprocess.run(["ufw", "delete", "allow", f"{old_port_https}/tcp"], capture_output=True)
    
    # Step 4: Update systemd service environment so new process picks up correct ports
    try:
        service_path = "/etc/systemd/system/skynet.service"
        if os.path.exists(service_path):
            with open(service_path, "r") as f:
                content = f.read()
            import re as _re
            content = _re.sub(r'Environment=SKYNET_PORT=\d+', f'Environment=SKYNET_PORT={new_port}', content)
            content = _re.sub(r'Environment=SKYNET_HTTPS_PORT=\d+', f'Environment=SKYNET_HTTPS_PORT={new_port_https}', content)
            with open(service_path, "w") as f:
                f.write(content)
            subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
    except Exception as e:
        log.warning(f"Failed to update systemd service: {e}")
        
    # Step 5: Schedule restart after response is sent
    def delayed_restart():
        import time; time.sleep(2)
        subprocess.Popen(["systemctl", "restart", "skynet"])
    threading.Thread(target=delayed_restart, daemon=True).start()
    return jsonify({
        "success": True, 
        "msg": f"Порты изменены на HTTP:{new_port} и HTTPS:{new_port_https}. Панель перезапускается...", 
        "new_port": new_port,
        "new_port_https": new_port_https
    })

# ─── API: Fail2Ban Installation ───────────────────────────────────────────────

@app.route("/panel/api/system/install-fail2ban", methods=["POST"])
@login_required
def api_install_fail2ban():
    def _install():
        subprocess.run(["apt-get", "install", "-y", "fail2ban"], capture_output=True)
        # Create local jail override
        jail_conf = f"""[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log

[skynet-panel]
enabled = true
port = {PORT}
filter = skynet-panel
logpath = /var/log/skynet-auth.log
maxretry = 5
"""
        filter_conf = """[Definition]
failregex = .* Неверный пароль от <HOST>
            .* LOGIN_FAIL from <HOST>
            .* Failed login from <HOST>
ignoreregex =
"""
        try:
            with open("/etc/fail2ban/jail.local", "w") as f:
                f.write(jail_conf)
            os.makedirs("/etc/fail2ban/filter.d", exist_ok=True)
            with open("/etc/fail2ban/filter.d/skynet-panel.conf", "w") as f:
                f.write(filter_conf)
            subprocess.run(["systemctl", "enable", "fail2ban"], capture_output=True)
            subprocess.run(["systemctl", "restart", "fail2ban"], capture_output=True)
        except Exception as e:
            log.error(f"Fail2Ban config error: {e}")
    threading.Thread(target=_install, daemon=True).start()
    return jsonify({"success": True, "msg": "Fail2Ban устанавливается в фоне (~30 сек)..."})

@app.route("/panel/api/system/fail2ban-status")
@login_required
def api_fail2ban_status():
    r = subprocess.run(["fail2ban-client", "status"], capture_output=True, text=True)
    installed = r.returncode == 0
    return jsonify({"success": True, "installed": installed, "output": r.stdout[:500] if installed else ""})

# ─── API: SSL / HTTPS Configuration ─────────────────────────────────────────

@app.route("/panel/api/system/set-ssl", methods=["POST"])
@login_required
def api_set_ssl():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "off")        # off | self-signed | letsencrypt
    domain = data.get("domain", "").strip()

    if mode == "self-signed":
        # Generate self-signed certificate
        cert_dir = "/etc/sky-net/ssl"
        os.makedirs(cert_dir, exist_ok=True)
        cmd = [
            "openssl", "req", "-x509", "-nodes", "-newkey", "rsa:2048",
            "-keyout", f"{cert_dir}/key.pem",
            "-out", f"{cert_dir}/cert.pem",
            "-days", "3650",
            "-subj", f"/CN={domain or 'sky-net-panel'}"
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            return jsonify({"success": False, "msg": r.stderr[:300]})
        with get_db() as db:
            db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_mode','self-signed')")
            db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_cert',?)", (f"{cert_dir}/cert.pem",))
            db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_key',?)", (f"{cert_dir}/key.pem",))
            db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('panel_domain',?)", (domain,))
            db.commit()
        return jsonify({"success": True, "msg": "Самоподписанный сертификат создан. Перезапустите панель."})

    elif mode == "letsencrypt":
        if not domain:
            return jsonify({"success": False, "msg": "Укажите домен для Let's Encrypt"}), 400
        def _certbot():
            # Open port 80 if needed for Certbot
            log.info(f"Preparing Port 80 for Certbot on {domain}...")
            subprocess.run(["ufw", "allow", "80/tcp"], check=False, timeout=10)
            
            try:
                r = subprocess.run(
                    ["certbot", "certonly", "--standalone", "--non-interactive",
                     "--agree-tos", "--register-unsafely-without-email", "-d", domain],
                    capture_output=True, text=True, timeout=120
                )
                if r.returncode == 0:
                    with get_db() as db:
                        cert = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
                        key = f"/etc/letsencrypt/live/{domain}/privkey.pem"
                        db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_mode','letsencrypt')")
                        db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_cert',?)", (cert,))
                        db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_key',?)", (key,))
                        db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('panel_domain',?)", (domain,))
                        db.commit()
                    log.info(f"Let's Encrypt cert issued for {domain}")
                else:
                    log.error(f"Certbot failed: {r.stderr}")
            except subprocess.TimeoutExpired:
                log.error("Certbot timed out")
            finally:
                # Optionally close port 80 if you want to be extra secure, 
                # but many keep it open for renewals. 
                # subprocess.run(["ufw", "deny", "80/tcp"], check=False)
                pass
        threading.Thread(target=_certbot, daemon=True).start()
        return jsonify({"success": True, "msg": f"Запрос сертификата Let's Encrypt для {domain}. Это займёт ~30 сек."})

    else:  # off
        with get_db() as db:
            db.execute("INSERT OR REPLACE INTO settings (key,value) VALUES ('ssl_mode','off')")
            db.commit()
        return jsonify({"success": True, "msg": "HTTPS отключён. HTTP режим активен."})

# ─── API: System Updates (GitHub) ──────────────────────────────────────────

@app.route("/panel/api/system/restart", methods=["POST"])
@login_required
def api_restart_panel():
    def _restart():
        import time; time.sleep(1); subprocess.Popen(["systemctl", "restart", "skynet"])
    threading.Thread(target=_restart, daemon=True).start()
    return jsonify({"success": True, "msg": "Панель перезапускается... Страница обновится через 3 сек."})

@app.route("/panel/api/system/update/check", methods=["GET"])
@login_required
def api_system_update_check():
    """Проверка обновлений на GitHub."""
    import subprocess
    try:
        # Fetch with timeout to avoid hanging the panel
        subprocess.run(["git", "fetch", "origin", "main"], check=True, timeout=30)
        current_hash = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
        remote_hash = subprocess.check_output(["git", "rev-parse", "--short", "origin/main"]).decode().strip()
        behind_count = int(subprocess.check_output(["git", "rev-list", "--count", "HEAD..origin/main"]).decode().strip())
        
        return jsonify({
            "success": True,
            "current_hash": current_hash,
            "remote_hash": remote_hash,
            "needs_update": behind_count > 0,
            "behind_count": behind_count
        })
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route("/panel/api/system/update/apply", methods=["POST"])
@login_required
def api_system_update_apply():
    """Применение обновления и перезапуск сервиса."""
    import subprocess
    try:
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
        # Перезагружаем сервис. Subprocess.Popen не блокирует выполнение ответа.
        subprocess.Popen(["systemctl", "restart", "skynet"])
        return jsonify({"success": True, "msg": "Обновление применено. Панель перезапускается..."})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

# ─── Traffic History ─────────────────────────────────────────────────────────

traffic_history = {"up": deque([0]*60, maxlen=60), "down": deque([0]*60, maxlen=60)}


@app.route("/panel/api/system/reboot", methods=["POST"])
@login_required
def api_system_reboot():
    log.warning("User requested system reboot")
    subprocess.Popen(["reboot"])
    return jsonify({"success": True, "message": "Rebooting..."})

@app.route("/panel/api/trafficHistory")
@login_required
def api_traffic_history():
    return jsonify({"up": list(traffic_history["up"]), "down": list(traffic_history["down"])})

# ─── Pages (HTML rendered from templates/main.html) ──────────────────────────

@app.route("/")
@login_required
def page_dashboard():
    return render_template_string(MAIN_HTML, page="dashboard")

@app.route("/<page>")
@login_required
def page_dynamic(page):
    if "." in page:
        abort(404)
    return render_template_string(MAIN_HTML, page=page)

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
                                lh = s.get("last_handshake", int(time.time()))
                                db.execute(
                                    "UPDATE client_traffics SET up=?, down=?, last_online=? WHERE id=?",
                                    (s.get("tx", 0), s.get("rx", 0), lh, client["id"])
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

def enrich_inbound_with_clients(db, ib_dict: dict) -> dict:
    """Fetch clients from DB and inject them into inbound settings for config generation."""
    clients = db.execute(
        "SELECT * FROM client_traffics WHERE inbound_id=? AND enable=1",
        (ib_dict["id"],)
    ).fetchall()
    settings = json.loads(ib_dict.get("settings", "{}"))
    settings["clients"] = [
        {
            "username": c["username"],
            "public_key": c["public_key"],
            "preshared_key": c["preshared_key"],
            "allowed_ips": c["allowed_ips"],
            "enable": bool(c["enable"]),
        }
        for c in clients
    ]
    ib_dict["settings"] = json.dumps(settings)
    return ib_dict

def start_all_inbounds():
    with get_db() as db:
        inbounds = db.execute("SELECT * FROM inbounds WHERE enable=1").fetchall()
        for ib in inbounds:
            try:
                ib_dict = enrich_inbound_with_clients(db, dict(ib))
                AdapterFactory.get(ib["protocol"]).start(ib_dict)
            except Exception as e: log.error(f"Startup error for inbound {ib['id']}: {e}")

def start_telegram_bot():
    """Starts the telegram_bot.py as a separate subprocess."""
    with get_db() as db:
        token = db.execute("SELECT value FROM settings WHERE key='telegram_bot_token'").fetchone()
        allowed_ids = db.execute("SELECT value FROM settings WHERE key='telegram_allowed_ids'").fetchone()

    if not token or not token[0]:
        log.info("Telegram Bot Token not configured. Skipping bot start.")
        return

    env = os.environ.copy()
    env["TELEGRAM_BOT_TOKEN"] = token[0]
    env["TELEGRAM_ALLOWED_IDS"] = allowed_ids[0] if (allowed_ids and allowed_ids[0]) else ""
    env["SKYNET_DB"] = os.path.abspath(DB_FILE)

    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_bot.py")
    if os.path.exists(script_path):
        log.info("Starting Telegram Bot...")
        subprocess.Popen(["python3", script_path], env=env)
    else:
        log.error(f"Telegram bot script not found at {script_path}")

if __name__ == "__main__":
    init_db()
    # Start the bot
    start_telegram_bot()

    
    # Global Routing & System Optimization
    try:
        # Enable IP Forwarding
        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
        
        # We don't need to add hardcoded MASQUERADE here because each dynamic 
        # inbound setup (via Adapter) will now call _setup_nat() which 
        # handles interface detection and NAT for its specific subnet.
        
        log.info("Global IP forwarding enabled")
    except Exception as e:
        log.error(f"Global routing error: {e}")

    # This will trigger start() on all enabled inbounds, 
    # which now includes centralized routing setup.
    start_all_inbounds()
    t = threading.Thread(target=poll_traffic, daemon=True)
    t.start()
    # Load SSL Settings
    ssl_ctx = None
    with get_db() as db:
        s_mode = db.execute("SELECT value FROM settings WHERE key='ssl_mode'").fetchone()
        s_cert = db.execute("SELECT value FROM settings WHERE key='ssl_cert'").fetchone()
        s_key = db.execute("SELECT value FROM settings WHERE key='ssl_key'").fetchone()
        if s_mode and s_mode[0] != "off" and s_cert and s_key:
            if os.path.exists(s_cert[0]) and os.path.exists(s_key[0]):
                ssl_ctx = (s_cert[0], s_key[0])
                log.info(f"SSL enabled: {s_mode[0]} mode")

    log.info(f"Sky-Net HTTP server binding on port {PORT}")
    if ssl_ctx:
        from werkzeug.serving import make_server
        def run_http():
            try:
                srv = make_server("0.0.0.0", PORT, app, threaded=True)
                srv.serve_forever()
            except Exception as e:
                log.error(f"Failed to start secondary HTTP server: {e}")
                
        t_http = threading.Thread(target=run_http, daemon=True)
        t_http.start()
        
        log.info(f"Sky-Net HTTPS server binding on port {HTTPS_PORT}")
        app.run(host="0.0.0.0", port=HTTPS_PORT, debug=False, threaded=True, ssl_context=ssl_ctx)
    else:
        app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
