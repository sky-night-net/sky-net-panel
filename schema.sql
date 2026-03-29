-- Sky-Net VPN Panel Database Schema
-- Initialized 2026-03-29

-- Users table (admin/admin by default via Python logic)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Inbounds table
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

-- Client traffic/settings table
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

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT DEFAULT ''
);

-- Traffic history for charts
CREATE TABLE IF NOT EXISTS traffic_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts INTEGER,
    up INTEGER DEFAULT 0,
    down INTEGER DEFAULT 0
);

-- Advanced Firewall rules
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
    comment TEXT DEFAULT '',
    schedule TEXT DEFAULT 'always'
);

-- Initial Base Settings
INSERT OR IGNORE INTO settings (key, value) VALUES ('panel_port', '4467');
INSERT OR IGNORE INTO settings (key, value) VALUES ('panel_https_port', '4466');
INSERT OR IGNORE INTO settings (key, value) VALUES ('session_timeout', '3600');
INSERT OR IGNORE INTO settings (key, value) VALUES ('ntp_servers', 'pool.ntp.org');
INSERT OR IGNORE INTO settings (key, value) VALUES ('fail2ban_enabled', 'false');
INSERT OR IGNORE INTO settings (key, value) VALUES ('secret_key', 'def-secret-key-123');
