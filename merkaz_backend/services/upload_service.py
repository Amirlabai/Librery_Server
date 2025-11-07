"""
Upload service - File upload logic and workflow.
"""
import os
import threading
from datetime import datetime
from utils.path_utils import get_project_root
from utils.csv_utils import get_next_upload_id
from utils.log_utils import log_event
from utils.file_utils import allowed_file, is_file_malicious
import config.config as config

# File lock for thread-safe CSV logging
_log_lock = threading.Lock()

class UploadService:
    """Service for upload operations."""
    
    @staticmethod
    def get_upload_directory():
        """Get the upload directory path."""
        project_root = get_project_root()
        return os.path.join(project_root, config.UPLOAD_FOLDER)
    
    @staticmethod
    def validate_file(file):
        """Validate a file for upload."""
        if not allowed_file(file.filename):
            return False, "File type not allowed"
        
        if is_file_malicious(file.stream):
            return False, "Malicious file detected"
        
        return True, None
    
    @staticmethod
    def get_next_upload_id():
        """Get the next unique upload ID."""
        return get_next_upload_id()
    
    @staticmethod
    def log_pending_upload(upload_id, email, user_id, filename, path):
        """Log a pending upload to the pending log."""
        with _log_lock:
            log_event(config.UPLOAD_PENDING_LOG_FILE, [
                upload_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                user_id if user_id else '',
                filename,
                path
            ])
    
    @staticmethod
    def log_completed_upload(upload_id, original_timestamp, email, user_id, filename, final_path):
        """Log a completed upload to the completed log."""
        with _log_lock:
            log_event(config.UPLOAD_COMPLETED_LOG_FILE, [
                upload_id,
                original_timestamp,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                user_id if user_id else '',
                filename,
                final_path
            ])
    
    @staticmethod
    def log_declined_upload(email, user_id, filename):
        """Log a declined upload."""
        with _log_lock:
            log_event(config.DECLINED_UPLOAD_LOG_FILE, [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                user_id if user_id else '',
                filename
            ])

