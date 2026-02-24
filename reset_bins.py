import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'waste.db')

def reset_bins():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Reset all bins to low levels for fresh demo
    starting_levels = [
        (1, 12.5),   # Bin A — Sector 18 Market
        (2, 8.3),    # Bin B — Sector 62 Metro
        (3, 23.7),   # Bin C — Botanical Garden
        (4, 5.1),    # Bin D — Sector 15 Park
        (5, 17.8),   # Bin E — DLF Mall Noida
        (6, 31.2),   # Bin F — Sector 29 Market
    ]
    
    for bin_id, level in starting_levels:
        cursor.execute(
            "UPDATE bins SET fill_level=?, last_updated=CURRENT_TIMESTAMP WHERE id=?",
            (level, bin_id)
        )
    
    # Clear alert history for fresh demo
    cursor.execute("DELETE FROM alerts")
    
    # Clear fill history for clean predictions
    cursor.execute("DELETE FROM fill_history")
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print("✅ Bins reset for demo day!")
    print("=" * 50)
    print("Bin A — Sector 18 Market  → 12.5%")
    print("Bin B — Sector 62 Metro   → 8.3%")
    print("Bin C — Botanical Garden  → 23.7%")
    print("Bin D — Sector 15 Park    → 5.1%")
    print("Bin E — DLF Mall Noida    → 17.8%")
    print("Bin F — Sector 29 Market  → 31.2%")
    print("=" * 50)
    print("🚀 Start app.py now for live demo!")

if __name__ == "__main__":
    reset_bins()