import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            reg_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone() is None:
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("INSERT INTO users (id, username, reg_date) VALUES (?, ?, ?)", 
                       (user_id, username, date))
        conn.commit()
    conn.close()