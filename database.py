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

    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        user_id INTEGER, 
                        text TEXT, 
                        status TEXT DEFAULT 'Open')''')
    
    conn.commit()
    conn.close()



def add_ticket(user_id, text):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (user_id, text) VALUES (?, ?)", (user_id, text))
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

def get_all_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, reg_date FROM users")
    users = cursor.fetchall()
    conn.close()
    return users
