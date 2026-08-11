"""
User repository - Data access layer for user data (CSV or DB).
"""
import threading

import config.config as config
from models.user_entity import User
from utils.logger_config import get_logger
from utils.path_utils import resolve_config_path

logger = get_logger(__name__)
_auth_db_lock = threading.Lock()

class UserRepository:
    """Repository for user data operations."""
    
    @staticmethod
    def find_by_email(email):
        """Find a user by email in the authentication database."""
        logger.debug(f"Finding user by email: {email}")
        return User.find_by_email(email)
    
    @staticmethod
    def find_pending_by_email(email):
        """Find a user by email in the pending database."""
        logger.debug(f"Finding pending user by email: {email}")
        return User.find_pending_by_email(email)
    
    @staticmethod
    def find_denied_by_email(email):
        """Find a user by email in the denied database."""
        logger.debug(f"Finding denied user by email: {email}")
        return User.find_denied_by_email(email)
    
    @staticmethod
    def get_all():
        """Get all authenticated users."""
        logger.debug("Retrieving all authenticated users")
        return User.get_all()
    
    @staticmethod
    def save_all(users):
        """Save all authenticated users."""
        logger.debug(f"Saving {len(users)} authenticated users")
        with _auth_db_lock:
            User.save_all(users)
        logger.info(f"Saved {len(users)} authenticated users")

    @staticmethod
    def set_challenge(email: str, challenge_value: str):
        """
        Set challenge field for a user. Returns (status, error).
        status: 'success' | 'already_activated' | 'not_found'
        """
        auth_path = resolve_config_path(config.AUTH_USER_DATABASE)
        with _auth_db_lock:
            users = User.get_all()
            user_found = False
            already_activated = False
            email = User._normalize_email(email)
            for user in users:
                if user.email == email:
                    user_found = True
                    if user.challenge == 'activated' and challenge_value == 'activated':
                        already_activated = True
                    else:
                        user.challenge = challenge_value
                    break
            if not user_found:
                return 'not_found', "User not found"
            if already_activated:
                return 'already_activated', None
            User.save_all(users)
        return 'success', None
    
    @staticmethod
    def get_pending():
        """Get all pending users."""
        logger.debug("Retrieving all pending users")
        return User.get_pending()
    
    @staticmethod
    def save_pending(users):
        """Save all pending users."""
        logger.debug(f"Saving {len(users)} pending users")
        User.save_pending(users)
        logger.info(f"Saved {len(users)} pending users")
    
    @staticmethod
    def get_denied():
        """Get all denied users."""
        logger.debug("Retrieving all denied users")
        return User.get_denied()
    
    @staticmethod
    def save_denied(users):
        """Save all denied users."""
        logger.debug(f"Saving {len(users)} denied users")
        User.save_denied(users)
        logger.info(f"Saved {len(users)} denied users")
    
    @staticmethod
    def get_admin_emails():
        """Get all admin email addresses."""
        logger.debug("Retrieving admin emails")
        return User.get_admin_emails()
    
    @staticmethod
    def create_user(email, password, role, status, user_id, is_boss_admin=False, first_name=None, last_name=None):
        """Create a new user using the factory method."""
        logger.debug(f"Creating user - Email: {email}, Role: {role}, Status: {status}, ID: {user_id}, Boss Admin: {is_boss_admin}")
        user = User.create_user(email=email, password=password, role=role, status=status, user_id=user_id, is_boss_admin=is_boss_admin, first_name=first_name, last_name=last_name)
        logger.info(f"User created - Email: {email}, ID: {user_id}, Boss Admin: {is_boss_admin}")
        return user
    
    @staticmethod
    def toggle_role(email):
        """Toggle a user's role between admin and user."""
        logger.debug(f"Toggling role for user: {email}")
        user = User.toggle_role(email)
        logger.info(f"Role toggled - Email: {email}, New role: {user.role}")
        return user
    
    @staticmethod
    def toggle_status(email):
        """Toggle a user's status between active and inactive."""
        logger.debug(f"Toggling status for user: {email}")
        user = User.toggle_status(email)
        logger.info(f"Status toggled - Email: {email}, New status: {user.status}")
        return user

    @staticmethod
    def is_user_boss_admin(email):
        """Check if a user is a boss admin."""
        user = User.find_by_email(email)
        return bool(user and user.is_boss_admin)
