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


# ============================================
# جدول الفواتير
# ============================================
def init_invoices_db():
    """تهيئة جدول الفواتير"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT,
            number TEXT NOT NULL,
            client_name TEXT,
            total REAL,
            tax_rate REAL,
            lang TEXT,
            data_json TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_invoice(invoice, username=None, lang="fr"):
    """حفظ فاتورة في قاعدة البيانات"""
    import json
    init_invoices_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO invoices 
           (timestamp, username, number, client_name, total, tax_rate, lang, data_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username or "",
            invoice.get("number", ""),
            invoice.get("client_name", ""),
            invoice.get("total", 0),
            invoice.get("tax_rate", 0.20),
            lang,
            json.dumps(invoice, ensure_ascii=False),
        )
    )
    conn.commit()
    conn.close()
    return True


def get_invoices(username=None, limit=50):
    """جلب الفواتير (اختياري: حسب المستخدم)"""
    init_invoices_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if username:
        cursor.execute(
            """SELECT timestamp, number, client_name, total, tax_rate, lang 
               FROM invoices WHERE username = ? 
               ORDER BY id DESC LIMIT ?""",
            (username, limit)
        )
    else:
        cursor.execute(
            """SELECT timestamp, number, client_name, total, tax_rate, lang 
               FROM invoices ORDER BY id DESC LIMIT ?""",
            (limit,)
        )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_invoice_by_number(number):
    """جلب فاتورة بالكامل عبر رقمها"""
    import json
    init_invoices_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT data_json FROM invoices WHERE number = ? LIMIT 1",
        (number,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except Exception:
            return None
    return None


def get_invoices_stats(username=None):
    """إحصائيات الفواتير"""
    init_invoices_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if username:
        cursor.execute(
            "SELECT COUNT(*), COALESCE(SUM(total), 0) FROM invoices WHERE username = ?",
            (username,)
        )
    else:
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM invoices")
    count, total = cursor.fetchone()
    conn.close()
    return {"count": count or 0, "total": total or 0}

