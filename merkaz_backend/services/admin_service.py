"""
Admin service - Admin operations, approvals, and reports.
"""
from models.user_entity import User
from utils.csv_utils import get_next_user_id

class AdminService:
    """Service for admin operations."""
    
    @staticmethod
    def approve_user(email):
        """Approve a pending user registration."""
        pending_users = User.get_pending()
        user_to_approve = next((user for user in pending_users if user.email == email), None)
        
        if not user_to_approve:
            return None, f"User {email} not found in pending list"
        
        # Ensure user has an ID
        if user_to_approve.user_id is None:
            user_to_approve.user_id = get_next_user_id()
        
        auth_users = User.get_all()
        user_to_approve.status = 'active'
        auth_users.append(user_to_approve)
        User.save_all(auth_users)
        
        remaining_pending = [user for user in pending_users if user.email != email]
        User.save_pending(remaining_pending)
        
        return user_to_approve, None
    
    @staticmethod
    def deny_user(email):
        """Deny a pending user registration."""
        pending_users = User.get_pending()
        user_to_deny = next((user for user in pending_users if user.email == email), None)
        
        if not user_to_deny:
            return None, f"User {email} not found"
        
        # Ensure user has an ID
        if user_to_deny.user_id is None:
            user_to_deny.user_id = get_next_user_id()
        
        denied_users = User.get_denied()
        denied_users.append(user_to_deny)
        User.save_denied(denied_users)
        
        remaining_pending = [user for user in pending_users if user.email != email]
        User.save_pending(remaining_pending)
        
        return user_to_deny, None
    
    @staticmethod
    def toggle_user_role(email):
        """Toggle a user's role between admin and user."""
        users = User.get_all()
        user_found = False
        for user in users:
            if user.email == email:
                user.role = 'user' if user.is_admin else 'admin'
                user_found = True
                break
        
        if not user_found:
            return None, f"User {email} not found"
        
        User.save_all(users)
        return users, None
    
    @staticmethod
    def toggle_user_status(email):
        """Toggle a user's status between active and inactive."""
        users = User.get_all()
        user_found = False
        for user in users:
            if user.email == email:
                user.status = 'inactive' if user.is_active else 'active'
                user_found = True
                break
        
        if not user_found:
            return None, f"User {email} not found"
        
        User.save_all(users)
        return users, None

