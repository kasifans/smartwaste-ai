import sqlite3
import random
import time
import threading
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'waste.db')

# ─────────────────────────────────────────
# BIN SENSOR SCHEMA (Pathway-compatible)
# ─────────────────────────────────────────
class BinSensorSchema:
    def __init__(self, bin_id, fill_level, timestamp, location):
        self.bin_id = bin_id
        self.fill_level = fill_level
        self.timestamp = timestamp
        self.location = location

# ─────────────────────────────────────────
# LIVE SENSOR DATA GENERATOR
# ─────────────────────────────────────────
def generate_sensor_data():
    bins = [
        {"id": 1, "location": "Sector 18 Market"},
        {"id": 2, "location": "Sector 62 Metro"},
        {"id": 3, "location": "Botanical Garden"},
        {"id": 4, "location": "Sector 15 Park"},
        {"id": 5, "location": "DLF Mall Noida"},
        {"id": 6, "location": "Sector 29 Market"},
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, fill_level FROM bins")
    current_levels = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()

    readings = []
    for bin in bins:
        bin_id = bin["id"]
        current = current_levels.get(bin_id, 0)
        increase = random.uniform(0.5, 3.0)
        new_level = min(100, current + increase)

        readings.append(BinSensorSchema(
            bin_id=bin_id,
            fill_level=round(new_level, 2),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            location=bin["location"]
        ))

    return readings

# ─────────────────────────────────────────
# STREAM PROCESSOR
# ─────────────────────────────────────────
def process_stream(reading):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE bins SET fill_level=?, last_updated=? WHERE id=?",
            (reading.fill_level, reading.timestamp, reading.bin_id)
        )
        cursor.execute(
            "INSERT INTO fill_history (bin_id, fill_level) VALUES (?,?)",
            (reading.bin_id, reading.fill_level)
        )
        conn.commit()
        conn.close()

        status = "🔴 CRITICAL" if reading.fill_level >= 80 else "🟡 HIGH" if reading.fill_level >= 60 else "🟢 NORMAL"
        print(f"[Stream] Bin {reading.bin_id} | {reading.location} | {reading.fill_level}% | {status}")

        if reading.fill_level >= 80:
            trigger_alert(reading.bin_id, reading.location, reading.fill_level)

    except Exception as e:
        print(f"[Stream Error] {e}")


# ─────────────────────────────────────────
# ALERT TRIGGER
# ─────────────────────────────────────────
def trigger_alert(bin_id, location, fill_level):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM alerts 
            WHERE bin_id=? 
            AND sent_at > datetime('now', '-30 minutes')
        """, (bin_id,))
        already_alerted = cursor.fetchone()[0] > 0
        conn.close()

        if not already_alerted:
            from alerts import send_whatsapp_alert
            send_whatsapp_alert(
                bin_name=f"Bin {bin_id}",
                location=location,
                fill_level=fill_level
            )

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO alerts (bin_id, message) VALUES (?,?)",
                (bin_id, f"Auto stream alert — {fill_level}%")
            )
            conn.commit()
            conn.close()

            print(f"[Alert] WhatsApp sent for Bin {bin_id} at {fill_level}%")

    except Exception as e:
        print(f"[Alert Error] {e}")


# ─────────────────────────────────────────
# MAIN STREAMING PIPELINE
# ─────────────────────────────────────────
def run_pathway_pipeline():
    print("=" * 50)
    print("🚀 Real-Time Streaming Pipeline Started")
    print("📡 Ingesting live bin sensor data...")
    print("🔄 Update interval: 10 seconds")
    print("=" * 50)

    cycle = 0
    while True:
        cycle += 1
        print(f"\n[Pipeline] Cycle {cycle} — {datetime.now().strftime('%H:%M:%S')}")

        readings = generate_sensor_data()
        for reading in readings:
            process_stream(reading)

        print(f"[Pipeline] ✅ {len(readings)} bins updated")
        time.sleep(10)


# ─────────────────────────────────────────
# START AS BACKGROUND THREAD
# ─────────────────────────────────────────
def start_pipeline_thread():
    thread = threading.Thread(target=run_pathway_pipeline, daemon=True)
    thread.start()
    print("[Pipeline] Background streaming thread started")
    return thread


if __name__ == "__main__":
    run_pathway_pipeline()