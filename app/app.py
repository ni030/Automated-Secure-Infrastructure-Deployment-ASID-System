from flask import Flask, jsonify, render_template_string
import subprocess

app = Flask(__name__)
print("🔥 THIS IS MY CURRENT APP")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🚀 DevOps Dashboard</title>
    <style>
        body {
            font-family: Arial;
            background: #0f172a;
            color: white;
            text-align: center;
        }
        .card {
            background: #1e293b;
            padding: 20px;
            margin: 20px;
            border-radius: 10px;
        }
        button {
            padding: 10px;
            margin: 10px;
            background: #22c55e;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>

<h1>🚀 DevOps Automation Dashboard</h1>

<div class="card">
    <h2>📦 Container Status</h2>
    <p id="status">Loading...</p>
    <button onclick="checkStatus()">Refresh</button>
</div>

<div class="card">
    <h2>⚡ Actions</h2>
    <button onclick="restart()">Restart App</button>
</div>

<script>
function checkStatus(){
    fetch('/status')
    .then(res => res.json())
    .then(data => {
        document.getElementById('status').innerText = data.status;
    });
}

function restart(){
    fetch('/restart')
    .then(res => res.json())
    .then(data => {
        alert(data.msg);
        checkStatus();
    });
}

checkStatus();
</script>

</body>
</html>
"""

@app.route("/")
def dashboard():
    return render_template_string(HTML)

@app.route("/status")
def status():
    result = subprocess.run(
        ["ssh", "ni@172.20.10.3", "docker ps"],
        capture_output=True,
        text=True
    )
    return {
        "status": result.stdout or result.stderr
    }

@app.route("/restart")
def restart():
    result = subprocess.run(
        ["ssh", "ni@172.20.10.3", "docker restart myapp"],
        capture_output=True,
        text=True
    )
    return {
        "msg": result.stdout or result.stderr
    }

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/debug")
def debug():
    result = subprocess.getoutput("which docker")
    return {"docker_path": result}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)