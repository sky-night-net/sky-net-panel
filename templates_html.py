"""
Sky-Net HTML Templates v2.0
───────────────────────────
No emoji. Light/Dark theme toggle. Extended pages:
Dashboard, Inbounds, Clients, Firewall, System, Settings
"""

LOGIN_HTML = r"""<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sky-Net | Login</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0f172a;
  --bg-grad: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
  --blue: #00a8e8;
  --card: rgba(30, 41, 59, 0.6);
  --border: rgba(255, 255, 255, 0.1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; height: 100vh; background: var(--bg); background-image: var(--bg-grad); display: flex; align-items: center; justify-content: center; color: #fff; overflow: hidden; }
.login-card { background: var(--card); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 24px; padding: 50px; width: 100%; max-width: 420px; box-shadow: 0 25px 50px rgba(0,0,0,0.3); text-align: center; position: relative; }
.logo { font-size: 28px; font-weight: 900; color: var(--blue); letter-spacing: 3px; margin-bottom: 40px; }
.fg { margin-bottom: 20px; text-align: left; }
.fg label { display: block; font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
.fg input { width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 12px; padding: 14px 18px; color: #fff; font-size: 15px; outline: none; transition: 0.2s; }
.fg input:focus { border-color: var(--blue); box-shadow: 0 0 0 4px rgba(0, 168, 232, 0.1); }
.btn { width: 100%; background: var(--blue); color: #fff; padding: 14px; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s; margin-top: 20px; }
.btn:hover { transform: translateY(-1px); opacity: 0.9; }
.error { color: #f43f5e; background: rgba(244, 63, 94, 0.1); padding: 10px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; }
.lang-toggle { position: absolute; top: 20px; right: 25px; display: flex; gap: 10px; font-size: 12px; font-weight: 700; color: #94a3b8; cursor: pointer; }
.lang-toggle span { transition: 0.2s; }
.lang-toggle span.active { color: var(--blue); }
</style></head><body>
<div class="login-card">
  <div class="lang-toggle">
    <span id="lang-ru" onclick="setL('ru')">RU</span>
    <span style="opacity:0.3">|</span>
    <span id="lang-en" onclick="setL('en')">EN</span>
  </div>
  <div class="logo">SKY-NET</div>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST">
    <div class="fg"><label data-i18n="sec_new_login">Имя пользователя</label><input name="username" required></div>
    <div class="fg"><label data-i18n="sec_new_pw">Пароль</label><input name="password" type="password" required></div>
    <button class="btn" type="submit" data-i18n="login_btn">ВОЙТИ В ПАНЕЛЬ</button>
  </form>
</div>
<script>
const dict = {
  en: { sec_new_login: "Username", sec_new_pw: "Password", login_btn: "LOGIN TO PANEL" },
  ru: { sec_new_login: "Имя пользователя", sec_new_pw: "Пароль", login_btn: "ВОЙТИ В ПАНЕЛЬ" }
};
function setL(l){
  localStorage.setItem('lang', l);
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const k = el.getAttribute('data-i18n');
    if(dict[l][k]) el.innerText = dict[l][k];
  });
  document.getElementById('lang-ru').className = (l==='ru'?'active':'');
  document.getElementById('lang-en').className = (l==='en'?'active':'');
}
setL(localStorage.getItem('lang') || 'ru');
</script>
</body></html>"""


