"""
Upload repository - Manage upload logs and data.
"""
import os
import csv
import config.config as config
from utils.path_utils import get_project_root

class UploadRepository:
    """Repository for upload data operations."""
    
    @staticmethod
    def get_pending_log_path():
        """Get the path to the pending upload log file."""
        project_root = get_project_root()
        return os.path.join(project_root, config.UPLOAD_PENDING_LOG_FILE)
    
    @staticmethod
    def get_completed_log_path():
        """Get the path to the completed upload log file."""
        project_root = get_project_root()
        return os.path.join(project_root, config.UPLOAD_COMPLETED_LOG_FILE)
    
    @staticmethod
    def get_declined_log_path():
        """Get the path to the declined upload log file."""
        project_root = get_project_root()
        return os.path.join(project_root, config.DECLINED_UPLOAD_LOG_FILE)
    
    @staticmethod
    def read_pending_uploads():
        """Read all pending uploads from the log file."""
        pending_log_path = UploadRepository.get_pending_log_path()
        uploads = []
        try:
            with open(pending_log_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 6:
                        uploads.append({
                            'upload_id': row[0],
                            'timestamp': row[1],
                            'email': row[2],
                            'user_id': row[3],
                            'filename': row[4],
                            'path': row[5]
                        })
        except FileNotFoundError:
            pass
        return uploads
    
    @staticmethod
    def read_completed_uploads():
        """Read all completed uploads from the log file."""
        completed_log_path = UploadRepository.get_completed_log_path()
        uploads = []
        try:
            with open(completed_log_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 7:
                        uploads.append({
                            'upload_id': row[0],
                            'original_timestamp': row[1],
                            'approval_timestamp': row[2],
                            'email': row[3],
                            'user_id': row[4],
                            'filename': row[5],
                            'final_path': row[6]
                        })
        except FileNotFoundError:
            pass
        return uploads

