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

# Initialize upon import
init_db()
