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
.login-card { background: var(--card); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 24px; padding: 50px; width: 100%; max-width: 420px; box-shadow: 0 25px 50px rgba(0,0,0,0.3); text-align: center; }
.logo { font-size: 28px; font-weight: 900; color: var(--blue); letter-spacing: 3px; margin-bottom: 40px; }
.fg { margin-bottom: 20px; text-align: left; }
.fg label { display: block; font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
.fg input { width: 100%; background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 12px; padding: 14px 18px; color: #fff; font-size: 15px; outline: none; transition: 0.2s; }
.fg input:focus { border-color: var(--blue); box-shadow: 0 0 0 4px rgba(0, 168, 232, 0.1); }
.btn { width: 100%; background: var(--blue); color: #fff; padding: 14px; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s; margin-top: 20px; }
.btn:hover { transform: translateY(-1px); opacity: 0.9; }
.error { color: #f43f5e; background: rgba(244, 63, 94, 0.1); padding: 10px; border-radius: 8px; font-size: 14px; margin-bottom: 20px; }
</style></head><body>
<div class="login-card">
  <div class="logo">SKY-NET</div>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <form method="POST">
    <div class="fg"><label>Имя пользователя</label><input name="username" required></div>
    <div class="fg"><label>Пароль</label><input name="password" type="password" required></div>
    <button class="btn" type="submit">ВОЙТИ В ПАНЕЛЬ</button>
  </form>
</div>
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

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--kg-bg); color: var(--kg-text); min-height: 100vh; line-height: 1.5; overflow-x: hidden; }

/* Sidebar */
.sidebar { width: 260px; background: var(--kg-sidebar); border-right: 1px solid var(--kg-border); display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100; backdrop-filter: blur(20px); transition: transform 0.3s ease; }
.sidebar .logo { padding: 35px 30px; color: var(--kg-blue); font-weight: 900; font-size: 22px; text-transform: uppercase; letter-spacing: 2px; }
.sidebar nav { flex: 1; padding: 10px 0; overflow-y: auto; }
.sidebar nav a { display: flex; align-items: center; gap: 15px; padding: 14px 30px; color: var(--kg-text-dim); text-decoration: none; font-size: 14px; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
.sidebar nav a:hover { color: #fff; background: rgba(255,255,255,0.03); }
.sidebar nav a.active { color: #fff; border-left-color: var(--kg-blue); background: rgba(0,168,232,0.1); font-weight: 600; }
.sidebar nav .section { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.2); padding: 30px 30px 10px; font-weight: 800; letter-spacing: 1.5px; }

/* Mobile Overlay */
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.show { transform: translateX(0); box-shadow: 20px 0 60px rgba(0,0,0,0.5); }
  .sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 95; backdrop-filter: blur(4px); }
  .sidebar-overlay.show { display: block; }
}

/* Header */
.main { margin-left: 260px; flex: 1; display: flex; flex-direction: column; min-width: 0; transition: margin 0.3s; }
@media (max-width: 768px) { .main { margin-left: 0; } }

.header { height: 60px; background: var(--kg-sidebar); border-bottom: 1px solid var(--kg-border); display: flex; align-items: center; justify-content: space-between; padding: 0 30px; position: sticky; top: 0; z-index: 90; }
.header h1 { font-size: 18px; font-weight: 600; color: #fff; display:none; }
.header-right { display: flex; align-items: center; gap: 20px; margin-left: auto; }
.user-info { font-size: 13px; color: var(--kg-text-dim); display: flex; align-items: center; gap: 8px; }
.user-info strong { color: #fff; }
.logout-btn { background: rgba(255, 82, 82, 0.1); color: var(--kg-red); text-decoration: none; font-size: 12px; font-weight: 600; padding: 6px 14px; border-radius: 6px; transition: 0.2s; }
.logout-btn:hover { background: rgba(255, 82, 82, 0.2); }

.hamburger { display: none; cursor: pointer; padding: 10px; color: #fff; margin-right: 15px; }
@media (max-width: 768px) { .hamburger { display: block; } .header { padding: 0 15px; } }
.hamburger div { width: 22px; height: 2px; background: currentColor; margin: 4px 0; border-radius: 2px; }

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

/* Dashboard Keenetic Styles */
.k-conn-block { padding: 20px 25px 0 25px; display: flex; align-items: flex-start; justify-content: space-between; }
.k-conn-left { display: flex; gap: 15px; }
.k-toggle { width: 34px; height: 20px; background: var(--kg-blue); border-radius: 10px; position: relative; cursor: pointer; margin-top: 2px; }
.k-toggle::after { content: ''; position: absolute; width: 16px; height: 16px; background: #fff; border-radius: 50%; top: 2px; right: 2px; }
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
.stat-item { display: flex; justify-content: space-between; align-items: center; padding: 15px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.stat-item:last-child { border-bottom: none; }
.stat-label { font-size: 14px; color: var(--kg-text-dim); font-weight: 500; }
.stat-val { font-size: 15px; font-weight: 700; color: #fff; font-family: 'JetBrains Mono', monospace; }

.stat-circles { display: flex; justify-content: space-around; margin-top: 20px; gap: 20px; }
.circle-stat { text-align: center; }
.circle-val { font-size: 26px; font-weight: 800; color: var(--kg-blue); }
.circle-label { font-size: 11px; color: var(--kg-text-dim); text-transform: uppercase; font-weight: 800; margin-top: 5px; letter-spacing: 1px; }

.chart-container-wrapper { padding: 15px 25px 0 25px; }
.chart-container { height: 160px; width: 100%; border-bottom: 1px solid var(--kg-border); border-top: 1px dotted rgba(255,255,255,0.1); position: relative; margin-top: 10px; }
.chart-legend { display: flex; align-items: center; justify-content: space-between; padding: 10px 0 0 0; font-size: 11px; color: var(--kg-text-dim); }
.legend-center { display: flex; gap: 15px; }
.legend-item { display: flex; align-items: center; gap: 5px; }
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

<div class="sidebar">
  <div class="logo">SKY-NET</div>
  <nav>
    <div class="section">Статус</div>
    <a href="#" data-page="dashboard" class="active">Системный монитор</a>
    <div class="section">Интернет</div>
    <a href="#" data-page="inbounds">VPN серверы</a>
    <a href="#" data-page="clients">Подключенные клиенты</a>
    <div class="section">Сетевые правила</div>
    <a href="#" data-page="firewall">Межсетевой экран</a>
    <div class="section">Управление</div>
    <a href="#" data-page="system">Настройки системы</a>
    <a href="#" data-page="logs">Журнал событий</a>
    <a href="#" data-page="settings">Параметры панели</a>
  </nav>
</div>

<div class="main">
    <div class="header">
      <div style="display:flex; align-items:center;">
        <div class="hamburger" onclick="toggleSidebar()">
          <div></div><div></div><div></div>
        </div>
        <h1 id="page-title-text" style="display:none">Системный монитор</h1>
      </div>
      <div class="header-right" style="display:flex; align-items:center; gap: 15px;">
        <svg fill="none" stroke="currentColor" stroke-width="2" width="22" height="22" viewBox="0 0 24 24" style="color:var(--kg-blue); cursor:pointer;" onclick="openWidgetSettings()"><path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
        <div class="user-info hide-mobile">
          <span style="opacity:0.5">Пользователь:</span>
          <strong>{{ session.get('username') }}</strong>
        </div>
        <a href="/logout" class="logout-btn">Выход</a>
      </div>
    </div>
  <div class="sidebar-overlay" onclick="toggleSidebar()"></div>
  <div class="content">

<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
  
  <div class="grid" id="sortable-dashboard">
    <!-- Dynamic Interface Blocks -->
    <div id="dynamic-interfaces-container" style="display:contents"></div>
    
    <!-- BLOCK 2: О СИСТЕМЕ -->
    <div class="card" id="block-system">
      <div class="card-header">
        <h3 style="margin:0">О СИСТЕМЕ</h3>
        <svg fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" viewBox="0 0 24 24" style="color:var(--kg-text-dim);"><path d="M4 8h16M4 16h16"></path></svg>
      </div>
      
      <div class="k-grid" style="grid-template-columns: 1fr 1fr;">
        <div class="k-kv"><span class="k-lbl">Имя устройства</span><span class="k-val" id="d-host">--</span></div>
        <div class="k-kv"><span class="k-lbl">Версия системы</span><span class="k-val" id="d-os">--</span></div>
        <div class="k-kv"><span class="k-lbl">Время работы</span><span class="k-val" id="uptime-val">--</span></div>
      </div>
      
      <div style="padding: 20px 25px; border-top: 1px solid var(--kg-border); display:flex; justify-content:space-around; align-items:center;">
        <div style="text-align:center"><div style="font-size:18px; font-weight:700; color:var(--kg-blue)" id="cpu-val">0%</div><div class="k-lbl">CPU</div></div>
        <div style="text-align:center"><div style="font-size:18px; font-weight:700; color:var(--kg-blue)" id="ram-val">0%</div><div class="k-lbl">RAM</div></div>
        <div style="text-align:center"><div style="font-size:18px; font-weight:700; color:var(--kg-blue)" id="disk-val">0%</div><div class="k-lbl">ДИСК</div></div>
      </div>
    </div>
    
  </div> <!-- end grid -->

  <div class="grid" style="margin-top:25px;" id="sortable-dashboard-bottom">
    <!-- BLOCK 3: АКТИВНЫЕ СЕССИИ И ТРАФИК -->
    <div class="card" style="grid-column: span 12;" id="block-clients">
      <div class="card-header">
        <svg fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" viewBox="0 0 24 24" style="color:var(--kg-text-dim); margin-right:4px;"><path d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
        <h3>АКТИВНЫЕ СЕССИИ И ТРАФИК</h3>
      </div>
      <div class="table-container" style="padding: 0 25px 25px 25px;">
        <table>
          <thead>
            <tr>
              <th>Пользователь</th>
              <th>Протокол</th>
              <th>Трафик (↑/↓)</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody id="dash-clients-table">
            <!-- Active clients will be rendered here -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- BLOCK 4: СЕТЕВЫЕ ИНТЕРФЕЙСЫ -->
    <div class="card" id="block-interfaces" style="display:none;">
      <div class="card-header"><h3>СЕТЕВЫЕ ИНТЕРФЕЙСЫ</h3></div>
      <div id="net-ifaces" class="card-padd"></div>
    </div>
  </div> <!-- end grid -->
</div>

<!-- INBOUNDS -->
<div class="page" id="page-inbounds">
  <div class="card no-blue">
    <div class="card-header"><h3>VPN ПОДКЛЮЧЕНИЯ</h3><button class="btn btn-p" onclick="openAddInbound()">Добавить подключение</button></div>
    <div id="inbounds-list">
      <!-- Inbounds will be rendered as horizontal rows here -->
    </div>
  </div>
</div>

<!-- CLIENTS -->
<div class="page" id="page-clients">
  <div class="card no-blue">
    <div class="card-header" style="justify-content: space-between;">
      <h3>ПОДКЛЮЧЕННЫЕ КЛИЕНТЫ</h3>
      <div class="fg" style="margin:0"><input id="clientSearch" placeholder="Поиск клиентов..." style="width: 250px;"></div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Клиент</th>
            <th>Сервер</th>
            <th>IP адрес</th>
            <th>Трафик (↑/↓)</th>
            <th>Лимит</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody id="clients-table"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- FIREWALL -->
<div class="page" id="page-firewall">
  <div class="card">
    <div class="card-header" style="justify-content: space-between;">
      <h3>МЕЖСЕТЕВОЙ ЭКРАН (UFW)</h3>
      <div style="display:flex; gap:10px; align-items:center">
        <span id="fw-status" class="badge">--</span>
        <button class="btn btn-o btn-sm" onclick="fwToggle(true)">Включить</button>
        <button class="btn btn-d btn-sm" onclick="fwToggle(false)">Выключить</button>
      </div>
    </div>
    <div id="fw-rules"></div>
  </div>
  
  <div class="card">
    <div class="card-header"><h3>ДОБАВИТЬ ПРАВИЛО</h3></div>
    <div class="fr">
      <div class="fg"><label>Порт</label><input id="fw-port" placeholder="например, 22"></div>
      <div class="fg"><label>Протокол</label><select id="fw-proto"><option value="">Любой</option><option value="tcp">TCP</option><option value="udp">UDP</option></select></div>
    </div>
    <div class="fr">
      <div class="fg"><label>Действие</label><select id="fw-action"><option value="allow">Разрешить</option><option value="deny">Запретить</option></select></div>
      <div class="fg"><label>Источник IP (опционально)</label><input id="fw-from" placeholder="any"></div>
    </div>
    <button class="btn btn-p" onclick="fwAddRule()">Добавить правило</button>
  </div>
</div>

<!-- SYSTEM -->
<div class="page" id="page-system">
  <div class="card no-blue">
    <div class="card-header"><h3>УПРАВЛЕНИЕ СИСТЕМОЙ</h3></div>
    <div class="stat-item"><span class="stat-label">Сервис Sky-Net</span><button class="btn btn-o btn-sm" onclick="setupService()">Настроить Автозапуск</button></div>
    <div class="stat-item"><span class="stat-label">Защита Fail2Ban</span><button class="btn btn-o btn-sm" onclick="installFail2Ban()">Установить защиту</button></div>
    <div class="stat-item"><span class="stat-label">SSL Сертификат</span>
      <div style="display:flex;gap:10px"><div class="fg" style="margin:0"><input id="ssl-domain" placeholder="vpn.example.com" style="width:200px"></div><button class="btn btn-o btn-sm" onclick="issueSSL()">Выпустить</button></div>
    </div>
  </div>
  <div class="fr">
    <div class="card"><div class="card-header"><h3>ИМЯ УСТРОЙСТВА</h3></div><div class="fg"><input id="sys-hostname"></div><button class="btn btn-p btn-sm" onclick="saveHostname()">Сохранить</button></div>
    <div class="card"><div class="card-header"><h3>ЧАСОВОЙ ПОЯС</h3></div><div class="fg"><input id="sys-tz"></div><button class="btn btn-p btn-sm" onclick="saveTimezone()">Сохранить</button></div>
  </div>
</div>

<!-- LOGS -->
<div class="page" id="page-logs">
  <div class="card no-blue">
    <div class="card-header"><h3>ЖУРНАЛ СОБЫТИЙ</h3>
      <div style="display:flex;gap:10px">
        <input id="log-unit" placeholder="Юнит (напр. skynet)" style="width:150px">
        <button class="btn btn-p btn-sm" onclick="loadLogs()">Обновить</button>
      </div>
    </div>
    <div class="log-box" id="log-output">Загрузка...</div>
  </div>
</div>

<!-- SETTINGS -->
<div class="page" id="page-settings">
  <div class="card no-blue">
    <div class="card-header"><h3>ПАРАМЕТРЫ ПАНЕЛИ</h3></div>
    <div class="fr">
      <div class="fg"><label>Порт панели</label><input id="s-port" type="number"></div>
      <div class="fg"><label>Базовый путь</label><input id="s-basepath" placeholder="/panel"></div>
    </div>
    <button class="btn btn-p" onclick="saveSettings()">Сохранить изменения</button>
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
      <button class="btn btn-o" onclick="resetWidgets()">Сброс</button>
      <button class="btn btn-p" onclick="closeModal('widgetSettingsModal')">Готово</button>
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
      <button class="btn btn-o" onclick="copyConfig()">Копировать</button>
      <button class="btn btn-s" id="downloadBtn">Скачать .conf</button>
      <button class="btn btn-o" onclick="closeModal('qrModal')">Закрыть</button>
    </div>
  </div>
</div>

<script>
const API=p=>fetch(p).then(r=>r.json());
const POST=(p,b)=>fetch(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(r=>r.json());
function fmtB(b){if(!b||b===0)return'0 B';const k=1024,s=['B','KB','MB','GB','TB'];const i=Math.floor(Math.log(b)/Math.log(k));return(b/Math.pow(k,i)).toFixed(1)+' '+s[i]}
function fmtUp(s){const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d+'d '+h+'h '+m+'m'}
function fmtDate(ts){if(!ts||ts===0)return'Никогда';return new Date(ts*1000).toLocaleDateString()}
function closeModal(id){document.getElementById(id).classList.remove('show')}

// Theme
function toggleTheme(){const t=document.documentElement.getAttribute('data-theme')==='light'?'':'light';
document.documentElement.setAttribute('data-theme',t);localStorage.setItem('theme',t)}
(function(){const t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t)})();

// Nav
document.querySelectorAll('.sidebar nav a').forEach(a=>{
  a.addEventListener('click',e=>{e.preventDefault();
    document.querySelectorAll('.sidebar nav a').forEach(x=>x.classList.remove('active'));a.classList.add('active');
    document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
    document.getElementById('page-'+a.dataset.page).classList.add('active');
    const fn={dashboard:loadDashboard,inbounds:loadInbounds,clients:loadAllClients,
      firewall:loadFirewall,system:loadSystem,logs:loadLogs,settings:loadSettings}[a.dataset.page];
    if(fn)fn()})});
const initPage='{{page}}';if(initPage){document.querySelectorAll('.sidebar nav a').forEach(a=>{if(a.dataset.page===initPage)a.click()})}

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
    cont.innerHTML += `<div class="widget-card">
      <div class="widget-card-title">${title}</div>
      <div class="widget-card-toggle" onclick="toggleWidgetSettings('${id}')">
        <div class="w-tgl ${hidden?'':'on'}"></div>
        <div class="w-lbl">Показать плитку</div>
      </div>
    </div>`;
  });
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
  const newName = prompt('Введите новое имя для ' + iface + ':', current);
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
  const [st_res, net_res, hist_res] = await Promise.all([
    API('/server/status'), API('/panel/api/system/network'), API('/panel/api/trafficHistory')
  ]);
  const st = st_res; const net = net_res; const hist = hist_res;
  
  const d_ip=document.getElementById('d-ip'), d_host=document.getElementById('d-host'), d_os=document.getElementById('d-os');
  if(d_host) d_host.textContent = st.hostname || 'Sky-Net';
  if(d_os) d_os.textContent = st.os_version || 'Ubuntu';
  
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
            <h3 style="margin:0; text-transform:uppercase;">ИНТЕРНЕТ (${i.name})</h3>
            <svg fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" viewBox="0 0 24 24" style="color:var(--kg-text-dim);"><path d="M4 8h16M4 16h16"></path></svg>
          </div>
          <div class="k-conn-block">
            <div class="k-conn-left">
              <div class="k-toggle ${i.is_up?'on':''}" id="tgl-${i.name}"></div>
              <div>
                <div class="k-conn-title" onclick="renameInterface('${i.name}')" style="cursor:pointer; border-bottom:1px dashed rgba(255,255,255,0.3); display:inline-block; padding-bottom:1px;" title="Нажмите, чтобы переименовать" id="title-${i.name}">${savedName}</div>
                <div class="k-conn-subtitle">${i.name}</div>
                <div class="k-badge">
                  <div class="dot ${i.is_up?'dot-green':'dot-blue'}" style="width:5px;height:5px;" id="updot-${i.name}"></div>
                  <span style="margin-left:5px" id="upbadge-${i.name}">${i.is_up?'ПОДКЛЮЧЕНО '+fmtUp(st.uptime||0):'ОТКЛЮЧЕНО'}</span>
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

  const cv = document.getElementById('cpu-val'); if(cv) cv.textContent=st.cpu+'%';
  const rv = document.getElementById('ram-val'); if(rv) rv.textContent=Math.round(st.mem_percent)+'%';
  const dv = document.getElementById('disk-val'); if(dv) dv.textContent=Math.round(st.disk_percent||0)+'%';
  const uv = document.getElementById('uptime-val'); if(uv) uv.textContent=fmtUp(st.uptime||0);
  
  const ib=await API('/panel/api/inbounds/list');
  if(ib.success){
    let tu=0,td=0;
    const clt=document.getElementById('dash-clients-table'); if(clt) clt.innerHTML='';
    ib.obj.forEach(i=>{
      (i.clients||[]).forEach(c=>{
        tu+=c.up||0; td+=c.down||0;
        if(clt){
          const nowS = Math.floor(Date.now()/1000);
          const isActive = (nowS - (c.last_online||0)) < 180;
          clt.innerHTML += `<tr><td><b>${c.username}</b></td><td><span class="badge badge-proto" style="font-size:10px">${PL[i.protocol]}</span></td><td>${fmtB(c.up)} / ${fmtB(c.down)}</td><td><span class="badge ${isActive?'badge-on':'badge-off'}">${isActive?'Активен':'Оффлайн'}</span></td></tr>`;
        }
      })
    });
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
          <p>${PL[ib.protocol]} • Порт: ${ib.port} • Клиентов: ${(ib.clients||[]).length}</p>
        </div>
      </div>
      <div class="ib-actions">
        <span class="badge ${ib.enable?'badge-on':'badge-off'}">${ib.enable?'Работает':'Пауза'}</span>
        <button class="btn btn-o btn-sm" onclick="toggleInbound(${ib.id})">${ib.enable?'Выключить':'Включить'}</button>
        <button class="btn btn-p btn-sm" onclick="openAddClient(${ib.id})">+ Клиент</button>
        <button class="btn btn-d btn-sm" onclick="deleteInbound(${ib.id})">Удалить</button>
      </div>
    </div>`
  })}

async function loadAllClients(){
  const r=await API('/panel/api/inbounds/list');if(!r.success)return;
  const tb=document.getElementById('clients-table');tb.innerHTML='';
  r.obj.forEach(ib=>{(ib.clients||[]).forEach(c=>{
    tb.innerHTML+=`<tr>
      <td><b>${c.username}</b></td>
      <td><span class="badge badge-proto">${PL[ib.protocol]}</span></td>
      <td><code>${c.allowed_ips}</code></td>
      <td>${fmtB(c.up)} / ${fmtB(c.down)}</td>
      <td>${c.total_limit?fmtB(c.total_limit):'Без лимита'}</td>
      <td><span class="badge ${c.enable?'badge-on':'badge-off'}">${c.enable?'Вкл':'Выкл'}</span></td>
      <td>
        <button class="btn btn-o btn-sm" onclick="showQR(${c.id}, '${c.username}', '${ib.protocol}')">QR</button>
        <button class="btn btn-d btn-sm" onclick="deleteClient(${c.id})">Удалить</button>
      </td></tr>`})});
  document.getElementById('clientSearch').oninput=function(){const q=this.value.toLowerCase();
    tb.querySelectorAll('tr').forEach(tr=>{tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none'})}
}

function toggleSidebar(){
  document.querySelector('.sidebar').classList.toggle('show');
  document.querySelector('.sidebar-overlay').classList.toggle('show');
}
function openAddInbound(){document.getElementById('addInboundModal').classList.add('show');updateObfsFields()}
function openAddClient(id){
  const user = prompt('Введите имя пользователя:');
  if(user) POST('/panel/api/inbounds/addClient',{inbound_id:id,username:user,total_limit:0,expiry_time:0}).then(()=>loadInbounds());
}
async function toggleInbound(id){await POST(`/panel/api/inbounds/toggle/${id}`,{});loadInbounds()}
async function deleteInbound(id){if(!confirm('Удалить этот сервер и всех клиентов?'))return;await POST(`/panel/api/inbounds/del/${id}`,{});loadInbounds()}
function updateObfsFields(){const p=document.getElementById('ib-protocol').value;const c=document.getElementById('obfs-fields');
  const addr = document.getElementById('ib-address');
  if(p==='openvpn_xor'){
    if(addr) addr.value = '10.9.0.1/24';
    c.innerHTML=`
    <div class="fg"><label>Пароль обфускации</label><input id="obfs-scramble" value=""></div>
    <div class="fg" style="flex-direction:row;align-items:center;gap:10px;margin-top:10px">
      <input type="checkbox" id="obfs-bypass" style="width:20px;height:20px">
      <label style="margin:0">Маршруты для обхода (bypassing)</label>
    </div>`}
  else{
    if(addr) addr.value = '10.8.0.1/24';
    const v2=p==='amneziawg_v2';
    let html = `
      <div class="modal-section">
        <div class="section-title">Мусорные пакеты (Junk)</div>
        <div class="grid-3">
          <div class="fg"><label title="Количество мусорных пакетов">Jc</label><input id="obfs-Jc" type="number" value="5"></div>
          <div class="fg"><label title="Мин. размер мусора">Jmin</label><input id="obfs-Jmin" type="number" value="50"></div>
          <div class="fg"><label title="Макс. размер мусора">Jmax</label><input id="obfs-Jmax" type="number" value="1000"></div>
        </div>
      </div>
      
      <div class="modal-section">
        <div class="section-title">Паддинг пакетов (Padding)</div>
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
        <div class="section-title">Заголовки (Headers)</div>
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
async function deleteClient(id){if(!confirm('Удалить клиента?'))return;await POST(`/panel/api/inbounds/delClient/${id}`,{});loadAllClients()}

async function loadFirewall(){const r=await API('/panel/api/firewall/status');
  document.getElementById('fw-status').textContent=r.active?'ВКЛЮЧЕН':'ВЫКЛЮЧЕН';
  document.getElementById('fw-status').className='badge '+(r.active?'badge-on':'badge-off');
  const c=document.getElementById('fw-rules');c.innerHTML='';
  (r.rules||[]).forEach((rule,i)=>{c.innerHTML+=`<div class="stat-item"><span>${rule}</span><button class="btn btn-d btn-sm" onclick="fwDel(${i+1})">Удалить</button></div>`})}

async function fwToggle(en){await POST('/panel/api/firewall/toggle',{enable:en});loadFirewall()}
async function fwAddRule(){await POST('/panel/api/firewall/addRule',{port:document.getElementById('fw-port').value,proto:document.getElementById('fw-proto').value,action:document.getElementById('fw-action').value,from_ip:document.getElementById('fw-from').value||'any'});loadFirewall()}
async function fwDel(n){if(!confirm('Удалить правило #'+n+'?'))return;await POST('/panel/api/firewall/delRule',{rule_num:n});loadFirewall()}

async function loadSystem(){
  const h=await API('/panel/api/system/hostname');document.getElementById('sys-hostname').value=h.hostname||'';
  const tz=await API('/panel/api/system/timezone');document.getElementById('sys-tz').value=tz.timezone||'';
}
async function saveHostname(){await POST('/panel/api/system/hostname',{hostname:document.getElementById('sys-hostname').value})}
async function saveTimezone(){await POST('/panel/api/system/timezone',{timezone:document.getElementById('sys-tz').value})}
async function loadLogs(){const unit=document.getElementById('log-unit').value;
  const r=await API(`/panel/api/system/logs?lines=100&unit=${unit}`);
  document.getElementById('log-output').textContent=r.logs||'Нет логов'}

async function loadSettings(){const r=await API('/panel/api/settings');if(!r.success)return;
  document.getElementById('s-port').value=r.obj.panel_port||'9090';document.getElementById('s-basepath').value=r.obj.web_base_path||''}

async function saveSettings(){await POST('/panel/api/settings',{panel_port:document.getElementById('s-port').value,web_base_path:document.getElementById('s-basepath').value})}
async function setupService(){if(!confirm('Создать службу автозапуска?'))return;const r=await POST('/panel/api/system/setupService',{});alert(r.msg)}
async function installFail2Ban(){if(!confirm('Установить Fail2Ban?'))return;const r=await POST('/panel/api/system/installFail2Ban',{});alert(r.msg)}
async function issueSSL(){const d=document.getElementById('ssl-domain').value;if(!d)return alert('Укажите домен');const r=await POST('/panel/api/system/issueSSL',{domain:d});alert(r.msg)}

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
