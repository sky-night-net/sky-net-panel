#!/usr/bin/env python3
import telebot
import sqlite3
import os
import subprocess
import time
import json
from datetime import datetime
from adapters import AdapterFactory

# Configuration from environment (set by sky_net.py or systemd)
DB_FILE = os.getenv("SKYNET_DB", "sky_net.db")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_IDS = os.getenv("TELEGRAM_ALLOWED_IDS", "").split(",")

if not TOKEN:
    print("Telegram Bot Token not found. Bot disabled.")
    exit(0)

bot = telebot.TeleBot(TOKEN)

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def is_authorized(message):
    uid = str(message.from_user.id)
    if uid in ALLOWED_IDS:
        return True
    bot.reply_to(message, f"❌ Доступ запрещен. Ваш ID: {uid}")
    return False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_authorized(message): return
    help_text = """
🚀 *Sky-Net Bot* — Управление VPN сервером

Команды:
/status — Состояние сервера (CPU, RAM, Uptime)
/servers — Список VPN серверов и протоколов
/clients — Список всех клиентов
/backup — Создать и отправить бэкап системы
/restart — Перезагрузить панель Sky-Net
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def server_status(message):
    if not is_authorized(message): return
    try:
        uptime = subprocess.check_output(["uptime", "-p"]).decode().strip()
        cpu = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", shell=True).decode().strip()
        ram = subprocess.check_output("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2 }'", shell=True).decode().strip()
        
        status = f"📊 *Статус сервера*\n\n" \
                 f"⏱ *Uptime:* {uptime}\n" \
                 f"🔥 *CPU Load:* {cpu}%\n" \
                 f"🧠 *RAM Usage:* {ram}\n" \
                 f"⏰ *Server Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        bot.reply_to(message, status, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['servers'])
def list_servers(message):
    if not is_authorized(message): return
    try:
        db = get_db()
        servers = db.execute("SELECT name, protocol, port, is_active FROM inbounds").fetchall()
        if not servers:
            bot.reply_to(message, "📭 Список серверов пуст.")
            return
        
        text = "🌐 *Список VPN серверов:*\n\n"
        for s in servers:
            status = "✅" if s['is_active'] else "❌"
            text += f"{status} *{s['name']}* ({s['protocol']})\n   Port: `{s['port']}`\n"
        bot.reply_to(message, text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка БД: {e}")

@bot.message_handler(commands=['clients'])
def list_clients(message):
    if not is_authorized(message): return
    try:
        db = get_db()
        clients = db.execute("SELECT username, protocol_type, is_active FROM clients").fetchall()
        if not clients:
            bot.reply_to(message, "📭 Список клиентов пуст.")
            return
        
        text = f"👥 *Список клиентов (всего {len(clients)}):*\n\n"
        for c in clients:
            status = "🟢" if c['is_active'] else "🔴"
            text += f"{status} `{c['username']}` — {c['protocol_type']}\n"
        bot.reply_to(message, text[:4000], parse_mode='Markdown') # Simple truncation for long lists
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка БД: {e}")

@bot.message_handler(commands=['backup'])
def send_backup(message):
    if not is_authorized(message): return
    bot.reply_to(message, "📦 Подготовка бэкапа... Пожалуйста, подождите.")
    import zipfile, tempfile, shutil
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"skynet_backup_{ts}.zip"
    tmp_path = os.path.join(tempfile.gettempdir(), backup_name)
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(DB_FILE): zf.write(DB_FILE, "sky_net.db")
            for cfg_dir in ["/etc/openvpn", "/etc/wireguard"]:
                if os.path.isdir(cfg_dir):
                    for root, dirs, files in os.walk(cfg_dir):
                        for fname in files:
                            fp = os.path.join(root, fname)
                            zf.write(fp, fp.lstrip("/"))
        
        with open(tmp_path, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"📄 Полный бэкап Sky-Net ({ts})")
        os.remove(tmp_path)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при создании бэкапа: {e}")

@bot.message_handler(commands=['restart'])
def restart_panel(message):
    if not is_authorized(message): return
    bot.reply_to(message, "🔄 Перезапуск сервиса skynet... Связь будет временно прервана.")
    try:
        subprocess.Popen(["systemctl", "restart", "skynet"])
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

# --- Client Creation Wizard ---

@bot.message_handler(commands=['add_client'])
def add_client_start(message):
    if not is_authorized(message): return
    msg = bot.reply_to(message, "👤 *Введите имя нового клиента:*", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_username_step)

def process_username_step(message):
    try:
        username = message.text.strip()
        if not username or username.startswith('/'):
             bot.reply_to(message, "❌ Некорректное имя. /add_client для повтора.")
             return
        
        db = get_db()
        servers = db.execute("SELECT id, name, protocol, remark FROM inbounds WHERE enable=1").fetchall()
        if not servers:
            bot.reply_to(message, "❌ Нет активных VPN серверов.")
            return

        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for s in servers:
            markup.add(f"{s['id']}: {s['remark'] or s['name']} ({s['protocol']})")
        
        msg = bot.reply_to(message, "🔌 *Выберите сервер:*", reply_markup=markup, parse_mode='Markdown')
        bot.register_next_step_handler(msg, process_server_step, username)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

def process_server_step(message, username):
    try:
        inbound_id = int(message.text.split(":")[0])
        with get_db() as db:
            ib = db.execute("SELECT * FROM inbounds WHERE id=?", (inbound_id,)).fetchone()
            if not ib:
                bot.reply_to(message, "❌ Сервер не найден.", reply_markup=telebot.types.ReplyKeyboardRemove())
                return

            # IP logic (simplified from sky_net.py)
            existing = db.execute(
                "SELECT allowed_ips FROM client_traffics WHERE inbound_id=? ORDER BY id DESC LIMIT 1",
                (inbound_id,)
            ).fetchone()
            if existing:
                try:
                    last_ip = existing["allowed_ips"].split("/")[0]
                    parts = last_ip.split(".")
                    parts[3] = str(int(parts[3]) + 1)
                    next_ip = ".".join(parts) + "/32"
                except: next_ip = "10.8.0.2/32"
            else:
                next_ip = "10.8.0.2/32"

            adapter = AdapterFactory.get(ib["protocol"])
            keys = {}
            try: keys = adapter.generate_keypair()
            except: pass

            db.execute(
                "INSERT INTO client_traffics (inbound_id, username, public_key, private_key, preshared_key, allowed_ips) "
                "VALUES (?,?,?,?,?,?)",
                (inbound_id, username, keys.get("public_key", ""), keys.get("private_key", ""), 
                 keys.get("preshared_key", ""), next_ip)
            )
            db.commit()
            client = db.execute("SELECT * FROM client_traffics WHERE id=last_insert_rowid()").fetchone()
            
            if ib["enable"]:
                try: adapter.add_client(dict(client), dict(ib))
                except Exception as ex: print(f"Adapter add_client error: {ex}")

            bot.reply_to(message, f"✅ Клиент *{username}* (IP: {next_ip}) успешно создан на сервере *{ib['remark'] or ib['name']}*!", 
                         reply_markup=telebot.types.ReplyKeyboardRemove(), parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при создании: {e}", reply_markup=telebot.types.ReplyKeyboardRemove())

if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()
