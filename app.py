from scapy.all import ARP, Ether, srp
from flask import Flask, jsonify, render_template_string, Response
import requests
import json
import os
import psutil
import time
import threading
import csv
import io
from database import init_db, update_device, get_all_history

app = Flask(__name__)
NICKNAMES_FILE = "nicknames.json"

# Database initialize karo
init_db()

# ── Speed Monitor ─────────────────────────────────────────
current_speed = {"upload": 0, "download": 0}

def speed_monitor():
    while True:
        stats1 = psutil.net_io_counters()
        time.sleep(1)
        stats2 = psutil.net_io_counters()
        current_speed["upload"]   = round((stats2.bytes_sent - stats1.bytes_sent) / (1024 * 1024), 3)
        current_speed["download"] = round((stats2.bytes_recv - stats1.bytes_recv) / (1024 * 1024), 3)

threading.Thread(target=speed_monitor, daemon=True).start()

# ── Nicknames ─────────────────────────────────────────────
def load_nicknames():
    if os.path.exists(NICKNAMES_FILE):
        with open(NICKNAMES_FILE, "r") as f:
            return json.load(f)
    return {}

# ── Manufacturer ──────────────────────────────────────────
def get_manufacturer(mac):
    try:
        mac_prefix = mac.replace(":", "-").upper()[:8]
        url = f"https://api.macvendors.com/{mac_prefix}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.text
        return "Unknown"
    except:
        return "Unknown"

# ── Scanner ───────────────────────────────────────────────
def scan_network():
    ip_range = "192.168.1.1/24"
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=3, verbose=0)[0]

    nicknames = load_nicknames()
    devices = []
    for sent, received in result:
        mac          = received.hwsrc
        ip           = received.psrc
        name         = nicknames.get(mac, "Unknown Device")
        manufacturer = get_manufacturer(mac)

        # Database me save karo
        update_device(name, ip, mac, manufacturer)

        devices.append({
            "ip":           ip,
            "mac":          mac,
            "manufacturer": manufacturer,
            "name":         name
        })
    return devices

# ── API Routes ────────────────────────────────────────────
@app.route("/api/devices")
def api_devices():
    return jsonify(scan_network())

@app.route("/api/speed")
def api_speed():
    return jsonify(current_speed)

@app.route("/api/history")
def api_history():
    return jsonify(get_all_history())

