"""
Security helpers — Rate limiting + audit
"""
import os
import json
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTEMPTS_FILE = os.path.join(BASE_DIR, "login_attempts.json")

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _load_attempts():
    if not os.path.exists(ATTEMPTS_FILE):
        return {}
    try:
        with open(ATTEMPTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_attempts(data):
    with open(ATTEMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_rate_limit(username):
    """هل المستخدم مقفل حالياً؟"""
    data = _load_attempts()
    if username not in data:
        return False, 0

    entry = data[username]
    locked_until = entry.get("locked_until")
    if not locked_until:
        return False, 0

    locked_dt = datetime.fromisoformat(locked_until)
    if datetime.now() < locked_dt:
        minutes_left = int((locked_dt - datetime.now()).total_seconds() / 60) + 1
        return True, minutes_left
    else:
        # انتهى القفل — احذفه
        del data[username]
        _save_attempts(data)
        return False, 0


def record_attempt(username, success):
    """سجّل محاولة دخول"""
    data = _load_attempts()
    now = datetime.now().isoformat()

    if username not in data:
        data[username] = {"attempts": 0, "last_attempt": now, "locked_until": None}

    if success:
        # نجح — صفّر
        data[username] = {"attempts": 0, "last_attempt": now, "locked_until": None}
    else:
        data[username]["attempts"] = data[username].get("attempts", 0) + 1
        data[username]["last_attempt"] = now
        if data[username]["attempts"] >= MAX_ATTEMPTS:
            lock_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
            data[username]["locked_until"] = lock_until

    _save_attempts(data)
    return data[username]["attempts"]


def get_stats():
    """إحصائيات المحاولات"""
    data = _load_attempts()
    locked = sum(1 for u in data.values() if u.get("locked_until") and 
                 datetime.fromisoformat(u["locked_until"]) > datetime.now())
    return {
        "total_users_tracked": len(data),
        "currently_locked": locked,
    }
