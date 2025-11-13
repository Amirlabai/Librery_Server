"""
Admin service - Admin operations, approvals, and reports.
"""
from models.user_entity import User
from utils.csv_utils import get_next_user_id
from utils.logger_config import get_logger

logger = get_logger(__name__)

class AdminService:
    """Service for admin operations."""
    
    @staticmethod
    def approve_user(email):
        """Approve a pending user registration."""
        logger.info(f"Approving user: {email}")
        pending_users = User.get_pending()
        user_to_approve = next((user for user in pending_users if user.email == email), None)
        
        if not user_to_approve:
            logger.warning(f"User approval failed - User {email} not found in pending list")
            return None, f"User {email} not found in pending list"
        
        # Ensure user has an ID
        if user_to_approve.user_id is None:
            user_to_approve.user_id = get_next_user_id()
            logger.debug(f"Assigned user_id {user_to_approve.user_id} to user {email}")
        
        auth_users = User.get_all()
        user_to_approve.status = 'active'
        auth_users.append(user_to_approve)
        User.save_all(auth_users)
        logger.debug(f"User {email} added to authenticated users")
        
        remaining_pending = [user for user in pending_users if user.email != email]
        User.save_pending(remaining_pending)
        logger.debug(f"User {email} removed from pending list")
        logger.info(f"User {email} approved successfully")
        
        return user_to_approve, None
    
    @staticmethod
    def deny_user(email):
        """Deny a pending user registration."""
        logger.info(f"Denying user: {email}")
        pending_users = User.get_pending()
        user_to_deny = next((user for user in pending_users if user.email == email), None)
        
        if not user_to_deny:
            logger.warning(f"User denial failed - User {email} not found in pending list")
            return None, f"User {email} not found"
        
        # Ensure user has an ID
        if user_to_deny.user_id is None:
            user_to_deny.user_id = get_next_user_id()
            logger.debug(f"Assigned user_id {user_to_deny.user_id} to user {email}")
        
        denied_users = User.get_denied()
        denied_users.append(user_to_deny)
        User.save_denied(denied_users)
        logger.debug(f"User {email} added to denied users")
        
        remaining_pending = [user for user in pending_users if user.email != email]
        User.save_pending(remaining_pending)
        logger.debug(f"User {email} removed from pending list")
        logger.info(f"User {email} denied successfully")
        
        return user_to_deny, None
    
    @staticmethod
    def toggle_user_role(email):
        """Toggle a user's role between admin and user. Uses polymorphic User.toggle_role()."""
        logger.info(f"Toggling role for user: {email}")
        try:
            updated_user = User.toggle_role(email)
            logger.info(f"Role toggled successfully - User: {email}, New role: {updated_user.role}")
            return updated_user, None
        except ValueError as e:
            logger.error(f"Toggle role failed - User {email} not found: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def toggle_user_status(email):
        """Toggle a user's status between active and inactive. Uses User.toggle_status()."""
        logger.info(f"Toggling status for user: {email}")
        try:
            updated_user = User.toggle_status(email)
            logger.info(f"Status toggled successfully - User: {email}, New status: {updated_user.status}")
            return updated_user, None
        except ValueError as e:
            logger.error(f"Toggle status failed - User {email} not found: {str(e)}")
            return None, str(e)
    
    @staticmethod
    def re_pend_user(email):
        """Move a denied user back to pending."""
        logger.info(f"Re-pending user: {email}")
        denied_users = User.get_denied()
        user_to_re_pend = next((user for user in denied_users if user.email == email), None)
        
        if not user_to_re_pend:
            logger.warning(f"Re-pend failed - User {email} not found in denied list")
            return None, f"User {email} not found"
        
        # Ensure user has an ID
        if user_to_re_pend.user_id is None:
            user_to_re_pend.user_id = get_next_user_id()
            logger.debug(f"Assigned user_id {user_to_re_pend.user_id} to user {email}")
        
        pending_users = User.get_pending()
        pending_users.append(user_to_re_pend)
        User.save_pending(pending_users)
        logger.debug(f"User {email} moved to pending list")
        
        remaining_denied = [user for user in denied_users if user.email != email]
        User.save_denied(remaining_denied)
        logger.debug(f"User {email} removed from denied list")
        logger.info(f"User {email} moved back to pending successfully")
        
        return user_to_re_pend, None

