import sqlite3
from datetime import datetime

DB_PATH = "history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_input TEXT NOT NULL,
            agent TEXT,
            response TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_task(user_input, agent, response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (timestamp, user_input, agent, response) VALUES (?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_input, agent, response)
    )
    conn.commit()
    conn.close()

def get_tasks(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, user_input, agent, response FROM tasks ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT agent, COUNT(*) FROM tasks GROUP BY agent ORDER BY COUNT(*) DESC")
    by_agent = cursor.fetchall()
    conn.close()
    return total, by_agent
