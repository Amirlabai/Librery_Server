"""
Auth service - Authentication and session handling.
"""
from flask import session
from datetime import datetime, timedelta

# Active sessions tracking
active_sessions = {}

def mark_user_online():
    """Mark the current user as online."""
    email = session.get("email")
    if not email:
        return
    active_sessions[email] = datetime.utcnow()
    print(f"🟢 {email} marked online")

def mark_user_offline():
    """Mark the current user as offline."""
    email = session.get("email")
    if email in active_sessions:
        del active_sessions[email]
        print(f"🔴 {email} marked offline")

def get_active_users():
    """Get list of currently active users."""
    return list(active_sessions.keys())

def is_user_authenticated():
    """Check if the current user is authenticated."""
    return session.get("logged_in", False)

def is_user_admin():
    """Check if the current user is an admin."""
    return session.get("is_admin", False)

def get_current_user_email():
    """Get the email of the current user."""
    return session.get("email")

def get_current_user_id():
    """Get the user ID of the current user."""
    return session.get("user_id")

