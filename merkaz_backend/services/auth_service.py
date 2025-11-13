"""
Auth service - Authentication and session handling.
"""
from flask import session
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from repositories.user_repository import UserRepository
from utils.logger_config import get_logger
from utils import get_next_user_id
import config.config as config

logger = get_logger(__name__)

# Active sessions tracking
active_sessions = {}

class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def login(email, password):
        """Authenticate a user and create session."""
        logger.info(f"Login attempt for email: {email}")
        user = UserRepository.find_by_email(email)
        
        if not user or not user.check_password(password):
            logger.warning(f"Login failed - Invalid credentials for email: {email}")
            return None, "Invalid credentials"
        
        if not user.is_active:
            logger.warning(f"Login failed - Account inactive for email: {email}")
            return None, "Account inactive"
        
        # Create session
        AuthService.create_session(user)
        # Mark user online
        active_sessions[user.email] = datetime.utcnow()
        logger.debug(f"User marked online: {user.email}")
        logger.info(f"Login successful - User: {email}, Role: {'admin' if user.is_admin else 'user'}")
        
        return user, None
    
    @staticmethod
    def register(email, password):
        """Register a new user."""
        logger.info(f"Registration attempt for email: {email}")
        
        # Check if email exists
        if AuthService.email_exists(email):
            logger.warning(f"Registration failed - Email already exists: {email}")
            return None, "Email already registered or pending"
        
        # Validate password
        if len(password) < 8:
            logger.warning(f"Registration failed - Password too short for email: {email}")
            return None, "Password must be at least 8 characters long"
        
        # Create new user
        hashed_password = generate_password_hash(password)
        user_id = get_next_user_id()
        logger.debug(f"Generated user_id: {user_id} for new user: {email}")
        
        new_user = UserRepository.create_user(email=email, password=hashed_password, role='user', status='pending', user_id=user_id)
        
        # Save to pending
        pending_users = UserRepository.get_pending()
        pending_users.append(new_user)
        UserRepository.save_pending(pending_users)
        logger.info(f"User registered successfully - Email: {email}, user_id: {user_id}, status: pending")
        
        return new_user, None
    
    @staticmethod
    def reset_password(email, new_password):
        """Reset a user's password."""
        logger.info(f"Password reset attempt for email: {email}")
        
        if len(new_password) < 8:
            logger.warning(f"Password reset failed - Password too short for email: {email}")
            return False, "Password must be at least 8 characters long"
        
        users = UserRepository.get_all()
        user_found = False
        for user in users:
            if user.email == email:
                user.password = generate_password_hash(new_password)
                user_found = True
                logger.debug(f"Password hash generated for user: {email}")
                break
        
        if not user_found:
            logger.error(f"Password reset failed - User not found: {email}")
            return False, "User not found"
        
        UserRepository.save_all(users)
        logger.info(f"Password reset successful for user: {email}")
        return True, None
    
    @staticmethod
    def refresh_session():
        """Refresh the current user's session with latest data from database."""
        logger.debug("Refreshing session")
        email = session.get("email")
        
        if not email:
            logger.warning("Session refresh failed - No email in session")
            return None, "Session invalid"
        
        user = UserRepository.find_by_email(email)
        if not user:
            logger.error(f"Session refresh failed - User not found: {email}")
            return None, "User not found"
        
        # Update session
        old_is_admin = session.get("is_admin", False)
        AuthService.create_session(user)
        
        if old_is_admin != user.is_admin:
            logger.info(f"Session refreshed - Role changed for user: {email}, new role: {'admin' if user.is_admin else 'user'}")
        else:
            logger.debug(f"Session refreshed for user: {email}, role: {'admin' if user.is_admin else 'user'}")
        
        return {
            "email": user.email,
            "role": "admin" if user.is_admin else "user",
            "is_admin": user.is_admin,
            "is_active": user.is_active
        }, None
    
    @staticmethod
    def create_session(user):
        """Create a session for the given user."""
        session["logged_in"] = True
        session["email"] = user.email
        session["user_id"] = user.user_id
        session["is_admin"] = user.is_admin
        logger.debug(f"Session created - User: {user.email}, user_id: {user.user_id}, is_admin: {user.is_admin}")
    
    @staticmethod
    def clear_session():
        """Clear the current session."""
        email = session.get("email", "unknown")
        session.clear()
        logger.debug(f"Session cleared for user: {email}")
    
    @staticmethod
    def find_user_by_email(email):
        """Find a user by email in authenticated users."""
        user = UserRepository.find_by_email(email)
        logger.debug(f"User lookup - Email: {email}, Found: {user is not None}")
        return user
    
    @staticmethod
    def email_exists(email):
        """Check if an email exists in auth, pending, or denied users."""
        exists = UserRepository.find_by_email(email) or UserRepository.find_pending_by_email(email) or UserRepository.find_denied_by_email(email)
        logger.debug(f"Email existence check - Email: {email}, Exists: {exists}")
        return exists


# Legacy functions for backward compatibility
def mark_user_online():
    """Mark the current user as online."""
    email = session.get("email")
    if not email:
        logger.debug("mark_user_online called but no email in session")
        return
    active_sessions[email] = datetime.utcnow()
    logger.debug(f"User marked online: {email}")

def mark_user_offline():
    """Mark the current user as offline."""
    email = session.get("email")
    if email in active_sessions:
        del active_sessions[email]
        logger.debug(f"User marked offline: {email}")
    else:
        logger.debug(f"mark_user_offline called but user {email} not in active sessions")

def get_active_users():
    """Get list of currently active users."""
    active_count = len(active_sessions)
    logger.debug(f"Retrieved active users list, count: {active_count}")
    return list(active_sessions.keys())

def is_user_authenticated():
    """Check if the current user is authenticated."""
    is_authenticated = session.get("logged_in", False)
    logger.debug(f"Authentication check: {is_authenticated}")
    return is_authenticated

def is_user_admin():
    """Check if the current user is an admin."""
    is_admin = session.get("is_admin", False)
    logger.debug(f"Admin check: {is_admin}")
    return is_admin

def get_current_user_email():
    """Get the email of the current user."""
    email = session.get("email")
    logger.debug(f"Retrieved current user email: {email}")
    return email

def get_current_user_id():
    """Get the user ID of the current user."""
    user_id = session.get("user_id")
    logger.debug(f"Retrieved current user ID: {user_id}")
    return user_id

