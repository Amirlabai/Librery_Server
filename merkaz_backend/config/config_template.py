import os
# --- Core App Settings ---
NGROK_LINK = "change_this_to_the_ngrok_link"
SUPER_SECRET_KEY = os.urandom(32).hex()
TOKEN_SECRET_KEY = os.urandom(32).hex()
ICON_PATH = "change_this_to_the_path_of_the_icon"


SERVER_ROOT_DIR = "change_this_to_the_root_directory_of_the_project"
SERVER_DATA_DIR = os.path.join(SERVER_ROOT_DIR, "data").replace('\\', '/')
SERVER_LOGS_DIR = os.path.join(SERVER_ROOT_DIR, "logs").replace('\\', '/')
SERVER_FILES_DIR = os.path.join(SERVER_ROOT_DIR, "server_files").replace('\\', '/')
SERVER_CACHE_DIR = os.path.join(SERVER_ROOT_DIR, "cache").replace('\\', '/')

# --- File Paths ---
SHARE_FOLDER = os.path.join(SERVER_FILES_DIR, "files_to_share").replace('\\', '/')
TRASH_FOLDER = os.path.join(SERVER_FILES_DIR, "trash").replace('\\', '/')
UPLOAD_FOLDER = os.path.join(SERVER_FILES_DIR, "uploads").replace('\\', '/')

# --- User Databases ---
AUTH_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "auth_users.csv").replace('\\', '/')
NEW_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "new_users.csv").replace('\\', '/')
DENIED_USER_DATABASE = os.path.join(SERVER_DATA_DIR, "denied_users.csv").replace('\\', '/')
PASSWORD_RESET_DATABASE = os.path.join(SERVER_DATA_DIR, "password_reset.csv").replace('\\', '/')
OUTSIDE_USERS_DATABASE_SOURCE = os.path.join(SERVER_DATA_DIR, "outside_users.csv").replace('\\', '/')

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

# --- chache files ---
ROOT_SEARCH_CACHE_FILE = os.path.join(SERVER_CACHE_DIR, "cache").replace('\\', '/')

# --- useful links ---
USEFUL_LINKS_FILE = os.path.join(SERVER_DATA_DIR, "useful_links.csv").replace('\\', '/')

# --- File Upload Settings ---
# General file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', '7z', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
# Video file extensions
VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
# General upload size limit: 100 MB
MAX_CONTENT_LENGTH = 100 * 1024 * 1024
# Video upload size limit: 2 GB
MAX_VIDEO_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024


# --- Mail Server ---
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=465
MAIL_USERNAME="change_this_to_the_email_of_the_mail_server"
MAIL_PASSWORD="change_this_to_the_password_of_the_mail_server"
MAIL_USE_TLS=False
MAIL_USE_SSL=True
MAIL_DEFAULT_SENDER="change_this_to_the_email_of_the_mail_server"

# --- Rate Limiting Settings | unused for now ---
# Global rate limit: 100 requests per minute per IP (allows bursts but prevents abuse)
RATE_LIMIT_GLOBAL = "100 per minute"

# Per-endpoint rate limits (more restrictive for heavy operations)
RATE_LIMIT_BROWSE = "30 per minute"  # File browsing - prevent recursive loops
RATE_LIMIT_DOWNLOAD = "20 per minute"  # File downloads - prevent mass downloads
RATE_LIMIT_UPLOAD = "10 per minute"  # File uploads - prevent spam
RATE_LIMIT_AUTH = "5 per minute"  # Login/register - prevent brute force
RATE_LIMIT_ADMIN = "50 per minute"  # Admin endpoints - moderate limit
RATE_LIMIT_SUGGEST = "3 per minute"  # Suggestions - already has cooldown, add rate limit

# Storage backend for rate limiting (memory-based, no Redis needed)
# Uses in-memory storage by default - resets on server restart
RATE_LIMIT_STORAGE_URI = "memory://"