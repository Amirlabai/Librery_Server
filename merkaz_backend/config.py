import os
# --- Core App Settings ---
SUPER_SECRET_KEY = "123_default_secret_key_for_dev"
TOKEN_SECRET_KEY = "123_default_token_key_for_dev"

SERVER_ROOT_DIR = "merkaz_server"
SERVER_DATA_DIR = os.path.join(SERVER_ROOT_DIR, "data")
SERVER_LOGS_DIR = os.path.join(SERVER_ROOT_DIR, "logs")
SERVER_FILES_DIR = os.path.join(SERVER_ROOT_DIR, "server_files")


# --- File Paths ---
SHARE_FOLDER = os.path.join(SERVER_FILES_DIR, "files_to_share")
TRASH_FOLDER = os.path.join(SERVER_FILES_DIR, "trash")
UPLOAD_FOLDER = os.path.join(SERVER_FILES_DIR, "uploads")

# --- User Databases ---
AUTH_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "auth_users.csv")
NEW_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "new_users.csv")
DENIED_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "denied_users.csv")
PASSWORD_RESET_DATABASE = os.path.join(SERVER_DATA_DIR, "password_reset.csv")

# ========== ID Sequence Management ==========
ID_SEQUENCE_FILE = os.path.join(SERVER_DATA_DIR, "user_id_sequence.txt")
UPLOAD_ID_SEQUENCE_FILE = os.path.join(SERVER_LOGS_DIR, "upload_id_sequence.txt")

# --- Log Files (still useful for event tracking) ---
SESSION_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "session_log.csv")
DOWNLOAD_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "download_log.csv")
SUGGESTION_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "suggestion_log.csv")
UPLOAD_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "upload_log.csv")  # Deprecated - kept for backward compatibility
UPLOAD_PENDING_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "upload_pending_log.csv")  # Active pending uploads
UPLOAD_COMPLETED_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "upload_completed_log.csv")  # Approved/moved uploads
DECLINED_UPLOAD_LOG_FILE = os.path.join(SERVER_LOGS_DIR, "declined_log.csv")

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
