"""
Admin Panel — إدارة المستخدمين
"""
import os
import yaml
from datetime import datetime
from translations_ui import t
from streamlit_authenticator.utilities.hasher import Hasher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(BASE_DIR, "auth_config.yaml")


def load_config():
    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def list_users():
    config = load_config()
    users = config.get("credentials", {}).get("usernames", {})
    result = []
    for username, data in users.items():
        result.append({
            "username": username,
            "email": data.get("email", "—"),
            "name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            "roles": ", ".join(data.get("roles", [])),
        })
    return result


def add_user(username, email, first_name, last_name, password, role="user", lang="ar"):
    config = load_config()
    users = config["credentials"]["usernames"]
    if username in users:
        return False, t("adm_user_exists", lang)
    users[username] = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "password": Hasher.hash(password),
        "roles": [role],
    }
    save_config(config)
    return True, f"تمت إضافة {username}"


def delete_user(username, lang="ar"):
    config = load_config()
    users = config["credentials"]["usernames"]
    if username not in users:
        return False, t("adm_user_not_found", lang)
    del users[username]
    save_config(config)
    return True, f"تم حذف {username}"


def change_password(username, new_password, lang="ar"):
    config = load_config()
    users = config["credentials"]["usernames"]
    if username not in users:
        return False, t("adm_user_not_found", lang)
    users[username]["password"] = Hasher.hash(new_password)
    save_config(config)
    return True, f"تم تغيير كلمة سر {username}"


def stats():
    users = list_users()
    admins = [u for u in users if "admin" in u["roles"]]
    return {
        "total": len(users),
        "admins": len(admins),
        "regular": len(users) - len(admins),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
