"""
User repository - Data access layer for user data (CSV or DB).
"""
import config.config as config
from models.user_entity import User

class UserRepository:
    """Repository for user data operations."""
    
    @staticmethod
    def find_by_email(email):
        """Find a user by email in the authentication database."""
        return User.find_by_email(email)
    
    @staticmethod
    def find_pending_by_email(email):
        """Find a user by email in the pending database."""
        return User.find_pending_by_email(email)
    
    @staticmethod
    def find_denied_by_email(email):
        """Find a user by email in the denied database."""
        return User.find_denied_by_email(email)
    
    @staticmethod
    def get_all():
        """Get all authenticated users."""
        return User.get_all()
    
    @staticmethod
    def save_all(users):
        """Save all authenticated users."""
        User.save_all(users)
    
    @staticmethod
    def get_pending():
        """Get all pending users."""
        return User.get_pending()
    
    @staticmethod
    def save_pending(users):
        """Save all pending users."""
        User.save_pending(users)
    
    @staticmethod
    def get_denied():
        """Get all denied users."""
        return User.get_denied()
    
    @staticmethod
    def save_denied(users):
        """Save all denied users."""
        User.save_denied(users)
    
    @staticmethod
    def get_admin_emails():
        """Get all admin email addresses."""
        return User.get_admin_emails()

