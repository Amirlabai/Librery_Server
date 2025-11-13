"""
User repository - Data access layer for user data (CSV or DB).
"""
import config.config as config
from models.user_entity import User
from utils.logger_config import get_logger

logger = get_logger(__name__)

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
        User.save_all(users)
        logger.info(f"Saved {len(users)} authenticated users")
    
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
    def create_user(email, password, role, status, user_id):
        """Create a new user using the factory method."""
        logger.debug(f"Creating user - Email: {email}, Role: {role}, Status: {status}, ID: {user_id}")
        user = User.create_user(email=email, password=password, role=role, status=status, user_id=user_id)
        logger.info(f"User created - Email: {email}, ID: {user_id}")
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

