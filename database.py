import sqlite3
from datetime import datetime

DB_FILE = "network_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Device history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            ip          TEXT,
            mac         TEXT,
            manufacturer TEXT,
            first_seen  TEXT,
            last_seen   TEXT,
            uptime_mins INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database ready!")

def update_device(name, ip, mac, manufacturer):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Pehle check karo — ye device pehle aaya tha?
    cursor.execute("SELECT id, uptime_mins FROM device_history WHERE mac = ?", (mac,))
    existing = cursor.fetchone()
    
    if existing:
        # Device pehle se hai — update karo
        cursor.execute("""
            UPDATE device_history
            SET last_seen = ?, uptime_mins = uptime_mins + 1, ip = ?, name = ?
            WHERE mac = ?
        """, (now, ip, name, mac))
    else:
        # Naya device — insert karo
        cursor.execute("""
            INSERT INTO device_history (name, ip, mac, manufacturer, first_seen, last_seen, uptime_mins)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (name, ip, mac, manufacturer, now, now))
    
    conn.commit()
    conn.close()

def get_all_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, ip, mac, manufacturer, first_seen, last_seen, uptime_mins
        FROM device_history
        ORDER BY last_seen DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "name":         row[0],
            "ip":           row[1],
            "mac":          row[2],
            "manufacturer": row[3],
            "first_seen":   row[4],
            "last_seen":    row[5],
            "uptime_mins":  row[6]
        })
    return history

def test_db():
    init_db()
    # Test data daalo
    update_device("Himanshu Laptop", "192.168.1.7", "44:f7:9f:7d:d8:6f", "Cloud Network")
    update_device("Mera Phone",      "192.168.1.8", "5a:59:12:4c:af:41", "Unknown")
    update_device("Wifi Router",     "192.168.1.1", "24:de:8a:4b:2c:11", "Nokia")
    
    print("\n📋 Database me saved devices:")
    print("-" * 60)
    for d in get_all_history():
        print(f"{d['name']:<20} | {d['ip']:<15} | Uptime: {d['uptime_mins']} mins")

if __name__ == "__main__":
    test_db()