# --- Core App Settings ---
NGROK_LINK = "web_ngrok_link"
SUPER_SECRET_KEY = "123_default_secret_key_for_dev"
TOKEN_SECRET_KEY = "123_default_token_key_for_dev"
ICON_PATH = "<path to icon>.ico"

# --- File Paths ---
SHARE_FOLDER = "files_to_share"
TRASH_FOLDER = "trash"
UPLOAD_FOLDER = "uploads"

# --- User Databases ---
AUTH_USER_DATABASE = "data/auth_users.csv"
NEW_USER_DATABASE = "data/new_users.csv"
DENIED_USER_DATABASE = "data/denied_users.csv"
PASSWORD_RESET_DATABASE = "data/password_reset.csv"

# --- Log Files (still useful for event tracking) ---
SESSION_LOG_FILE = "logs/session_log.csv"
DOWNLOAD_LOG_FILE = "logs/download_log.csv"
SUGGESTION_LOG_FILE = "logs/suggestion_log.csv"
UPLOAD_LOG_FILE = "logs/upload_log.csv"
DECLINED_UPLOAD_LOG_FILE = "logs/declined_log.csv"

# --- chache files ---
ROOT_SEARCH_CACHE_FILE = "cache"

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
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'app password from google'
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = 'your_email@gmail.com'
