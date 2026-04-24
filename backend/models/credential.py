import sqlite3
import os

DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/database"
DB_PATH = os.path.join(DB_DIR, "credentials.db")

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credential_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_ip VARCHAR(15) NOT NULL,
            service VARCHAR(20) NOT NULL,
            username VARCHAR(64) NOT NULL,
            password VARCHAR(256) NOT NULL,
            result VARCHAR(20) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_credential(target_ip: str, service: str, username: str, password: str, result: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO credential_attempts (target_ip, service, username, password, result)
        VALUES (?, ?, ?, ?, ?)
    """, (target_ip, service, username, password, result))
    conn.commit()
    conn.close()

def get_all_credentials():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM credential_attempts ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]

def batch_import_hashes(lines: list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse basic "user:hash" format if possible
        parts = line.split(":")
        if len(parts) >= 2:
            user = parts[0]
            password = ":".join(parts[1:])
        else:
            user = "Unknown"
            password = line
            
        cursor.execute("""
            INSERT INTO credential_attempts (target_ip, service, username, password, result)
            VALUES (?, ?, ?, ?, ?)
        """, ("Unknown", "Hash Dump", user, password, "unparsed_hash"))
        count += 1
        
    conn.commit()
    conn.close()
    return {"status": "success", "imported": count}

# Initialize upon import
init_db()
