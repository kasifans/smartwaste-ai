import sqlite3
import os

# Use /tmp for Render deployment, local database folder otherwise
if os.environ.get("RENDER"):
    DB_PATH = "/tmp/waste.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'waste.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bins (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            fill_level REAL DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fill_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id INTEGER,
            fill_level REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_id INTEGER,
            message TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert default bins if empty
    cursor.execute("SELECT COUNT(*) FROM bins")
    if cursor.fetchone()[0] == 0:
        bins = [
            (1, "Bin A", "Sector 18 Market", 28.5700, 77.3210, 12.5),
            (2, "Bin B", "Sector 62 Metro", 28.6270, 77.3660, 8.3),
            (3, "Bin C", "Botanical Garden", 28.5622, 77.3352, 23.7),
            (4, "Bin D", "Sector 15 Park", 28.5850, 77.3150, 5.1),
            (5, "Bin E", "DLF Mall Noida", 28.5672, 77.3210, 17.8),
            (6, "Bin F", "Sector 29 Market", 28.5750, 77.3350, 31.2),
        ]
        cursor.executemany(
            "INSERT INTO bins (id, name, location, latitude, longitude, fill_level) VALUES (?,?,?,?,?,?)",
            bins
        )

    conn.commit()
    conn.close()


def get_all_bins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location, latitude, longitude, fill_level, last_updated FROM bins")
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