MAIN_HTML = r"""<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sky-Net Panel</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/qrcode@1/build/qrcode.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
<style>
:root {
  --kg-bg: #1c2128;
  --kg-sidebar: #171b22;
  --kg-card: #222b37;
  --kg-border: #30363d;
  --kg-blue: #2fa1ed;
  --kg-text: #c9d1d9;
  --kg-text-dim: #8b949e;
  --kg-red: #ff5252;
  --kg-green: #37c871;
  --kg-shadow: 0 4px 12px rgba(0,0,0,0.2);
}
[data-theme="light"] {
  --kg-bg: #f6f8fa;
  --kg-sidebar: #ffffff;
  --kg-card: #ffffff;
  --kg-border: #d0d7de;
  --kg-text: #24292f;
  --kg-text-dim: #57606a;
}
[data-theme="light"] .card-header, [data-theme="light"] table, [data-theme="light"] .log-box { background: rgba(0,0,0,0.02); }
[data-theme="light"] .user-info strong, [data-theme="light"] .header h1, [data-theme="light"] .card-header h3, [data-theme="light"] .k-conn-title, [data-theme="light"] .k-val, [data-theme="light"] .stat-val { color: #24292f; }
[data-theme="light"] .btn { color: #fff; }
[data-theme="light"] .sd-body { border-color: var(--kg-border); }
[data-theme="light"] .sys-dropdown, [data-theme="light"] .sys-dropdown option, [data-theme="light"] .sd-fg label { background: #ffffff; color: #24292f; }
[data-theme="light"] .sd-select { color: #24292f; }

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--kg-bg); color: var(--kg-text); min-height: 100vh; line-height: 1.5; overflow-x: hidden; }

/* Sidebar */
.sidebar { width: 260px; background: var(--kg-sidebar); border-right: 1px solid var(--kg-border); display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100; backdrop-filter: blur(20px); transition: width 0.3s ease, transform 0.3s ease; overflow-x: hidden; }
.sidebar.collapsed { width: 70px; }
.sidebar .logo { padding: 35px 25px; color: var(--kg-blue); font-weight: 900; font-size: 22px; text-transform: uppercase; letter-spacing: 2px; white-space: nowrap; transition: 0.3s; }
.sidebar.collapsed .logo { opacity: 0; pointer-events: none; }
.sidebar nav { flex: 1; padding: 10px 0; overflow-y: auto; overflow-x: hidden; }
.sidebar nav a { display: flex; align-items: center; gap: 15px; padding: 14px 23px; color: var(--kg-text-dim); text-decoration: none; font-size: 14px; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; white-space: nowrap; }
.sidebar nav a svg { flex-shrink: 0; }
.sidebar nav a:hover { color: var(--kg-blue); }
.sidebar nav a.active { color: var(--kg-blue); background: rgba(0, 168, 232, 0.05); }
.sidebar.collapsed nav a span { opacity: 0; pointer-events: none; transition: 0.2s; }
.sidebar nav .section { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.2); padding: 30px 25px 10px; font-weight: 800; letter-spacing: 1.5px; white-space: nowrap; transition: 0.3s; }
.sidebar.collapsed nav .section { opacity: 0; pointer-events: none; height: 0; padding-top: 20px; padding-bottom: 0; }
.sidebar-sep { height: 1px; background: rgba(255,255,255,0.05); margin: 10px 25px; }

/* Mobile Overlay */
@media (max-width: 768px) {
  .sidebar { width: 260px; transform: translateX(-100%); }
  .sidebar.collapsed { width: 260px; transform: translateX(-100%); }
  .sidebar.show { transform: translateX(0); box-shadow: 20px 0 60px rgba(0,0,0,0.5); }
  .sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 95; backdrop-filter: blur(4px); }
  .sidebar-overlay.show { display: block; }
}

/* Header */
.main { margin-left: 260px; flex: 1; display: flex; flex-direction: column; min-width: 0; transition: margin-left 0.3s ease; }
.sidebar.collapsed ~ .main { margin-left: 70px; }
@media (max-width: 768px) { .main { margin-left: 0 !important; } }

.header { height: 60px; background: var(--kg-sidebar); border-bottom: 1px solid var(--kg-border); display: flex; align-items: center; justify-content: space-between; padding: 0 30px; position: sticky; top: 0; z-index: 90; }
.header-left { display: flex; align-items: center; gap: 20px; }
.hamburger { cursor: pointer; padding: 10px; color: var(--kg-blue); display: flex; flex-direction: column; justify-content: center; transition: 0.2s; }
.hamburger:hover { color: #fff; }
.hamburger div { width: 24px; height: 3px; background: currentColor; margin: 3px 0; border-radius: 2px; }
.header h1 { font-size: 18px; font-weight: 600; color: #fff; display:none; }

.header-right { display: flex; align-items: center; gap: 20px; position: relative; }
.user-info { font-size: 13px; color: var(--kg-text-dim); display: flex; align-items: center; gap: 8px; cursor: pointer; }
.user-info strong { color: #fff; }
.sys-menu-btn { cursor: pointer; color: var(--kg-blue); padding: 5px; transition: 0.2s; display: flex; align-items: center; justify-content: center; }
.sys-menu-btn:hover { color: #fff; }

/* System Dropdown Keenetic Style */
.sys-dropdown { position: absolute; top: 50px; right: 0; width: 320px; background: #1f2532; border: 1px solid var(--kg-border); border-radius: 8px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); display: none; flex-direction: column; z-index: 200; overflow: hidden; }
.sys-dropdown.show { display: flex; animation: slideDown 0.2s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.sd-body { padding: 25px; display: flex; flex-direction: column; gap: 15px; }
.sd-fg { position: relative; }
.sd-fg label { position: absolute; top: -8px; left: 10px; background: #1f2532; padding: 0 5px; font-size: 11px; color: var(--kg-text-dim); z-index: 10; font-weight: normal; }
.sd-select { width: 100%; appearance: none; background: transparent; border: 1px solid var(--kg-border); border-radius: 6px; padding: 12px 15px; color: #fff; font-size: 13px; outline: none; cursor: pointer; transition: 0.2s; }
.sd-select:focus { border-color: var(--kg-blue); }
.sd-select option { background: #1f2532; color: #fff; }
.sd-links { display: flex; flex-direction: column; gap: 14px; margin-top: 5px; }
.sd-link { color: var(--kg-blue); font-size: 13px; text-decoration: underline; cursor: pointer; text-decoration-color: rgba(47,161,237,0.3); text-underline-offset: 4px; transition: 0.2s; }
.sd-link:hover { text-decoration-color: var(--kg-blue); }
.sd-footer { padding: 15px 25px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 10px; }
.sd-footer .btn { width: 100%; justify-content: center; }

/* Content & Grid */
.content { padding: 25px max(25px, calc((100% - 1400px)/2)); flex: 1; width: 100%; display: flex; flex-direction: column; gap: 25px; }
.grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 25px; }
.card { grid-column: span 6; background: var(--kg-card); border: 1px solid var(--kg-border); border-radius: 8px; box-shadow: var(--kg-shadow); overflow: hidden; position: relative; transition: box-shadow 0.2s; }
@media (max-width: 1100px) { .card { grid-column: span 12; } }

.card-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 25px; border-bottom: 1px solid var(--kg-border); cursor: grab; background: rgba(0,0,0,0.1); }
.card-title-group { display: flex; align-items: center; gap: 10px; }
.card-header h3 { font-size: 13px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: 1px; }

.sortable-ghost { opacity: 0.3; transform: scale(0.98); }

.card-padd { padding: 25px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } }
/* Sortable widget grid styles */
.widget-grid { display: grid; grid-template-columns: 1fr; gap: 15px; margin-bottom: 15px; }

/* Dashboard Keenetic Styles */
.k-conn-block { padding: 20px 25px 0 25px; display: flex; align-items: flex-start; justify-content: space-between; }
.k-conn-left { display: flex; gap: 15px; }
.k-toggle { width: 34px; height: 20px; background: var(--kg-border); border-radius: 10px; position: relative; transition: 0.22s; cursor: pointer; }
.k-toggle::after { content: ''; position: absolute; width: 14px; height: 14px; background: var(--kg-text-dim); border-radius: 50%; top: 3px; left: 3px; transition: 0.22s; }
.k-toggle.on { background: var(--kg-blue); }
.k-toggle.on::after { background: #fff; transform: translateX(14px); }
.k-conn-title { font-size: 15px; font-weight: 500; color: #fff; line-height: 1.2; margin-bottom: 2px; }
.k-conn-subtitle { font-size: 13px; color: var(--kg-text-dim); margin-bottom: 10px; }
.k-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; text-transform: uppercase; background: rgba(255,255,255,0.05); color: var(--kg-green); border: 1px solid rgba(255,255,255,0.05); }

.k-btn-group { display: flex; flex-direction: column; gap: 8px; }
.k-icon-btn { width: 32px; height: 32px; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: var(--kg-text-dim); background: transparent; cursor: pointer; transition: 0.2s; }
.k-icon-btn:hover { border-color: var(--kg-blue); color: var(--kg-blue); }

.k-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px 25px 25px 25px; }
@media(max-width: 900px) { .k-grid { grid-template-columns: repeat(2, 1fr); gap: 15px; } }
@media(max-width: 600px) { .k-grid { grid-template-columns: 1fr; } }
.k-kv { display: flex; flex-direction: column; gap: 4px; margin-bottom: 15px; }
.k-lbl { font-size: 13px; color: var(--kg-text-dim); }
.k-val { font-size: 14px; color: #fff; font-weight: 400; }
.k-val.red { color: var(--kg-red); }
.k-val-link { color: var(--kg-blue); cursor: pointer; text-decoration: none; }

/* Stats */
.stat-item { display: flex; justify-content: space-between; align-items: center; padding: 18px 25px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.stat-item:last-child { border-bottom: none; }
.stat-label { font-size: 14px; font-weight: 600; color: #fff; }
.stat-label { font-size: 14px; color: var(--kg-text-dim); font-weight: 500; }
.stat-val { font-size: 15px; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; }

.stat-circles { display: flex; justify-content: space-around; margin-top: 20px; gap: 20px; }
.circle-stat { text-align: center; }
.circle-val { font-size: 26px; font-weight: 800; color: var(--kg-blue); }
.circle-label { font-size: 11px; color: var(--kg-text-dim); text-transform: uppercase; font-weight: 800; margin-top: 5px; letter-spacing: 1px; }

.chart-container-wrapper { padding: 15px 25px 0 25px; }
.chart-container { height: 160px; width: 100%; border-bottom: 1px solid var(--kg-border); border-top: 1px dotted rgba(255,255,255,0.1); position: relative; margin-top: 10px; }
.legend-item { display: flex; align-items: center; gap: 5px; }

/* Firewall Tabs */
.fw-tab {
  padding: 10px 0;
  color: var(--kg-text-dim);
  font-size: 13px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: 0.2s;
  white-space: nowrap;
}
.fw-tab.active {
  color: var(--kg-blue);
  border-bottom-color: var(--kg-blue);
  font-weight: 500;
}
.fw-tab:hover {
  color: #fff;
}
.fw-table th {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--kg-border);
}
.fw-table td {
  padding: 12px;
  vertical-align: middle;
}
.k-table tr:hover {
  background: rgba(255,255,255,0.02);
}

/* Keenetic-style notched fields (Premium) */
.kn-field {
  position: relative;
  margin-bottom: 24px;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 6px;
  background: transparent;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.kn-field label {
  position: absolute;
  top: -10px;
  left: 12px;
  background: #1a222f; /* Must match the exact modal/card background */
  padding: 0 6px;
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  pointer-events: none;
  font-weight: 500;
  z-index: 10;
}
.kn-field input,
.kn-field select {
  width: 100%;
  background: transparent;
  border: none;
  color: #fff;
  padding: 14px 14px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  -webkit-appearance: none;
  appearance: none;
  position: relative;
  z-index: 5;
}
.kn-field select {
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255,255,255,0.4)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 40px;
}
.kn-field:focus-within {
  border-color: var(--kg-blue);
  box-shadow: 0 0 0 1px var(--kg-blue);
}
.kn-field:focus-within label {
  color: var(--kg-blue);
}

.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot-green { background: var(--kg-green); }
.dot-blue { background: var(--kg-blue); }

/* Settings Modal specific */
.widget-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
@media(max-width: 600px) { .widget-grid { grid-template-columns: 1fr; } }
.widget-card { background: var(--kg-bg); border: 1px solid var(--kg-border); border-radius: 8px; padding: 15px; display: flex; flex-direction: column; gap: 12px; }
.widget-card-title { font-size: 13px; font-weight: 700; color: #fff; text-transform: uppercase; letter-spacing: 1px; }
.widget-card-toggle { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.w-tgl { width: 34px; height: 20px; background: var(--kg-border); border-radius: 10px; position: relative; transition: 0.2s; }
.w-tgl::after { content: ''; position: absolute; width: 16px; height: 16px; background: var(--kg-text-dim); border-radius: 50%; top: 2px; left: 2px; transition: 0.2s; }
.w-tgl.on { background: var(--kg-blue); }
.w-tgl.on::after { background: #fff; transform: translateX(14px); }
.w-lbl { font-size: 13px; color: var(--kg-text-dim); }


/* Forms & Buttons */
.fg { margin-bottom: 20px; }
.fg label { display: block; font-size: 12px; font-weight: 800; color: var(--kg-text-dim); text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
.fg input:not([type="checkbox"]), .fg select, .fg textarea { width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--kg-border); border-radius: 10px; padding: 12px 16px; color: #fff; font-size: 14px; outline: none; transition: 0.2s; }
.fg input:focus { border-color: var(--kg-blue); box-shadow: 0 0 0 3px rgba(0, 168, 232, 0.1); }

.btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: 12px; font-size: 14px; font-weight: 700; cursor: pointer; transition: 0.2s; border: none; outline: none; }
.btn-p { background: var(--kg-blue); color: #fff; }
.btn-p:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-o { background: rgba(255,255,255,0.05); color: #fff; border: 1px solid var(--kg-border); }
.btn-o:hover { background: rgba(255,255,255,0.1); border-color: var(--kg-blue); }
.btn-s { background: var(--kg-green); color: #fff; }
.btn-d { background: rgba(244, 63, 94, 0.1); color: var(--kg-red); border: 1px solid rgba(244, 63, 94, 0.2); }
.btn-d:hover { background: rgba(244, 63, 94, 0.2); }
.btn-sm { padding: 8px 14px; font-size: 12px; }

.fr { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 600px) { .fr, .grid-3, .grid-4 { grid-template-columns: 1fr; } }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }

/* Tables */
.table-container { width: 100%; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th { text-align: left; padding: 12px 15px; color: var(--kg-text-dim); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--kg-border); }
td { padding: 15px; font-size: 14px; border-bottom: 1px solid rgba(255,255,255,0.02); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(255,255,255,0.02); }

.hide-mobile { display: none; }
@media (min-width: 769px) { .hide-mobile { display: flex; } }

/* Modals */
.overlay { display: none; position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(8px); }
.overlay.show { display: flex; }
.modal { background: #1e293b; border: 1px solid var(--kg-border); border-radius: 24px; width: 650px; max-width: 95%; box-shadow: var(--kg-shadow); overflow: hidden; }
.modal-header { padding: 25px 30px; border-bottom: 1px solid var(--kg-border); background: rgba(255,255,255,0.02); font-weight: 700; font-size: 18px; }
.modal-body { padding: 30px; max-height: 80vh; overflow-y: auto; }
.modal-footer { padding: 20px 30px; border-top: 1px solid var(--kg-border); display: flex; justify-content: flex-end; gap: 15px; }

.modal-section { margin-top: 15px; border-top: 1px solid var(--kg-border); padding-top: 15px; }
.section-title { font-size: 10px; text-transform: uppercase; color: var(--kg-blue); font-weight: 800; margin-bottom: 12px; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
.section-title::after { content: ""; flex: 1; height: 1px; background: rgba(0,168,232,0.15); }

.page { display: none; animation: fadeIn 0.4s ease; }
.page.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Inbound Row */
.ib-row { background: rgba(255,255,255,0.02); border: 1px solid var(--kg-border); border-radius: 6px; padding: 20px 30px; margin-bottom: 15px; display: flex; align-items: center; justify-content: space-between; transition: 0.2s; }
.ib-row:hover { border-color: var(--kg-blue); background: rgba(0,168,232,0.05); }
.ib-info { display: flex; align-items: center; gap: 24px; }
.ib-icon-box { width: 44px; height: 44px; background: rgba(0,168,232,0.15); border-radius: 10px; display: flex; align-items: center; justify-content: center; color: var(--kg-blue); font-size: 20px; font-weight: 800; }
.ib-details h4 { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.ib-details p { font-size: 13px; color: var(--kg-text-dim); }
.ib-actions { display: flex; gap: 12px; align-items: center; }

.log-box { background: #000; color: #0f0; font-family: 'Courier New', monospace; font-size: 12px; padding: 20px; border-radius: 4px; height: 400px; overflow-y: auto; white-space: pre-wrap; }
</style></head><body>

<div class="sidebar" id="sidebar">
  <div class="logo">SKY-NET</div>
  <nav>
    <a href="#" data-page="dashboard" class="active">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
      <span data-i18n="nav_dash">Системный монитор</span>
    </a>
    <a href="#" data-page="inbounds">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
      <span data-i18n="nav_vpns">VPN серверы</span>
    </a>
    <a href="#" data-page="clients">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0 1 14.08 0"></path><path d="M1.42 9a16 16 0 0 1 21.16 0"></path><path d="M8.53 16.11a6 6 0 0 1 6.95 0"></path><line x1="12" y1="20" x2="12.01" y2="20"></line></svg>
      <span data-i18n="nav_clients">Подключенные клиенты</span>
    </a>
    <a href="#" data-page="firewall">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      <span data-i18n="nav_fw">Межсетевой экран</span>
    </a>
    <a href="#" data-page="system">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
      <span data-i18n="nav_sys">Настройки системы</span>
    </a>
    <div class="sidebar-sep"></div>
    <a href="#" data-page="instructions">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
      <span data-i18n="nav_instr">Инструкции</span>
    </a>
    <a href="#" data-page="logs" style="display:none"><span data-i18n="sys_log">Журнал событий</span></a>
    <a href="#" data-page="settings" style="display:none"><span data-i18n="sys_params">Параметры панели</span></a>
  </nav>
</div>

<div class="main">
    <div class="header">
      <div class="header-left">
        <div class="hamburger" onclick="toggleSidebarCol()">
          <div></div><div></div><div></div>
        </div>
        <h1 id="page-title-text" style="display:none" data-i18n="nav_dash">Системный монитор</h1>
      </div>
      <div class="header-right">
        <svg fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" viewBox="0 0 24 24" class="sys-menu-btn" onclick="toggleSysMenu()"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <svg fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" viewBox="0 0 24 24" class="sys-menu-btn" onclick="toggleSysMenu()"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        <div class="user-info hide-mobile" onclick="toggleSysMenu()">
          <span style="opacity:0.5" data-i18n="user_lbl">Пользователь:</span>
          <strong>{{ session.get('username', 'admin') }}</strong>
        </div>
        
        <!-- System Dropdown Menu -->
        <div class="sys-dropdown" id="sys-menu">
          <div class="sd-body">
            <div class="sd-fg">
              <label data-i18n="lang_lbl">Выберите язык</label>
              <select class="sd-select" id="lang-select" onchange="changeLang(this.value)"><option value="ru">Русский</option><option value="en">English</option></select>
            </div>
            <div class="sd-fg">
              <label data-i18n="theme_lbl">Стиль оформления</label>
              <select class="sd-select" id="theme-select" onchange="changeTheme(this.value)"><option value="dark">Темный</option><option value="light">Светлый</option></select>
            </div>
            <div class="sd-links">
              <span class="sd-link" data-i18n="sys_log" onclick="switchPage('logs'); toggleSysMenu()">Системный журнал</span>
              <span class="sd-link" data-i18n="cli" onclick="switchPage('cli'); toggleSysMenu()">Командная строка</span>
              <span class="sd-link" onclick="switchPage('instructions'); toggleSysMenu()">Инструкции</span>
            </div>
          </div>
          <div class="sd-footer">
            <button class="btn btn-p" data-i18n="reboot" onclick="rebootServer()">Перезагрузка</button>
            <a href="/logout" class="btn btn-p" style="text-decoration:none" data-i18n="logout">Выйти</a>
          </div>
        </div>
      </div>
    </div>
  <div class="sidebar-overlay" onclick="toggleSidebarColModal()"></div>
  <div class="content">

<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
  
  <div class="grid" id="sortable-dashboard">
    <!-- Dynamic Interface Blocks -->
    <div id="dynamic-interfaces-container" style="display:contents"></div>
    
    <!-- BLOCK 2: О СИСТЕМЕ -->
    <div class="card" id="block-system">
      <div class="card-header">
        <h3 style="margin:0" data-i18n="sys_info">О СИСТЕМЕ</h3>
        <svg fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" viewBox="0 0 24 24" style="color:var(--kg-text-dim);"><path d="M4 8h16M4 16h16"></path></svg>
      </div>
      
      <!-- SVG Ring Gauges -->
      <div style="display:flex; justify-content:space-around; align-items:center; padding:25px 15px 15px; gap:10px;">
        <!-- CPU Gauge -->
        <div style="text-align:center;">
          <div style="position:relative; width:90px; height:90px; margin:0 auto;">
            <svg viewBox="0 0 36 36" style="width:90px; height:90px; transform:rotate(-90deg);">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3"></circle>
              <circle id="cpu-ring" cx="18" cy="18" r="15.9" fill="none" stroke="var(--kg-blue)" stroke-width="3" stroke-dasharray="0, 100" stroke-linecap="round" style="transition: stroke-dasharray 0.8s ease;"></circle>
            </svg>
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:16px; font-weight:800; color:#fff;" id="cpu-val">0%</div>
          </div>
          <div style="font-size:11px; color:var(--kg-text-dim); text-transform:uppercase; font-weight:700; margin-top:8px; letter-spacing:1px;">CPU</div>
        </div>
        <!-- RAM Gauge -->
        <div style="text-align:center;">
          <div style="position:relative; width:90px; height:90px; margin:0 auto;">
            <svg viewBox="0 0 36 36" style="width:90px; height:90px; transform:rotate(-90deg);">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3"></circle>
              <circle id="ram-ring" cx="18" cy="18" r="15.9" fill="none" stroke="var(--kg-green)" stroke-width="3" stroke-dasharray="0, 100" stroke-linecap="round" style="transition: stroke-dasharray 0.8s ease;"></circle>
            </svg>
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:16px; font-weight:800; color:#fff;" id="ram-val">0%</div>
          </div>
          <div style="font-size:11px; color:var(--kg-text-dim); text-transform:uppercase; font-weight:700; margin-top:8px; letter-spacing:1px;">RAM</div>
          <div style="font-size:10px; color:var(--kg-text-dim); margin-top:2px;" id="ram-detail"></div>
        </div>
        <!-- DISK Gauge -->
        <div style="text-align:center;">
          <div style="position:relative; width:90px; height:90px; margin:0 auto;">
            <svg viewBox="0 0 36 36" style="width:90px; height:90px; transform:rotate(-90deg);">
              <circle cx="18" cy="18" r="15.9" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3"></circle>
              <circle id="disk-ring" cx="18" cy="18" r="15.9" fill="none" stroke="#f59e0b" stroke-width="3" stroke-dasharray="0, 100" stroke-linecap="round" style="transition: stroke-dasharray 0.8s ease;"></circle>
            </svg>
            <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:16px; font-weight:800; color:#fff;" id="disk-val">0%</div>
          </div>
          <div style="font-size:11px; color:var(--kg-text-dim); text-transform:uppercase; font-weight:700; margin-top:8px; letter-spacing:1px;" data-i18n="disk_lbl">ДИСК</div>
          <div style="font-size:10px; color:var(--kg-text-dim); margin-top:2px;" id="disk-detail"></div>
        </div>
      </div>

      <!-- System Info Grid -->
      <div style="border-top:1px solid var(--kg-border); padding:0;">
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="var(--kg-blue)" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="hostname_lbl">Хост</span>
          </div>
          <span class="k-val" id="d-host" style="font-family:'JetBrains Mono',monospace;">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="var(--kg-green)" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="uptime_lbl">Аптайм</span>
          </div>
          <span class="k-val" id="uptime-val" style="font-family:'JetBrains Mono',monospace; color:var(--kg-green);">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="#f59e0b" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="sys_info">Система</span>
          </div>
          <span class="k-val" id="d-os" style="font-size:12px;">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="var(--kg-blue)" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            <span class="k-lbl" style="margin:0;">Load Avg</span>
          </div>
          <span class="k-val" id="d-loadavg" style="font-family:'JetBrains Mono',monospace;">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="var(--kg-blue)" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="current_server_time">Время сервера</span>
          </div>
          <span class="k-val" id="d-time" style="font-family:'JetBrains Mono',monospace; color:#fff;">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="var(--kg-green)" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="nav_sys">Версия</span>
          </div>
          <span class="k-val" id="d-version" style="font-size:12px; font-weight:700;">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="#f59e0b" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="port">HTTPS Порт</span>
          </div>
          <span class="k-val" id="d-https-port" style="font-size:12px; font-weight:700;">--</span>
        </div>
        <div class="stat-item">
          <div style="display:flex; align-items:center; gap:10px;">
            <svg fill="none" stroke="#10b981" stroke-width="2" width="16" height="16" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span class="k-lbl" style="margin:0;" data-i18n="sys_ssl">SSL Статус</span>
          </div>
          <span class="k-val" id="d-ssl-status" style="font-size:12px; font-weight:700; color:var(--kg-green);">Проверка...</span>
        </div>
      </div>
    </div>
    
  </div> <!-- end grid -->

  <div class="grid" style="margin-top:25px;" id="sortable-dashboard-bottom">
    <!-- BLOCK 3: АКТИВНЫЕ СЕССИИ И ТРАФИК -->
    <div class="card" style="grid-column: span 12;" id="block-clients">
      <div class="card-header">
        <svg fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" viewBox="0 0 24 24" style="color:var(--kg-text-dim); margin-right:4px;"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
        <h3 data-i18n="sys_sessions">АКТИВНЫЕ СЕССИИ И ТРАФИК</h3>
      </div>
      <div id="dash-clients-list" style="padding: 0 0 10px 0;">
        <!-- Active clients will be rendered here as stat-items -->
        <div style="padding:40px 25px; text-align:center; color:var(--kg-text-dim); font-size:13px;">
          <div style="padding:40px 25px; text-align:center; color:var(--kg-text-dim); font-size:13px;" data-i18n="no_active_sessions">
            Нет активных сессий
          </div>
        </div>
      </div>
    </div>

    <!-- BLOCK 4: СЕТЕВЫЕ ИНТЕРФЕЙСЫ -->
    <div class="card" id="block-interfaces" style="display:none;">
      <div class="card-header"><h3 data-i18n="nav_ifaces">СЕТЕВЫЕ ИНТЕРФЕЙСЫ</h3></div>
      <div id="net-ifaces" class="card-padd"></div>
    </div>
  </div> <!-- end grid -->
  
  <div style="text-align: center; margin-top: 30px; margin-bottom: 20px;">
    <button class="btn btn-o" onclick="openWidgetSettings()" style="display:flex; align-items:center; gap:8px; margin: 0 auto; background:transparent; border:none; color:var(--kg-blue); font-size:14px; font-weight:600;">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
      <span data-i18n="widget_title">Редактировать системный монитор</span>
    </button>
  </div>
</div>

<!-- INBOUNDS -->
<div class="page" id="page-inbounds">
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="nav_vpns">VPN ПОДКЛЮЧЕНИЯ</h3><button class="btn btn-p" onclick="openAddInbound()" data-i18n="ib_add_title">Добавить подключение</button></div>
    <div id="inbounds-list">
      <!-- Inbounds will be rendered as horizontal rows here -->
    </div>
  </div>
</div>

<!-- CLIENTS -->
<div class="page" id="page-clients">
  <div class="card no-blue">
    <div class="card-header" style="justify-content: space-between;">
      <h3 data-i18n="nav_clients">ПОДКЛЮЧЕННЫЕ КЛИЕНТЫ</h3>
      <div class="fg" style="margin:0"><input id="clientSearch" placeholder="Поиск клиентов..." style="width: 250px;"></div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th data-i18n="client">Клиент</th>
            <th data-i18n="server">Сервер</th>
            <th data-i18n="ip_addr">IP адрес</th>
            <th data-i18n="up_down">Трафик (↑/↓)</th>
            <th data-i18n="limit">Лимит</th>
            <th data-i18n="status">Статус</th>
            <th data-i18n="actions">Действия</th>
          </tr>
        </thead>
        <tbody id="clients-table"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- FIREWALL -->
<div class="page" id="page-firewall">
  <div class="card" style="background:transparent; padding:0; border:none; box-shadow:none;">
    <div style="margin-bottom:20px;">
      <h2 style="margin:0 0 10px; font-size:22px; font-weight:600; color:white;" data-i18n="fw_title">Межсетевой экран</h2>
      <p style="margin:0; font-size:13px; color:var(--kg-text-dim); line-height:1.5;" data-i18n="fw_desc">
        Чтобы добавить правило межсетевого экрана, выберите из списка интерфейс, на котором будет отслеживаться входящий трафик, и нажмите <b>Добавить правило</b>.
      </p>
      <div style="margin-top:10px;">
        <span id="fw-status-badge" class="badge" style="display:inline-block;">--</span>
        <button class="btn btn-o btn-sm" onclick="fwToggle(true)" style="margin-left:10px;" data-i18n="enable">Включить UFW</button>
        <button class="btn btn-d btn-sm" onclick="fwToggle(false)" data-i18n="disable">Выключить UFW</button>
      </div>
    </div>
    
    <div id="fw-tabs-container" style="display:flex; gap:20px; border-bottom:1px solid var(--kg-border); margin-bottom:20px; overflow-x:auto;">
      <!-- Tabs injected by JS -->
    </div>
    
    <div style="margin-bottom:20px;">
      <button class="btn btn-o" onclick="fwOpenModal()" style="display:flex; align-items:center; gap:6px;">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        <span data-i18n="add_rule">Добавить правило</span>
      </button>
    </div>
    
    <div class="table-responsive" style="background:var(--kg-bg-card); border-radius:8px;">
      <table class="k-table fw-table" style="width:100%; text-align:left; font-size:13px;">
        <thead>
          <tr style="border-bottom:1px solid var(--kg-border); color:var(--kg-text-dim); font-size:12px;">
            <th style="padding:12px; font-weight:500; width:40px;"></th>
            <th style="padding:12px; font-weight:500; width:60px;" data-i18n="fw_prio_col">Приор.</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_action_col">Действие</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_proto_col">Протокол</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_iface_col">Интерфейс</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_src_col">Источник</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_srcp_col">Порт ист.</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_dst_col">Назначение</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_dstp_col">Порт назн.</th>
            <th style="padding:12px; font-weight:500;" data-i18n="fw_name_col">Имя / Комментарий</th>
            <th style="padding:12px; width:40px;"></th>
          </tr>
        </thead>
        <tbody id="fw-rules-body_2"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- FIREWALL MODAL -->
<div class="modal" id="modal-fw" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; display:none; justify-content:center; align-items:center; backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);">
  <div id="modal-fw-content" style="background:#1a222f; width:100%; max-width:480px; border-radius:12px; box-shadow:0 30px 60px rgba(0,0,0,0.6); position:relative; overflow:hidden; animation: modalIn 0.3s ease-out; margin: auto;">
    <div style="padding:40px 40px 24px 40px;">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
        <h2 style="margin:0; font-size:28px; font-weight:700; color:white;" data-i18n="fw_modal_title">Правило межсетевого экрана</h2>
        <div style="cursor:pointer; color:rgba(255,255,255,0.5); padding:4px;" onclick="document.getElementById('modal-fw').style.display='none'">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </div>
      </div>
      <p style="margin:0; color:rgba(255,255,255,0.5); font-size:14px; line-height:1.6;" data-i18n="fw_modal_desc">Выберите действие, которое нужно выполнить для входящих пакетов, и укажите условия, при которых это действие должно быть выполнено.</p>
    </div>
    
    <div style="padding:0 40px 40px 40px; max-height:70vh; overflow-y:auto;">
      <input type="hidden" id="fw-m-id">
      
      <label style="display:flex; align-items:center; gap:12px; margin-bottom:32px; cursor:pointer;">
        <input type="checkbox" id="fw-m-enabled" checked style="width:20px;height:20px; accent-color:var(--kg-blue); cursor:pointer;">
        <span style="color:white; font-size:16px;" data-i18n="fw_enable_rule">Включить правило</span>
      </label>
      
      <div class="kn-field" style="margin-bottom:32px;">
        <label data-i18n="name">Имя</label>
        <input id="fw-m-name" placeholder="Например: Блокировка ICMP">
      </div>
      
      <div class="kn-field">
        <label data-i18n="fw_action_lbl">Действие</label>
        <select id="fw-m-action">
          <option value="allow" data-i18n="allow">Разрешить</option>
          <option value="deny" data-i18n="deny">Запретить</option>
          <option value="reject" data-i18n="fw_reject">Отбросить</option>
        </select>
      </div>
      
      <div class="kn-field" id="kn-srcip-box">
        <label data-i18n="fw_src_ip_lbl">IP-адрес источника</label>
        <select id="fw-m-srcip-sel" onchange="fwOnCustomChange(this, 'fw-m-srcip-val')">
          <option value="any" data-i18n="any">Любой</option>
          <option value="custom" data-i18n="fw_custom_ip">Указать IP или подсеть...</option>
        </select>
        <input id="fw-m-srcip-val" style="display:none; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.1); padding-top:10px;" placeholder="например: 10.8.0.0/24">
      </div>
      
      <div class="kn-field" id="kn-dstip-box">
        <label data-i18n="fw_dst_ip_lbl">IP-адрес назначения</label>
        <select id="fw-m-dstip-sel" onchange="fwOnCustomChange(this, 'fw-m-dstip-val')">
          <option value="any" data-i18n="any">Любой</option>
          <option value="custom" data-i18n="fw_custom_ip">Указать IP или подсеть...</option>
        </select>
        <input id="fw-m-dstip-val" style="display:none; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.1); padding-top:10px;" placeholder="например: 1.1.1.1">
      </div>
      
      <div class="kn-field" id="kn-srcport-box">
        <label data-i18n="fw_src_port_lbl">Номер порта источника</label>
        <select id="fw-m-srcport-sel" onchange="fwOnCustomChange(this, 'fw-m-srcport-val')">
          <option value="any" data-i18n="any">Любой</option>
          <option value="custom" data-i18n="fw_custom_port">Указать порт или диапазон...</option>
        </select>
        <input id="fw-m-srcport-val" style="display:none; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.1); padding-top:10px;" placeholder="например: 80 или 3000:4000">
      </div>
      
      <div class="kn-field">
        <label data-i18n="protocol">Протокол</label>
        <select id="fw-m-proto">
          <option value="tcp">TCP</option>
          <option value="udp">UDP</option>
          <option value="any" data-i18n="any">Любой</option>
          <option value="icmp">ICMP</option>
        </select>
      </div>
      
      <div class="kn-field" id="kn-dstport-box">
        <label data-i18n="fw_dst_port_lbl">Номер порта назначения</label>
        <select id="fw-m-dstport-sel" onchange="fwOnCustomChange(this, 'fw-m-dstport-val')">
          <option value="any" data-i18n="any">Любой</option>
          <option value="custom" data-i18n="fw_custom_port">Указать порт или диапазон...</option>
        </select>
        <input id="fw-m-dstport-val" style="display:none; margin-top:10px; border-top:1px dashed rgba(255,255,255,0.1); padding-top:10px;" placeholder="например: 443 или 8000:9000">
      </div>
      
      <div class="kn-field">
        <label data-i18n="fw_iface_lbl">Интерфейс</label>
        <select id="fw-m-iface"></select>
      </div>
      
      <div class="kn-field">
        <label data-i18n="fw_prio_lbl">Переместить в</label>
        <select id="fw-m-prio">
          <option value="10" data-i18n="fw_prio_start">Начало списка</option>
          <option value="50" data-i18n="fw_prio_mid">Середина списка</option>
          <option value="100" selected data-i18n="fw_prio_end">Конец (текущая позиция)</option>
        </select>
      </div>
      
      <div class="kn-field" style="margin-bottom:0;">
        <label data-i18n="fw_schedule_lbl">Расписание работы</label>
        <select id="fw-m-schedule">
          <option value="always" data-i18n="fw_always">Работает постоянно</option>
        </select>
      </div>
    </div>
    
    <div style="padding:0 40px 40px 40px; display:flex; gap:16px;">
      <button class="btn" style="flex:1.5; height:50px; background:var(--kg-blue); color:white; border:none; border-radius:8px; font-weight:600; font-size:16px; cursor:pointer;" onclick="fwSaveModal()" data-i18n="fw_save">Сохранить</button>
      <button class="btn" style="flex:1; height:50px; background:rgba(255,255,255,0.05); color:var(--kg-blue); border:1px solid rgba(0,161,228,0.3); border-radius:8px; font-weight:600; font-size:16px; cursor:pointer;" onclick="document.getElementById('modal-fw').style.display='none'" data-i18n="fw_cancel">Отменить</button>
    </div>
  </div>
</div>


<!-- SYSTEM -->
<div class="page" id="page-system">

  <!-- Block 1: Hostname & Timezone -->
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="sys_time">УСТРОЙСТВО И ВРЕМЯ</h3></div>
    <div style="padding:25px;">
      <div class="fr">
        <div class="fg"><label data-i18n="hostname_lbl">Имя устройства</label><input id="sys-hostname" placeholder="sky-net"></div>
        <div class="fg"><label data-i18n="tz_lbl">Часовой пояс</label>
          <select id="sys-tz">
            <option value="UTC">UTC</option>
            <option value="Europe/Moscow">Europe/Moscow (UTC+3)</option>
            <option value="Europe/Kiev">Europe/Kiev (UTC+2)</option>
            <option value="Europe/Berlin">Europe/Berlin (UTC+1)</option>
            <option value="Europe/London">Europe/London (UTC+0)</option>
            <option value="Asia/Tashkent">Asia/Tashkent (UTC+5)</option>
            <option value="Asia/Almaty">Asia/Almaty (UTC+6)</option>
            <option value="Asia/Novosibirsk">Asia/Novosibirsk (UTC+7)</option>
            <option value="Asia/Irkutsk">Asia/Irkutsk (UTC+8)</option>
            <option value="Asia/Yakutsk">Asia/Yakutsk (UTC+9)</option>
            <option value="Asia/Vladivostok">Asia/Vladivostok (UTC+10)</option>
            <option value="Asia/Baku">Asia/Baku (UTC+4)</option>
            <option value="Asia/Dubai">Asia/Dubai (UTC+4)</option>
            <option value="Asia/Kolkata">Asia/Kolkata (UTC+5:30)</option>
            <option value="Asia/Bangkok">Asia/Bangkok (UTC+7)</option>
            <option value="Asia/Singapore">Asia/Singapore (UTC+8)</option>
            <option value="Asia/Tokyo">Asia/Tokyo (UTC+9)</option>
            <option value="America/New_York">America/New_York (UTC-5)</option>
            <option value="America/Chicago">America/Chicago (UTC-6)</option>
            <option value="America/Los_Angeles">America/Los_Angeles (UTC-8)</option>
            <option value="America/Sao_Paulo">America/Sao_Paulo (UTC-3)</option>
            <option value="Africa/Cairo">Africa/Cairo (UTC+2)</option>
            <option value="Australia/Sydney">Australia/Sydney (UTC+10)</option>
            <option value="Pacific/Auckland">Pacific/Auckland (UTC+12)</option>
          </select>
        </div>
      </div>
      <div style="margin-top:5px; display:flex; gap:10px; align-items:center; font-size:12px; color:var(--kg-text-dim);">
        <span data-i18n="current_server_time">Текущее время сервера:</span>
        <span id="server-clock" style="font-family:monospace; color:var(--kg-green);">—</span>
      </div>
      <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:15px;">
        <button class="btn btn-o" onclick="saveHostname()" data-i18n="save">Сохранить имя</button>
        <button class="btn btn-o" onclick="saveTimezone()" data-i18n="save">Сохранить часовой пояс</button>
        <button class="btn btn-o" onclick="setupService()" data-i18n="sec_setup_auto">Настроить Автозапуск</button>
      </div>
    </div>
  </div>

  <!-- Block 2: Security (Credentials + Port + Fail2Ban) -->
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="sec_title">БЕЗОПАСНОСТЬ</h3></div>
    <div style="padding:25px;">
      <div style="margin-bottom:20px;">
        <h4 style="margin:0 0 12px; font-size:13px; text-transform:uppercase; color:var(--kg-text-dim);" data-i18n="sec_login_pw">Смена логина и пароля</h4>
        <div class="fr">
          <div class="fg"><label data-i18n="sec_new_login">Новый логин</label><input id="new-login" placeholder="admin"></div>
          <div class="fg"><label data-i18n="sec_new_pw">Новый пароль</label><input id="new-password" type="password" placeholder="минимум 6 символов"></div>
          <div class="fg"><label data-i18n="sec_confirm">Подтверждение</label><input id="confirm-password" type="password" placeholder="повторите пароль"></div>
        </div>
        <button class="btn btn-p" style="margin-top:10px;" onclick="changeCredentials()" data-i18n="save">Обновить данные входа</button>
      </div>
      <hr style="border-color:var(--kg-border); margin:20px 0;">
      <div style="margin-bottom:20px;">
        <h4 style="margin:0 0 12px; font-size:13px; text-transform:uppercase; color:var(--kg-text-dim);" data-i18n="sys_params">Порты веб-панели</h4>
        <div class="fr">
          <div class="fg"><label data-i18n="port">HTTP Порт (1024-65535)</label><input id="new-panel-port" type="number" placeholder="4466"></div>
          <div class="fg"><label data-i18n="port">HTTPS Порт (1024-65535)</label><input id="new-panel-port-https" type="number" placeholder="4466"></div>
          <div class="fg" style="align-self:flex-end;">
            <button class="btn btn-p" onclick="changePanelPort()" data-i18n="sec_apply_ports">Применить порты</button>
          </div>
        </div>
        <p style="font-size:11px; color:var(--kg-orange); margin:5px 0 0;" data-i18n="sec_restart_warn">Внимание: панель перезапустится на новых портах.</p>
      </div>
      <hr style="border-color:var(--kg-border); margin:20px 0;">
      <div>
        <h4 style="margin:0 0 12px; font-size:13px; text-transform:uppercase; color:var(--kg-text-dim);" data-i18n="f2b_title">Fail2Ban — защита от брутфорса</h4>
        <p style="font-size:12px; color:var(--kg-text-dim); margin:0 0 10px;" data-i18n="f2b_desc">Автоматически блокирует IP-адреса, которые пытаются подобрать пароль к SSH или панели.</p>
        <div style="display:flex; gap:10px; align-items:center;">
          <span id="f2b-status" class="badge badge-off" data-i18n="f2b_not_installed">Не установлен</span>
          <button class="btn btn-o" onclick="installFail2Ban()" data-i18n="f2b_install">Установить Fail2Ban</button>
          <button class="btn btn-o btn-sm" onclick="checkFail2Ban()" data-i18n="status">Проверить статус</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Block 3: SSL / HTTPS -->
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="sys_ssl">SSL / HTTPS</h3></div>
    <div style="padding:25px;">
      <div class="fr" style="margin-bottom:15px;">
      <div class="fr" style="margin-bottom:15px;">
        <div class="fg"><label data-i18n="ext_ip_lbl">Домен (например: sky-night.net)</label><input id="ssl-domain" placeholder="sky-night.net" data-i18n-ph="ext_ip_lbl"></div>
        <div class="fg"><label data-i18n="protocol">Режим SSL</label>
          <select id="ssl-mode">
            <option value="off" data-i18n="ssl_off_opt">HTTP (без SSL)</option>
            <option value="self-signed">Self-Signed HTTPS</option>
            <option value="letsencrypt">Let's Encrypt HTTPS</option>
          </select>
        </div>
      </div>
      </div>
      <p style="font-size:11px; color:var(--kg-text-dim); margin:0 0 15px;" data-i18n="instr_ssl_p">Self-Signed: браузер предупредит — это нормально. Let's Encrypt: бесплатный доверенный сертификат, требует домен.</p>
      <div id="ssl-status-box" style="margin-top:20px; padding:15px; background:rgba(0,0,0,0.2); border-radius:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <span style="font-size:12px; color:var(--kg-text-dim);" data-i18n="status">Текущий режим:</span>
          <span id="ssl-badge" class="badge" data-i18n="loading">Загрузка...</span>
        </div>
        <div id="ssl-details" style="font-size:12px; line-height:1.5;">
          <div style="color:var(--kg-text-dim); margin-bottom:4px;" data-i18n="sys_ssl">SSL сертификат: <span id="ssl-cert-state" style="color:white;">--</span></div>
          <div id="ssl-restart-warn" style="display:none; color:#f59e0b; font-weight:600; margin-top:10px;">⚠️ Требуется перезапуск панели для активации HTTPS</div>
          <div id="ssl-active-info" style="display:none; color:var(--kg-green); font-weight:600; margin-top:10px;"></div>
        </div>
      </div>
      <div style="display:flex; gap:10px; margin-top:15px;">
        <button class="btn btn-p" style="flex:1;" onclick="applySSL()" data-i18n="ssl_apply_btn">Применить настройки SSL</button>
        <button class="btn btn-o" style="flex:0.5; border-color:#f59e0b; color:#f59e0b;" onclick="restartPanel()" data-i18n="restart_btn">Перезапуск</button>
      </div>
    </div>
  </div>

  <!-- Block 4: Telegram -->
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="sys_tg">TELEGRAM УПРАВЛЕНИЕ</h3></div>
    <div style="padding:25px;">
      <p style="font-size:12px; color:var(--kg-text-dim); margin:0 0 15px;" data-i18n="instr_tg_p">Создайте бота через @BotFather и введите токен. Управляйте VPN прямо из Telegram.</p>
      <div class="fr">
        <div class="fg" style="flex:2"><label data-i18n="tg_token_lbl">Bot Token (@BotFather)</label><input id="tg-token" placeholder="123456789:ABCdef..."></div>
        <div class="fg"><label data-i18n="tg_id_lbl">Ваш Telegram ID</label><input id="tg-allowed-ids" placeholder="123456789"></div>
      </div>
      <button class="btn btn-p" style="margin-top:10px;" onclick="saveTelegramSettings()" data-i18n="save">Сохранить и запустить бота</button>
      <p style="font-size:11px; color:var(--kg-text-dim); margin:8px 0 0;" data-i18n="instructions">Команды бота: /status /servers /add_server /clients /add_client /get_config /logs /restart</p>
    </div>
  </div>

  <!-- Block 5: Backup & Restore -->
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="sys_backup">РЕЗЕРВНОЕ КОПИРОВАНИЕ</h3></div>
    <div style="padding:25px;">
      <p style="font-size:12px; color:var(--kg-text-dim); margin:0 0 15px;" data-i18n="instr_backup_p">Полная копия базы данных и всех конфигураций VPN в одном ZIP-архиве.</p>
      <div style="display:flex; gap:10px; margin-top:20px;">
        <button class="btn btn-o" onclick="downloadBackup()" data-i18n="qr_down">Скачать бэкап</button>
        <div style="position:relative;">
          <button class="btn btn-p" onclick="document.getElementById('restore-file').click()" data-i18n="import">Восстановить из файла</button>
          <input type="file" id="restore-file" style="display:none;" onchange="uploadRestore(this)">
        </div>
      </div>
      <p style="font-size:11px; color:var(--kg-orange); margin:10px 0 0;" data-i18n="sec_restart_warn">При восстановлении панель перезапустится автоматически.</p>
    </div>
  </div>

  <!-- Block 6: Update Management -->
  <div class="card no-blue" id="block-update">
    <div class="card-header"><h3 data-i18n="sys_update">ОБНОВЛЕНИЕ ПАНЕЛИ</h3></div>
    <div style="padding:25px;">
      <p style="font-size:12px; color:var(--kg-text-dim); margin:0 0 15px;">Проверка наличия новых версий на GitHub и автоматическая установка.</p>
      <div class="fr">
        <div class="fg"><label>Текущий коммит</label><span id="current-hash" style="font-family:monospace; color:var(--kg-blue); font-size:14px;">...</span></div>
        <div class="fg"><label>Последний на GitHub</label><span id="remote-hash" style="font-family:monospace; color:var(--kg-green); font-size:14px;">...</span></div>
      </div>
      <div id="update-info" style="margin-top:12px; font-weight:600; font-size:13px;"></div>
      <div style="margin-top:20px; display:flex; gap:10px;">
        <button class="btn btn-p" onclick="checkUpdate()">Проверить обновления</button>
        <button id="btn-apply-update" class="btn btn-s" style="display:none;" onclick="applyUpdate()">Установить обновление</button>
      </div>
    </div>
  </div>

</div>

<!-- LOGS -->
<div class="page" id="page-logs">
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="sys_log">ЖУРНАЛ СОБЫТИЙ</h3>
      <div style="display:flex;gap:10px">
        <select id="log-retention" class="sd-select" style="width:120px" onchange="applyLogSettings()">
          <option value="">Хранение...</option><option value="1day">1 день</option>
          <option value="1week">1 неделя</option><option value="1month">1 месяц</option>
        </select>
        <button class="btn btn-s btn-sm" onclick="downloadLogs()">Скачать .txt</button>
        <input id="log-unit" placeholder="Юнит (напр. skynet)" style="width:150px">
        <button class="btn btn-p btn-sm" onclick="loadLogs()">Обновить</button>
      </div>
    </div>
    <div class="log-box" id="log-output">Загрузка...</div>
  </div>
</div>

<!-- CLI -->
<div class="page" id="page-cli">
  <div class="card no-blue">
    <div class="card-header"><h3 data-i18n="cli_title">КОМАНДНАЯ СТРОКА</h3></div>
    <!-- Toolbar -->
    <div style="display:flex; flex-wrap:wrap; gap:8px; padding:15px 25px; border-bottom:1px solid var(--kg-border); background:rgba(0,0,0,0.15);">
      <button class="btn btn-o btn-sm" onclick="cliQuick('clear')" title="Очистить экран"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14"></path></svg> Очистить</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('uname -a && uptime && hostname')" title="Информация о системе"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg> Система</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('top -bn1 | head -20')" title="Процессы"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg> Процессы</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('systemctl list-units --type=service --state=running --no-pager')" title="Службы"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.6 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.6a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"></path></svg> Службы</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('ip a && echo --- && ip r')" title="Сеть"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"></path></svg> Сеть</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('df -hT && echo --- && lsblk')" title="Диски"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg> Диски</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('free -h')" title="Память"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg> Память</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('last -10')" title="Последние входы"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0110 0v4"></path></svg> Входы</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('systemctl restart skynet')" title="Перезапустить Sky-Net"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"></path></svg> Рестарт</button>
      <button class="btn btn-o btn-sm" onclick="cliQuick('cd /opt/sky-net && git pull && sudo systemctl restart skynet')" title="Git Pull + Перезапуск"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><polyline points="16 16 12 12 8 16"></polyline><line x1="12" y1="12" x2="12" y2="21"></line><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"></path></svg> Обновить</button>
      <button class="btn btn-d btn-sm" onclick="if(confirm('Перезагрузить сервер?')) cliQuick('reboot')" title="Перезагрузка сервера"><svg fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg> Reboot</button>
    </div>
    <div class="log-box" id="cli-output" style="height: 350px;">root@sky-net:~# </div>
    <div style="display:flex; padding: 20px; border-top: 1px solid var(--kg-border); background: rgba(0,0,0,0.1);">
      <span style="color:var(--kg-green); font-family:monospace; margin-right: 10px; align-self: center;">$&gt;</span>
      <input id="cli-input" style="flex:1; background: transparent; border: none; color: inherit; outline: none; font-family: monospace; font-size: 14px;" placeholder="ls -la" onkeypress="if(event.key==='Enter') runCliCommand()">
    </div>
  </div>
</div>

<!-- SETTINGS -->
<div class="page" id="page-settings">
  <div class="card no-blue">
    <div class="card-header"><h3>ПАРАМЕТРЫ ПАНЕЛИ</h3></div>
    <div style="padding:25px;">
      <div class="fr">
        <div class="fg"><label>Порт панели</label><input id="s-port" type="number"></div>
        <div class="fg"><label>Базовый путь</label><input id="s-basepath" placeholder="/panel"></div>
      </div>
      <button class="btn btn-p" onclick="saveSettings()">Сохранить изменения</button>
    </div>
  </div>
</div>

<!-- INSTRUCTIONS -->
<div class="page" id="page-instructions">
  <div class="card no-blue" style="grid-column: span 12;">
    <div class="card-header"><h3 data-i18n="instr_title">ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ</h3></div>
    <div style="padding:40px;">
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:30px;">
        <div>
          <h4 style="color:var(--kg-blue); margin-bottom:12px; font-size:18px;" data-i18n="instr_tg_h">1. Подключение к Telegram</h4>
          <p style="color:var(--kg-text-dim); line-height:1.6;" data-i18n="instr_tg_p">Создайте бота через <a href="https://t.me/BotFather" target="_blank" style="color:var(--kg-blue)">@BotFather</a>, получите Token и введите его в разделе <strong>"Настройки системы"</strong>. После этого вы сможете управлять сервером через команды бота:</p>
          <ul style="margin:10px 0 0 20px; color:var(--kg-text-dim); font-size:13px; line-height:1.8;">
            <li data-i18n="instr_status"><code>/status</code> — Состояние сервера</li>
            <li data-i18n="instr_servers"><code>/servers</code> — Список VPN протоколов</li>
            <li data-i18n="instr_clients"><code>/clients</code> — Список пользователей</li>
            <li data-i18n="instr_backup"><code>/backup</code> — Создать и скачать бэкап</li>
          </ul>
        </div>
        <div>
          <h4 style="color:var(--kg-blue); margin-bottom:12px; font-size:18px;" data-i18n="instr_port_h">2. Смена порта панели</h4>
          <p style="color:var(--kg-text-dim); line-height:1.6;" data-i18n="instr_port_p">Вы можете сменить основные порты управления (HTTP и HTTPS) на любые свободные. Панель автоматически откроет доступ в брандмауэре (UFW) и перезагрузится. <strong>Важно:</strong> после смены портов введите новый адрес в браузере вручную.</p>
        </div>
        <div>
          <h4 style="color:var(--kg-blue); margin-bottom:12px; font-size:18px;" data-i18n="instr_ssl_h">3. Настройка SSL (HTTPS)</h4>
          <p style="color:var(--kg-text-dim); line-height:1.6;" data-i18n="instr_ssl_p">Для безопасного подключения используйте <strong>Let's Encrypt</strong> (требуется домен) или <strong>Самоподписанный сертификат</strong>. При использовании самоподписанного сертификата браузер покажет предупреждение — это нормально, трафик всё равно зашифрован.</p>
        </div>
        <div>
          <h4 style="color:var(--kg-blue); margin-bottom:12px; font-size:18px;" data-i18n="instr_backup_h">4. Резервное копирование</h4>
          <p style="color:var(--kg-text-dim); line-height:1.6;" data-i18n="instr_backup_p">Регулярно скачивайте бэкап в разделе <strong>"Бэкап и восстановление"</strong>. Файл содержит полную базу пользователей и все конфигурации VPN. В случае сбоя или переезда на другой сервер вы сможете восстановить всё за один клик.</p>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- MODALS -->
<div class="overlay" id="addInboundModal">
  <div class="modal">
    <div class="modal-header">Добавить VPN подключение</div>
    <div class="modal-body">
      <div class="fg"><label>Протокол</label>
        <select id="ib-protocol" onchange="updateObfsFields()">
          <option value="amneziawg_v1">AmneziaWG v1 (Legacy)</option>
          <option value="amneziawg_v2">AmneziaWG v2</option>
          <option value="openvpn_xor">OpenVPN + XOR Patch</option>
        </select></div>
      <div class="fr">
        <div class="fg"><label>Имя</label><input id="ib-remark" placeholder="VPN Home"></div>
        <div class="fg"><label>Порт</label><input id="ib-port" type="number" value="51820"></div>
      </div>
      <details style="margin-bottom:15px; cursor:pointer;" class="adv-params">
        <summary style="color:#00a8e8; font-weight:bold;">Дополнительные параметры (MTU, DNS, Подсеть)</summary>
        <div class="fr" style="margin-top:10px;">
          <div class="fg"><label>MTU</label><input id="ib-mtu" type="number" value="1420"></div>
          <div class="fg"><label>DNS (через запятую)</label><input id="ib-dns" value="1.1.1.1, 8.8.8.8"></div>
        </div>
        <div class="fr">
          <div class="fg"><label>Подсеть VPN</label><input id="ib-address" value="10.8.0.1/24"></div>
          <div class="fg"><label>Внешний IP сервера (опцио)</label><input id="ib-server-ip" placeholder="Авто"></div>
        </div>
      </details>
      <div id="obfs-fields"></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-o" onclick="closeModal('addInboundModal')">Отмена</button>
      <button class="btn btn-p" onclick="submitInbound()">Создать</button>
    </div>
  </div>
</div>

<div class="overlay" id="widgetSettingsModal">
  <div class="modal" style="max-width: 600px;">
    <div class="modal-header">Расположение плиток</div>
    <div class="modal-body">
      <div class="widget-grid" id="widget-grid-container">
        <!-- Tiles rendered here -->
      </div>
    </div>
    <div class="modal-footer" style="justify-content: flex-end;">
      <button class="btn btn-o" onclick="resetWidgets()" data-i18n="reset">Сброс</button>
      <button class="btn btn-p" onclick="closeModal('widgetSettingsModal')" data-i18n="done">Готово</button>
    </div>
  </div>
</div>

<div class="overlay" id="qrModal">
  <div class="modal">
    <div class="modal-header">Конфигурация клиента</div>
    <div class="modal-body" style="text-align:center">
      <div style="background:#fff;padding:20px;display:inline-block;border-radius:10px;margin-bottom:15px">
        <img id="qrImage" style="width:400px;height:400px;object-fit:contain">
      </div>
      <textarea id="qrConfigText" readonly style="width:100%;height:150px;font-family:monospace;font-size:12px;background:#111419;color:#00a8e8;border:1px solid #30363d;padding:10px;border-radius:4px"></textarea>
    </div>
    <div class="modal-footer">
      <button class="btn btn-o" onclick="copyConfig()" data-i18n="qr_copy">Копировать</button>
      <button class="btn btn-s" id="downloadBtn" data-i18n="qr_down">Скачать .conf</button>
      <button class="btn btn-o" onclick="closeModal('qrModal')" data-i18n="qr_close">Закрыть</button>
    </div>
  </div>
</div>

<div id="debug-error-bar" style="display:none; position:fixed; bottom:20px; right:20px; z-index:999999; background:rgba(244, 63, 94, 0.9); backdrop-filter:blur(10px); color:white; padding:15px 25px; border-radius:12px; font-weight:600; font-size:14px; box-shadow:0 10px 25px rgba(244,63,94,0.3); border:1px solid rgba(255,255,255,0.1); max-width:400px; word-wrap:break-word;"></div>
<script>
window.onerror = function(msg, url, lineNo, columnNo, error) {
  const bar = document.getElementById('debug-error-bar');
  if(bar) {
    bar.innerHTML = '⚠️ <b>UI Crash Detected:</b><br>' + msg + '<br><small style="opacity:0.8">Line: ' + lineNo + '</small>';
    bar.style.display = 'block';
  }
  return false;
};
window.addEventListener('unhandledrejection', function(event) {
  const bar = document.getElementById('debug-error-bar');
  if(bar) {
    bar.innerHTML = '⚠️ <b>API/Promise Error:</b><br>' + (event.reason ? event.reason.message || event.reason : 'Unknown error');
    bar.style.display = 'block';
    setTimeout(() => { bar.style.display = 'none'; }, 8000);
  }
});
const API = async (p) => {
  console.log("SKY-NET API CALL:", p);
  try {
    const r = await fetch(p, { credentials: 'include' });
    if(r.status === 401) { console.warn("401 Unauthorized for " + p); window.location.href = '/login'; return {success:false}; }
    if(!r.ok) { 
      const err = "API Fetch failed: " + p + " Status: " + r.status;
      console.error(err);
      notifyError(err);
      return {success:false, status: r.status}; 
    }
    const data = await r.json();
    console.log("SKY-NET API SUCCESS:", p, data);
    return data;
  } catch(e) {
    const err = "API Exception: " + p + " error: " + e.message;
    console.error(err);
    notifyError(err);
    return {success:false, error: e.message};
  }
};
const POST = async (p, body={}) => {
  console.log("SKY-NET POST CALL:", p, body);
  try {
    const r = await fetch(p, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      credentials: 'include'
    });
    if(r.status === 401) { console.warn("401 Unauthorized for " + p); window.location.href = '/login'; return {success:false}; }
    if(!r.ok) { 
      const err = "API POST failed: " + p + " Status: " + r.status;
      console.error(err);
      notifyError(err);
      return {success:false, status: r.status}; 
    }
    const data = await r.json();
    console.log("SKY-NET POST SUCCESS:", p, data);
    return data;
  } catch(e) {
    const err = "API POST Exception: " + p + " error: " + e.message;
    console.error(err);
    notifyError(err);
    return {success:false, error: e.message};
  }
};
function notifyError(msg) {
  const bar = document.getElementById('debug-error-bar');
  if(bar) {
    bar.textContent = msg;
    bar.style.display = 'block';
    setTimeout(() => bar.style.display = 'none', 10000);
  }
}
console.log("SKY-NET FRONTEND LOADED V3.0");
function fmtB(b){if(!b||b===0)return'0 B';const k=1024,s=['B','KB','MB','GB','TB'];const i=Math.floor(Math.log(b)/Math.log(k));return(b/Math.pow(k,i)).toFixed(1)+' '+s[i]}
function fmtUp(s){const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d+'d '+h+'h '+m+'m'}
function fmtDate(ts){if(!ts||ts===0)return'Никогда';return new Date(ts*1000).toLocaleDateString()}
function closeModal(id){document.getElementById(id).classList.remove('show')}

// Locale & Theme
const I18N = {
  en: {
    "instr_clients":"— List of users", "instr_backup":"— Create and download backup",
    "instr_port_h":"2. Change Panel Port",
    "instr_port_p":"You can change the main management ports (HTTP and HTTPS) to any free ones. The panel will automatically open access in the firewall (UFW) and restart. Important: after changing ports, enter the new address in the browser manually.",
    "instr_ssl_h":"3. SSL Configuration (HTTPS)",
    "instr_ssl_p":"For a secure connection, use Let's Encrypt (domain required) or a Self-signed certificate. When using a self-signed certificate, the browser will show a warning — this is normal, the traffic is still encrypted.",
    "instr_backup_h":"4. Backup",
    "instr_backup_p":"Regularly download backups in the \"Backup and Restore\" section. The file contains a complete user database and all VPN configurations. In case of failure or moving to another server, you can restore everything in one click.",
    "allow":"Allow", "deny":"Deny", "reject":"Reject", "any":"Any", "protocol":"Protocol", "name":"Name", "port":"Port",
    "adv_params":"Advanced parameters (MTU, DNS, Subnet)", "create":"Create", "reset":"Reset",
    "done":"Done", "qr_title":"Client Configuration", "qr_copy":"Copy", "qr_down": "Download .conf", "qr_close":"Close",
    "widget_title":"Tile Layout", "nav_ifaces":"Network Interfaces", "login_btn":"LOGIN TO PANEL", "disk_lbl":"DISK",
    "active_lbl":"ACTIVE", "offline_lbl":"OFFLINE", "no_limit":"No limit", "on_lbl":"On", "off_lbl":"Off",
    "running_lbl":"Running", "paused_lbl":"Paused", "disable_act":"Disable", "enable_act":"Enable",
    "logs_act":"Logs", "add_client_act":"+ Client", "delete_act":"Delete", "rename_hint":"Click to rename",
    "internet_lbl":"INTERNET", "traffic_total_lbl":"Total Traffic", "no_active_sessions":"No active sessions",
    "sys_device_time":"DEVICE & TIME", "current_server_time":"Current server time:",
    "f2b_installed_active":"Installed & Active", "f2b_not_installed":"Not installed", "status_disabled":"DISABLED",
    "ssl_apply_btn":"Apply SSL Settings", "restart_btn":"Restart", "ssl_off_opt":"HTTP (no SSL)",
    "all_rules_tab":"All Rules", "fw_active_lbl":"UFW: ACTIVE", "fw_inactive_lbl":"UFW: INACTIVE",
    "adv_params_lbl":"Advanced parameters (MTU, DNS, Subnet)", "dns_lbl":"DNS (COMMA SEPARATED)",
    "subnet_lbl":"VPN SUBNET", "ext_ip_lbl":"EXTERNAL SERVER IP (OPTIONAL)",
    "junk_lbl":"JUNK PACKETS (JUNK)", "padding_lbl":"PACKET PADDING (PADDING)", "headers_lbl":"HEADERS",
    "fw_sync_confirm":"Import current rules from system to panel? (Original priorities will not be preserved)",
    "fw_no_rules_p1":"No rules for interface", "obfs_pw":"Obfuscation Password", "obfs_bypass":"Bypassing routes",
    "f2b_install":"Install Fail2Ban", "f2b_confirm":"Install Fail2Ban?", "ssl_confirm":"Apply SSL settings and restart panel?",
    "f2b_title":"Fail2Ban — Brute-force protection", "f2b_desc":"Automatically blocks IP addresses trying to brute-force SSH or panel passwords.",
    "sys_device_time_h":"DEVICE & TIME", "sec_title_h":"SECURITY", "ib_add_title":"Add VPN Connection",
    "waiting_lbl":"WAITING", "ssl_cert_found":"Certificate file found", "ssl_cert_not_found":"Certificate file not found",
    "ssl_restart_needed":"⚠️ Panel restart required to activate HTTPS (port ",
    "tg_save_success":"Telegram settings saved. Restart the panel.", "error_lbl":"Error", "no_logs":"No logs",
    "ssl_domain_err":"Specify a domain for Let's Encrypt",
    "ssl_ip_err":"Let's Encrypt requires a domain (e.g., sky-net.io). For IP address use \"Self-Signed\".",
    "restart_confirm":"Restart management panel?", "del_client_confirm":"Delete client?", "del_ib_confirm":"Delete this server and all clients?",
    "add_clt_prompt":"Enter username:", "rename_prompt":"Enter new name for ",
    "sec_login_pw":"Change Login & Password", "sec_new_login":"New login", "sec_new_pw":"New password",
    "sec_confirm":"Confirm Password", "sys_params":"Web Panel Ports", "sec_apply_ports":"Apply Ports",
    "sec_restart_warn":"Attention: panel will restart on new ports.", "import":"Restore from file",
    "tg_token_lbl":"Bot Token (@BotFather)", "user_lbl":"User:", "lang_lbl":"Select Language",
    "theme_lbl":"Visual Theme", "logout":"Logout", "reboot":"Reboot",
    "enable":"Enable UFW", "disable":"Disable UFW", "add_rule":"Add Rule",
    "fw_title":"Firewall", "fw_desc":"To add a firewall rule, select an interface to monitor incoming traffic and click Add Rule.",
    "fw_modal_title":"Firewall Rule", "fw_modal_desc":"Choose the action for incoming packets and specify conditions.",
    "fw_enable_rule":"Enable rule", "fw_action_lbl":"Action", "fw_reject":"Reject",
    "fw_src_ip_lbl":"Source IP address", "fw_dst_ip_lbl":"Destination IP address",
    "fw_src_port_lbl":"Source port", "fw_dst_port_lbl":"Destination port",
    "fw_custom_ip":"Specify IP or subnet...", "fw_custom_port":"Specify port or range...",
    "fw_iface_lbl":"Interface", "fw_prio_lbl":"Move to",
    "fw_prio_start":"Top of list", "fw_prio_mid":"Middle of list", "fw_prio_end":"End (current position)",
    "fw_schedule_lbl":"Schedule", "fw_always":"Always active",
    "fw_save":"Save", "fw_cancel":"Cancel",
    "fw_del_confirm":"Delete rule?", "fw_apply_confirm":"Apply all settings to the system?",
    "fw_sync_done":"Import completed!", "fw_name_ph":"e.g.: Block ICMP",
    "fw_prio_col":"Prio.", "fw_action_col":"Action", "fw_proto_col":"Protocol",
    "fw_iface_col":"Interface", "fw_src_col":"Source", "fw_srcp_col":"Src Port",
    "fw_dst_col":"Destination", "fw_dstp_col":"Dst Port", "fw_name_col":"Name / Comment"
  }
};
function _T(key) {
  const lang = localStorage.getItem('lang') || 'ru';
  if(lang === 'ru') return {
    "active_lbl":"АКТИВЕН", "offline_lbl":"ОФФЛАЙН", "no_limit":"Без лимита", "on_lbl":"Вкл", "off_lbl":"Выкл",
    "running_lbl":"Работает", "paused_lbl":"Пауза", "disable_act":"Выключить", "enable_act":"Включить",
    "logs_act":"Журнал", "add_client_act":"+ Клиент", "delete_act":"Удалить", "rename_hint":"Нажмите, чтобы переименовать",
    "internet_lbl":"ИНТЕРНЕТ", "traffic_total_lbl":"Трафик (Всего)", "no_active_sessions":"Нет активных сессий",
    "nav_ifaces":"СЕТЕВЫЕ ИНТЕРФЕЙСЫ", "login_btn":"ВОЙТИ В ПАНЕЛЬ", "disk_lbl":"ДИСК", "widget_title":"Расположение плиток",
    "current_server_time":"Текущее время сервера:", "f2b_installed_active":"Установлен и активен",
    "f2b_not_installed":"Не установлен", "status_disabled":"ОТКЛЮЧЕН", "all_rules_tab":"Все правила",
    "obfs_pw":"Пароль обфускации", "obfs_bypass":"Маршруты для обхода (bypassing)",
    "junk_lbl":"Мусорные пакеты (Junk)", "padding_lbl":"Паддинг пакетов (Padding)", "headers_lbl":"Заголовки (Headers)",
    "fw_no_rules_p1":"Нет правил для интерфейса", "f2b_confirm":"Установить Fail2Ban?",
    "f2b_title":"Fail2Ban — защита от брутфорса", "f2b_desc":"Автоматически блокирует IP-адреса, которые пытаются подобрать пароль к SSH или панели.",
    "waiting_lbl":"ОЖИДАНИЕ", "ssl_cert_found":"Файл сертификата найден", "ssl_cert_not_found":"Файлы не найдены",
    "ssl_restart_needed":"⚠️ Требуется перезапуск панели для активации HTTPS (порт ",
    "tg_save_success":"Настройки Telegram сохранены. Перезапустите панель.", "error_lbl":"Ошибка", "no_logs":"Нет логов",
    "ssl_domain_err":"Укажите домен для Let's Encrypt", "restart_confirm":"Перезапустить панель управления?",
    "del_client_confirm":"Удалить клиента?", "del_ib_confirm":"Удалить этот сервер и всех клиентов?",
    "add_clt_prompt":"Введите имя пользователя:", "rename_prompt":"Введите новое имя для ",
    "sec_login_pw":"Смена логина и пароля", "sec_new_login":"Новый логин", "sec_new_pw":"Новый пароль",
    "sec_confirm":"Подтверждение", "sys_params":"Порты веб-панели", "sec_apply_ports":"Применить порты",
    "sec_restart_warn":"Внимание: панель перезапустится на новых портах.", "import":"Восстановить из файла",
    "tg_token_lbl":"Bot Token (@BotFather)", "user_lbl":"Пользователь:", "lang_lbl":"Выберите язык",
    "theme_lbl":"Стиль оформления", "logout":"Выйти", "reboot":"Перезагрузка",
    "enable":"Включить UFW", "disable":"Выключить UFW", "add_rule":"Добавить правило",
    "fw_title":"Межсетевой экран", "fw_desc":"Чтобы добавить правило, выберите интерфейс и нажмите Добавить правило.",
    "fw_modal_title":"Правило межсетевого экрана",
    "fw_modal_desc":"Выберите действие для входящих пакетов и укажите условия.",
    "fw_enable_rule":"Включить правило", "fw_action_lbl":"Действие",
    "allow":"Разрешить", "deny":"Запретить", "reject":"Отклонить", "fw_reject":"Отбросить",
    "fw_src_ip_lbl":"IP-адрес источника", "fw_dst_ip_lbl":"IP-адрес назначения",
    "fw_src_port_lbl":"Порт источника", "fw_dst_port_lbl":"Порт назначения",
    "fw_custom_ip":"Указать IP или подсеть...", "fw_custom_port":"Указать порт или диапазон...",
    "fw_iface_lbl":"Интерфейс", "fw_prio_lbl":"Переместить в",
    "fw_prio_start":"Начало списка", "fw_prio_mid":"Середина списка", "fw_prio_end":"Конец (текущая позиция)",
    "fw_schedule_lbl":"Расписание работы", "fw_always":"Работает постоянно",
    "fw_save":"Сохранить", "fw_cancel":"Отменить",
    "fw_del_confirm":"Удалить правило?", "fw_apply_confirm":"Применить все настройки в систему?",
    "fw_sync_done":"Импорт завершен!", "fw_sync_confirm":"Импортировать текущие правила из системы?",
    "any":"Любой", "protocol":"Протокол", "name":"Имя"
  }[key] || key;
  return (I18N[lang] && I18N[lang][key]) ? I18N[lang][key] : key;
}
function changeLang(lang) {
  localStorage.setItem('lang', lang);
  if(lang === 'ru') { location.reload(); return; }
  
  // 1. Data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const val = _T(key);
    if(el.tagName === 'INPUT') el.placeholder = val;
    else el.textContent = val;
  });
  
  // 2. Data-i18n-ph (Placeholders)
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    el.placeholder = _T(el.getAttribute('data-i18n-ph'));
  });

  // 3. Data-i18n-title (Tooltips)
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = _T(el.getAttribute('data-i18n-title'));
  });
  
  // 2. Placeholder translation
  const placeholders = {
    "Поиск клиентов...": "search_clt",
    "Юнит (напр. skynet)": "log_unit_ph",
    "Например: Блокировка ICMP": "fw_name_ph",
    "например: 10.8.0.0/24": "fw_ip_ph",
    "минимум 6 символов": "sec_new_pw",
    "повторите пароль": "sec_repeat_pw"
  };
  document.querySelectorAll('input[placeholder]').forEach(el => {
    const key = placeholders[el.placeholder];
    if(key && I18N[lang][key]) el.placeholder = I18N[lang][key];
  });

  if(lang === 'en') {
    // 3. Brute-force H3 headers
    const textNodes = [
       ['О СИСТЕМЕ', 'SYSTEM INFO'], ['АКТИВНЫЕ СЕССИИ И ТРАФИК', 'ACTIVE SESSIONS & TRAFFIC'],
       ['СЕТЕВЫЕ ИНТЕРФЕЙСЫ', 'NETWORK INTERFACES'], ['VPN ПОДКЛЮЧЕНИЯ', 'VPN CONNECTIONS'],
       ['ПОДКЛЮЧЕННЫЕ КЛИЕНТЫ', 'CONNECTED CLIENTS'], ['МЕЖСЕТЕВОЙ ЭКРАН', 'FIREWALL (UFW)'],
       ['УСТРОЙСТВО И ВРЕМЯ', 'DEVICE & TIME'], ['TELEGRAM УПРАВЛЕНИЕ', 'TELEGRAM MANAGEMENT'],
       ['РЕЗЕРВНОЕ КОПИРОВАНИЕ', 'BACKUP & RESTORE'], ['ОБНОВЛЕНИЕ ПАНЕЛИ', 'UPDATE MANAGEMENT'],
       ['ДОБАВИТЬ ПРАВИЛО', 'ADD RULE'], ['УПРАВЛЕНИЕ СИСТЕМОЙ', 'SYSTEM MANAGEMENT'],
       ['ПАРАМЕТРЫ ПАНЕЛИ', 'PANEL SETTINGS'], ['ЖУРНАЛ СОБЫТИЙ', 'SYSTEM LOG'],
       ['КОМАНДНАЯ СТРОКА', 'COMMAND LINE'], ['БЕЗОПАСНОСТЬ', 'SECURITY'],
       ['ИНСТРУКЦИИ ПО ИСПОЛЬЗОВАНИЮ', 'INSTRUCTIONS FOR USE'],
       ['СМЕНА ЛОГИНА И ПАРОЛЯ', 'CHANGE LOGIN & PASSWORD'],
       ['ПОРТЫ ВЕБ-ПАНЕЛИ', 'PANEL PORTS'], ['Добавить VPN подключение', 'Add VPN Connection']
    ];
    document.querySelectorAll('h3, h2, h4, .modal-header').forEach(el => {
       const mapped = textNodes.find(t => el.textContent.trim().includes(t[0]));
       if(mapped) {
          const svg = el.querySelector('svg');
          el.textContent = mapped[1] + (svg ? ' ' : '');
          if(svg) el.appendChild(svg);
       }
    });
    
    // 4. Buttons
    const btnNodes = [
      ['Добавить подключение', 'Add Connection'], ['Обновить', 'Refresh'], ['Создать', 'Create'],
      ['Отмена', 'Cancel'], ['Добавить правило', 'Add Rule'], ['Готово', 'Done'],
      ['Сброс', 'Reset'], ['Сохранить изменения', 'Save Changes'], ['Сохранить', 'Save'],
      ['Скачать', 'Download'], ['Запустить Web SSH', 'Start Web SSH'], ['Выключить', 'Disable'],
      ['Включить', 'Enable'], ['Удалить', 'Delete'], ['Перезагрузка', 'Reboot'],
      ['Проверить обновления', 'Check Updates'], ['Установить обновление', 'Install Update'],
      ['Скачать бэкап', 'Download Backup'], ['Восстановить из файла', 'Restore from file'],
      ['Применить порты', 'Apply Ports'], ['Настроить Автозапуск', 'Setup Autostart'],
      ['Копировать', 'Copy'], ['Скачать .conf', 'Download .conf'], ['Закрыть', 'Close'],
      ['Настроить Автозапуск', 'Setup Autostart']
    ];
    document.querySelectorAll('button, .btn, summary').forEach(el => {
      const mapped = btnNodes.find(t => el.textContent.trim().includes(t[0]));
      if(mapped) {
        const svg = el.querySelector('svg');
        el.textContent = mapped[1];
        if(svg) el.prepend(svg);
      }
    });
    
    // 5. Labels and Table Headers
    const spanNodes = [
      ['Имя устройства', 'Hostname'], ['Версия системы', 'OS Version'], ['Время работы', 'Uptime'],
      ['Пользователь', 'User'], ['Протокол', 'Protocol'], ['Трафик', 'Traffic'], ['Статус', 'Status'],
      ['Клиент', 'Client'], ['Сервер', 'Server'], ['IP адрес', 'IP Address'], ['Лимит', 'Limit'],
      ['Действия', 'Actions'], ['Часовой пояс', 'Timezone'], ['Порт панели', 'Panel Port'],
      ['Базовый путь', 'Base Path'], ['Ваш Telegram ID', 'Your Telegram ID'],
      ['Текущий коммит', 'Current Commit'], ['Последний на GitHub', 'Latest on GitHub'],
      ['Действие', 'Action'], ['Интерфейс', 'Interface'], ['Источник', 'Source'],
      ['Порт ист.', 'Src Port'], ['Назначение', 'Destination'], ['Порт назн.', 'Dst Port'],
      ['Имя / Комментарий', 'Name / Comment'], ['ИМЯ / КОММЕНТАРИЙ', 'NAME / COMMENT'],
      ['новый логин', 'new username'], ['новый пароль', 'new password'],
      ['ПОДТВЕРЖДЕНИЕ', 'CONFIRMATION'], ['Имя', 'Name'], ['Порт', 'Port'],
      ['Включить правило', 'Enable rule'], ['Переместить в', 'Move to'],
      ['Расписание работы', 'Schedule'], ['Имя устройства', 'Hostname'], ['Часовой пояс', 'Timezone']
    ];
    document.querySelectorAll('.k-lbl, th, label, td, span').forEach(el => {
      const txt = el.textContent.trim();
      if(txt === 'Разрешить') el.textContent = 'Allow';
      if(txt === 'Запретить') el.textContent = 'Deny';
      if(txt === 'Любой') el.textContent = 'Any';
      const mapped = spanNodes.find(t => txt === t[0]);
      if(mapped) el.textContent = mapped[1];
    });

    // 6. Paragraphs and spans
    const pNodes = [
      ['Нет активных сессий', 'No active sessions'],
      ['Создайте бота через @BotFather', 'Create a bot via @BotFather and enter the token.'],
      ['Полная копия базы данных', 'Full copy of database and configs in one ZIP.'],
      ['При восстановлении панель перезапустится', 'Restart required after restoration.'],
      ['Проверка наличия новых версий', 'Checking for updates on GitHub...'],
      ['Внимание: панель перезапустится', 'Note: the panel will restart on the new ports.'],
      ['чтобы добавить правило', 'To add a firewall rule, select an interface...'],
      ['Правила применяются в том порядке', 'Rules are applied in the order they appear.'],
      ['UFW: АКТИВЕН', 'UFW: ACTIVE'], ['UFW: ОТКЛЮЧЕН', 'UFW: INACTIVE']
    ];
    document.querySelectorAll('p, span, div, li').forEach(el => {
      if(el.children.length > 0) return;
      const mapped = pNodes.find(t => el.textContent.trim().includes(t[0]));
      if(mapped) el.textContent = mapped[1];
    });
  }
}
function changeTheme(t){
  document.documentElement.setAttribute('data-theme',t==='light'?'light':'');
  localStorage.setItem('theme',t);
}
(function(){
  const t=localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme',t==='light'?'light':'');
  const l=localStorage.getItem('lang') || 'ru';
  document.addEventListener('DOMContentLoaded', () => {
    const ts = document.getElementById('theme-select'); if(ts) ts.value = t;
    const ls = document.getElementById('lang-select'); if(ls) ls.value = l;
    if(l !== 'ru') changeLang(l);
  });
})();

// Nav
const loadSettings = async () => {};

function switchPage(page, noPush=false) {
  let targetUrl = page === 'dashboard' ? '/' : '/' + page;
  if(!noPush && window.location.pathname !== targetUrl) {
    window.history.pushState({page: page}, '', targetUrl);
  }
  document.querySelectorAll('.sidebar nav a').forEach(a=>{
    a.classList.remove('active');
    if(a.dataset.page===page) a.classList.add('active');
  });
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  const pg = document.getElementById('page-'+page);
  if(pg) pg.classList.add('active');
  const dsetTitle = document.getElementById('page-title-text');
  if(dsetTitle) {
     const titleT = document.querySelector(`.sidebar nav a[data-page="${page}"] span`);
     if (titleT) dsetTitle.textContent = titleT.textContent;
  }
  const fn={dashboard:loadDashboard,inbounds:loadInbounds,clients:loadAllClients,
    firewall:loadFirewall,system:loadSystem,logs:loadLogs,settings:loadSettings}[page];
  if(fn)fn();
}

document.querySelectorAll('.sidebar nav a').forEach(a=>{
  a.addEventListener('click',e=>{e.preventDefault(); switchPage(a.dataset.page);})});

window.addEventListener('popstate', (e) => {
  if(e.state && e.state.page) switchPage(e.state.page, true);
});

const initPage='{{page}}';if(initPage){switchPage(initPage, true);}

// Logs & CLI
async function applyLogSettings() {
  const r = document.getElementById('log-retention').value;
  if(!r) return;
  const l = localStorage.getItem('lang');
  alert(l==='en'?'Applying log settings...':'Применение настроек журнала...');
  await POST('/panel/api/system/logs/settings', {retention: r});
  alert(l==='en'?'Settings applied (old logs vacuumed).':'Настройки применены (старые логи очищены).');
}
function downloadLogs() {
  const u = document.getElementById('log-unit').value || 'skynet';
  window.open(`/panel/api/system/logs/download?unit=${u}`, '_blank');
}

async function runCliCommand() {
  const input = document.getElementById('cli-input');
  const out = document.getElementById('cli-output');
  const cmd = input.value.trim();
  if(!cmd) return;
  out.textContent += `root@sky-net:~# ${cmd}\n`;
  input.value = '';
  try {
    const resp = await fetch('/panel/api/system/cmd', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({cmd: cmd})});
    const r = await resp.json();
    out.textContent += (r.output || '(no output)') + "\n\n";
  } catch(e) { out.textContent += "Error: " + e.message + "\n\n"; }
  out.scrollTop = out.scrollHeight;
}
async function cliQuick(cmd) {
  const out = document.getElementById('cli-output');
  if(cmd === 'clear') { out.textContent = 'root@sky-net:~# '; return; }
  out.textContent += `root@sky-net:~# ${cmd}\n`;
  try {
    const resp = await fetch('/panel/api/system/cmd', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({cmd: cmd})});
    const r = await resp.json();
    out.textContent += (r.output || '(no output)') + "\n\n";
  } catch(e) { out.textContent += "Error: " + e.message + "\n\n"; }
  out.scrollTop = out.scrollHeight;
}

// Dashboard logic
let interfaceCharts = {};
let lastNetS = {};
let lastNetR = {};
let lastTime = 0;

function isWidgetHidden(id) {
  const hidden = localStorage.getItem('hidden_widgets') ? localStorage.getItem('hidden_widgets').split(',') : [];
  return hidden.includes(id);
}
function toggleWidgetSettings(id) {
  let hidden = localStorage.getItem('hidden_widgets') ? localStorage.getItem('hidden_widgets').split(',') : [];
  if(hidden.includes(id)) { hidden = hidden.filter(x => x !== id); }
  else { hidden.push(id); }
  localStorage.setItem('hidden_widgets', hidden.join(','));
  openWidgetSettings();
  loadDashboard();
}
function openWidgetSettings() {
  const cont = document.getElementById('widget-grid-container');
  cont.innerHTML = '';
  document.querySelectorAll('.card').forEach(card => {
    const id = card.id;
    if(!id) return;
    const titleObj = card.querySelector('h3');
    if(!titleObj) return;
    const title = titleObj.textContent;
    const hidden = isWidgetHidden(id);
    cont.innerHTML += `<div class="widget-card" data-id="${id}" style="cursor:grab">
      <div class="widget-card-title">${title}</div>
      <div class="widget-card-toggle" onclick="toggleWidgetSettings('${id}')">
        <div class="w-tgl ${hidden?'':'on'}"></div>
        <div class="w-lbl">Показать плитку</div>
      </div>
    </div>`;
  });
  
  if(!window.widgetSortable) {
    if(typeof Sortable !== 'undefined') {
      window.widgetSortable = new Sortable(cont, {
        animation: 150,
        ghostClass: 'sortable-ghost',
        onEnd: function() {
          const order = Array.from(cont.children).map(c => c.dataset.id).join('|');
          localStorage.setItem('sort_d1', order);
          const parent = document.getElementById('sortable-dashboard');
          if(parent) {
            order.split('|').forEach(ordId => {
              const el = document.getElementById(ordId);
              if(el && el.parentElement === parent) parent.appendChild(el); 
            });
          }
        }
      });
    }
  }
  
  document.getElementById('widgetSettingsModal').classList.add('show');
}
function resetWidgets() {
  localStorage.removeItem('hidden_widgets');
  localStorage.removeItem('sort_d1');
  localStorage.removeItem('sort_d2');
  location.reload();
}

function renameInterface(iface) {
  const current = localStorage.getItem('iface_name_' + iface) || 'Sky-Net Interface';
  const newName = prompt(_T('rename_prompt') + iface + ':', current);
  if (newName !== null) {
     localStorage.setItem('iface_name_' + iface, newName.trim() || 'Sky-Net Interface');
     loadDashboard();
  }
}

function toggleIfaceView(iface, viewType) {
  const key = 'hide_' + viewType + '_' + iface;
  if(localStorage.getItem(key)) localStorage.removeItem(key);
  else localStorage.setItem(key, '1');
  const d = document.getElementById(viewType + '-wrap-' + iface);
  if(d) d.style.display = localStorage.getItem(key) ? 'none' : '';
  const btn = document.getElementById('btn-' + viewType + '-' + iface);
  if(btn) {
     if(localStorage.getItem(key)) { btn.style.color=''; btn.style.background=''; }
     else { btn.style.color='var(--kg-blue)'; btn.style.background='rgba(47,161,237,0.1)'; }
  }
}

async function rebootServer(){ if(confirm('Вы действительно хотите перезагрузить СЕРВЕР? Соединение будет разорвано.')) { await POST('/panel/api/system/reboot',{}); alert('Запрос отправлен. Подождите 1-2 минуты.'); } }

let interfaceHistory = {};

async function loadDashboard(){
  let st={}, net=[], hist={up:[],down:[]};
  try { st = await API('/panel/api/server/status'); } catch(e) { console.error("Status API fail", e); }
  try { net = await API('/panel/api/system/network') || []; } catch(e) { console.error("Network API fail", e); }
  try { hist = await API('/panel/api/trafficHistory') || {up:[],down:[]}; } catch(e) { console.error("Traffic API fail", e); }
  
  const d_ip=document.getElementById('d-ip'), d_host=document.getElementById('d-host'), d_os=document.getElementById('d-os');
  const d_time=document.getElementById('d-time'), d_version=document.getElementById('d-version'), d_https=document.getElementById('d-https');
  if(d_host) d_host.textContent = st.hostname || 'Sky-Net';
  if(d_os) d_os.textContent = st.os_version || 'Ubuntu';
  if(d_time && st.server_time) d_time.textContent = new Date(st.server_time * 1000).toLocaleString('ru-RU');
  if(d_version) d_version.textContent = st.panel_version || 'v3.0';
  if(d_https) {
    d_https.textContent = st.https_status === 'Активен' ? _T('running_lbl') : _T('status_disabled');
    d_https.style.color = (st.https_status === 'Активен') ? 'var(--kg-green)' : 'var(--kg-red)';
  }
  
  const curTime = new Date().toLocaleTimeString('ru-RU');
  const now = Date.now();
  let dt = 1;
  if(lastTime > 0) dt = (now - lastTime) / 1000;
  
  const dynCont = document.getElementById('sortable-dashboard');
  if(net.success && dynCont) {
    (net.interfaces || []).forEach(i => {
      // Exclude loopback interfaces
      if(i.name === 'lo') return;
      
      const id = 'block-internet-' + i.name;
      const isHidden = isWidgetHidden(id);
      
      let ds = '0.00', dr = '0.00';
      const nicStats = st.interfaces ? st.interfaces[i.name] : null;
      if(nicStats && lastTime > 0) {
        const prevS = lastNetS[i.name] || 0;
        const prevR = lastNetR[i.name] || 0;
        ds = ((nicStats.bytes_sent - prevS) * 8 / 1000000 / dt).toFixed(2);
        dr = ((nicStats.bytes_recv - prevR) * 8 / 1000000 / dt).toFixed(2);
      }
      if(nicStats) {
        lastNetS[i.name] = nicStats.bytes_sent;
        lastNetR[i.name] = nicStats.bytes_recv;
      }
      
      const ips = i.addresses.map(a => a.ip).join(', ') || '--';
      const mac = i.mac || 'Авто';
      const bs = nicStats ? fmtB(nicStats.bytes_sent) : '--';
      const br = nicStats ? fmtB(nicStats.bytes_recv) : '--';
      const savedName = localStorage.getItem('iface_name_' + i.name) || 'Sky-Net Interface';
      const hideChart = localStorage.getItem('hide_chart_' + i.name) ? 'none' : '';
      const hideGrid = localStorage.getItem('hide_grid_' + i.name) ? 'none' : '';
      const chartBtnStyle = hideChart ? '' : 'color:var(--kg-blue); background:rgba(47,161,237,0.1);';
      const gridBtnStyle = hideGrid ? '' : 'color:var(--kg-blue); background:rgba(47,161,237,0.1);';
      
      let cardEl = document.getElementById(id);
      if(!cardEl) {
        const html = `<div class="card" id="${id}" style="${isHidden?'display:none;':''}">
          <div class="card-header" style="cursor:grab">
            <h3 style="margin:0; text-transform:uppercase;">${_T('internet_lbl')} (${i.name})</h3>
            <svg fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" viewBox="0 0 24 24" style="color:var(--kg-text-dim);"><path d="M4 8h16M4 16h16"></path></svg>
          </div>
              <div class="k-k-conn-block">
              <div class="k-conn-left">
                <div class="k-toggle ${i.is_up?'on':''}" id="tgl-${i.name}"></div>
                <div>
                  <div class="k-conn-title" onclick="renameInterface('${i.name}')" style="cursor:pointer; border-bottom:1px dashed rgba(255,255,255,0.3); display:inline-block; padding-bottom:1px;" title="${_T('rename_hint')}" id="title-${i.name}">${savedName}</div>
                  <div class="k-conn-subtitle">${i.name}</div>
                  <div class="k-badge">
                    <div class="dot ${i.is_up?'dot-green':'dot-blue'}" style="width:5px;height:5px;" id="updot-${i.name}"></div>
                    <span style="margin-left:5px" id="upbadge-${i.name}">${i.is_up? _T('connected_lbl') + ' '+fmtUp(st.uptime||0) : _T('disconnected_lbl')}</span>
                  </div>
                </div>
              </div>
            <div class="k-btn-group">
              <button class="k-icon-btn" id="btn-chart-${i.name}" style="transition:0.2s; ${chartBtnStyle}" onclick="toggleIfaceView('${i.name}', 'chart')" title="Показать/скрыть график"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18M7 16l4-4 4 4 4-4"/></svg></button>
              <button class="k-icon-btn" id="btn-grid-${i.name}" style="transition:0.2s; ${gridBtnStyle}" onclick="toggleIfaceView('${i.name}', 'grid')" title="Показать/скрыть детали"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h4v4H4zM16 4h4v4h-4zM4 16h4v4H4zM16 16h4v4h-4z"/></svg></button>
            </div>
          </div>
          <div class="chart-container-wrapper" id="chart-wrap-${i.name}" style="display:${hideChart}">
            <div class="chart-container"><canvas id="chart-${i.name}"></canvas></div>
            <div class="chart-legend">
              <span id="ct1-${i.name}">${curTime}</span>
              <div class="legend-center">
                <div class="legend-item"><div class="dot dot-green"></div>Передача: <span style="color:#fff" id="tx-${i.name}">${ds} Мбит/с</span></div>
                <div class="legend-item"><div class="dot dot-blue"></div>Прием: <span style="color:#fff" id="rx-${i.name}">${dr} Мбит/с</span></div>
              </div>
              <span id="ct2-${i.name}">${curTime}</span>
            </div>
          </div>
          <div class="k-grid" id="grid-wrap-${i.name}" style="display:${hideGrid}">
            <div>
              <div class="k-kv"><span class="k-lbl">IP-адрес</span><span class="k-val" id="ip-${i.name}" style="word-break:break-all">${ips}</span></div>
              <div class="k-kv"><span class="k-lbl">Шлюз</span><span class="k-val">Авто</span></div>
              <div class="k-kv"><span class="k-lbl">Маска подсети</span><span class="k-val">Авто</span></div>
            </div>
            <div>
              <div class="k-kv"><span class="k-lbl">MAC-адрес</span><span class="k-val" id="mac-${i.name}">${mac}</span></div>
              <div class="k-kv"><span class="k-lbl">Прием</span><span class="k-val" id="drv-${i.name}">${dr} Мбит/с</span></div>
              <div class="k-kv"><span class="k-lbl">Передача</span><span class="k-val" id="dsv-${i.name}">${ds} Мбит/с</span></div>
            </div>
            <div>
              <div class="k-kv"><span class="k-lbl">Принято</span><span class="k-val" id="brv-${i.name}">${br}</span></div>
              <div class="k-kv"><span class="k-lbl">Отправлено</span><span class="k-val" id="bsv-${i.name}">${bs}</span></div>
              <div class="k-kv"><span class="k-lbl">DNS-сервер</span><span class="k-val k-val-link">1.1.1.1</span></div>
            </div>
          </div>
        </div>`;
        const sysBlock = document.getElementById('block-system');
        if(sysBlock) sysBlock.insertAdjacentHTML('beforebegin', html);
        else dynCont.insertAdjacentHTML('afterbegin', html);
        interfaceHistory[i.name] = { up: Array(60).fill(0), down: Array(60).fill(0) };
      } else {
        cardEl.style.display = isHidden ? 'none' : '';
        const titleEl = document.getElementById('title-'+i.name); if(titleEl) titleEl.textContent = savedName;
        const upEl = document.getElementById('upbadge-'+i.name); if(upEl) upEl.textContent = i.is_up?'ПОДКЛЮЧЕНО '+fmtUp(st.uptime||0):'ОТКЛЮЧЕНО';
        const tglEl = document.getElementById('tgl-'+i.name); if(tglEl) { if(i.is_up) tglEl.classList.add('on'); else tglEl.classList.remove('on'); }
        const dotEl = document.getElementById('updot-'+i.name); if(dotEl) { if(i.is_up) { dotEl.classList.add('dot-green'); dotEl.classList.remove('dot-blue'); } else { dotEl.classList.add('dot-blue'); dotEl.classList.remove('dot-green'); } }
        const ct1 = document.getElementById('ct1-'+i.name); if(ct1) ct1.textContent = curTime;
        const ct2 = document.getElementById('ct2-'+i.name); if(ct2) ct2.textContent = curTime;
        const txEl = document.getElementById('tx-'+i.name); if(txEl) txEl.textContent = ds + ' Мбит/с';
        const rxEl = document.getElementById('rx-'+i.name); if(rxEl) rxEl.textContent = dr + ' Мбит/с';
        const ipEl = document.getElementById('ip-'+i.name); if(ipEl) ipEl.textContent = ips;
        const macEl = document.getElementById('mac-'+i.name); if(macEl) macEl.textContent = mac;
        const dsv = document.getElementById('dsv-'+i.name); if(dsv) dsv.textContent = ds + ' Мбит/с';
        const drv = document.getElementById('drv-'+i.name); if(drv) drv.textContent = dr + ' Мбит/с';
        const brv = document.getElementById('brv-'+i.name); if(brv) brv.textContent = br;
        const bsv = document.getElementById('bsv-'+i.name); if(bsv) bsv.textContent = bs;
      }
      
      const cCtx = document.getElementById('chart-'+i.name);
      if(cCtx) {
        if(!interfaceHistory[i.name]) interfaceHistory[i.name] = { up: Array(60).fill(0), down: Array(60).fill(0) };
        const h = interfaceHistory[i.name];
        h.up.push(Math.max(0, parseFloat(ds))); h.up.shift();
        h.down.push(Math.max(0, parseFloat(dr))); h.down.shift();
        
        if(!interfaceCharts[i.name]){
           interfaceCharts[i.name] = new Chart(cCtx.getContext('2d'),{type:'line',data:{labels:Array.from({length:60},(_,idx)=>idx),datasets:[{label:'Tx',data:h.up,borderColor:'#2fb45a',fill:true,backgroundColor:'rgba(47,180,90,0.1)',tension:.4,pointRadius:0},{label:'Rx',data:h.down,borderColor:'#00a8e8',fill:true,backgroundColor:'rgba(0,168,232,0.1)',tension:.4,pointRadius:0}]},options:{maintainAspectRatio:false,animation:false,scales:{x:{display:false},y:{display:false,min:0,suggestedMax:1}},plugins:{legend:{display:false}}}});
        } else {
           interfaceCharts[i.name].data.datasets[0].data = h.up; 
           interfaceCharts[i.name].data.datasets[1].data = h.down;
           interfaceCharts[i.name].update();
        }
      }
    });

    if(dynCont && !dynCont.dataset.sorted) {
      const order = localStorage.getItem('sort_d1');
      if(order) {
        order.split('|').forEach(ordId => {
          const el = document.getElementById(ordId);
          if(el && el.parentElement === dynCont) dynCont.appendChild(el); 
        });
      }
      dynCont.dataset.sorted = "true";
    }
  }

  
  lastTime = now;

  const blockSys = document.getElementById('block-system');
  if(blockSys) blockSys.style.display = isWidgetHidden('block-system') ? 'none' : '';
  const blockCli = document.getElementById('block-clients');
  if(blockCli) blockCli.style.display = isWidgetHidden('block-clients') ? 'none' : '';

  const cpuP = st.cpu||0; const ramP = Math.round(st.mem_percent||0); const diskP = Math.round(st.disk_percent||0);
  const cv = document.getElementById('cpu-val'); if(cv) cv.textContent=cpuP+'%';
  const rv = document.getElementById('ram-val'); if(rv) rv.textContent=ramP+'%';
  const dv = document.getElementById('disk-val'); if(dv) dv.textContent=diskP+'%';
  const uv = document.getElementById('uptime-val'); if(uv) uv.textContent=fmtUp(st.uptime||0);
  // Animate SVG rings
  const cr = document.getElementById('cpu-ring'); if(cr) cr.setAttribute('stroke-dasharray', cpuP+', 100');
  const rr = document.getElementById('ram-ring'); if(rr) rr.setAttribute('stroke-dasharray', ramP+', 100');
  const dr2 = document.getElementById('disk-ring'); if(dr2) dr2.setAttribute('stroke-dasharray', diskP+', 100');
  // Color coding: red when high
  if(cr) cr.setAttribute('stroke', cpuP > 80 ? 'var(--kg-red)' : 'var(--kg-blue)');
  if(rr) rr.setAttribute('stroke', ramP > 85 ? 'var(--kg-red)' : 'var(--kg-green)');
  if(dr2) dr2.setAttribute('stroke', diskP > 85 ? 'var(--kg-red)' : '#f59e0b');
  // Extra details
  const ramDet = document.getElementById('ram-detail');
  if(ramDet && st.mem_total) { ramDet.textContent = ((st.mem_used||0)/1073741824).toFixed(1)+'/'+(st.mem_total/1073741824).toFixed(1)+' GB'; }
  const diskDet = document.getElementById('disk-detail');
  if(diskDet && st.disk_total) { diskDet.textContent = ((st.disk_used||0)/1073741824).toFixed(0)+'/'+(st.disk_total/1073741824).toFixed(0)+' GB'; }
  const lavg = document.getElementById('d-loadavg');
  if(lavg) lavg.textContent = st.load_avg || st.cpu + '% load';
  
  const ib=await API('/panel/api/inbounds/list');
  if(ib.success){
    let tu=0,td=0;
    const clt=document.getElementById('dash-clients-list'); if(clt) clt.innerHTML='';
    let totalC = 0;
    ib.obj.forEach(i=>{
      (i.clients||[]).forEach(c=>{
        totalC++;
        tu+=c.up||0; td+=c.down||0;
        if(clt){
          const nowS = Math.floor(Date.now()/1000);
          const isActive = (nowS - (c.last_online||0)) < 240;
          clt.innerHTML += `
            <div class="stat-item" style="padding: 12px 25px;">
              <div style="display:flex; align-items:center; gap:15px; flex:1;">
                <div style="background:rgba(255,255,255,0.05); width:36px; height:36px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:var(--kg-blue);">
                  <svg fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                </div>
                <div>
                  <div style="font-size:14px; font-weight:700; color:#fff; line-height:1.2;">${c.username}</div>
                  <div style="font-size:11px; color:var(--kg-text-dim);">${PL[i.protocol]}</div>
                </div>
              </div>
              <div style="text-align:right; margin-right:20px;">
                <div style="font-size:12px; font-weight:600; color:#fff;">↑ ${fmtB(c.up)} / ↓ ${fmtB(c.down)}</div>
                <div style="font-size:10px; color:var(--kg-text-dim);">${_T('traffic_total_lbl')}</div>
              </div>
              <div>
                <span class="badge ${isActive?'badge-on':'badge-off'}" style="min-width:80px; text-align:center; font-weight:700;">${isActive? _T('active_lbl') : _T('offline_lbl')}</span>
              </div>
            </div>`;
        }
      })
    });
    if(totalC === 0 && clt) {
      clt.innerHTML = `<div style="padding:40px 25px; text-align:center; color:var(--kg-text-dim); font-size:13px;">${_T('no_active_sessions')}</div>`;
    }
  }
}

const PL={'amneziawg_v1':'AmneziaWG v1','amneziawg_v2':'AmneziaWG v2','openvpn_xor':'OpenVPN XOR'};

async function loadInbounds(){
  const r=await API('/panel/api/inbounds/list');if(!r.success)return;
  const cont=document.getElementById('inbounds-list');cont.innerHTML='';
  r.obj.forEach(ib=>{
    cont.innerHTML+=`<div class="ib-row">
      <div class="ib-info">
        <div class="ib-icon-box">${ib.protocol.includes('wg')?'W':'O'}</div>
        <div class="ib-details">
          <h4>${ib.remark}</h4>
          <p>${PL[ib.protocol]} • ${_T('port')}: ${ib.port} • ${_T('nav_clients')}: ${(ib.clients||[]).length}</p>
        </div>
      </div>
      <div class="ib-actions">
        <span class="badge ${ib.enable?'badge-on':'badge-off'}">${ib.enable? _T('running_lbl') : _T('paused_lbl')}</span>
        <button class="btn btn-o btn-sm" onclick="toggleInbound(${ib.id})">${ib.enable? _T('disable_act') : _T('enable_act')}</button>
        <button class="btn btn-p btn-sm" onclick="showInboundLogs(${ib.id})" style="background:var(--kg-blue); border-color:var(--kg-blue);">${_T('logs_act')}</button>
        <button class="btn btn-p btn-sm" onclick="openAddClient(${ib.id})">${_T('add_client_act')}</button>
        <button class="btn btn-d btn-sm" onclick="deleteInbound(${ib.id})">${_T('delete_act')}</button>
      </div>
    </div>`
  })}

async function showInboundLogs(id) {
  let intervalId = null;
  const updateLogs = async () => {
    const r = await API('/panel/api/inbounds/logs/' + id);
    if(!r.success) { 
      if(intervalId) clearInterval(intervalId);
      return; 
    }
    const logBox = document.getElementById('log-box-' + id);
    if(logBox) {
      logBox.textContent = r.logs;
      logBox.scrollTop = logBox.scrollHeight;
    }
    return r;
  };

  const r = await updateLogs();
  if(!r || !r.success) return;
  
  const modal = document.createElement('div');
  modal.id = 'log-modal-' + id;
  modal.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:2000; display:flex; align-items:center; justify-content:center; padding:20px;";
  modal.innerHTML = `
    <div style="background:#1a1a1a; width:90%; max-width:1000px; height:80%; border-radius:12px; border:1px solid var(--kg-border); display:flex; flex-direction:column; overflow:hidden;">
      <div style="padding:15px 25px; border-bottom:1px solid var(--kg-border); display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; text-transform:uppercase; font-size:14px; display:flex; align-items:center; gap:10px;">
          Журнал подключений (ID: ${id})
          <span class="badge badge-on" style="font-size:9px; padding:2px 6px;">LIVE</span>
        </h3>
        <button onclick="closeLogModal(${id})" style="background:none; border:none; color:#fff; cursor:pointer; font-size:20px;">&times;</button>
      </div>
      <div id="log-box-${id}" style="flex:1; padding:20px; overflow:auto; font-family:'JetBrains Mono', monospace; font-size:12px; color:var(--kg-text-dim); white-space:pre-wrap; background:#000; border-bottom:1px solid var(--kg-border);">
        ${r.logs.replace(/</g, '&lt;').replace(/>/g, '&gt;')}
      </div>
      <div style="padding:15px 25px; display:flex; justify-content:space-between; align-items:center;">
        <div style="font-size:11px; color:var(--kg-text-dim);">Авто-обновление каждые 5 сек.</div>
        <div style="display:flex; gap:10px;">
          <button onclick="showInboundLogs(${id})" class="btn btn-p btn-sm">Сброс</button>
          <button onclick="closeLogModal(${id})" class="btn btn-o btn-sm">Закрыть</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(modal);
  
  intervalId = setInterval(updateLogs, 5000);
  window._logIntervals = window._logIntervals || {};
  window._logIntervals[id] = intervalId;
}

function closeLogModal(id) {
  if(window._logIntervals && window._logIntervals[id]) {
    clearInterval(window._logIntervals[id]);
    delete window._logIntervals[id];
  }
  const modal = document.getElementById('log-modal-' + id);
  if(modal) modal.remove();
}

async function loadAllClients(){
  const r=await API('/panel/api/inbounds/list');if(!r.success)return;
  const tb=document.getElementById('clients-table');tb.innerHTML='';
  r.obj.forEach(ib=>{(ib.clients||[]).forEach(c=>{
    tb.innerHTML+=`<tr>
      <td><b>${c.username}</b></td>
      <td><span class="badge badge-proto">${PL[ib.protocol]}</span></td>
      <td><code>${c.allowed_ips}</code></td>
      <td>${fmtB(c.up)} / ${fmtB(c.down)}</td>
      <td>${c.total_limit?fmtB(c.total_limit): _T('no_limit')}</td>
      <td><span class="badge ${c.enable?'badge-on':'badge-off'}">${c.enable? _T('on_lbl') : _T('off_lbl')}</span></td>
      <td>
        <button class="btn btn-o btn-sm" onclick="showQR(${c.id}, '${c.username}', '${ib.protocol}')">QR</button>
        <button class="btn btn-d btn-sm" onclick="deleteClient(${c.id})">${_T('delete_act')}</button>
      </td></tr>`})});
  document.getElementById('clientSearch').oninput=function(){const q=this.value.toLowerCase();
    tb.querySelectorAll('tr').forEach(tr=>{tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none'})}
}

function toggleSidebarCol(){
  if(window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.add('show');
    document.querySelector('.sidebar-overlay').classList.add('show');
  } else {
    document.getElementById('sidebar').classList.toggle('collapsed');
  }
}
function toggleSidebarColModal(){
  document.getElementById('sidebar').classList.remove('show');
  document.querySelector('.sidebar-overlay').classList.remove('show');
}
function toggleSysMenu(){
  document.getElementById('sys-menu').classList.toggle('show');
}
document.addEventListener('click', function(e) {
  const menu = document.getElementById('sys-menu');
  if(!e.target.closest('.header-right') && menu && menu.classList.contains('show')) {
    menu.classList.remove('show');
  }
});
function openAddInbound(){document.getElementById('addInboundModal').classList.add('show');updateObfsFields()}
function openAddClient(id){
  const user = prompt(_T('add_clt_prompt'));
  if(user) POST('/panel/api/inbounds/addClient',{inbound_id:id,username:user,total_limit:0,expiry_time:0}).then(()=>loadInbounds());
}
async function toggleInbound(id){await POST(`/panel/api/inbounds/toggle/${id}`,{});loadInbounds()}
async function deleteInbound(id){if(!confirm(_T('del_ib_confirm')))return;await POST(`/panel/api/inbounds/del/${id}`,{});loadInbounds()}
function updateObfsFields(){const p=document.getElementById('ib-protocol').value;const c=document.getElementById('obfs-fields');
  const addr = document.getElementById('ib-address');
  if(p==='openvpn_xor'){
    if(addr) addr.value = '10.9.0.1/24';
    c.innerHTML=`
    <div class="fg"><label>${_T('obfs_pw')}</label><input id="obfs-scramble" value=""></div>
    <div class="fg" style="flex-direction:row;align-items:center;gap:10px;margin-top:10px">
      <input type="checkbox" id="obfs-bypass" style="width:20px;height:20px">
      <label style="margin:0">${_T('obfs_bypass')}</label>
    </div>`}
  else{
    if(addr) addr.value = '10.8.0.1/24';
    const v2=p==='amneziawg_v2';
    let html = `
      <div class="modal-section">
        <div class="section-title">${_T('junk_lbl')}</div>
        <div class="grid-3">
          <div class="fg"><label title="Number of junk packets">Jc</label><input id="obfs-Jc" type="number" value="5"></div>
          <div class="fg"><label title="Min junk size">Jmin</label><input id="obfs-Jmin" type="number" value="50"></div>
          <div class="fg"><label title="Max junk size">Jmax</label><input id="obfs-Jmax" type="number" value="1000"></div>
        </div>
      </div>
      
      <div class="modal-section">
        <div class="section-title">${_T('padding_lbl')}</div>
        <div class="grid-4">
          <div class="fg"><label title="Init Padding">S1</label><input id="obfs-S1" type="number" value="69"></div>
          <div class="fg"><label title="Response Padding">S2</label><input id="obfs-S2" type="number" value="115"></div>
          ${v2 ? `
            <div class="fg"><label title="Cookie Padding">S3</label><input id="obfs-S3" type="number" value="69"></div>
            <div class="fg"><label title="Data Padding">S4</label><input id="obfs-S4" type="number" value="69"></div>
          ` : ''}
        </div>
      </div>

      <div class="modal-section">
        <div class="section-title">${_T('headers_lbl')}</div>
        <div class="fr">
          <div class="fg"><label>H1 (Init)</label><input id="obfs-H1" type="text" value="924883749"></div>
          <div class="fg"><label>H2 (Resp)</label><input id="obfs-H2" type="text" value="16843009"></div>
        </div>
        <div class="fr">
          <div class="fg"><label>H3 (Cookie)</label><input id="obfs-H3" type="text" value="305419896"></div>
          <div class="fg"><label>H4 (Data)</label><input id="obfs-H4" type="text" value="878082202"></div>
        </div>
      </div>
    `;
    
    if(v2){
      html += `
      <div class="modal-section">
        <div class="section-title">Сигнатуры (CPS)</div>
        <div class="grid-5">
          <div class="fg"><label>I1</label><input id="obfs-I1" type="text" value="" placeholder="<b 0x..>"></div>
          <div class="fg"><label>I2</label><input id="obfs-I2" type="text" value="" placeholder="<r ..>"></div>
          <div class="fg"><label>I3</label><input id="obfs-I3" type="text" value="" placeholder="<t>"></div>
          <div class="fg"><label>I4</label><input id="obfs-I4" type="text" value="" placeholder=""></div>
          <div class="fg"><label>I5</label><input id="obfs-I5" type="text" value="" placeholder=""></div>
        </div>
      </div>
      `;
    }
    c.innerHTML = html;
  }
}

async function submitInbound(){
  const p=document.getElementById('ib-protocol').value;
  const body={protocol:p,remark:document.getElementById('ib-remark').value,port:document.getElementById('ib-port').value,obfuscation:{},settings:{}};
  const mtu=document.getElementById('ib-mtu');if(mtu&&mtu.value)body.settings.mtu=parseInt(mtu.value);
  const dns=document.getElementById('ib-dns');if(dns&&dns.value)body.settings.dns=dns.value;
  const address=document.getElementById('ib-address');if(address&&address.value)body.settings.address=address.value;
  const sip=document.getElementById('ib-server-ip');if(sip&&sip.value)body.settings.server_ip=sip.value;
  if(p==='openvpn_xor'){
    body.obfuscation={
      scramble_password:document.getElementById('obfs-scramble').value,
      bypass_routes:document.getElementById('obfs-bypass').checked
    }
  }
  else{
    ['Jc','Jmin','Jmax','S1','S2','S3','S4','H1','H2','H3','H4','I1','I2','I3','I4','I5'].forEach(k=>{
      const el=document.getElementById('obfs-'+k);
      if(el && el.value !== "") body.obfuscation[k]=el.value;
    });
  }
  await POST('/panel/api/inbounds/add',body);closeModal('addInboundModal');loadInbounds()}

async function showQR(cid, username, proto){
  const r=await API(`/panel/api/inbounds/clientConfig/${cid}`);if(!r.success)return;
  document.getElementById('qrConfigText').value=r.config;
  const img=document.getElementById('qrImage');
  img.src=''; img.style.display='none';
  const modalBody = img.parentElement.parentElement;
  const existingWarning = document.getElementById('qr-warning');
  if(existingWarning) existingWarning.remove();

  if(r.config.length > 2500) {
    const warn = document.createElement('div');
    warn.id = 'qr-warning';
    warn.style = 'color:#e63946; font-size:12px; margin-bottom:10px; font-weight:bold';
    warn.textContent = 'Конфигурация слишком большая для QR-кода. Пожалуйста, используйте файл (.ovpn)';
    modalBody.insertBefore(warn, img.parentElement);
  } else {
    try{
      QRCode.toDataURL(r.config,{
        width:600,
        margin:2,
        errorCorrectionLevel:'L'
      },(err,url)=>{
        if(!err) { img.src=url; img.style.display='inline-block'; }
        else console.error('QR Error:', err);
      });
    }catch(e){console.error('QR Catch:', e)}
  }
  document.getElementById('downloadBtn').onclick=()=>{
    const blob=new Blob([r.config],{type:'text/plain'});const url=URL.createObjectURL(blob);
    const a=document.createElement('a');a.href=url;a.download=username+(proto.includes('openvpn')?'.ovpn':'.conf');
    document.body.appendChild(a);a.click();document.body.removeChild(a);URL.revokeObjectURL(url)};
  document.getElementById('qrModal').classList.add('show')}

function copyConfig(){const t=document.getElementById('qrConfigText');t.select();document.execCommand('copy')}
async function deleteClient(id){if(!confirm(_T('del_client_confirm')))return;await POST(`/panel/api/inbounds/delClient/${id}`,{});loadAllClients()}

let currentFwIface = 'any';
let fwRulesData = [];
let fwInterfacesData = [];

async function loadFirewall() {
  // First load on clean install: if DB has no rules yet, auto-import from UFW
  const preCheck = await API('/panel/api/firewall');
  if(preCheck.success && (!preCheck.rules || preCheck.rules.length === 0)) {
    await POST('/panel/api/firewall/sync', {});
  }
  const r = await API('/panel/api/firewall');
  if(!r.success) return;
  
  const b = document.getElementById('fw-status-badge');
  if(b) {
    b.textContent = r.active ? _T('fw_active_lbl') : _T('fw_inactive_lbl');
    b.className = 'badge ' + (r.active ? 'badge-on' : 'badge-off');
  }
  
  const tc = document.getElementById('fw-tabs-container');
  if(tc) {
    tc.innerHTML = `<div class="fw-tab ${currentFwIface==='any'?'active':''}" onclick="fwSwitchTab('any')">${_T('all_rules_tab')}</div>`;
    (r.interfaces || []).sort().forEach(iface => {
      tc.innerHTML += `<div class="fw-tab ${currentFwIface===iface?'active':''}" onclick="fwSwitchTab('${iface}')">${iface}</div>`;
    });
  }
  
  const ms = document.getElementById('fw-m-iface');
  if(ms) {
    ms.innerHTML = `<option value="any">${_T('any')}</option>`;
    (r.interfaces || []).sort().forEach(iface => {
      ms.innerHTML += `<option value="${iface}">${iface}</option>`;
    });
  }
  
  fwInterfacesData = r.interfaces || [];

  fwRulesData = r.rules || [];
  renderFwRules();
}

function fwSwitchTab(iface) {
  currentFwIface = iface;
  loadFirewall();
}

async function fwSync() {
  if(!confirm(_T('fw_sync_confirm') || 'Import current rules from system?')) return;
  const r = await POST('/panel/api/firewall/sync');
  if(r.success) {
    loadFirewall();
    alert(_T('fw_sync_done') || 'Импорт завершен!');
  } else {
    alert((_T('error_lbl') || 'Ошибка') + ': ' + r.msg);
  }
}

function renderFwRules() {
  const tbody = document.getElementById('fw-rules-body_2');
  if(!tbody) return;
  tbody.innerHTML = '';
  
  const filtered = currentFwIface === 'any' ? fwRulesData : fwRulesData.filter(x => x.interface === currentFwIface);
  
  if (filtered.length === 0) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td colspan="11" style="padding:40px; text-align:center; color:var(--kg-text-dim); font-size:14px;">
      <div style="margin-bottom:10px;"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:0.3"><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z"></path><path d="M12 8V12"></path><path d="M12 16H12.01"></path></svg></div>
      ${_T('fw_no_rules_p1') || 'No rules for interface'} ${currentFwIface==='any'? _T('any') : currentFwIface}
    </td>`;
    tbody.appendChild(tr);
    return;
  }

  filtered.forEach(rule => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--kg-border)';
    tr.innerHTML = `
      <td style="padding:12px;"><input type="checkbox" ${rule.enabled?'checked':''} onchange="fwFastToggle(${rule.id}, this.checked)"></td>
      <td style="padding:12px;">${rule.priority}</td>
      <td style="padding:12px;"><span class="badge ${rule.action==='allow'?'badge-on':(rule.action==='deny'?'badge-off':'badge-warn')}">${rule.action==='allow'? _T('allow'):(rule.action==='deny'? _T('deny'): _T('reject'))}</span></td>
      <td style="padding:12px;">${rule.protocol.toUpperCase()}</td>
      <td style="padding:12px; color:var(--kg-text-dim);">${rule.interface==='any'? _T('any') : rule.interface}</td>
      <td style="padding:12px;">${rule.src_ip}</td>
      <td style="padding:12px;">${rule.src_port}</td>
      <td style="padding:12px;">${rule.dst_ip}</td>
      <td style="padding:12px;">${rule.dst_port}</td>
      <td style="padding:12px; color:var(--kg-text-dim); font-size:12px;">${rule.comment || '--'}</td>
      <td style="padding:12px; text-align:right; white-space:nowrap;">
         <button class="btn btn-o btn-sm" onclick="fwOpenModal(${rule.id})" title="Редактировать">
           <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
         </button>
         <button class="btn btn-d btn-sm" onclick="fwDelete(${rule.id})" title="Удалить">
           <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
         </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

async function fwFastToggle(id, enabled) {
  const rule = fwRulesData.find(x => x.id === id);
  if(!rule) return;
  const data = {...rule, enabled: enabled ? 1 : 0};
  const r = await POST('/panel/api/firewall/save', data);
  if(r.success) {
      // Auto-apply on toggle
      await POST('/panel/api/firewall/apply', {});
  }
}

function fwOnCustomChange(sel, inputId) {
  const inp = document.getElementById(inputId);
  if(sel.value === 'custom') {
    inp.style.display = 'block';
    inp.focus();
  } else {
    inp.style.display = 'none';
    inp.value = '';
  }
}

function fwSetSelect(id, val, inputId) {
  const sel = document.getElementById(id);
  const inp = document.getElementById(inputId);
  if (!sel) return;
  
  if (val === 'any') {
    sel.value = 'any';
    if(inp) { inp.style.display = 'none'; inp.value = ''; }
  } else {
    sel.value = 'custom';
    if(inp) {
      inp.style.display = 'block';
      inp.value = val;
    }
  }
}

function fwOpenModal(id = null) {
  const m = document.getElementById('modal-fw');
  m.style.display = 'flex';
  
  // Clear interfaces list and re-populate
  const ifaceSel = document.getElementById('fw-m-iface');
  ifaceSel.innerHTML = '<option value="any">' + _T('any') + '</option>';
  fwInterfacesData.forEach(iface => {
    const opt = document.createElement('option');
    opt.value = iface;
    opt.text = iface;
    ifaceSel.add(opt);
  });

  if(id) {
    const r = fwRulesData.find(x => x.id === id);
    document.getElementById('fw-m-id').value = r.id;
    document.getElementById('fw-m-enabled').checked = !!r.enabled;
    document.getElementById('fw-m-name').value = r.comment;
    document.getElementById('fw-m-action').value = r.action;
    document.getElementById('fw-m-iface').value = r.interface;
    
    fwSetSelect('fw-m-srcip-sel', r.src_ip, 'fw-m-srcip-val');
    fwSetSelect('fw-m-dstip-sel', r.dst_ip, 'fw-m-dstip-val');
    fwSetSelect('fw-m-srcport-sel', r.src_port, 'fw-m-srcport-val');
    fwSetSelect('fw-m-dstport-sel', r.dst_port, 'fw-m-dstport-val');
    
    document.getElementById('fw-m-proto').value = r.protocol;
    document.getElementById('fw-m-prio').value = String(r.priority);
  } else {
    document.getElementById('fw-m-id').value = '';
    document.getElementById('fw-m-enabled').checked = true;
    document.getElementById('fw-m-name').value = '';
    document.getElementById('fw-m-action').value = 'allow';
    document.getElementById('fw-m-iface').value = currentFwIface === 'any' ? 'any' : currentFwIface;
    
    fwSetSelect('fw-m-srcip-sel', 'any', 'fw-m-srcip-val');
    fwSetSelect('fw-m-dstip-sel', 'any', 'fw-m-dstip-val');
    fwSetSelect('fw-m-srcport-sel', 'any', 'fw-m-srcport-val');
    fwSetSelect('fw-m-dstport-sel', 'any', 'fw-m-dstport-val');
    
    document.getElementById('fw-m-proto').value = 'tcp';
    document.getElementById('fw-m-prio').value = '100';
  }
}

async function fwSaveModal() {
  const getVal = (selId, inpId) => {
    const sel = document.getElementById(selId);
    return sel.value === 'custom' ? document.getElementById(inpId).value : 'any';
  };

  const data = {
    id: document.getElementById('fw-m-id').value || null,
    enabled: document.getElementById('fw-m-enabled').checked ? 1 : 0,
    comment: document.getElementById('fw-m-name').value,
    action: document.getElementById('fw-m-action').value,
    interface: document.getElementById('fw-m-iface').value,
    src_ip: getVal('fw-m-srcip-sel', 'fw-m-srcip-val'),
    dst_ip: getVal('fw-m-dstip-sel', 'fw-m-dstip-val'),
    src_port: getVal('fw-m-srcport-sel', 'fw-m-srcport-val'),
    dst_port: getVal('fw-m-dstport-sel', 'fw-m-dstport-val'),
    protocol: document.getElementById('fw-m-proto').value,
    priority: parseInt(document.getElementById('fw-m-prio').value)
  };
  const r = await POST('/panel/api/firewall/save', data);
  if(r.success) {
    document.getElementById('modal-fw').style.display = 'none';
    // Automatically apply to system
    await POST('/panel/api/firewall/apply', {}); 
    loadFirewall();
  }
}

async function fwDelete(id) {
  if(!confirm(_T('fw_del_confirm') || 'Удалить правило?')) return;
  const r = await POST('/panel/api/firewall/delete', {id});
  if(r.success) {
      await POST('/panel/api/firewall/apply', {});
      loadFirewall();
  }
}

async function fwApply() {
  if(!confirm(_T('fw_apply_confirm') || 'Применить все настройки в систему?')) return;
  const r = await POST('/panel/api/firewall/apply', {});
  alert(r.msg);
  loadFirewall();
}

async function fwToggle(en) {
  await POST('/panel/api/firewall/toggle', {enable: en});
  loadFirewall();
}

async function saveNTP() {
  const s = document.getElementById('sys-ntp').value;
  const r = await POST('/panel/api/system/ntp', {servers: s});
  alert(r.msg);
}

async function checkUpdate() {
  const info = document.getElementById('update-info');
  const btn = document.getElementById('btn-apply-update');
  info.innerHTML = "Проверка...";
  try {
    const d = await API('/panel/api/system/update/check');
    if (d.success) {
      document.getElementById('current-hash').innerText = d.current_hash;
      document.getElementById('remote-hash').innerText = d.remote_hash;
      if (d.needs_update) {
        info.innerHTML = `<span style="color:var(--kg-green)">Найдено ${d.behind_count} новых изменений на GitHub!</span>`;
        btn.style.display = 'block';
      } else {
        info.innerHTML = "У вас установлена последняя версия.";
        btn.style.display = 'none';
      }
    } else {
      info.innerHTML = `<span style="color:var(--kg-red)">Ошибка: ${d.msg}</span>`;
    }
  } catch(e) { info.innerHTML = `<span style="color:var(--kg-red)">Ошибка сети</span>`; }
}

async function applyUpdate() {
  if (!confirm("Вы уверены, что хотите обновить панель? Сервис будет перезагружен.")) return;
  const info = document.getElementById('update-info');
  info.innerHTML = "Обновление...";
  try {
    const d = await POST('/panel/api/system/update/apply', {});
    if (d.success) {
      alert(d.msg);
      setTimeout(() => window.location.reload(), 5000);
    } else {
      alert(d.msg || "Ошибка обновления");
    }
  } catch(e) { alert(e.message); }
}

async function loadSystem(){
  const h_el = document.getElementById('sys-hostname');
  if(h_el) {
    const h=await API('/panel/api/system/hostname');
    h_el.value=h.hostname||'';
  }
  
  const tz_el = document.getElementById('sys-tz');
  if(tz_el) {
    const tz=await API('/panel/api/system/timezone');
    if(tz && tz.timezone){
      let found=false;
      for(let o of tz_el.options){if(o.value===tz.timezone){o.selected=true;found=true;break;}}
      if(!found){const opt=document.createElement('option');opt.value=tz.timezone;opt.text=tz.timezone;opt.selected=true;tz_el.add(opt);}
    }
  }

  const ntp_el = document.getElementById('sys-ntp');
  if(ntp_el) {
    const ntp=await API('/panel/api/system/ntp');
    if(ntp && ntp.servers) ntp_el.value = ntp.servers;
  }
  
  const st=await API('/panel/api/server/status');
  if(st && st.panel_port){
    const http_input = document.getElementById('new-panel-port');
    const https_input = document.getElementById('new-panel-port-https');
    if(http_input) http_input.value = st.panel_port;
    if(https_input) https_input.value = st.panel_port_https || (st.panel_port + 1);
  }
  checkFail2Ban();
  checkSSLStatus();
}
async function saveHostname(){const r=await POST('/panel/api/system/hostname',{hostname:document.getElementById('sys-hostname').value});alert(r.success?'Сохранено':'Ошибка')}
async function saveTimezone(){const r=await POST('/panel/api/system/timezone',{timezone:document.getElementById('sys-tz').value});alert(r.success?'Часовой пояс обновлён':'Ошибка')}

// Live Server Clock
async function updateServerClock(){
  const r=await API('/panel/api/system/time');
  const el=document.getElementById('server-clock');
  if(el && r.time) el.textContent=r.time+' ('+r.timezone+')';
}
setInterval(updateServerClock, 1000);
updateServerClock();

// Credentials
async function changeCredentials(){
  const login=document.getElementById('new-login').value.trim();
  const pass=document.getElementById('new-password').value;
  const conf=document.getElementById('confirm-password').value;
  if(!login||!pass)return alert('Заполните все поля');
  if(pass!==conf)return alert('Пароли не совпадают');
  if(pass.length<6)return alert('Пароль минимум 6 символов');
  if(!confirm('Сменить данные входа? Вы будете выйдены из системы.'))return;
  const r=await POST('/panel/api/system/change-credentials',{login,password:pass});
  alert(r.msg);
  if(r.success)setTimeout(()=>window.location.href='/login',1000);
}

// Panel Port Change
async function changePanelPort(){
  const p=parseInt(document.getElementById('new-panel-port').value);
  const p_https=parseInt(document.getElementById('new-panel-port-https').value);
  if(!p||!p_https||p<1024||p>65535||p_https<1024||p_https>65535)return alert('Оба порта должны быть от 1024 до 65535');
  if(p===p_https)return alert('Порты HTTP и HTTPS должны различаться');
  if(!confirm(`Новые порты:\nHTTP: ${p}\nHTTPS: ${p_https}\n\nПанель перезапустится. Применить?`))return;
  const r=await POST('/panel/api/system/change-port', {port: p, port_https: p_https});
  alert(r.msg);
  if(r.success){
    setTimeout(()=>{
      const host=window.location.hostname;
      const is_secure = window.location.protocol === 'https:';
      window.location.href = is_secure ? `https://${host}:${r.new_port_https}` : `http://${host}:${r.new_port}`;
    }, 3000);
  }
}

// Fail2Ban
async function installFail2Ban(){if(!confirm(_T('f2b_confirm')))return;const r=await POST('/panel/api/system/install-fail2ban',{});alert(r.msg)}
async function checkFail2Ban(){
  const r=await API('/panel/api/system/fail2ban-status');
  const el=document.getElementById('f2b-status');
  if(el){el.textContent=r.installed? _T('f2b_installed_active') : _T('f2b_not_installed');el.className='badge '+(r.installed?'badge-on':'badge-off');}
}

// SSL
async function applySSL(){
  const mode=document.getElementById('ssl-mode').value;
  const domain=document.getElementById('ssl-domain').value.trim();
  if(mode==='letsencrypt'&&!domain)return alert(_T('ssl_domain_err'));
  // Small hint: Let's Encrypt doesn't work with bare IPs
  if(mode==='letsencrypt' && /^(\d{1,3}\.){3}\d{1,3}$/.test(domain)){
      return alert(_T('ssl_ip_err'));
  }
  const r=await POST('/panel/api/system/set-ssl',{mode,domain});
  alert(r.msg);
  checkSSLStatus();
}

async function restartPanel(){
  if(!confirm(_T('restart_confirm'))) return;
  const r=await POST('/panel/api/system/restart',{});
  alert(r.msg);
  setTimeout(()=>window.location.reload(), 3000);
}

// Telegram
async function saveTelegramSettings(){
  const token=document.getElementById('tg-token').value.trim();
  const ids=document.getElementById('tg-allowed-ids').value.trim();
  if(!token)return alert(_T('tg_token_lbl'));
  const r=await POST('/panel/api/settings',{telegram_bot_token:token,telegram_allowed_ids:ids});
  alert(r.success? _T('tg_save_success') : _T('error_lbl'));
}

async function loadLogs(){const unit=document.getElementById('log-unit').value;
  const r=await API(`/panel/api/system/logs?lines=100&unit=${unit}`);
  document.getElementById('log-output').textContent=r.logs|| _T('no_logs')}

async function issueSSL(){const d=document.getElementById('ssl-domain').value;if(!d)return alert('Укажите домен');const r=await POST('/panel/api/system/set-ssl',{mode:'letsencrypt',domain:d});alert(r.msg)}

async function checkSSLStatus(){
  const r = await API('/panel/api/system/ssl-status');
  const st = await API('/panel/api/server/status');
  if(!r || !st) return;
  const dSslStatus = document.getElementById('d-ssl-status');
  const badge = document.getElementById('ssl-badge');
  const certState = document.getElementById('ssl-cert-state');
  const restartWarn = document.getElementById('ssl-restart-warn');
  const activeInfo = document.getElementById('ssl-active-info');
  
  if(badge) {
      badge.textContent = r.mode === 'off' ? _T('status_disabled') : r.mode.toUpperCase();
      badge.className = 'badge ' + (r.mode === 'off' ? 'badge-off' : 'badge-on');
  }
  
  if(dSslStatus) {
      dSslStatus.textContent = r.active ? _T('active_lbl') : (r.mode==='off'? _T('off_lbl') : _T('waiting_lbl'));
      dSslStatus.style.color = r.active ? 'var(--kg-green)' : (r.mode==='off'?'var(--kg-text-dim)':'#f59e0b');
  }
  
  if(certState) certState.textContent = r.cert_path ? _T('ssl_cert_found') : _T('ssl_cert_not_found');
  
  if(restartWarn && activeInfo) {
      if (r.mode !== 'off' && !r.active) {
          restartWarn.style.display = 'block';
          restartWarn.innerHTML = _T('ssl_restart_needed') + st.panel_port_https + ')';
          activeInfo.style.display = 'none';
      } else if (r.active) {
          restartWarn.style.display = 'none';
          activeInfo.style.display = 'block';
          activeInfo.innerHTML = `✅ HTTPS активен на порту ${st.panel_port_https}. Используйте https://[IP-или-Домен]:${st.panel_port_https}`;
      } else {
          restartWarn.style.display = 'none';
          activeInfo.style.display = 'none';
      }
  }
}

// Backup & Restore
async function downloadBackup(){
  window.location.href='/panel/api/system/backup';
}
async function uploadRestore(input){
  if(!input.files[0]) return;
  if(!confirm('Восстановить систему из этого файла? Панель перезапустится.')) return;
  const fd = new FormData();
  fd.append('file', input.files[0]);
  const r = await fetch('/panel/api/system/restore', {
    method: 'POST',
    body: fd
  }).then(res => res.json());
  alert(r.msg);
  if(r.success) setTimeout(() => window.location.reload(), 3000);
}


loadDashboard();setInterval(loadDashboard,15000);
document.addEventListener('DOMContentLoaded', () => {
    const s1 = document.getElementById('sortable-dashboard');
    if(s1) new Sortable(s1, { animation: 150, handle: '.card-header', ghostClass: 'sortable-ghost',
        store: { get: (s) => (localStorage.getItem('sort_d1')?localStorage.getItem('sort_d1').split('|'):[]), set: (s) => localStorage.setItem('sort_d1', s.toArray().join('|')) }
    });
    const s2 = document.getElementById('sortable-dashboard-bottom');
    if(s2) new Sortable(s2, { animation: 150, handle: '.card-header', ghostClass: 'sortable-ghost',
        store: { get: (s) => (localStorage.getItem('sort_d2')?localStorage.getItem('sort_d2').split('|'):[]), set: (s) => localStorage.setItem('sort_d2', s.toArray().join('|')) }
    });
});
</script>
</body></html>"""
