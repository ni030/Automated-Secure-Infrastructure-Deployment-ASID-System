from flask import Flask, jsonify, render_template_string, request
import subprocess
import datetime
import ipaddress

app = Flask(__name__)

VM = "ni@172.20.10.3"
CONTAINER = "myapp"
BLOCKED_IPS = set()
LOG_FILE = "logs.txt"

# ================= SSH HELPER =================
def run_ssh(cmd):
    result = subprocess.run([
        "ssh", VM, cmd
    ], capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

# ================= HTML UI =================
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🚀 DevOps Security Dashboard</title>
<style>
    :root {
        --bg-main: #0f172a; --bg-card: #1e293b; --text-main: #f8fafc;
        --text-muted: #94a3b8; --border: #334155; --primary: #3b82f6;
        --primary-hover: #2563eb; --success: #10b981; --success-hover: #059669;
        --danger: #ef4444; --danger-hover: #dc2626; --warning: #f59e0b; 
        --warning-hover: #d97706; --input-bg: #0b1120;
    }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: var(--bg-main); color: var(--text-main); margin: 0; padding: 2rem; line-height: 1.5; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { font-size: 2rem; font-weight: 700; margin-bottom: 2rem; border-bottom: 1px solid var(--border); padding-bottom: 1rem; }
    h2 { font-size: 1.25rem; margin-top: 0; margin-bottom: 1.5rem; }
    .dashboard-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
    @media (min-width: 768px) { .dashboard-grid { grid-template-columns: 1fr 1fr; } }
    .card { background: var(--bg-card); padding: 1.5rem; border-radius: 12px; border: 1px solid var(--border); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    button { padding: 0.6rem 1.2rem; margin-right: 0.5rem; margin-bottom: 0.5rem; background: var(--primary); color: white; font-weight: 600; border: none; border-radius: 6px; cursor: pointer; transition: 0.2s ease; }
    button:hover { background: var(--primary-hover); }
    .btn-success { background: var(--success); } .btn-success:hover { background: var(--success-hover); }
    .btn-danger { background: var(--danger); } .btn-danger:hover { background: var(--danger-hover); }
    .btn-warn { background: var(--warning); color: #fff;} .btn-warn:hover { background: var(--warning-hover); }
    input { width: 100%; box-sizing: border-box; padding: 0.75rem 1rem; margin-bottom: 1rem; background: var(--input-bg); border: 1px solid var(--border); color: var(--text-main); border-radius: 6px; outline: none; }
    input:focus { border-color: var(--primary); }
    .input-group { display: flex; gap: 10px; }
    .terminal-box { background: #000000; border-radius: 8px; border: 1px solid var(--border); padding: 1rem; font-family: "JetBrains Mono", Consolas, monospace; font-size: 0.85rem; color: #4ade80; overflow-y: auto; text-align: left; }
    #logs { height: 250px; white-space: pre-wrap; }
    #fw-status { height: 150px; color: #94a3b8; white-space: pre-wrap; margin-top: 1rem;}
    .status-badge { font-size: 1.1rem; font-weight: bold; margin-bottom: 1rem; padding: 0.5rem 1rem; background: var(--input-bg); border-radius: 6px; display: inline-block; border: 1px solid var(--border); }
</style>
</head>
<body>

<div class="container">
    <h1>🚀 DevOps Automation Dashboard</h1>
    <div class="dashboard-grid">
        <div class="column">
            <div class="card" style="margin-bottom: 1.5rem;">
                <h2>📦 Container Operations</h2>
                <div id="status" class="status-badge">Loading...</div>
                <div style="margin-top: 10px;">
                    <button class="btn-success" onclick="checkStatus()">Refresh Status</button>
                    <button onclick="restart()">Restart App</button>
                    <button class="btn-success" onclick="selfHeal()">Run Self-Heal</button>
                </div>
            </div>

            <div class="card" style="margin-bottom: 1.5rem;">
                <h2>🛡️ Intrusion Response (Fast Deny)</h2>
                <input id="attack-ip" type="text" placeholder="Enter attacker IP (e.g. 192.168.1.100)">
                <button class="btn-danger" onclick="detectAttack()">Simulate Attack & Block</button>
                <div id="attackStatus" style="margin-top: 10px; font-weight: bold; color: var(--danger);"></div>
            </div>

            <div class="card">
                <h2>🔥 Advanced Firewall Rules</h2>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0;">Leave a field blank to apply to all (e.g., Port only = Any IP). Supports exact IPs or Subnets.</p>
                <div class="input-group">
                    <input id="fw-ip" type="text" placeholder="IP/Subnet (e.g. 10.0.0.5 or 10.0.0.0/24)">
                    <input id="fw-port" type="number" placeholder="Port (e.g. 80)">
                </div>
                <button class="btn-success" onclick="manageRule('allow')">Allow</button>
                <button class="btn-danger" onclick="manageRule('deny')">Deny</button>
                <button class="btn-warn" onclick="manageRule('delete')">Delete Rule</button>
                <div id="fw-status" class="terminal-box">Loading rules...</div>
            </div>
        </div>

        <div class="column">
            <div class="card" style="height: 100%; box-sizing: border-box;">
                <h2>📜 System Logs</h2>
                <div id="logs" class="terminal-box"></div>
            </div>
        </div>
    </div>
</div>

<script>
// --- Container Logic ---
function checkStatus(){ fetch('/status').then(res=>res.json()).then(data=>{ document.getElementById('status').innerText = data.status; }); }
function restart(){ fetch('/restart').then(res=>res.json()).then(data=>{ alert(data.msg); checkStatus(); loadLogs(); }); }
function selfHeal(){ fetch('/self-heal').then(res=>res.json()).then(data=>{ alert(data.msg); checkStatus(); loadLogs(); }); }

// --- Attack / IP Logic ---
function detectAttack(){
    let ip = document.getElementById('attack-ip').value;
    fetch('/detect?ip='+ip).then(res=>res.json()).then(data=>{
        document.getElementById('attackStatus').innerText = data.msg;
        document.getElementById('attack-ip').value = '';
        loadLogs(); loadFirewall();
    });
}

// --- Advanced Firewall Logic ---
function manageRule(action){
    let ip = document.getElementById('fw-ip').value.trim();
    let port = document.getElementById('fw-port').value.trim();

    fetch('/firewall/rule', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ip, port, action})
    }).then(res=>res.json()).then(data=>{
        alert(data.msg || data.error);
        if(!data.error) {
            document.getElementById('fw-ip').value = '';
            document.getElementById('fw-port').value = '';
        }
        loadFirewall(); loadLogs();
    });
}

function loadFirewall(){ fetch('/firewall/list').then(res=>res.json()).then(data=>{ document.getElementById('fw-status').innerText = data.rules; }); }
function loadLogs(){ fetch('/logs').then(res=>res.json()).then(data=>{ let logDiv = document.getElementById('logs'); logDiv.innerText = data.logs; logDiv.scrollTop = logDiv.scrollHeight; }); }

setInterval(checkStatus, 5000); setInterval(loadLogs, 5000);
checkStatus(); loadLogs(); loadFirewall();
</script>
</body>
</html>
"""

# ================= ROUTES =================
@app.route("/")
def dashboard():
    return render_template_string(HTML)

@app.route("/status")
def status():
    output = run_ssh(f"docker inspect -f '{{{{.State.Running}}}}' {CONTAINER}")
    return {"status": "🟢 Running" if "true" in output else "🔴 Stopped"}

@app.route("/restart")
def restart():
    run_ssh(f"docker restart {CONTAINER}")
    log(f"Restart triggered manually for {CONTAINER}")
    return {"msg": "Container restarted successfully."}

@app.route("/self-heal")
def self_heal():
    state = run_ssh(f"docker inspect -f '{{{{.State.Running}}}}' {CONTAINER}")
    if "false" in state:
        run_ssh(f"docker restart {CONTAINER}")
        log(f"Self-heal triggered: {CONTAINER} was down and has been restarted.")
        return {"msg": "Container was down → restarted"}
    log(f"Self-heal check passed: {CONTAINER} is healthy.")
    return {"msg": "Container healthy"}

@app.route("/detect")
def detect():
    ip = request.args.get("ip")
    if not ip: return {"msg": "No IP provided"}

    try:
        valid_ip = str(ipaddress.ip_address(ip))
        if valid_ip not in BLOCKED_IPS:
            run_ssh(f"sudo ufw deny from {valid_ip}")
            BLOCKED_IPS.add(valid_ip)
            log(f"🚨 Nmap simulated attack from {valid_ip} → BLOCKED via UFW")
            return {"msg": f"🚨 Attack detected from {valid_ip}, blocked!"}
        return {"msg": f"{valid_ip} is already blocked."}
    except ValueError:
        return {"msg": "Invalid IP format."}

# ================= ADVANCED FIREWALL =================
def validate_fw_inputs(ip_raw, port_raw):
    """Validates and formats IPs, Subnets, and Ports"""
    ip, port = None, None
    
    if ip_raw:
        try:
            ip = str(ipaddress.ip_address(ip_raw))
        except ValueError:
            try:
                # Also support CIDR subnet blocks (e.g., 192.168.1.0/24)
                ip = str(ipaddress.ip_network(ip_raw, strict=False))
            except ValueError:
                return None, None, "Invalid IP Address or Subnet format."
                
    if port_raw:
        if not str(port_raw).isdigit() or not (1 <= int(port_raw) <= 65535):
            return None, None, "Invalid port. Must be between 1 and 65535."
        port = str(port_raw)
        
    if not ip and not port:
        return None, None, "You must provide either an IP, a Port, or both."
        
    return ip, port, None

@app.route("/firewall/rule", methods=["POST"])
def manage_firewall():
    ip_raw = request.json.get("ip")
    port_raw = request.json.get("port")
    action = request.json.get("action") # Can be 'allow', 'deny', or 'delete'

    ip, port, err = validate_fw_inputs(ip_raw, port_raw)
    if err: return {"error": err}

    if action not in ['allow', 'deny', 'delete']:
        return {"error": "Invalid firewall action."}

    # Construct the base UFW targeting syntax
    if ip and port:
        target = f"from {ip} to any port {port}"
        log_target = f"IP {ip} on Port {port}"
    elif ip:
        target = f"from {ip}"
        log_target = f"IP {ip}"
    else:
        target = f"{port}"
        log_target = f"Port {port}"
        
    # Execute the UFW Commands via SSH
    if action == "delete":
        # BUG FIX: UFW requires exact matching of rule types. 
        # By attempting to delete both the 'allow' and 'deny' variations, 
        # we guarantee the rule is removed no matter how it was created.
        run_ssh(f"sudo ufw delete allow {target}")
        run_ssh(f"sudo ufw delete deny {target}")
        
        # Keep our internal tracked list synced
        if ip in BLOCKED_IPS:
            BLOCKED_IPS.discard(ip)
            
        log(f"Firewall Delete: Wiped rules for {log_target}")
        return {"msg": f"Rules successfully deleted for {log_target}"}
    else:
        # Action is either "allow" or "deny"
        run_ssh(f"sudo ufw {action} {target}")
        log(f"Firewall {action.capitalize()}: {log_target}")
        return {"msg": f"Rule added: {action.upper()} {log_target}"}

@app.route("/firewall/list")
def list_firewall():
    output = run_ssh("sudo ufw status")
    return {"rules": output}

# ================= LOGGING =================
@app.route("/logs")
def get_logs():
    try:
        with open(LOG_FILE, "r") as f:
            return {"logs": f.read()}
    except FileNotFoundError:
        return {"logs": "System started. Waiting for events..."}

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)