# Service exports
from .mail_service import (
    mail,
    send_new_user_notification,
    send_approval_email,
    send_denial_email,
    send_password_reset_email
)
from .auth_service import (
    AuthService,
    mark_user_online,
    mark_user_offline,
    get_active_users,
    is_user_authenticated,
    is_user_admin,
    get_current_user_email,
    get_current_user_id
)
from .file_service import FileService
from .upload_service import UploadService
from .admin_service import AdminService

__all__ = [
    'mail',
    'send_new_user_notification',
    'send_approval_email',
    'send_denial_email',
    'send_password_reset_email',
    'AuthService',
    'mark_user_online',
    'mark_user_offline',
    'get_active_users',
    'is_user_authenticated',
    'is_user_admin',
    'get_current_user_email',
    'get_current_user_id',
    'FileService',
    'UploadService',
    'AdminService'
]

