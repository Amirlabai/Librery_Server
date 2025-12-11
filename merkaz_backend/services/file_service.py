"""
File service - File management and validation.
"""
import pandas as pd
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
from repositories.download_repository import DownloadRepository
from repositories.suggestion_repository import SuggestionRepository
from repositories.upload_repository import UploadRepository
import config.config as config
import time
import threading

logger = get_logger(__name__)

# Cache monitoring state
_pending_log_monitor_lock = threading.Lock()
_pending_log_row_count = None
_pending_log_last_change_time = None
_cache_priming_timer = None

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
    def _has_files_recursive(directory_path):
        """
        Recursively check if a directory contains any files at any depth.
        
        Args:
            directory_path: Path to the directory to check
            
        Returns:
            True if the directory contains files at any depth, False if completely empty
        """
        if not os.path.isdir(directory_path):
            return False

        try:
            size = 0
            has_files = False
            for item_name in os.listdir(directory_path):
                if item_name.startswith('.'):
                    continue
                
                item_path = os.path.join(directory_path, item_name)
                
                # If it's a file, return True immediately
                if os.path.isfile(item_path):
                    size += os.path.getsize(item_path)
                    has_files = True
                
                # If it's a directory, recursively check it
                if os.path.isdir(item_path):
                    _has_files, sub_size = FileService._has_files_recursive(item_path)
                    size += sub_size
                    if _has_files:
                        has_files = True
            
            # Return whether files were found and total size
            return has_files, size
        except (PermissionError, OSError) as e:
            logger.warning(f"Error checking directory {directory_path}: {e}")
            return False, 0
    
    @staticmethod
    def browse_directory(subpath):
        """Browse a directory and return files/folders with metadata."""
        logger.debug(f"Browsing directory - Path: {subpath}")
        share_dir = FileService.get_share_directory()
        upload_completed_log = UploadRepository.get_completed_log_path()
        
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
                
                # Check if folder contains files recursively
                if os.path.isdir(item_path_os):
                    has_files, size = FileService._has_files_recursive(item_path_os)
                else:
                    # For files, get the file size
                    try:
                        size = os.path.getsize(item_path_os)
                        has_files = True
                    except (OSError, PermissionError):
                        size = 0
                        has_files = False

                item_data = {
                    "upload_id": item_id,
                    "name": item_name,
                    "path": item_path_url,
                    "has_files": has_files,
                    "size": size
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
            log_event(DownloadRepository.get_download_log_path(), [
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
            log_event(DownloadRepository.get_download_log_path(), [
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
    def get_file_mime_type(file_path):
        """Get MIME type of a file."""
        try:
            import magic
            with open(file_path, 'rb') as f:
                file_signature = f.read(2048)
                mime_type = magic.from_buffer(file_signature, mime=True)
                return mime_type
        except Exception as e:
            logger.warning(f"Could not determine MIME type for {file_path}: {e}")
            # Fallback to extension-based detection
            ext = os.path.splitext(file_path)[1].lower()
            mime_map = {
                '.txt': 'text/plain',
                '.pdf': 'application/pdf',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.mp4': 'video/mp4',
                '.mov': 'video/quicktime',
                '.avi': 'video/x-msvideo',
                '.mkv': 'video/x-matroska',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xls': 'application/vnd.ms-excel',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.zip': 'application/zip',
                '.rar': 'application/x-rar-compressed',
                '.7z': 'application/x-7z-compressed'
            }
            return mime_map.get(ext, 'application/octet-stream')
    
    @staticmethod
    def is_previewable(file_path):
        """Check if file can be previewed in browser."""
        mime_type = FileService.get_file_mime_type(file_path)
        previewable_types = [
            'text/', 'image/', 'application/pdf', 'video/',
            'application/vnd.openxmlformats-officedocument',
            'application/vnd.ms-'
        ]
        return any(mime_type.startswith(prefix) for prefix in previewable_types)
    
    @staticmethod
    def get_preview_file_path(file_path):
        """Get the directory and filename for file preview."""
        logger.debug(f"Getting preview file path - Path: {file_path}")
        share_dir = FileService.get_share_directory()
        
        directory, filename = os.path.split(file_path)
        safe_dir = os.path.join(share_dir, directory)
        full_path = os.path.join(safe_dir, filename)
        
        if not os.path.abspath(full_path).startswith(os.path.abspath(share_dir)):
            logger.warning(f"File preview access denied - Path: {file_path}")
            return None, None, None, "Access denied"
        
        if not os.path.exists(full_path):
            logger.warning(f"File preview failed - File not found: {file_path}")
            return None, None, None, "File not found"
        
        mime_type = FileService.get_file_mime_type(full_path)
        return safe_dir, filename, mime_type, None
    
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
    def _get_pending_log_row_count():
        """Get the current row count of upload_pending_log.csv (excluding header)."""
        try:
            if not os.path.exists(config.UPLOAD_PENDING_LOG_FILE):
                return 0
            with open(config.UPLOAD_PENDING_LOG_FILE, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                return sum(1 for _ in reader)
        except Exception as e:
            logger.warning(f"Error reading pending log row count: {e}")
            return None

    @staticmethod
    def _check_and_trigger_cache_priming():
        """Check if pending log hasn't changed in 1 minute and trigger cache priming."""
        global _pending_log_row_count, _pending_log_last_change_time, _cache_priming_timer
        
        with _pending_log_monitor_lock:
            current_count = FileService._get_pending_log_row_count()
            current_time = time.time()
            
            if current_count is None:
                return
            
            # Initialize tracking on first call
            if _pending_log_row_count is None:
                _pending_log_row_count = current_count
                _pending_log_last_change_time = current_time
                logger.debug(f"Initialized pending log monitoring - Row count: {current_count}")
                
                # Schedule first check in 1 minute
                _cache_priming_timer = threading.Timer(60.0, FileService._trigger_cache_priming)
                _cache_priming_timer.daemon = True
                _cache_priming_timer.start()
                logger.debug("Scheduled initial cache priming check in 1 minute")
                return
            
            # If count changed, update tracking
            if current_count != _pending_log_row_count:
                _pending_log_row_count = current_count
                _pending_log_last_change_time = current_time
                logger.debug(f"Pending log changed - Row count: {current_count}")
                
                # Cancel existing timer if any
                if _cache_priming_timer:
                    _cache_priming_timer.cancel()
                    _cache_priming_timer = None
                
                # Schedule new check in 1 minute
                _cache_priming_timer = threading.Timer(60.0, FileService._trigger_cache_priming)
                _cache_priming_timer.daemon = True
                _cache_priming_timer.start()
                logger.debug("Scheduled cache priming check in 1 minute")
            else:
                # Count hasn't changed, check if 1 minute has passed
                if _pending_log_last_change_time is not None:
                    elapsed = current_time - _pending_log_last_change_time
                    if elapsed >= 60.0:
                        FileService._trigger_cache_priming()
                        _pending_log_last_change_time = None
                        _cache_priming_timer = None

    @staticmethod
    def _trigger_cache_priming():
        """Trigger cache priming in a background thread."""
        logger.info("Triggering cache priming after 1 minute of no pending log changes")
        thread = threading.Thread(target=FileService.prime_search_cache, daemon=True)
        thread.start()

    @staticmethod
    def monitor_pending_log_changes():
        """
        Monitor upload_pending_log.csv for changes.
        When row count hasn't changed for 1 minute, triggers cache priming.
        Should be called after operations that modify the pending log.
        """
        FileService._check_and_trigger_cache_priming()

    @staticmethod
    def prime_search_cache():
        """
        Prime the search cache by reading upload_completed_log.csv and splitting it
        into separate CSV files based on the first character of filenames (a-z).
        Files starting with non-a-z characters are saved to misc.csv.
        """
        logger.info("Starting search cache priming")
        start_time = time.time()
        
        try:
            # Ensure cache directory exists
            if not os.path.exists(config.ROOT_SEARCH_CACHE_FILE):
                os.makedirs(config.ROOT_SEARCH_CACHE_FILE)
                logger.info(f"Created cache directory: {config.ROOT_SEARCH_CACHE_FILE}")
            
            # Read the upload completed log
            df = pd.read_csv(config.UPLOAD_COMPLETED_LOG_FILE, encoding='utf-8')
            logger.debug(f"Loaded {len(df)} rows from upload_completed_log.csv")
            
            # Dictionary to store rows grouped by first letter
            cache_dict = {}
            misc_rows = []
            
            # Process each row
            for idx, row in df.iterrows():
                filename = str(row['filename']) if pd.notna(row['filename']) else ''
                
                if not filename:
                    misc_rows.append(row)
                    continue
                
                # Get first character and convert to lowercase
                first_char = filename[0].lower()
                
                # Check if it's a-z
                if first_char.isalpha() and 'a' <= first_char <= 'z':
                    if first_char not in cache_dict:
                        cache_dict[first_char] = []
                    cache_dict[first_char].append(row)
                else:
                    # Non-a-z character, add to misc
                    misc_rows.append(row)
            
            # Save each letter's cache file (without headers to match search_uploaded_files reading format)
            for letter, rows in cache_dict.items():
                cache_file_path = os.path.join(config.ROOT_SEARCH_CACHE_FILE, f"{letter}.csv")
                letter_df = pd.DataFrame(rows)
                letter_df.to_csv(cache_file_path, index=False, header=False, encoding='utf-8')
                logger.debug(f"Saved {len(rows)} rows to {letter}.csv")
            
            # Save misc file for non-a-z files
            if misc_rows:
                misc_file_path = os.path.join(config.ROOT_SEARCH_CACHE_FILE, "misc.csv")
                misc_df = pd.DataFrame(misc_rows)
                misc_df.to_csv(misc_file_path, index=False, header=False, encoding='utf-8')
                logger.debug(f"Saved {len(misc_rows)} rows to misc.csv")
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"Search cache priming completed - Elapsed time: {elapsed_time:.2f} seconds, "
                       f"Created {len(cache_dict)} letter files, {len(misc_rows)} misc files")
            
            return True, None
            
        except FileNotFoundError:
            error_msg = f"Upload completed log file not found: {config.UPLOAD_COMPLETED_LOG_FILE}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            logger.exception("Error during search cache priming")
            return False, str(e)

    @staticmethod
    def search_uploaded_files(query, folder_path=''):
        """
        Search for uploaded files in the upload_completed_log based on a query string
        against the filename (column 6).
        Returns a dict in the format similar to browse_directory() with file results.
        """
        start_time = time.time()
        logger.debug(f"Searching uploaded files - Query: {query}")
        files = []

        try:
            # Get first character of query and build cache file path
            if not query:
                return {
                    "files": [],
                    "folders": [],
                    "current_path": "",
                    "back_path": None
                }, "Empty query"
            
            first_char = query[0].lower()
            
            # Determine cache file: a-z use letter.csv, others use misc.csv
            if first_char.isalpha() and 'a' <= first_char <= 'z':
                cache_file_path = os.path.join(config.ROOT_SEARCH_CACHE_FILE, f"{first_char}.csv")
            else:
                cache_file_path = os.path.join(config.ROOT_SEARCH_CACHE_FILE, "misc.csv")
            
            # Load the cache CSV file into DataFrame
            df = pd.read_csv(cache_file_path, header=None, encoding='utf-8')

            if folder_path:
                df = df[df[6].str.contains(folder_path, na=False, case=False)]

            # Column 5 (0-indexed) is the filename
            matching = df[df[5].str.contains(query, na=False, case=False)]
            for idx, row in matching.iterrows():
                item_data = {
                    "upload_id": str(row[0]),
                    "name": row[5],
                    "path": row[6],
                    "is_folder": False
                }
                files.append(item_data)
            files.sort(key=lambda x: x['name'].lower())
        except FileNotFoundError:
            logger.warning(f"Search cache file not found: {cache_file_path}")
            FileService._trigger_cache_priming()
            return {
                "files": [],
                "folders": [],
                "current_path": "",
                "back_path": None
            }, "Search cache file not found"
        except Exception as e:
            logger.exception("Error during search_uploaded_files")
            return {
                "files": [],
                "folders": [],
                "current_path": "",
                "back_path": None
            }, str(e)

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Search completed - Query: {query}, Elapsed time: {elapsed_time} seconds")
        return {
            "files": files,
            "folders": [],
            "current_path": f"search:{query}",
            "back_path": None
        }, None
    
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
        
        log_event(SuggestionRepository.get_suggestion_log_path(), [
            now.strftime("%Y-%m-%d %H:%M:%S"),
            email,
            suggestion_text
        ])
        logger.info(f"Suggestion submitted successfully - User: {email}, Cooldown: {COOLDOWN_LEVELS[cooldown_index]}s")
        session_data["last_suggestion_time"] = now.isoformat()
        if cooldown_index < len(COOLDOWN_LEVELS) - 1:
            session_data["cooldown_index"] = cooldown_index + 1
        
        return True, None

