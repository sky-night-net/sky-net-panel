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
body{font-family:'Inter',sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;
background:#111827;color:#e5e7eb}
.card{background:#1f2937;border:1px solid #374151;border-radius:16px;padding:48px 40px;width:380px;text-align:center;box-shadow:0 20px 50px rgba(0,0,0,.5)}
.card h1{font-size:26px;color:#f9fafb;margin-bottom:6px;letter-spacing:-.5px}
.card .sub{color:#6b7280;font-size:13px;margin-bottom:32px}
.card input{width:100%;padding:12px 16px;border:1px solid #374151;border-radius:10px;background:#111827;color:#f9fafb;font-size:14px;margin-bottom:14px;outline:none;transition:border .2s}
.card input:focus{border-color:#3b82f6}
.card button{width:100%;padding:13px;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;background:#3b82f6;color:#fff;transition:background .2s}
.card button:hover{background:#2563eb}
.error{color:#ef4444;font-size:13px;margin-bottom:12px}
</style></head><body>
<form class="card" method="POST">
<h1>Sky-Net</h1><p class="sub">Universal VPN Control Panel</p>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<input name="username" placeholder="Login" autocomplete="username" required>
<input name="password" type="password" placeholder="Password" autocomplete="current-password" required>
<button type="submit">Sign In</button>
</form></body></html>"""


MAIN_HTML = r"""<!DOCTYPE html>
<html lang="ru"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sky-Net Panel</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
<style>
:root{
  --bg:#111827;--bg2:#1f2937;--bg3:#374151;--border:#374151;
  --text:#f9fafb;--text2:#9ca3af;--text3:#6b7280;
  --accent:#3b82f6;--accent-h:#2563eb;--green:#10b981;--red:#ef4444;--orange:#f59e0b;--cyan:#06b6d4;
}
[data-theme="light"]{
  --bg:#f3f4f6;--bg2:#ffffff;--bg3:#e5e7eb;--border:#d1d5db;
  --text:#111827;--text2:#4b5563;--text3:#6b7280;
  --accent:#3b82f6;--accent-h:#2563eb;--green:#059669;--red:#dc2626;--orange:#d97706;--cyan:#0891b2;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);display:flex;min-height:100vh;transition:background .3s,color .3s}
.sidebar{width:220px;background:var(--bg2);border-right:1px solid var(--border);display:flex;flex-direction:column;position:fixed;height:100vh;z-index:10;transition:background .3s}
.sidebar .logo{padding:20px 16px 16px;border-bottom:1px solid var(--border)}
.sidebar .logo h2{font-size:18px;font-weight:700;color:var(--accent);letter-spacing:-.5px}
.sidebar .logo span{font-size:11px;color:var(--text3);display:block;margin-top:2px}
.sidebar nav{flex:1;padding:12px 8px;overflow-y:auto}
.sidebar nav .section-label{font-size:10px;text-transform:uppercase;letter-spacing:1.2px;color:var(--text3);padding:12px 12px 4px;font-weight:600}
.sidebar nav a{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:8px;color:var(--text2);text-decoration:none;font-size:13px;font-weight:500;transition:all .15s;margin-bottom:2px}
.sidebar nav a:hover{background:var(--bg3);color:var(--text)}
.sidebar nav a.active{background:var(--accent);color:#fff}
.sidebar .bottom{padding:12px 16px;border-top:1px solid var(--border);display:flex;flex-direction:column;gap:8px}
.sidebar .bottom a{color:var(--text3);text-decoration:none;font-size:12px}
.sidebar .bottom a:hover{color:var(--red)}
.theme-btn{cursor:pointer;background:var(--bg3);border:1px solid var(--border);color:var(--text2);padding:6px 10px;border-radius:6px;font-size:11px;font-weight:600;transition:all .15s}
.theme-btn:hover{color:var(--text);border-color:var(--accent)}
.main{margin-left:220px;flex:1;padding:28px 32px;min-height:100vh}
.page{display:none}.page.active{display:block}
.page-title{font-size:20px;font-weight:700;margin-bottom:20px;color:var(--text)}
/* Stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:20px}
.stat{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;transition:background .3s}
.stat .label{font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}
.stat .val{font-size:24px;font-weight:700;color:var(--accent)}
.stat .bar{height:4px;background:var(--bg3);border-radius:2px;margin-top:10px;overflow:hidden}
.stat .bar .fill{height:100%;border-radius:2px;transition:width .5s}
.fill-blue{background:var(--accent)}.fill-green{background:var(--green)}.fill-orange{background:var(--orange)}.fill-red{background:var(--red)}
/* Card */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px;transition:background .3s}
.card .hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.card h3{font-size:15px;font-weight:600}
/* Table */
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:8px 10px;font-size:11px;color:var(--text3);text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--border);font-weight:600}
td{padding:10px;font-size:13px;border-bottom:1px solid var(--border);color:var(--text)}
tr:hover{background:var(--bg3)}
.badge{padding:3px 8px;border-radius:6px;font-size:11px;font-weight:600;display:inline-block}
.badge-on{background:rgba(16,185,129,.12);color:var(--green)}.badge-off{background:rgba(239,68,68,.12);color:var(--red)}
.badge-proto{background:rgba(59,130,246,.12);color:var(--accent)}
/* Buttons */
.btn{padding:7px 14px;border:none;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;transition:all .15s;display:inline-flex;align-items:center;gap:4px}
.btn-p{background:var(--accent);color:#fff}.btn-p:hover{background:var(--accent-h)}
.btn-d{background:rgba(239,68,68,.1);color:var(--red);border:1px solid rgba(239,68,68,.2)}.btn-d:hover{background:rgba(239,68,68,.2)}
.btn-s{background:rgba(16,185,129,.1);color:var(--green);border:1px solid rgba(16,185,129,.2)}
.btn-o{background:transparent;color:var(--accent);border:1px solid var(--border)}.btn-o:hover{border-color:var(--accent)}
.btn-sm{padding:5px 10px;font-size:11px}
/* Modal */
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;align-items:center;justify-content:center}
.overlay.show{display:flex}
.modal{background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:28px;width:520px;max-height:85vh;overflow-y:auto}
.modal h3{margin-bottom:18px;font-size:17px}
.fg{margin-bottom:14px}
.fg label{display:block;font-size:11px;color:var(--text3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.fg input,.fg select,.fg textarea{width:100%;padding:9px 12px;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--text);font-size:13px;outline:none;transition:border .2s}
.fg input:focus,.fg select:focus{border-color:var(--accent)}
.fr{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.fr3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.obfs-box{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;margin-top:6px}
.obfs-box h4{font-size:12px;color:var(--accent);margin-bottom:10px;text-transform:uppercase;letter-spacing:.5px}
/* Config Modal */
#qrModal .modal{text-align:center}
#qrCanvas{margin:12px auto}
#qrConfigText{width:100%;min-height:100px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--green);font-family:'Courier New',monospace;font-size:11px;padding:10px;resize:vertical}
/* Logs */
.log-output{background:#0d1117;color:#c9d1d9;font-family:'Courier New',monospace;font-size:12px;padding:12px;border-radius:8px;max-height:400px;overflow-y:auto;white-space:pre-wrap;line-height:1.5}
/* Traffic bar */
.tbar{width:100%;height:3px;background:var(--bg3);border-radius:2px;overflow:hidden;margin-top:4px}
.tbar .fill{height:100%;background:linear-gradient(90deg,var(--green),var(--orange),var(--red))}
/* Firewall */
.fw-rule{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-bottom:1px solid var(--border);font-size:13px}
</style></head><body>

<div class="sidebar">
  <div class="logo"><h2>Sky-Net</h2><span>VPN Panel v2.0</span></div>
  <nav>
    <div class="section-label">Monitoring</div>
    <a href="#" data-page="dashboard" class="active">Dashboard</a>
    <div class="section-label">VPN</div>
    <a href="#" data-page="inbounds">Inbounds</a>
    <a href="#" data-page="clients">Clients</a>
    <div class="section-label">Server</div>
    <a href="#" data-page="firewall">Firewall</a>
    <a href="#" data-page="system">System</a>
    <a href="#" data-page="logs">Logs</a>
    <div class="section-label">Admin</div>
    <a href="#" data-page="settings">Settings</a>
  </nav>
  <div class="bottom">
    <button class="theme-btn" onclick="toggleTheme()">Switch Theme</button>
    <a href="/logout">Sign Out ({{ session.get('username','admin') }})</a>
  </div>
</div>

<div class="main">

<!-- DASHBOARD -->
<div class="page active" id="page-dashboard">
  <div class="page-title">Dashboard</div>
  <div class="stats">
    <div class="stat"><div class="label">CPU</div><div class="val" id="cpu-val">0%</div><div class="bar"><div class="fill fill-blue" id="cpu-bar" style="width:0%"></div></div></div>
    <div class="stat"><div class="label">Memory</div><div class="val" id="ram-val">0%</div><div class="bar"><div class="fill fill-green" id="ram-bar" style="width:0%"></div></div></div>
    <div class="stat"><div class="label">Disk</div><div class="val" id="disk-val">0%</div><div class="bar"><div class="fill fill-orange" id="disk-bar" style="width:0%"></div></div></div>
    <div class="stat"><div class="label">Uptime</div><div class="val" id="uptime-val">--</div></div>
  </div>
  <div class="stats">
    <div class="stat"><div class="label">Inbounds</div><div class="val" id="d-ibc">0</div></div>
    <div class="stat"><div class="label">Clients</div><div class="val" id="d-clc">0</div></div>
    <div class="stat"><div class="label">Upload Total</div><div class="val" id="d-up">0 B</div></div>
    <div class="stat"><div class="label">Download Total</div><div class="val" id="d-down">0 B</div></div>
  </div>
  <div class="card"><div class="hdr"><h3>Traffic History</h3></div><canvas id="trafficChart" height="70"></canvas></div>
  <div class="card"><div class="hdr"><h3>Network Interfaces</h3></div><div id="net-ifaces"></div></div>
</div>

<!-- INBOUNDS -->
<div class="page" id="page-inbounds">
  <div class="card"><div class="hdr"><h3>Inbounds</h3><button class="btn btn-p" onclick="openAddInbound()">Add Inbound</button></div>
  <table><thead><tr><th>#</th><th>Protocol</th><th>Name</th><th>Port</th><th>Upload / Download</th><th>Status</th><th>Clients</th><th>Actions</th></tr></thead>
  <tbody id="inbounds-table"></tbody></table></div>
</div>

<!-- CLIENTS -->
<div class="page" id="page-clients">
  <div class="card"><div class="hdr"><h3>All Clients</h3>
    <input id="clientSearch" placeholder="Search..." style="padding:7px 12px;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--text);width:220px;font-size:13px;outline:none"></div>
  <table><thead><tr><th>Name</th><th>Inbound</th><th>IP</th><th>Upload / Download</th><th>Limit</th><th>Expiry</th><th>Status</th><th>Actions</th></tr></thead>
  <tbody id="clients-table"></tbody></table></div>
</div>

<!-- FIREWALL -->
<div class="page" id="page-firewall">
  <div class="card"><div class="hdr"><h3>UFW Firewall</h3>
    <div style="display:flex;gap:8px;align-items:center">
      <span id="fw-status" class="badge badge-off">--</span>
      <button class="btn btn-sm btn-s" onclick="fwToggle(true)">Enable</button>
      <button class="btn btn-sm btn-d" onclick="fwToggle(false)">Disable</button>
    </div></div>
    <div id="fw-rules"></div>
  </div>
  <div class="card"><div class="hdr"><h3>Add Rule</h3></div>
    <div class="fr">
      <div class="fg"><label>Port</label><input id="fw-port" placeholder="22"></div>
      <div class="fg"><label>Protocol</label><select id="fw-proto"><option value="">Any</option><option value="tcp">TCP</option><option value="udp">UDP</option></select></div>
    </div>
    <div class="fr">
      <div class="fg"><label>Action</label><select id="fw-action"><option value="allow">Allow</option><option value="deny">Deny</option><option value="reject">Reject</option></select></div>
      <div class="fg"><label>From IP (optional)</label><input id="fw-from" placeholder="any"></div>
    </div>
    <button class="btn btn-p" onclick="fwAddRule()">Add Rule</button>
  </div>
</div>

<!-- SYSTEM -->
<div class="page" id="page-system">
  <div class="page-title">System Management</div>
  <div class="card"><div class="hdr"><h3>Sky-Net Persistence</h3></div>
    <p style="font-size:13px;color:var(--text2);margin-bottom:12px">Install systemd service to keep Sky-Net running after reboot and on crashes.</p>
    <button class="btn btn-p" onclick="setupService()">Setup Systemd Service</button>
  </div>
  <div class="fr" style="margin-bottom:16px">
    <div class="card"><div class="hdr"><h3>Fail2Ban Protection</h3></div>
      <p style="font-size:12px;color:var(--text2);margin-bottom:12px">Install and configure Fail2Ban to protect panel port 9090.</p>
      <button class="btn btn-o" onclick="installFail2Ban()">Install Fail2Ban</button></div>
    <div class="card"><div class="hdr"><h3>SSL Certificate</h3></div>
      <div class="fg"><label>Domain</label><input id="ssl-domain" placeholder="vpn.example.com"></div>
      <button class="btn btn-o btn-sm" onclick="issueSSL()">Issue SSL (acme.sh)</button></div>
  </div>
  <div class="fr" style="margin-bottom:16px">
    <div class="card"><div class="hdr"><h3>Hostname</h3></div>
      <div class="fg"><input id="sys-hostname" placeholder="server-01"></div>
      <button class="btn btn-p btn-sm" onclick="saveHostname()">Save</button></div>
    <div class="card"><div class="hdr"><h3>Timezone</h3></div>
      <div class="fg"><input id="sys-tz" placeholder="UTC"></div>
      <button class="btn btn-p btn-sm" onclick="saveTimezone()">Save</button></div>
  </div>
  <div class="card"><div class="hdr"><h3>DNS Servers</h3></div>
    <div class="fg"><label>Nameservers (one per line)</label><textarea id="sys-dns" rows="3" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--text);font-size:13px;resize:vertical"></textarea></div>
    <button class="btn btn-p btn-sm" onclick="saveDNS()">Save DNS</button>
  </div>
  <div class="card"><div class="hdr"><h3>Running Services</h3></div>
    <div id="services-list" style="max-height:300px;overflow-y:auto"></div>
  </div>
</div>

<!-- LOGS -->
<div class="page" id="page-logs">
  <div class="card"><div class="hdr"><h3>System Logs</h3>
    <div style="display:flex;gap:8px">
      <input id="log-unit" placeholder="Unit (optional)" style="padding:6px 10px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text);font-size:12px;width:160px">
      <select id="log-lines" style="padding:6px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text);font-size:12px">
        <option value="50">50 lines</option><option value="100">100</option><option value="200">200</option><option value="500">500</option>
      </select>
      <button class="btn btn-p btn-sm" onclick="loadLogs()">Refresh</button>
    </div></div>
    <div class="log-output" id="log-output">Loading...</div>
  </div>
</div>

<!-- SETTINGS -->
<div class="page" id="page-settings">
  <div class="page-title">Panel Settings</div>
  <div class="card"><div class="hdr"><h3>General</h3></div>
    <div class="fr">
      <div class="fg"><label>Panel Port</label><input id="s-port" type="number"></div>
      <div class="fg"><label>Base Path</label><input id="s-basepath" placeholder="/mypath"></div>
    </div>
    <div class="fr">
      <div class="fg"><label>Session Timeout (sec)</label><input id="s-timeout" type="number" value="3600"></div>
      <div class="fg"><label>Poll Interval (sec)</label><input id="s-poll" type="number" value="15"></div>
    </div>
    <button class="btn btn-p" onclick="saveSettings()">Save</button>
  </div>
  <div class="card"><div class="hdr"><h3>Telegram Notifications</h3></div>
    <div class="fr">
      <div class="fg"><label>Bot Token</label><input id="s-tg-token" placeholder="123456:ABC..."></div>
      <div class="fg"><label>Chat ID</label><input id="s-tg-chat" placeholder="-100123456"></div>
    </div>
    <button class="btn btn-p" onclick="saveSettings()">Save</button>
  </div>
  <div class="card"><div class="hdr"><h3>Admin Credentials</h3></div>
    <div class="fg"><label>Current Password</label><input id="s-oldpass" type="password"></div>
    <div class="fr">
      <div class="fg"><label>New Username</label><input id="s-newuser"></div>
      <div class="fg"><label>New Password</label><input id="s-newpass" type="password"></div>
    </div>
    <button class="btn btn-p" onclick="changePassword()">Update Credentials</button>
  </div>
  <div class="card"><div class="hdr"><h3>Database</h3></div>
    <div style="display:flex;gap:12px">
      <button class="btn btn-s" onclick="backupDB()">Backup DB</button>
      <a href="/panel/api/db/export" class="btn btn-o">Export DB</a>
      <label class="btn btn-o" style="cursor:pointer">Import DB<input type="file" id="db-import-file" style="display:none" onchange="importDB()"></label>
    </div>
  </div>
</div>
</div>

<!-- MODALS -->
<div class="overlay" id="addInboundModal">
<div class="modal"><h3>Add Inbound</h3>
  <div class="fg"><label>Protocol</label>
    <select id="ib-protocol" onchange="updateObfsFields()">
      <option value="amneziawg_v1">AmneziaWG v1 (Legacy)</option>
      <option value="amneziawg_v2">AmneziaWG v2</option>
      <option value="openvpn_xor">OpenVPN + XOR Patch</option>
    </select></div>
  <div class="fr">
    <div class="fg"><label>Name</label><input id="ib-remark" placeholder="My VPN"></div>
    <div class="fg"><label>Port</label><input id="ib-port" type="number" value="51820"></div>
  </div>
  <div class="fr">
    <div class="fg"><label>Listen Address</label><input id="ib-listen" value="0.0.0.0"></div>
    <div class="fg"><label>MTU</label><input id="ib-mtu" type="number" value="1420"></div>
  </div>
  <div class="fr">
    <div class="fg"><label>Server Address</label><input id="ib-address" value="10.8.0.1/24"></div>
    <div class="fg"><label>DNS</label><input id="ib-dns" value="1.1.1.1, 8.8.8.8"></div>
  </div>
  <div id="obfs-fields"></div>
  <div style="display:flex;gap:10px;margin-top:18px">
    <button class="btn btn-p" onclick="submitInbound()" style="flex:1">Create</button>
    <button class="btn btn-d" onclick="closeModal('addInboundModal')" style="flex:1">Cancel</button>
  </div>
</div></div>

<div class="overlay" id="addClientModal">
<div class="modal"><h3>Add Client</h3>
  <input type="hidden" id="cl-inbound-id">
  <div class="fg"><label>Username</label><input id="cl-username" placeholder="user1"></div>
  <div class="fr">
    <div class="fg"><label>Traffic Limit (bytes, 0 = unlimited)</label><input id="cl-limit" type="number" value="0"></div>
    <div class="fg"><label>Traffic Limit (GB helper)</label>
      <select onchange="document.getElementById('cl-limit').value=this.value">
        <option value="0">Unlimited</option><option value="1073741824">1 GB</option><option value="5368709120">5 GB</option>
        <option value="10737418240">10 GB</option><option value="53687091200">50 GB</option><option value="107374182400">100 GB</option>
      </select></div>
  </div>
  <div class="fr">
    <div class="fg"><label>Expiry (days from now, 0 = never)</label><input id="cl-expiry-days" type="number" value="0"></div>
    <div class="fg"><label>Allowed IPs (client side)</label><input id="cl-allowed" value="0.0.0.0/0, ::/0"></div>
  </div>
  <div style="display:flex;gap:10px;margin-top:18px">
    <button class="btn btn-p" onclick="submitClient()" style="flex:1">Create</button>
    <button class="btn btn-d" onclick="closeModal('addClientModal')" style="flex:1">Cancel</button>
  </div>
</div></div>

<div class="overlay" id="qrModal">
<div class="modal"><h3>Client Configuration</h3>
  <div style="background:#fff;padding:12px;display:inline-block;border-radius:12px;margin-bottom:12px">
    <img id="qrImage" style="display:block;width:200px;height:200px">
  </div>
  <textarea id="qrConfigText" readonly></textarea>
  <div style="display:flex;gap:10px;margin-top:12px">
    <button class="btn btn-p" onclick="copyConfig()" style="flex:1">Copy</button>
    <button class="btn btn-s" id="downloadBtn" style="flex:1">Download</button>
    <button class="btn btn-d" onclick="closeModal('qrModal')" style="flex:1">Close</button>
  </div>
</div></div>

<script>
const API=p=>fetch(p).then(r=>r.json());
const POST=(p,b)=>fetch(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(r=>r.json());
function fmtB(b){if(!b||b===0)return'0 B';const k=1024,s=['B','KB','MB','GB','TB'];const i=Math.floor(Math.log(b)/Math.log(k));return(b/Math.pow(k,i)).toFixed(1)+' '+s[i]}
function fmtUp(s){const d=Math.floor(s/86400),h=Math.floor(s%86400/3600),m=Math.floor(s%3600/60);return d+'d '+h+'h '+m+'m'}
function fmtDate(ts){if(!ts||ts===0)return'Never';return new Date(ts*1000).toLocaleDateString()}
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
  document.getElementById('cpu-val').textContent=st.cpu+'%';document.getElementById('cpu-bar').style.width=st.cpu+'%';
  document.getElementById('ram-val').textContent=Math.round(st.mem_percent)+'%';document.getElementById('ram-bar').style.width=st.mem_percent+'%';
  document.getElementById('disk-val').textContent=Math.round(st.disk_percent||0)+'%';document.getElementById('disk-bar').style.width=(st.disk_percent||0)+'%';
  document.getElementById('uptime-val').textContent=fmtUp(st.uptime||0);
  const ib=await API('/panel/api/inbounds/list');
  if(ib.success){let tc=0,tu=0,td=0;ib.obj.forEach(i=>{tc+=i.clients?i.clients.length:0;(i.clients||[]).forEach(c=>{tu+=c.up||0;td+=c.down||0})});
    document.getElementById('d-ibc').textContent=ib.obj.length;document.getElementById('d-clc').textContent=tc;
    document.getElementById('d-up').textContent=fmtB(tu);document.getElementById('d-down').textContent=fmtB(td)}
  const hist=await API('/panel/api/trafficHistory');
  const cColor=getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
  const cColor2=getComputedStyle(document.documentElement).getPropertyValue('--green').trim();
  if(!chart){chart=new Chart(document.getElementById('trafficChart'),{type:'line',data:{labels:Array.from({length:60},(_,i)=>i),
    datasets:[{label:'Upload',data:hist.up,borderColor:cColor,fill:false,tension:.3,pointRadius:0,borderWidth:2},
              {label:'Download',data:hist.down,borderColor:cColor2,fill:false,tension:.3,pointRadius:0,borderWidth:2}]},
    options:{scales:{x:{display:false},y:{ticks:{callback:v=>fmtB(v),color:'var(--text3)'},grid:{color:'var(--border)'}}},plugins:{legend:{labels:{color:'var(--text2)'}}},animation:false}});
  }else{chart.data.datasets[0].data=hist.up;chart.data.datasets[1].data=hist.down;chart.update()}
  // Network
  const net=await API('/panel/api/system/network');
  const nc=document.getElementById('net-ifaces');nc.innerHTML='';
  if(net.success)(net.interfaces||[]).forEach(i=>{
    const ips=i.addresses.map(a=>a.ip+' ('+a.type+')').join(', ')||'No IP';
    nc.innerHTML+=`<div class="fw-rule"><span><b>${i.name}</b> - ${ips}</span><span class="badge ${i.is_up?'badge-on':'badge-off'}">${i.is_up?'UP':'DOWN'}</span></div>`})
}

// Inbounds
const PL={'amneziawg_v1':'AWG v1','amneziawg_v2':'AWG v2','openvpn_xor':'OVPN+XOR'};
async function loadInbounds(){const r=await API('/panel/api/inbounds/list');if(!r.success)return;
  const tb=document.getElementById('inbounds-table');tb.innerHTML='';
  r.obj.forEach(ib=>{tb.innerHTML+=`<tr><td>${ib.id}</td><td><span class="badge badge-proto">${PL[ib.protocol]||ib.protocol}</span></td>
    <td>${ib.remark}</td><td>${ib.port}</td><td>${fmtB(ib.up)} / ${fmtB(ib.down)}</td>
    <td><span class="badge ${ib.enable?'badge-on':'badge-off'}">${ib.enable?'Active':'Off'}</span></td>
    <td>${(ib.clients||[]).length}</td>
    <td><button class="btn btn-sm btn-s" onclick="openAddClient(${ib.id})">+Client</button>
     <button class="btn btn-sm btn-o" onclick="toggleInbound(${ib.id})">${ib.enable?'Pause':'Start'}</button>
     <button class="btn btn-sm btn-d" onclick="deleteInbound(${ib.id})">Del</button></td></tr>`})}
function openAddInbound(){document.getElementById('addInboundModal').classList.add('show');updateObfsFields()}
function openAddClient(id){document.getElementById('cl-inbound-id').value=id;document.getElementById('addClientModal').classList.add('show')}
async function toggleInbound(id){await POST(`/panel/api/inbounds/toggle/${id}`,{});loadInbounds()}
async function deleteInbound(id){if(!confirm('Delete this inbound and all clients?'))return;await POST(`/panel/api/inbounds/del/${id}`,{});loadInbounds()}

function updateObfsFields(){const p=document.getElementById('ib-protocol').value;const c=document.getElementById('obfs-fields');
  if(p==='openvpn_xor'){c.innerHTML=`<div class="obfs-box"><h4>XOR Obfuscation</h4>
    <div class="fg"><label>Scramble Password</label><input id="obfs-scramble" value="skynet_xor_secret"></div>
    <div class="fr"><div class="fg"><label>Protocol</label><select id="obfs-proto"><option>udp</option><option>tcp</option></select></div>
    <div class="fg"><label>Cipher</label><input id="obfs-cipher" value="AES-256-GCM"></div></div></div>`}
  else{const v2=p==='amneziawg_v2';
    c.innerHTML=`<div class="obfs-box"><h4>Obfuscation Parameters ${v2?'(v2)':'(v1)'}</h4>
    <div class="fr3"><div class="fg"><label>Jc</label><input id="obfs-Jc" type="number" value="5"></div>
    <div class="fg"><label>Jmin</label><input id="obfs-Jmin" type="number" value="50"></div>
    <div class="fg"><label>Jmax</label><input id="obfs-Jmax" type="number" value="1000"></div></div>
    <div class="fr"><div class="fg"><label>S1</label><input id="obfs-S1" type="number" value="69"></div>
    <div class="fg"><label>S2</label><input id="obfs-S2" type="number" value="115"></div>
    ${v2?'<div class="fg"><label>S3</label><input id="obfs-S3" type="number" value="69"></div><div class="fg"><label>S4</label><input id="obfs-S4" type="number" value="69"></div>':''}</div>
    <div class="fr"><div class="fg"><label>H1</label><input id="obfs-H1" value="${v2?'5-2147483647':'924883749'}"></div>
    <div class="fg"><label>H2</label><input id="obfs-H2" value="${v2?'5-2147483647':'16843009'}"></div></div>
    <div class="fr"><div class="fg"><label>H3</label><input id="obfs-H3" value="${v2?'5-2147483647':'305419896'}"></div>
    <div class="fg"><label>H4</label><input id="obfs-H4" value="${v2?'5-2147483647':'878082202'}"></div></div>
    ${v2?`<div class="fg"><label>I1 (CPS Packet)</label><input id="obfs-I1" placeholder="<b 0x0d0a><r 32>"></div>
    <div class="fr"><div class="fg"><label>I2</label><input id="obfs-I2"></div><div class="fg"><label>I3</label><input id="obfs-I3"></div></div>
    <div class="fr"><div class="fg"><label>I4</label><input id="obfs-I4"></div><div class="fg"><label>I5</label><input id="obfs-I5"></div></div>`:''}</div>`}}

async function submitInbound(){const p=document.getElementById('ib-protocol').value;
  const body={protocol:p,remark:document.getElementById('ib-remark').value,port:document.getElementById('ib-port').value,obfuscation:{},
    settings:{address:document.getElementById('ib-address').value,dns:document.getElementById('ib-dns').value,mtu:parseInt(document.getElementById('ib-mtu').value)}};
  if(p==='openvpn_xor'){body.obfuscation={scramble_password:document.getElementById('obfs-scramble').value};
    body.settings.proto=document.getElementById('obfs-proto').value;body.settings.cipher=document.getElementById('obfs-cipher').value}
  else{['Jc','Jmin','Jmax','S1','S2','H1','H2','H3','H4'].forEach(k=>{const el=document.getElementById('obfs-'+k);if(el)body.obfuscation[k]=el.value});
    if(p==='amneziawg_v2'){['S3','S4','I1','I2','I3','I4','I5'].forEach(k=>{const el=document.getElementById('obfs-'+k);if(el&&el.value)body.obfuscation[k]=el.value})}}
  await POST('/panel/api/inbounds/add',body);closeModal('addInboundModal');loadInbounds()}

// Clients
async function loadAllClients(){const r=await API('/panel/api/inbounds/list');if(!r.success)return;
  const tb=document.getElementById('clients-table');tb.innerHTML='';
  r.obj.forEach(ib=>{(ib.clients||[]).forEach(c=>{
    const used=c.up+c.down;const lim=c.total_limit||0;const pct=lim?Math.min(100,used/lim*100):0;
    tb.innerHTML+=`<tr><td>${c.username}</td><td>${ib.remark} <span class="badge badge-proto">${PL[ib.protocol]}</span></td>
      <td><code>${c.allowed_ips}</code></td><td>${fmtB(c.up)} / ${fmtB(c.down)}</td>
      <td>${lim?fmtB(lim):'Unlim.'}<div class="tbar"><div class="fill" style="width:${pct}%"></div></div></td>
      <td>${fmtDate(c.expiry_time)}</td>
      <td><span class="badge ${c.enable?'badge-on':'badge-off'}">${c.enable?'On':'Off'}</span></td>
      <td><button class="btn btn-sm btn-o" onclick="showQR(${c.id}, '${c.username}', '${ib.protocol}')">QR</button>
       <button class="btn btn-sm btn-s" onclick="toggleClient(${c.id})">${c.enable?'Pause':'Start'}</button>
       <button class="btn btn-sm btn-o" onclick="resetTraffic(${c.id})">Reset</button>
       <button class="btn btn-sm btn-d" onclick="deleteClient(${c.id})">Del</button></td></tr>`})});
  document.getElementById('clientSearch').oninput=function(){const q=this.value.toLowerCase();
    tb.querySelectorAll('tr').forEach(tr=>{tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none'})}}

async function submitClient(){const days=parseInt(document.getElementById('cl-expiry-days').value)||0;
  const expiry=days>0?Math.floor(Date.now()/1000)+days*86400:0;
  await POST('/panel/api/inbounds/addClient',{inbound_id:document.getElementById('cl-inbound-id').value,
    username:document.getElementById('cl-username').value,total_limit:document.getElementById('cl-limit').value,expiry_time:expiry});
  closeModal('addClientModal');loadAllClients();loadInbounds()}
async function toggleClient(id){await POST(`/panel/api/inbounds/toggleClient/${id}`,{});loadAllClients()}
async function resetTraffic(id){await POST(`/panel/api/inbounds/resetClientTraffic/${id}`,{});loadAllClients()}
async function deleteClient(id){if(!confirm('Delete client?'))return;await POST(`/panel/api/inbounds/delClient/${id}`,{});loadAllClients();loadInbounds()}
async function showQR(cid, username, proto){const r=await API(`/panel/api/inbounds/clientConfig/${cid}`);if(!r.success)return;
  document.getElementById('qrConfigText').value=r.config;
  const img=document.getElementById('qrImage');
  try{QRCode.toDataURL(r.config,{width:400,margin:1,color:{dark:'#000000',light:'#ffffff'}},(err,url)=>{
    if(!err) img.src=url; else console.error(err)
  })}catch(e){console.error(e)}
  const dbtn=document.getElementById('downloadBtn');
  const ext=proto.includes('openvpn')?'.ovpn':'.conf';
  dbtn.onclick=()=>{
    const blob=new Blob([r.config],{type:'text/plain'});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download=username+ext;
    document.body.appendChild(a);a.click();
    document.body.removeChild(a);URL.revokeObjectURL(url);
  };
  document.getElementById('qrModal').classList.add('show')}
function copyConfig(){const t=document.getElementById('qrConfigText');t.select();document.execCommand('copy')}

// Firewall
async function loadFirewall(){const r=await API('/panel/api/firewall/status');
  document.getElementById('fw-status').textContent=r.active?'Active':'Inactive';
  document.getElementById('fw-status').className='badge '+(r.active?'badge-on':'badge-off');
  const c=document.getElementById('fw-rules');c.innerHTML='';
  (r.rules||[]).forEach((rule,i)=>{c.innerHTML+=`<div class="fw-rule"><span>${rule}</span><button class="btn btn-sm btn-d" onclick="fwDel(${i+1})">Delete</button></div>`})}
async function fwToggle(en){await POST('/panel/api/firewall/toggle',{enable:en});loadFirewall()}
async function fwAddRule(){await POST('/panel/api/firewall/addRule',{port:document.getElementById('fw-port').value,
  proto:document.getElementById('fw-proto').value,action:document.getElementById('fw-action').value,
  from_ip:document.getElementById('fw-from').value||'any'});loadFirewall()}
async function fwDel(n){if(!confirm('Delete rule #'+n+'?'))return;await POST('/panel/api/firewall/delRule',{rule_num:n});loadFirewall()}

// System
async function loadSystem(){
  const h=await API('/panel/api/system/hostname');document.getElementById('sys-hostname').value=h.hostname||'';
  const tz=await API('/panel/api/system/timezone');document.getElementById('sys-tz').value=tz.timezone||'';
  const dns=await API('/panel/api/system/dns');document.getElementById('sys-dns').value=(dns.servers||[]).join('\n');
  const sv=await API('/panel/api/system/services');const sl=document.getElementById('services-list');sl.innerHTML='';
  (sv.services||[]).forEach(s=>{sl.innerHTML+=`<div class="fw-rule"><span><b>${s.name}</b></span><span>${s.description||''}</span></div>`})}
async function saveHostname(){await POST('/panel/api/system/hostname',{hostname:document.getElementById('sys-hostname').value})}
async function saveTimezone(){await POST('/panel/api/system/timezone',{timezone:document.getElementById('sys-tz').value})}
async function saveDNS(){const lines=document.getElementById('sys-dns').value.split('\n').map(s=>s.trim()).filter(Boolean);
  await POST('/panel/api/system/dns',{servers:lines})}

// Logs
async function loadLogs(){const unit=document.getElementById('log-unit').value;const lines=document.getElementById('log-lines').value;
  const r=await API(`/panel/api/system/logs?lines=${lines}&unit=${unit}`);
  document.getElementById('log-output').textContent=r.logs||'No output'}

// Settings
async function loadSettings(){const r=await API('/panel/api/settings');if(!r.success)return;
  document.getElementById('s-port').value=r.obj.panel_port||'9090';
  document.getElementById('s-basepath').value=r.obj.web_base_path||'';
  document.getElementById('s-timeout').value=r.obj.session_timeout||'3600';
  document.getElementById('s-tg-token').value=r.obj.tg_bot_token||'';
  document.getElementById('s-tg-chat').value=r.obj.tg_chat_id||''}
async function saveSettings(){await POST('/panel/api/settings',{panel_port:document.getElementById('s-port').value,
  web_base_path:document.getElementById('s-basepath').value,session_timeout:document.getElementById('s-timeout').value,
  tg_bot_token:document.getElementById('s-tg-token').value,tg_chat_id:document.getElementById('s-tg-chat').value})}
async function changePassword(){const r=await POST('/panel/api/settings/updateUser',{old_password:document.getElementById('s-oldpass').value,
  new_username:document.getElementById('s-newuser').value,new_password:document.getElementById('s-newpass').value});
  alert(r.success?'Updated':'Error: '+(r.msg||''))}
function importDB(){const f=document.getElementById('db-import-file').files[0];if(!f)return;
  const fd=new FormData();fd.append('file',f);fetch('/panel/api/db/import',{method:'POST',body:fd}).then(r=>r.json()).then(r=>alert(r.msg||'Done'))}

async function setupService(){if(!confirm('Create systemd service?'))return;const r=await POST('/panel/api/system/setupService',{});alert(r.msg)}
async function installFail2Ban(){if(!confirm('Install Fail2Ban?'))return;const r=await POST('/panel/api/system/installFail2Ban',{});alert(r.msg)}
async function issueSSL(){const d=document.getElementById('ssl-domain').value;if(!d)return alert('Domain required');const r=await POST('/panel/api/system/issueSSL',{domain:d});alert(r.msg)}
async function backupDB(){const r=await POST('/panel/api/db/backup',{});alert(r.msg)}

// Init
loadDashboard();setInterval(loadDashboard,15000);
</script>
</body></html>"""
