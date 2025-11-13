"""
File service - File management and validation.
"""
import os
import shutil
import zipfile
import csv
from io import BytesIO
from datetime import datetime
from utils.file_utils import allowed_file, is_file_malicious
from utils.path_utils import get_project_root
from utils.log_utils import log_event
from utils.logger_config import get_logger
import config.config as config

logger = get_logger(__name__)

class FileService:
    """Service for file management operations."""
    
    @staticmethod
    def get_share_directory():
        """Get the share directory path."""
        project_root = get_project_root()
        share_dir = os.path.join(project_root, config.SHARE_FOLDER)
        logger.debug(f"Retrieved share directory: {share_dir}")
        return share_dir
    
    @staticmethod
    def get_upload_directory():
        """Get the upload directory path."""
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        logger.debug(f"Retrieved upload directory: {upload_dir}")
        return upload_dir
    
    @staticmethod
    def get_trash_directory():
        """Get the trash directory path."""
        project_root = get_project_root()
        trash_dir = os.path.join(project_root, config.TRASH_FOLDER)
        logger.debug(f"Retrieved trash directory: {trash_dir}")
        return trash_dir
    
    @staticmethod
    def validate_file_extension(filename):
        """Validate if file extension is allowed."""
        is_allowed = allowed_file(filename)
        logger.debug(f"File extension validation - File: {filename}, Allowed: {is_allowed}")
        return is_allowed
    
    @staticmethod
    def validate_file_safety(file_stream):
        """Validate if file is safe (not malicious)."""
        is_safe = not is_file_malicious(file_stream)
        logger.debug(f"File safety validation - Safe: {is_safe}")
        return is_safe
    
    @staticmethod
    def create_folder(folder_path):
        """Create a folder at the specified path."""
        logger.debug(f"Creating folder: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        logger.info(f"Folder created successfully: {folder_path}")
    
    @staticmethod
    def delete_item(source_path, trash_path):
        """Move an item to trash."""
        logger.info(f"Moving item to trash - Source: {source_path}, Trash: {trash_path}")
        shutil.move(source_path, trash_path)
        logger.debug(f"Item moved to trash successfully")
    
    @staticmethod
    def create_zip_from_folder(folder_path):
        """Create a ZIP file from a folder in memory."""
        logger.debug(f"Creating ZIP from folder: {folder_path}")
        memory_file = BytesIO()
        file_count = 0
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, os.path.relpath(file_path, folder_path))
                    file_count += 1
        memory_file.seek(0)
        logger.info(f"ZIP created successfully - Folder: {folder_path}, Files: {file_count}")
        return memory_file
    
    @staticmethod
    def browse_directory(subpath):
        """Browse a directory and return files/folders with metadata."""
        logger.debug(f"Browsing directory - Path: {subpath}")
        share_dir = FileService.get_share_directory()
        upload_completed_log = os.path.join(share_dir, config.UPLOAD_COMPLETED_LOG_FILE)
        
        safe_subpath = os.path.normpath(subpath).replace('\\', '/')
        if safe_subpath == '.':
            safe_subpath = ''
        
        if '/.' in safe_subpath:
            logger.warning(f"Invalid path detected: {safe_subpath}")
            return None, "Invalid path"
        
        current_path = os.path.join(share_dir, safe_subpath)
        
        if not os.path.abspath(current_path).startswith(os.path.abspath(share_dir)):
            logger.warning(f"Access denied - Path traversal attempt: {safe_subpath}")
            return None, "Access denied"
        
        folders = []
        files = []
        
        if os.path.exists(current_path) and os.path.isdir(current_path):
            for item_name in os.listdir(current_path):
                if item_name.startswith('.'):
                    continue
                
                item_path_os = os.path.join(current_path, item_name)
                item_path_url = os.path.join(safe_subpath, item_name).replace('\\', '/')
                
                # Look up upload_id from completed log
                item_id = "0"
                try:
                    with open(upload_completed_log, mode='r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        header = next(reader, None)
                        for row in reader:
                            if len(row) >= 7 and row[6] == item_path_url:
                                item_id = row[0]
                                break
                except (FileNotFoundError, StopIteration):
                    pass
                
                item_data = {
                    "upload_id": item_id,
                    "name": item_name,
                    "path": item_path_url
                }
                
                if os.path.isdir(item_path_os):
                    item_data["is_folder"] = True
                    folders.append(item_data)
                else:
                    item_data["is_folder"] = False
                    files.append(item_data)
        
        folders.sort(key=lambda x: x['name'].lower())
        files.sort(key=lambda x: x['name'].lower())
        
        back_path = os.path.dirname(safe_subpath).replace('\\', '/') if safe_subpath else None
        
        logger.info(f"Browse completed - Path: {safe_subpath}, Files: {len(files)}, Folders: {len(folders)}")
        return {
            "files": files,
            "folders": folders,
            "current_path": safe_subpath,
            "back_path": back_path
        }, None
    
    @staticmethod
    def delete_item(item_path, email):
        """Delete an item by moving it to trash."""
        logger.info(f"Delete request - Path: {item_path}, User: {email}")
        share_dir = FileService.get_share_directory()
        trash_dir = FileService.get_trash_directory()
        
        source_path = os.path.join(share_dir, item_path)
        
        if not os.path.exists(source_path) or not source_path.startswith(share_dir):
            logger.warning(f"Delete failed - File/folder not found: {item_path}")
            return False, "File or folder not found"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(item_path)
        dest_name = f"{timestamp}_{base_name}"
        dest_path = os.path.join(trash_dir, dest_name)
        
        try:
            shutil.move(source_path, dest_path)
            log_event(config.DOWNLOAD_LOG_FILE, [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                "DELETE",
                item_path
            ])
            logger.info(f"Item deleted successfully - Path: {item_path}, Moved to trash: {dest_name}")
            return True, None
        except Exception as e:
            logger.error(f"Error deleting item: {item_path}, Error: {str(e)}", exc_info=True)
            return False, f"Error deleting item: {e}"
    
    @staticmethod
    def create_folder(parent_path, folder_name, email):
        """Create a new folder."""
        logger.info(f"Create folder request - Name: {folder_name}, Parent: {parent_path}, User: {email}")
        
        if not folder_name:
            logger.warning("Create folder failed - Empty folder name")
            return False, "Folder name cannot be empty."
        
        if '/' in folder_name or '\\' in folder_name or '..' in folder_name:
            logger.warning(f"Create folder failed - Invalid characters in name: {folder_name}")
            return False, "Invalid characters in folder name."
        
        share_dir = FileService.get_share_directory()
        
        safe_parent_path = os.path.normpath(parent_path).replace('\\', '/')
        if safe_parent_path == '.':
            safe_parent_path = ''
        
        new_folder_path = os.path.join(share_dir, safe_parent_path, folder_name)
        
        if not os.path.abspath(new_folder_path).startswith(os.path.abspath(share_dir)):
            logger.warning(f"Create folder failed - Invalid path: {new_folder_path}")
            return False, "Invalid path."
        
        if os.path.exists(new_folder_path):
            logger.warning(f"Create folder failed - Already exists: {folder_name}")
            return False, f"A folder or file named '{folder_name}' already exists."
        
        try:
            os.makedirs(new_folder_path)
            folder_path_url = os.path.join(safe_parent_path, folder_name).replace('\\', '/') if safe_parent_path else folder_name
            log_event(config.DOWNLOAD_LOG_FILE, [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                "CREATE_FOLDER",
                folder_path_url
            ])
            logger.info(f"Folder created successfully - Path: {folder_path_url}")
            return True, None
        except Exception as e:
            logger.error(f"Error creating folder: {folder_name}, Error: {str(e)}", exc_info=True)
            return False, f"Error creating folder: {e}"
    
    @staticmethod
    def get_download_file_path(file_path):
        """Get the directory and filename for file download."""
        logger.debug(f"Getting download file path - Path: {file_path}")
        share_dir = FileService.get_share_directory()
        
        directory, filename = os.path.split(file_path)
        safe_dir = os.path.join(share_dir, directory)
        
        if not safe_dir.startswith(share_dir) or not os.path.isdir(safe_dir):
            logger.warning(f"File download access denied - Path: {file_path}")
            return None, None, "Access denied"
        
        return safe_dir, filename, None
    
    @staticmethod
    def get_download_folder_path(folder_path):
        """Get the absolute path for folder download."""
        logger.debug(f"Getting download folder path - Path: {folder_path}")
        share_dir = FileService.get_share_directory()
        
        absolute_folder_path = os.path.join(share_dir, folder_path)
        
        if not os.path.isdir(absolute_folder_path) or not absolute_folder_path.startswith(share_dir):
            logger.warning(f"Folder download failed - Folder not found: {folder_path}")
            return None, "Folder not found"
        
        return absolute_folder_path, None
    
    @staticmethod
    def submit_suggestion(suggestion_text, email, session_data):
        """Submit a suggestion with cooldown management."""
        logger.debug(f"Suggestion submission - User: {email}")
        
        if not suggestion_text:
            logger.warning(f"Suggestion submission failed - Empty suggestion text, User: {email}")
            return False, "Suggestion text is required"
        
        COOLDOWN_LEVELS = [0, 60, 300, 600, 1800, 3600]
        now = datetime.now()
        last_suggestion_time_str = session_data.get("last_suggestion_time")
        cooldown_index = session_data.get("cooldown_index", 0)
        
        if last_suggestion_time_str:
            last_suggestion_time = datetime.fromisoformat(last_suggestion_time_str)
            if last_suggestion_time.date() < now.date() and cooldown_index > 0:
                cooldown_index = 0
                session_data["cooldown_index"] = 0
            elapsed_time = (now - last_suggestion_time).total_seconds()
            current_cooldown = COOLDOWN_LEVELS[cooldown_index]
            if elapsed_time < current_cooldown:
                remaining = max(1, (current_cooldown - elapsed_time) / 60)
                if remaining == 1:
                    remaining_str = str(int(current_cooldown - elapsed_time)) + " seconds"
                else:
                    remaining_str = str(int(remaining)) + " minutes"
                logger.warning(f"Suggestion submission failed - Cooldown active, User: {email}, Remaining: {remaining_str}")
                return False, f"You must wait another {remaining_str} before submitting again."
        
        log_event(config.SUGGESTION_LOG_FILE, [
            now.strftime("%Y-%m-%d %H:%M:%S"),
            email,
            suggestion_text
        ])
        logger.info(f"Suggestion submitted successfully - User: {email}, Cooldown: {COOLDOWN_LEVELS[cooldown_index]}s")
        session_data["last_suggestion_time"] = now.isoformat()
        if cooldown_index < len(COOLDOWN_LEVELS) - 1:
            session_data["cooldown_index"] = cooldown_index + 1
        
        return True, None

