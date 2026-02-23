import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'waste.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            fill_level REAL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fill_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id INTEGER,
            fill_level REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bin_id) REFERENCES bins(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id INTEGER,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bin_id) REFERENCES bins(id)
        )
    ''')

    # Insert real Noida bin locations if empty
    cursor.execute("SELECT COUNT(*) FROM bins")
    if cursor.fetchone()[0] == 0:
        bins = [
            ("Bin A", "Sector 18 Market", 28.5700, 77.3210),
            ("Bin B", "Sector 62 Metro", 28.6270, 77.3660),
            ("Bin C", "Botanical Garden", 28.5622, 77.3352),
            ("Bin D", "Sector 15 Park", 28.5850, 77.3150),
            ("Bin E", "DLF Mall Noida", 28.5672, 77.3210),
            ("Bin F", "Sector 29 Market", 28.5750, 77.3350),
        ]
        cursor.executemany(
            "INSERT INTO bins (name, location, latitude, longitude) VALUES (?,?,?,?)",
            bins
        )

    conn.commit()
    conn.close()

def get_all_bins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bins")
    bins = cursor.fetchall()
    conn.close()
    return bins

def update_fill_level(bin_id, fill_level):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bins SET fill_level=?, last_updated=CURRENT_TIMESTAMP WHERE id=?",
        (fill_level, bin_id)
    )
    cursor.execute(
        "INSERT INTO fill_history (bin_id, fill_level) VALUES (?,?)",
        (bin_id, fill_level)
    )
    conn.commit()
    conn.close()

def get_fill_history(bin_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT fill_level, recorded_at FROM fill_history WHERE bin_id=? ORDER BY recorded_at DESC LIMIT 10",
        (bin_id,)
    )
    history = cursor.fetchall()
    conn.close()
    return history

def log_alert(bin_id, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alerts (bin_id, message) VALUES (?,?)",
        (bin_id, message)
    )
    conn.commit()
    conn.close()