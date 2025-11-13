"""
Upload repository - Manage upload logs and data.
"""
import os
import csv
import threading
import config.config as config
from utils.path_utils import get_project_root
from utils.logger_config import get_logger

logger = get_logger(__name__)

# File lock for thread-safe CSV logging
_log_lock = threading.Lock()

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
        logger.debug("Reading pending uploads")
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
        logger.debug(f"Read {len(uploads)} pending uploads")
        return uploads
    
    @staticmethod
    def read_completed_uploads():
        """Read all completed uploads from the log file."""
        logger.debug("Reading completed uploads")
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
        logger.debug(f"Read {len(uploads)} completed uploads")
        return uploads
    
    @staticmethod
    def read_declined_uploads():
        """Read all declined uploads from the log file."""
        logger.debug("Reading declined uploads")
        declined_log_path = UploadRepository.get_declined_log_path()
        uploads = []
        try:
            with open(declined_log_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uploads.append(row)
        except FileNotFoundError:
            pass
        logger.debug(f"Read {len(uploads)} declined uploads")
        return uploads
    
    @staticmethod
    def find_pending_by_id(upload_id):
        """Find a pending upload by upload_id."""
        logger.debug(f"Finding pending upload by ID: {upload_id}")
        pending_log_path = UploadRepository.get_pending_log_path()
        try:
            with open(pending_log_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reversed(list(reader)):
                    if len(row) >= 6 and row[0] == str(upload_id):
                        return {
                            'upload_id': row[0],
                            'timestamp': row[1],
                            'email': row[2],
                            'user_id': row[3],
                            'filename': row[4],
                            'path': row[5]
                        }
        except FileNotFoundError:
            pass
        return None
    
    @staticmethod
    def find_pending_by_filename(filename):
        """Find pending uploads by filename or path."""
        logger.debug(f"Finding pending uploads by filename: {filename}")
        pending_log_path = UploadRepository.get_pending_log_path()
        matches = []
        try:
            with open(pending_log_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reversed(list(reader)):
                    if len(row) >= 6:
                        if row[4] == filename or row[5] == filename:
                            matches.append({
                                'upload_id': row[0],
                                'timestamp': row[1],
                                'email': row[2],
                                'user_id': row[3],
                                'filename': row[4],
                                'path': row[5]
                            })
        except FileNotFoundError:
            pass
        return matches
    
    @staticmethod
    def remove_from_pending(upload_id):
        """Remove an entry from the pending log by upload_id."""
        logger.debug(f"Removing pending upload by ID: {upload_id}")
        pending_log_path = UploadRepository.get_pending_log_path()
        
        if not os.path.exists(pending_log_path):
            return None
        
        rows = []
        removed_row = None
        
        with _log_lock:
            try:
                with open(pending_log_path, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    rows = [header] if header else []
                    for row in reader:
                        if len(row) >= 6 and row[0] == str(upload_id):
                            removed_row = row
                        else:
                            rows.append(row)
                
                if removed_row:
                    with open(pending_log_path, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
                    logger.info(f"Removed pending upload - ID: {upload_id}")
            except (FileNotFoundError, StopIteration):
                return None
        
        return removed_row
    
    @staticmethod
    def update_completed_path(upload_id, new_path):
        """Update the path of a completed upload."""
        logger.debug(f"Updating completed upload path - ID: {upload_id}, New path: {new_path}")
        completed_log_path = UploadRepository.get_completed_log_path()
        
        rows = []
        found = False
        
        with _log_lock:
            try:
                with open(completed_log_path, mode='r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    rows = [header] if header else []
                    for row in reader:
                        if len(row) >= 7 and row[0] == str(upload_id):
                            row[6] = new_path
                            found = True
                        rows.append(row)
                
                if found:
                    with open(completed_log_path, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(rows)
                    logger.info(f"Updated completed upload path - ID: {upload_id}")
                    return True
                else:
                    logger.warning(f"Completed upload not found - ID: {upload_id}")
                    return False
            except FileNotFoundError:
                logger.error("Completed log file not found")
                return False
            except Exception as e:
                logger.error(f"Error updating completed upload path: {str(e)}")
                return False

