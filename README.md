# 🏠 Home Network Monitoring System

A Python-based home network monitoring dashboard that detects connected devices,
tracks bandwidth usage, monitors uptime, and maintains device history — all in a live web dashboard.

![Dashboard Preview](screenshot.png)

---

## 🔍 What It Does

- Scans your WiFi network and detects all connected devices
- Shows device name, IP address, MAC address, and manufacturer
- Monitors real-time upload and download speed
- Tracks how long each device has been connected (Uptime)
- Maintains full device history with first seen and last seen timestamps
- Export device history as CSV report

---

## 🛠️ Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python, Flask           |
| Networking | Scapy, psutil           |
| Database   | SQLite                  |
| Frontend   | HTML, CSS, JavaScript   |
| OS         | Windows / Linux         |

---

## ⚙️ How To Run

### 1. Clone the repository
git clone https://github.com/yourusername/network-monitor.git
cd network-monitor

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

### 3. Install dependencies
pip install flask flask-socketio scapy psutil requests

### 4. Install Npcap (Windows only)
Download and install from: https://npcap.com/#download
Make sure to check "WinPcap API-compatible Mode" during install.

### 5. Run the app
python app.py

### 6. Open dashboard
Open your browser and go to: http://localhost:5000

---

## 📁 Project Structure

network-monitor/
│
├── app.py              # Main Flask server + Dashboard
├── database.py         # SQLite database logic
├── nicknames.json      # Device custom names
├── network_history.db  # Auto-generated database
└── README.md

---

## 📸 Features Preview

- Live device table with Online status
- Real-time Upload and Download speed cards
- Device history table with uptime tracking
- One-click CSV export for reporting

---

## 🎯 Use Cases

- Monitor who is connected to your home WiFi
- Track bandwidth usage in real time
- Maintain logs of device activity
- Learn networking concepts hands-on

---

## 👨‍💻 Author

Himanshu — Aspiring Network Engineer / IT Support
