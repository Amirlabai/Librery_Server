from flask import session
from datetime import datetime, timedelta
active_sessions = {}


def mark_user_online():
    email = session.get("email")
    if not email:
        return
    active_sessions[email] = datetime.utcnow()
    print(f"🟢 {email} marked online")

def mark_user_offline():
    email = session.get("email")
    if email in active_sessions:
        del active_sessions[email]
        print(f"🔴 {email} marked offline")

def get_active_users():
    return list(active_sessions.keys())
