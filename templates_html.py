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
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;min-height:100vh;display:flex}
.left{flex:1;background:#1c2128;display:flex;align-items:center;justify-content:center;padding:40px}
.right{flex:1;background:#00a8e8;display:flex;align-items:center;justify-content:center;color:#fff}
.right h1{font-size:48px;font-weight:700;letter-spacing:2px;text-transform:uppercase}
.card{width:100%;max-width:360px;text-align:center}
.card h2{font-size:24px;color:#fff;margin-bottom:30px;font-weight:600}
.fg{margin-bottom:15px;text-align:left}
.fg input{width:100%;padding:14px;border:1px solid #374151;border-radius:6px;background:#252a33;color:#fff;font-size:15px;outline:none}
.fg input:focus{border-color:#00a8e8}
.btn{width:100%;padding:14px;border:none;border-radius:6px;background:#00a8e8;color:#fff;font-size:16px;font-weight:600;cursor:pointer;transition:opacity .2s}
.btn:hover{opacity:.9}
.error{color:#ef4444;font-size:14px;margin-bottom:15px}
.links{margin-top:20px;font-size:13px;color:#777d85}
.links a{color:#00a8e8;text-decoration:none}
</style></head><body>
<div class="left"><form class="card" method="POST">
  <h2>Вход в веб-конфигуратор</h2>
  {% if error %}<div class="error">{{ error }}</div>{% endif %}
  <div class="fg"><input name="username" placeholder="Имя пользователя" required></div>
  <div class="fg"><input name="password" type="password" placeholder="Пароль" required></div>
  <button class="btn" type="submit">Войти</button>
  <div class="links"><a href="#">Не могу войти</a> &nbsp;|&nbsp; <a href="#">Центр поддержки</a></div>
</form></div>
<div class="right"><h1>Sky-Net Panel</h1></div>
</body></html>"""


MAIN_HTML = r"""<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sky-Net Panel</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/qrcode@1/build/qrcode.min.js"></script>
<style>
:root {
  --kg-sidebar: #1d252f;
  --kg-bg: #111419;
  --kg-card: #1c2128;
  --kg-text: #ffffff;
  --kg-text-dim: #9aa0a6;
  --kg-border: #30363d;
  --kg-blue: #00a8e8;
  --kg-green: #2fb45a;
  --kg-red: #e63946;
}

[data-theme="light"] {
  --kg-bg: #f3f5f6;
  --kg-card: #ffffff;
  --kg-text: #333333;
  --kg-text-dim: #777d85;
  --kg-border: #e2e4e7;
  --kg-sidebar: #015caa;
  --kg-blue: #015caa;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--kg-bg); color: var(--kg-text); display: flex; min-height: 100vh; line-height: 1.5; }

/* Sidebar */
.sidebar { width: 220px; background: var(--kg-sidebar); border-right: 1px solid var(--kg-border); display: flex; flex-direction: column; position: fixed; height: 100vh; z-index: 100; transition: width 0.3s; }
.sidebar .logo { padding: 24px 20px; text-align: center; border-bottom: 1px solid var(--kg-border); color: var(--kg-blue); font-weight: 700; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; }
.sidebar nav { flex: 1; padding: 10px 0; overflow-y: auto; }
.sidebar nav a { display: flex; align-items: center; gap: 12px; padding: 12px 20px; color: var(--kg-text-dim); text-decoration: none; font-size: 13px; font-weight: 500; transition: 0.2s; border-left: 3px solid transparent; }
.sidebar nav a:hover { color: #fff; background: rgba(255,255,255,0.05); }
.sidebar nav a.active { color: #fff; border-left-color: var(--kg-blue); background: rgba(0,168,232,0.15); font-weight: 600; }
.sidebar nav .section { font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.2); padding: 20px 20px 5px; font-weight: 800; letter-spacing: 1px; }

/* Main Area */
.main { margin-left: 220px; flex: 1; display: flex; flex-direction: column; min-width: 0; }
.header { height: 60px; background: var(--kg-card); border-bottom: 1px solid var(--kg-border); display: flex; align-items: center; justify-content: space-between; padding: 0 30px; position: sticky; top: 0; z-index: 90; }
.header h1 { font-size: 18px; font-weight: 600; }

.content { padding: 30px; }
.page { display: none; max-width: 1200px; }
.page.active { display: block; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* Cards & Widgets */
.card { background: var(--kg-card); border: 1px solid var(--kg-border); border-radius: 6px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--kg-border); padding-bottom: 12px; }
.card-header h3 { font-size: 14px; text-transform: uppercase; color: var(--kg-text-dim); letter-spacing: 1px; font-weight: 700; }

/* Dashboard Widgets */
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }
.stat-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.stat-item:last-child { border-bottom: none; }
.stat-label { font-size: 14px; color: var(--kg-text-dim); }
.stat-val { font-size: 15px; font-weight: 600; color: var(--kg-blue); }

/* Tables */
.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; min-width: 600px; }
th { text-align: left; padding: 12px 15px; font-size: 12px; text-transform: uppercase; color: var(--kg-text-dim); border-bottom: 2px solid var(--kg-border); font-weight: 700; }
td { padding: 15px; font-size: 14px; border-bottom: 1px solid var(--kg-border); vertical-align: middle; }
tr:hover { background: rgba(255,255,255,0.02); }

/* Buttons & Badges */
.btn { border: none; padding: 9px 18px; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 600; transition: 0.2s; display: inline-flex; align-items: center; gap: 8px; outline: none; }
.btn-p { background: var(--kg-blue); color: #fff; }
.btn-p:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-o { background: transparent; border: 1px solid var(--kg-border); color: var(--kg-text); }
.btn-o:hover { border-color: var(--kg-blue); color: var(--kg-blue); }
.btn-d { color: var(--kg-red); background: transparent; border: 1px solid transparent; }
.btn-d:hover { border-color: var(--kg-red); }
.btn-sm { padding: 5px 12px; font-size: 12px; }

.badge { padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.badge-on { background: rgba(47,180,90,0.15); color: #2fb45a; }
.badge-off { background: rgba(230,57,70,0.15); color: #e63946; }
.badge-proto { background: rgba(0,168,232,0.1); color: var(--kg-blue); }

/* Chart */
.chart-container { height: 180px; position: relative; margin-top: 15px; }

/* Modals */
.overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(2px); }
.overlay.show { display: flex; }
.modal { background: var(--kg-card); border: 1px solid var(--kg-border); border-radius: 8px; width: 520px; max-width: 95%; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
.modal-header { padding: 18px 24px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--kg-border); font-size: 16px; font-weight: 700; }
.modal-body { padding: 24px; }
.modal-footer { padding: 16px 24px; border-top: 1px solid var(--kg-border); display: flex; justify-content: flex-end; gap: 12px; }

.fg { margin-bottom: 20px; }
.fg label { display: block; font-size: 12px; text-transform: uppercase; color: var(--kg-text-dim); margin-bottom: 8px; font-weight: 600; }
.fg input, .fg select, .fg textarea { width: 100%; padding: 12px; border: 1px solid var(--kg-border); border-radius: 4px; background: rgba(0,0,0,0.2); color: #fff; font-size: 14px; outline: none; }
.fr { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

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
    <h1 id="page-title-text">Системный монитор</h1>
    <div class="header-right">
      <span style="font-size: 13px; color: var(--kg-text-dim)">{{ session.get('username') }}</span>
      <a href="/logout" style="margin-left: 15px; color: var(--kg-red); text-decoration: none; font-size: 13px">Выход</a>
    </div>
  </div>
  <div class="content">

<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
  <div class="grid">
    <div class="card">
      <div class="card-header"><h3>ИНТЕРНЕТ</h3></div>
      <div class="stat-item"><span class="stat-label">Внешний IP адрес</span><span class="stat-val" id="d-ip">--</span></div>
      <div class="stat-item"><span class="stat-label">Загрузка (общее)</span><span class="stat-val" id="d-up">0 B</span></div>
      <div class="stat-item"><span class="stat-label">Прием (общее)</span><span class="stat-val" id="d-down">0 B</span></div>
      <div class="chart-container"><canvas id="trafficChart"></canvas></div>
    </div>
    
    <div class="card">
      <div class="card-header"><h3>О СИСТЕМЕ</h3></div>
      <div class="stat-item"><span class="stat-label">Имя устройства</span><span class="stat-val" id="d-host" style="color:var(--kg-blue);font-weight:600">--</span></div>
    <div class="stat-item"><span class="stat-label">Версия системы</span><span class="stat-val" id="d-os" style="color:var(--kg-blue);font-weight:600">--</span></div>
      <div class="stat-item"><span class="stat-label">Время работы</span><span class="stat-val" id="uptime-val">--</span></div>
      <div class="stat-item"><span class="stat-label">Процессор</span><span class="stat-val" id="cpu-val">0%</span></div>
      <div class="stat-item"><span class="stat-label">Память</span><span class="stat-val" id="ram-val">0%</span></div>
      <div class="stat-item"><span class="stat-label">Диск</span><span class="stat-val" id="disk-val">0%</span></div>
    </div>
  </div>
  
  <div class="card">
    <div class="card-header"><h3>СЕТЕВЫЕ ИНТЕРФЕЙСЫ</h3></div>
    <div id="net-ifaces"></div>
  </div>
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
    <div class="card-header"><h3>ПОДКЛЮЧЕННЫЕ КЛИЕНТЫ</h3>
      <input id="clientSearch" placeholder="Поиск клиентов..." style="width: 250px; margin-left: 20px">
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
    <div class="card-header"><h3>МЕЖСЕТЕВОЙ ЭКРАН (UFW)</h3>
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
      <div style="display:flex;gap:10px"><input id="ssl-domain" placeholder="vpn.example.com" style="width:150px"><button class="btn btn-o btn-sm" onclick="issueSSL()">Выпустить</button></div>
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
      <div id="obfs-fields"></div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-o" onclick="closeModal('addInboundModal')">Отмена</button>
      <button class="btn btn-p" onclick="submitInbound()">Создать</button>
    </div>
  </div>
</div>

<div class="overlay" id="qrModal">
  <div class="modal">
    <div class="modal-header">Конфигурация клиента</div>
    <div class="modal-body" style="text-align:center">
      <div style="background:#fff;padding:15px;display:inline-block;border-radius:10px;margin-bottom:15px">
        <img id="qrImage" style="width:200px;height:200px">
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

// Dashboard
let chart;
async function loadDashboard(){
  const st=await API('/server/status');
  const d_ip=document.getElementById('d-ip'), d_host=document.getElementById('d-host'), d_os=document.getElementById('d-os');
  if(d_ip) d_ip.textContent = st.public_ip || '--';
  if(d_host) d_host.textContent = st.hostname || 'Sky-Net';
  if(d_os) d_os.textContent = st.os_version || 'Ubuntu';
  document.getElementById('cpu-val').textContent=st.cpu+'%';
  document.getElementById('ram-val').textContent=Math.round(st.mem_percent)+'%';
  document.getElementById('disk-val').textContent=Math.round(st.disk_percent||0)+'%';
  document.getElementById('uptime-val').textContent=fmtUp(st.uptime||0);
  
  const ib=await API('/panel/api/inbounds/list');
  if(ib.success){let tu=0,td=0;ib.obj.forEach(i=>{(i.clients||[]).forEach(c=>{tu+=c.up||0;td+=c.down||0})});
    document.getElementById('d-up').textContent=fmtB(tu);document.getElementById('d-down').textContent=fmtB(td)}
  
  const hist=await API('/panel/api/trafficHistory');
  if(!chart){
    const ctx = document.getElementById('trafficChart').getContext('2d');
    chart=new Chart(ctx,{type:'line',data:{labels:Array.from({length:60},(_,i)=>i),
    datasets:[{label:'Загрузка',data:hist.up,borderColor:'#00a8e8',fill:true,backgroundColor:'rgba(0,168,232,0.1)',tension:.4,pointRadius:0},
              {label:'Отдача',data:hist.down,borderColor:'#2fb45a',fill:true,backgroundColor:'rgba(47,180,90,0.1)',tension:.4,pointRadius:0}]},
    options:{maintainAspectRatio:false,scales:{x:{display:false},y:{display:false}},plugins:{legend:{display:false}},animation:false}});
  }else{chart.data.datasets[0].data=hist.up;chart.data.datasets[1].data=hist.down;chart.update()}
  
  const net=await API('/panel/api/system/network');
  const nc=document.getElementById('net-ifaces');nc.innerHTML='';
  if(net.success)(net.interfaces||[]).forEach(i=>{
    const ips=i.addresses.map(a=>a.ip).join(', ')||'Нет IP';
    nc.innerHTML+=`<div class="stat-item"><span class="stat-label"><b>${i.name}</b> (${ips})</span><span class="badge ${i.is_up?'badge-on':'badge-off'}">${i.is_up?'ПОДКЛЮЧЕНО':'ОТКЛЮЧЕНО'}</span></div>`})
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

function openAddInbound(){document.getElementById('addInboundModal').classList.add('show');updateObfsFields()}
function openAddClient(id){
  const user = prompt('Введите имя пользователя:');
  if(user) POST('/panel/api/inbounds/addClient',{inbound_id:id,username:user,total_limit:0,expiry_time:0}).then(()=>loadInbounds());
}
async function toggleInbound(id){await POST(`/panel/api/inbounds/toggle/${id}`,{});loadInbounds()}
async function deleteInbound(id){if(!confirm('Удалить этот сервер и всех клиентов?'))return;await POST(`/panel/api/inbounds/del/${id}`,{});loadInbounds()}

function updateObfsFields(){const p=document.getElementById('ib-protocol').value;const c=document.getElementById('obfs-fields');
  if(p==='openvpn_xor'){c.innerHTML=`<div class="fg"><label>Пароль обфускации</label><input id="obfs-scramble" value="skynet_xor_secret"></div>`}
  else{const v2=p==='amneziawg_v2';
    c.innerHTML=`<div class="fr"><div class="fg"><label>Jc</label><input id="obfs-Jc" type="number" value="5"></div><div class="fg"><label>Jmin</label><input id="obfs-Jmin" type="number" value="50"></div><div class="fg"><label>Jmax</label><input id="obfs-Jmax" type="number" value="1000"></div></div>
    <div class="fr"><div class="fg"><label>S1</label><input id="obfs-S1" type="number" value="69"></div><div class="fg"><label>S2</label><input id="obfs-S2" type="number" value="115"></div></div>`
  }}

async function submitInbound(){
  const p=document.getElementById('ib-protocol').value;
  const body={protocol:p,remark:document.getElementById('ib-remark').value,port:document.getElementById('ib-port').value,obfuscation:{},settings:{}};
  if(p==='openvpn_xor'){body.obfuscation={scramble_password:document.getElementById('obfs-scramble').value}}
  else{['Jc','Jmin','Jmax','S1','S2'].forEach(k=>{const el=document.getElementById('obfs-'+k);if(el)body.obfuscation[k]=el.value})}
  await POST('/panel/api/inbounds/add',body);closeModal('addInboundModal');loadInbounds()}

async function showQR(cid, username, proto){
  const r=await API(`/panel/api/inbounds/clientConfig/${cid}`);if(!r.success)return;
  document.getElementById('qrConfigText').value=r.config;
  const img=document.getElementById('qrImage');
  try{QRCode.toDataURL(r.config,{width:400,margin:1},(err,url)=>{if(!err)img.src=url})}catch(e){}
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
</script>
</body></html>"""
