"""
Upload service - File upload logic and workflow.
"""
import os
import shutil
import threading
from datetime import datetime
from utils.path_utils import get_project_root
from utils.csv_utils import get_next_upload_id
from utils.log_utils import log_event
from utils.file_utils import allowed_file, is_file_malicious
from utils.logger_config import get_logger
from repositories.user_repository import UserRepository
from repositories.upload_repository import UploadRepository
import config.config as config

logger = get_logger(__name__)

# File lock for thread-safe CSV logging
_log_lock = threading.Lock()

class UploadService:
    """Service for upload operations."""
    
    @staticmethod
    def get_upload_directory():
        """Get the upload directory path."""
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        logger.debug(f"Retrieved upload directory: {upload_dir}")
        return upload_dir
    
    @staticmethod
    def validate_file(file):
        """Validate a file for upload."""
        logger.debug(f"Validating file for upload: {file.filename}")
        if not allowed_file(file.filename):
            logger.warning(f"File validation failed - File type not allowed: {file.filename}")
            return False, "File type not allowed"
        
        if is_file_malicious(file.stream):
            logger.warning(f"File validation failed - Malicious file detected: {file.filename}")
            return False, "Malicious file detected"
        
        logger.debug(f"File validation successful: {file.filename}")
        return True, None
    
    @staticmethod
    def get_next_upload_id():
        """Get the next unique upload ID."""
        upload_id = get_next_upload_id()
        logger.debug(f"Generated next upload ID: {upload_id}")
        return upload_id
    
    @staticmethod
    def log_pending_upload(upload_id, email, user_id, filename, path):
        """Log a pending upload to the pending log."""
        logger.debug(f"Logging pending upload - ID: {upload_id}, File: {filename}, User: {email}")
        with _log_lock:
            log_event(config.UPLOAD_PENDING_LOG_FILE, [
                upload_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                user_id if user_id else '',
                filename,
                path
            ])
        logger.info(f"Pending upload logged - ID: {upload_id}, File: {filename}")
    
    @staticmethod
    def log_completed_upload(upload_id, original_timestamp, email, user_id, filename, final_path):
        """Log a completed upload to the completed log."""
        logger.debug(f"Logging completed upload - ID: {upload_id}, File: {filename}, User: {email}")
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
        logger.info(f"Completed upload logged - ID: {upload_id}, File: {filename}, Path: {final_path}")
    
    @staticmethod
    def log_declined_upload(email, user_id, filename):
        """Log a declined upload."""
        logger.debug(f"Logging declined upload - File: {filename}, User: {email}")
        with _log_lock:
            log_event(config.DECLINED_UPLOAD_LOG_FILE, [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                email,
                user_id if user_id else '',
                filename
            ])
        logger.info(f"Declined upload logged - File: {filename}, User: {email}")
    
    @staticmethod
    def get_unique_filename(upload_dir, filename, share_dir=None, share_subpath='', save_flat=True):
        """
        Generates a unique filename by appending _1, _2, etc. if a file with the same name exists.
        Checks in both the upload directory and the share directory (eventual destination).
        
        For folder uploads: saves files flat in uploads directory but preserves path in metadata.
        
        Args:
            upload_dir: Base upload directory
            filename: Original filename (may include relative path for folder uploads)
            share_dir: Optional base share directory to check for conflicts
            share_subpath: Optional subpath in share directory where file will eventually be placed
            save_flat: If True, save files flat (no directory structure) in upload_dir
        
        Returns:
            Tuple of (flat_filename_for_storage, full_save_path, full_relative_path_for_log)
        """
        # Extract directory structure and base filename
        if '/' in filename or '\\' in filename:
            dir_part = os.path.dirname(filename)
            base_name = os.path.basename(filename)
            full_relative_path = filename.replace('\\', '/')
        else:
            dir_part = ''
            base_name = filename
            full_relative_path = filename
        
        # For flat storage, always save to root of upload_dir
        if save_flat:
            target_dir = upload_dir
        else:
            target_dir = os.path.join(upload_dir, dir_part) if dir_part else upload_dir
        
        os.makedirs(target_dir, exist_ok=True)
        
        # Split base name into name and extension
        if '.' in base_name:
            name_part, ext = base_name.rsplit('.', 1)
        else:
            name_part = base_name
            ext = ''
        
        # Try original filename first
        counter = 0
        while True:
            if counter == 0:
                unique_base = base_name
            else:
                if ext:
                    unique_base = f"{name_part}_{counter}.{ext}"
                else:
                    unique_base = f"{name_part}_{counter}"
            
            full_path_upload = os.path.join(target_dir, unique_base)
            file_exists_in_upload = os.path.exists(full_path_upload)
            
            file_exists_in_share = False
            if share_dir and share_subpath:
                if dir_part:
                    share_path_with_structure = os.path.join(share_subpath, dir_part, unique_base).replace('\\', '/')
                else:
                    share_path_with_structure = os.path.join(share_subpath, unique_base).replace('\\', '/')
                share_dest_path = os.path.join(share_dir, share_path_with_structure)
                file_exists_in_share = os.path.exists(share_dest_path)
            elif share_dir:
                if dir_part:
                    share_dest_path = os.path.join(share_dir, dir_part, unique_base)
                else:
                    share_dest_path = os.path.join(share_dir, unique_base)
                file_exists_in_share = os.path.exists(share_dest_path)
            
            if not file_exists_in_upload and not file_exists_in_share:
                if dir_part and counter == 0:
                    full_relative_path_for_log = os.path.join(dir_part, unique_base).replace('\\', '/')
                elif dir_part:
                    full_relative_path_for_log = os.path.join(dir_part, unique_base).replace('\\', '/')
                else:
                    full_relative_path_for_log = unique_base
                
                return unique_base, full_path_upload, full_relative_path_for_log
            
            counter += 1
    
    @staticmethod
    def remove_from_pending_log(upload_id):
        """Remove an entry from the pending log by upload_id."""
        logger.debug(f"Removing pending upload by ID: {upload_id}")
        removed_row = UploadRepository.remove_from_pending(upload_id)
        return removed_row
    
    @staticmethod
    def upload_files(uploaded_files, upload_subpath, email, user_id):
        """Process multiple file uploads."""
        logger.info(f"Upload request - Files: {len(uploaded_files)}, User: {email}")
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        share_dir = os.path.join(project_root, config.SHARE_FOLDER)
        
        successful_uploads = []
        errors = []
        failed_files_by_type = {}
        
        for file in uploaded_files:
            if not file:
                continue
            
            filename = file.filename
            
            # Validate file
            is_valid, error_msg = UploadService.validate_file(file)
            if not is_valid:
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'no extension'
                error_type = 'file_type_not_allowed' if 'not allowed' in error_msg else 'malicious_file'
                if error_type not in failed_files_by_type:
                    failed_files_by_type[error_type] = {}
                if ext not in failed_files_by_type[error_type]:
                    failed_files_by_type[error_type][ext] = []
                failed_files_by_type[error_type][ext].append(filename)
                errors.append(f"{error_msg}: {filename}")
                continue
            
            # Security check
            if '..' in filename.split('/') or '..' in filename.split('\\') or os.path.isabs(filename):
                errors.append(f"Invalid path in filename: '{filename}' was skipped.")
                continue
            
            # Get unique filename
            try:
                with _log_lock:
                    flat_filename, save_path, full_relative_path = UploadService.get_unique_filename(
                        upload_dir,
                        filename,
                        share_dir=share_dir,
                        share_subpath=upload_subpath,
                        save_flat=True
                    )
            except Exception as e:
                errors.append(f"Could not generate unique filename for '{filename}'. Error: {e}")
                continue
            
            # Final security check
            if not os.path.abspath(save_path).startswith(os.path.abspath(upload_dir)):
                errors.append(f"Invalid save path for file: '{filename}' was skipped.")
                continue
            
            try:
                # Double-check file doesn't exist
                if os.path.exists(save_path):
                    with _log_lock:
                        flat_filename, save_path, full_relative_path = UploadService.get_unique_filename(
                            upload_dir,
                            filename,
                            share_dir=share_dir,
                            share_subpath=upload_subpath,
                            save_flat=True
                        )
                
                file.save(save_path)
                
                # Build suggested path
                if '/' in filename or '\\' in filename:
                    final_path_suggestion = os.path.join(upload_subpath, full_relative_path).replace('\\', '/')
                else:
                    final_path_suggestion = os.path.join(upload_subpath, filename).replace('\\', '/')
                
                # Generate upload ID and log
                upload_id = UploadService.get_next_upload_id()
                UploadService.log_pending_upload(upload_id, email, user_id, flat_filename, final_path_suggestion)
                
                successful_uploads.append(filename)
            except Exception as e:
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'no extension'
                error_type = 'upload_error'
                if error_type not in failed_files_by_type:
                    failed_files_by_type[error_type] = {}
                if ext not in failed_files_by_type[error_type]:
                    failed_files_by_type[error_type][ext] = []
                failed_files_by_type[error_type][ext].append(filename)
                errors.append(f"Could not upload '{filename}'. Error: {e}")
        
        # Format error summary
        error_summary = None
        if errors and len(errors) > 5:
            summary_parts = []
            for error_type, ext_dict in failed_files_by_type.items():
                for ext, files in ext_dict.items():
                    count = len(files)
                    if error_type == 'file_type_not_allowed':
                        summary_parts.append(f"{count} file(s) with .{ext} extension (file type not allowed)")
                    elif error_type == 'malicious_file':
                        summary_parts.append(f"{count} file(s) with .{ext} extension (malicious file detected)")
                    elif error_type == 'upload_error':
                        summary_parts.append(f"{count} file(s) with .{ext} extension (upload failed)")
            
            if summary_parts:
                error_summary = "Failed file types:\n" + "\n".join(summary_parts)
            else:
                error_summary = f"{len(errors)} files failed to upload"
        
        logger.info(f"Upload completed - Successful: {len(successful_uploads)}, Failed: {len(errors)}, User: {email}")
        return successful_uploads, errors, failed_files_by_type, error_summary
    
    @staticmethod
    def get_my_uploads(email, user_id):
        """Get all uploads for a specific user."""
        logger.debug(f"Getting user uploads - Email: {email}, User ID: {user_id}")
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        
        user_uploads = []
        declined_items = set()
        
        # Read declined items
        declined_uploads = UploadRepository.read_declined_uploads()
        for row in declined_uploads:
            declined_user_id = row.get('user_id', '')
            if (row.get('email') == email) or (declined_user_id and str(user_id) == declined_user_id):
                declined_items.add(row.get('filename', ''))
        
        # Read pending log
        pending_uploads = UploadRepository.read_pending_uploads()
        for upload in pending_uploads:
            row_email = upload.get('email')
            row_user_id = upload.get('user_id')
            
            matches_user = False
            if user_id and row_user_id:
                matches_user = str(user_id) == str(row_user_id)
            else:
                matches_user = row_email == email
            
            if matches_user:
                flat_filename = upload.get('filename')
                full_path = upload.get('path', '')
                file_exists = os.path.exists(os.path.join(upload_dir, flat_filename))
                display_filename = full_path if full_path else flat_filename
                
                if flat_filename in declined_items or display_filename in declined_items:
                    status = 'Declined'
                elif file_exists:
                    status = 'Pending Review'
                else:
                    status = 'Processing'
                
                user_uploads.append({
                    'upload_id': upload.get('upload_id'),
                    'timestamp': upload.get('timestamp'),
                    'email': row_email,
                    'user_id': row_user_id if row_user_id else None,
                    'filename': display_filename,
                    'path': full_path if full_path else '',
                    'status': status
                })
        
        # Read completed log
        completed_uploads = UploadRepository.read_completed_uploads()
        for upload in completed_uploads:
            row_email = upload.get('email')
            row_user_id = upload.get('user_id')
            
            matches_user = False
            if user_id and row_user_id:
                matches_user = str(user_id) == str(row_user_id)
            else:
                matches_user = row_email == email
            
            if matches_user:
                user_uploads.append({
                    'upload_id': upload.get('upload_id'),
                    'timestamp': upload.get('original_timestamp'),
                    'email': row_email,
                    'user_id': row_user_id if row_user_id else None,
                    'filename': upload.get('final_path'),
                    'path': upload.get('final_path'),
                    'status': 'Approved & Moved',
                    'approval_timestamp': upload.get('approval_timestamp')
                })
        
        user_uploads.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        logger.info(f"Retrieved {len(user_uploads)} uploads for user: {email}")
        return user_uploads
    
    @staticmethod
    def get_admin_uploads():
        """Get all pending uploads for admin review."""
        logger.debug("Getting admin uploads")
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        all_uploads_list = []
        
        pending_uploads = UploadRepository.read_pending_uploads()
        
        for upload in reversed(pending_uploads):
            upload_id = upload.get('upload_id')
            timestamp = upload.get('timestamp')
            email = upload.get('email')
            user_id = upload.get('user_id')
            flat_filename = upload.get('filename')
            suggested_full_path = upload.get('path', '')
            
            full_file_path = os.path.join(upload_dir, flat_filename)
            
            if os.path.exists(full_file_path):
                user_info = None
                if user_id:
                    try:
                        user = UserRepository.find_by_email(email)
                        if user:
                            user_info = {
                                "id": user.user_id,
                                "email": user.email,
                                "role": user.role
                            }
                    except:
                        pass
                
                if '/' in suggested_full_path:
                    display_filename = suggested_full_path
                else:
                    display_filename = flat_filename
                
                all_uploads_list.append({
                    "upload_id": upload_id,
                    "timestamp": timestamp,
                    "email": email,
                    "user_id": user_id if user_id else None,
                    "user": user_info,
                    "filename": display_filename,
                    "path": suggested_full_path,
                    "flat_filename": flat_filename
                })
        
        final_uploads_list = sorted(all_uploads_list, key=lambda x: x['timestamp'], reverse=True)
        logger.info(f"Retrieved {len(final_uploads_list)} pending uploads for admin review")
        return final_uploads_list
    
    @staticmethod
    def move_upload(upload_id, filename, target_path_str, email):
        """Move an upload from pending to approved location."""
        logger.info(f"Moving upload - ID: {upload_id}, Target: {target_path_str}, Admin: {email}")
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        share_dir = os.path.join(project_root, config.SHARE_FOLDER)
        
        flat_filename = None
        pending_entry = None
        
        # Look up entry from pending log
        if upload_id:
            pending_data = UploadRepository.find_pending_by_id(upload_id)
            if pending_data:
                pending_entry = [
                    pending_data['upload_id'],
                    pending_data['timestamp'],
                    pending_data['email'],
                    pending_data['user_id'],
                    pending_data['filename'],
                    pending_data['path']
                ]
                flat_filename = pending_data['filename']
                upload_id = pending_data['upload_id']
        
        if not pending_entry:
            # Try finding by filename
            matches = UploadRepository.find_pending_by_filename(filename)
            if matches:
                match = matches[0]
                pending_entry = [
                    match['upload_id'],
                    match['timestamp'],
                    match['email'],
                    match['user_id'],
                    match['filename'],
                    match['path']
                ]
                flat_filename = match['filename']
                upload_id = match['upload_id']
        
        if flat_filename is None:
            flat_filename = filename
        
        source_item = os.path.join(upload_dir, flat_filename)
        
        if not os.path.exists(source_item):
            logger.warning(f"Move failed - Source not found: {flat_filename}")
            return False, f'Source item "{flat_filename}" not found'
        
        destination_path = os.path.join(share_dir, target_path_str)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        # Check for conflicts
        if os.path.exists(destination_path) and os.path.isfile(destination_path):
            dest_dir = os.path.dirname(destination_path)
            dest_base = os.path.basename(destination_path)
            if dest_dir:
                rel_dir = os.path.relpath(dest_dir, share_dir)
                if rel_dir == '.':
                    rel_dir = ''
                dest_filename_with_path = os.path.join(rel_dir, dest_base).replace('\\', '/') if rel_dir else dest_base
            else:
                dest_filename_with_path = dest_base
            
            _, unique_dest_path, _ = UploadService.get_unique_filename(share_dir, dest_filename_with_path, save_flat=False)
            destination_path = unique_dest_path
            rel_path = os.path.relpath(unique_dest_path, share_dir).replace('\\', '/')
            target_path_str = rel_path
        
        safe_destination = os.path.abspath(destination_path)
        if not safe_destination.startswith(os.path.abspath(share_dir)):
            logger.warning(f"Move failed - Invalid target path: {target_path_str}")
            return False, "Invalid target path"
        
        try:
            shutil.move(source_item, destination_path)
            
            if pending_entry and upload_id:
                entry_upload_id, original_timestamp, row_email, user_id, _, _ = pending_entry
                UploadRepository.remove_from_pending(upload_id)
                UploadService.log_completed_upload(
                    entry_upload_id,
                    original_timestamp,
                    row_email,
                    user_id,
                    flat_filename,
                    target_path_str
                )
            
            logger.info(f"Upload moved successfully - ID: {upload_id}, Target: {target_path_str}")
            return True, None
        except FileNotFoundError:
            logger.error(f"Move failed - Source not found: {flat_filename}")
            return False, f'Source item "{flat_filename}" not found'
        except Exception as e:
            logger.error(f"Move failed - Error: {str(e)}")
            return False, f"An error occurred while moving the item: {e}"
    
    @staticmethod
    def decline_upload(upload_id, filename, email, user_id):
        """Decline an upload and remove it."""
        logger.info(f"Declining upload - ID: {upload_id}, File: {filename}, Admin: {email}")
        project_root = get_project_root()
        upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
        
        flat_filename = None
        pending_entry = None
        
        # Look up entry
        if upload_id:
            pending_data = UploadRepository.find_pending_by_id(upload_id)
            if pending_data:
                pending_entry = [
                    pending_data['upload_id'],
                    pending_data['timestamp'],
                    pending_data['email'],
                    pending_data['user_id'],
                    pending_data['filename'],
                    pending_data['path']
                ]
                flat_filename = pending_data['filename']
                upload_id = pending_data['upload_id']
        
        if not pending_entry:
            # Try finding by filename
            matches = UploadRepository.find_pending_by_filename(filename)
            if matches:
                match = matches[0]
                pending_entry = [
                    match['upload_id'],
                    match['timestamp'],
                    match['email'],
                    match['user_id'],
                    match['filename'],
                    match['path']
                ]
                flat_filename = match['filename']
                upload_id = match['upload_id']
        
        if flat_filename is None:
            flat_filename = filename
        
        item_to_delete = os.path.join(upload_dir, flat_filename)
        
        # Get email and user_id from pending entry if available
        if pending_entry:
            _, _, email_from_entry, user_id_from_entry, _, _ = pending_entry
            email = email_from_entry
            user_id = user_id_from_entry if user_id_from_entry else user_id
        
        # Get user_id if not provided
        if not user_id:
            user = UserRepository.find_by_email(email)
            user_id = user.user_id if user else None
        
        # Remove from pending log
        if upload_id:
            UploadRepository.remove_from_pending(upload_id)
        
        # Log to declined log
        UploadService.log_declined_upload(email, user_id, flat_filename)
        
        try:
            if os.path.exists(item_to_delete):
                if os.path.isdir(item_to_delete):
                    shutil.rmtree(item_to_delete)
                else:
                    os.remove(item_to_delete)
                logger.info(f"Upload declined and removed - ID: {upload_id}, File: {flat_filename}")
                return True, None
            else:
                logger.warning(f"Decline failed - Item already removed: {filename}")
                return False, f'Item "{filename}" was already removed.'
        except Exception as e:
            logger.error(f"Decline failed - Error: {str(e)}")
            return False, f"An error occurred while declining the item: {e}"
    
    @staticmethod
    def edit_upload_path(upload_id, new_path):
        """Edit the path of a completed upload."""
        logger.info(f"Editing upload path - ID: {upload_id}, New path: {new_path}")
        success = UploadRepository.update_completed_path(upload_id, new_path)
        
        if success:
            logger.info(f"Upload path updated - ID: {upload_id}, New path: {new_path}")
            return True, None
        else:
            logger.warning(f"Edit path failed - Upload ID not found: {upload_id}")
            return False, f"Upload ID {upload_id} not found in log"

