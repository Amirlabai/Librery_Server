import os
from utils.path_utils import get_project_root
# --- Core App Settings ---
SUPER_SECRET_KEY = "123_default_secret_key_for_dev"
TOKEN_SECRET_KEY = "123_default_token_key_for_dev"

project_root = get_project_root()
SERVER_ROOT_DIR = os.path.join(project_root, "merkaz_server").replace('\\', '/')
SERVER_DATA_DIR = os.path.join(SERVER_ROOT_DIR, "data").replace('\\', '/')
SERVER_LOGS_DIR = os.path.join(SERVER_ROOT_DIR, "logs").replace('\\', '/')
SERVER_FILES_DIR = os.path.join(SERVER_ROOT_DIR, "server_files").replace('\\', '/')

# --- File Paths ---
SHARE_FOLDER = os.path.join(SERVER_FILES_DIR, "files_to_share").replace('\\', '/')
TRASH_FOLDER = os.path.join(SERVER_FILES_DIR, "trash").replace('\\', '/')
UPLOAD_FOLDER = os.path.join(SERVER_FILES_DIR, "uploads").replace('\\', '/')

# --- User Databases ---
AUTH_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "auth_users.csv").replace('\\', '/')
NEW_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "new_users.csv").replace('\\', '/')
DENIED_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "denied_users.csv").replace('\\', '/')
PASSWORD_RESET_DATABASE = os.path.join(SERVER_DATA_DIR, "password_reset.csv").replace('\\', '/')

# --- ID Sequence Management ---
ID_SEQUENCE_FILE = os.path.join(SERVER_DATA_DIR, "user_id_sequence.txt").replace('\\', '/')
UPLOAD_ID_SEQUENCE_FILE = os.path.join(SERVER_LOGS_DIR, "upload_id_sequence.txt").replace('\\', '/')

# --- Log Files (still useful for event tracking) ---
SESSION_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "session_log.csv").replace('\\', '/')
DOWNLOAD_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "download_log.csv").replace('\\', '/')
SUGGESTION_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "suggestion_log.csv").replace('\\', '/')
UPLOAD_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "upload_log.csv").replace('\\', '/') # Deprecated - kept for backward compatibility
UPLOAD_PENDING_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "upload_pending_log.csv").replace('\\', '/')  # Active pending uploads
UPLOAD_COMPLETED_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "upload_completed_log.csv").replace('\\', '/')  # Approved/moved uploads
DECLINED_UPLOAD_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "declined_log.csv").replace('\\', '/')

# --- File Upload Settings ---
# General file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
# Video file extensions
VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
# General upload size limit: 100 MB
MAX_CONTENT_LENGTH = 100 * 1024 * 1024
# Video upload size limit: 1 GB
MAX_VIDEO_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024


# --- Mail Server ---
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=465
MAIL_USERNAME="amirlabay@gmail.com"
MAIL_PASSWORD="tidvwqwiiolgmiio"
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_DEFAULT_SENDER="amirlabay@gmail.com"