@app.route("/api/export")
def export_csv():
    history = get_all_history()
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["Device Name", "IP Address", "MAC Address",
                     "Manufacturer", "First Seen", "Last Seen", "Uptime (mins)"])

    # Data rows
    for d in history:
        writer.writerow([
            d["name"], d["ip"], d["mac"], d["manufacturer"],
            d["first_seen"], d["last_seen"], d["uptime_mins"]
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=network_history.csv"}
    )

# ── Dashboard ─────────────────────────────────────────────
@app.route("/")
def dashboard():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Network Monitor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #0f172a;
            color: #e2e8f0;
            font-family: monospace;
            padding: 30px;
        }
        h1 { color: #38bdf8; margin-bottom: 20px; }
        h2 { color: #38bdf8; margin: 30px 0 15px 0; font-size: 16px; }

        .speed-box {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1e293b;
            border-radius: 10px;
            padding: 20px 30px;
            flex: 1;
            text-align: center;
        }
        .card h3 { color: #94a3b8; font-size: 13px; margin-bottom: 8px; }
        .card .value { font-size: 28px; font-weight: bold; }
        .upload   .value { color: #f472b6; }
        .download .value { color: #4ade80; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 10px;
        }
        th {
            background: #1e293b;
            padding: 12px;
            text-align: left;
            color: #38bdf8;
        }
        td { padding: 12px; border-bottom: 1px solid #1e293b; }
        tr:hover { background: #1e293b; }
        .online  { color: #4ade80; font-weight: bold; }
        .uptime  { color: #fbbf24; }

        .btn {
            background: #38bdf8;
            color: #0f172a;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 20px;
            margin-right: 10px;
        }
        .btn:hover { background: #7dd3fc; }
        .btn-green {
            background: #4ade80;
            color: #0f172a;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .btn-green:hover { background: #86efac; }
        #status  { color: #64748b; font-size: 12px; margin-bottom: 15px; }
        #status2 { color: #64748b; font-size: 12px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <h1>🏠 Home Network Monitor</h1>

    <!-- Speed Cards -->
    <div class="speed-box">
        <div class="card upload">
            <h3>⬆️ UPLOAD SPEED</h3>
            <div class="value" id="upload">-- MB/s</div>
        </div>
        <div class="card download">
            <h3>⬇️ DOWNLOAD SPEED</h3>
            <div class="value" id="download">-- MB/s</div>
        </div>
    </div>

    <!-- Live Devices -->
    <h2>📡 Live Devices</h2>
    <button class="btn" onclick="loadDevices()">🔄 Refresh Scan</button>
    <p id="status">Loading...</p>
    <table>
        <thead>
            <tr>
                <th>Device Name</th>
                <th>IP Address</th>
                <th>MAC Address</th>
                <th>Manufacturer</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody id="device-table">
            <tr><td colspan="5">Scanning...</td></tr>
        </tbody>
    </table>

    <!-- History -->
    <h2>📋 Device History & Uptime</h2>
    <button class="btn" onclick="loadHistory()">🔄 Refresh History</button>
    <a href="/api/export"><button class="btn-green">📤 Export CSV</button></a>
    <p id="status2">Loading...</p>
    <table>
        <thead>
            <tr>
                <th>Device Name</th>
                <th>IP Address</th>
                <th>First Seen</th>
                <th>Last Seen</th>
                <th>Uptime</th>
            </tr>
        </thead>
        <tbody id="history-table">
            <tr><td colspan="5">Loading...</td></tr>
        </tbody>
    </table>

    <script>
        // Speed
        function loadSpeed() {
            fetch("/api/speed")
                .then(r => r.json())
                .then(data => {
                    document.getElementById("upload").innerText   = data.upload   + " MB/s";
                    document.getElementById("download").innerText = data.download + " MB/s";
                });
        }

        // Live devices
        function loadDevices() {
            document.getElementById("status").innerText = "Scanning...";
            fetch("/api/devices")
                .then(r => r.json())
                .then(devices => {
                    let rows = "";
                    devices.forEach(d => {
                        rows += `<tr>
                            <td>📱 ${d.name}</td>
                            <td>${d.ip}</td>
                            <td>${d.mac}</td>
                            <td>${d.manufacturer}</td>
                            <td class="online">● Online</td>
                        </tr>`;
                    });
                    document.getElementById("device-table").innerHTML = rows;
                    document.getElementById("status").innerText =
                        "Last scan: " + new Date().toLocaleTimeString();
                });
        }

        // History
        function loadHistory() {
            document.getElementById("status2").innerText = "Loading...";
            fetch("/api/history")
                .then(r => r.json())
                .then(history => {
                    let rows = "";
                    history.forEach(d => {
                        let uptime = d.uptime_mins < 60
                            ? d.uptime_mins + " mins"
                            : Math.floor(d.uptime_mins / 60) + " hrs " + (d.uptime_mins % 60) + " mins";
                        rows += `<tr>
                            <td>📱 ${d.name}</td>
                            <td>${d.ip}</td>
                            <td>${d.first_seen}</td>
                            <td>${d.last_seen}</td>
                            <td class="uptime">⏱️ ${uptime}</td>
                        </tr>`;
                    });
                    document.getElementById("history-table").innerHTML = rows;
                    document.getElementById("status2").innerText =
                        "Updated: " + new Date().toLocaleTimeString();
                });
        }

        loadDevices();
        loadHistory();
        loadSpeed();
        setInterval(loadSpeed,   2000);
        setInterval(loadHistory, 60000);
        setInterval(loadDevices, 30000);
    </script>
</body>
</html>
""")

if __name__ == "__main__":
    print("🚀 Server start ho raha hai...")
    print("👉 Browser me kholo: http://localhost:5000")
    app.run(debug=True)