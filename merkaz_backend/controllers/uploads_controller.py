import os
import csv
import shutil
import magic
import threading
from datetime import datetime
from flask import Blueprint, session, abort, jsonify, request, current_app, send_file


import config.config as config
from utils import log_event, get_project_root, get_next_upload_id
from utils.logger_config import get_logger
from models.user_entity import User

uploads_bp = Blueprint('uploads', __name__)
logger = get_logger(__name__)

# File lock for thread-safe CSV logging
_log_lock = threading.Lock()

def remove_from_pending_log(upload_id):
    """
    Removes an entry from the pending log by upload_id.
    Returns the removed row data if found, None otherwise.
    """
    project_root = get_project_root()
    pending_log_path = os.path.join(project_root, config.UPLOAD_PENDING_LOG_FILE)
    
    if not os.path.exists(pending_log_path):
        return None
    
    rows = []
    removed_row = None
    
    with _log_lock:
        try:
            # Read all rows
            with open(pending_log_path, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rows = [header] if header else []
                for row in reader:
                    if len(row) >= 6 and row[0] == str(upload_id):  # upload_id is first column
                        removed_row = row
                    else:
                        rows.append(row)
            
            # Write back all rows except the removed one
            if removed_row:
                with open(pending_log_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
        except (FileNotFoundError, StopIteration):
            return None
    
    return removed_row

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def is_file_malicious(file_stream):
    """
    Checks the magic number of a file to determine if it's potentially malicious.
    """
    file_signature = file_stream.read(2048)  # Read the first 2048 bytes
    file_stream.seek(0)  # Reset stream position
    
    file_type = magic.from_buffer(file_signature, mime=True)

    # Add more sophisticated checks here if needed
    if "executable" in file_type:
        return True
    
    return False

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
        - flat_filename_for_storage: Filename to use for actual file storage (flat, no directories)
        - full_save_path: Full path where file will be saved in upload_dir
        - full_relative_path_for_log: Full relative path including folder structure (for logging/reconstruction)
    """
    # Extract directory structure and base filename
    if '/' in filename or '\\' in filename:
        dir_part = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        full_relative_path = filename.replace('\\', '/')  # Preserve full path for logging
    else:
        dir_part = ''
        base_name = filename
        full_relative_path = filename
    
    # For flat storage, always save to root of upload_dir (no subdirectories)
    if save_flat:
        target_dir = upload_dir
    else:
        target_dir = os.path.join(upload_dir, dir_part) if dir_part else upload_dir
    
    # Ensure target directory exists
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
        
        # Full path in upload directory (always flat for save_flat=True)
        full_path_upload = os.path.join(target_dir, unique_base)
        
        # Check if file exists in upload directory
        file_exists_in_upload = os.path.exists(full_path_upload)
        
        # Also check if file exists in share directory (eventual destination)
        # Use the full relative path (with directory structure) for share directory check
        file_exists_in_share = False
        if share_dir and share_subpath:
            # Combine share_subpath with the directory structure from filename
            if dir_part:
                share_path_with_structure = os.path.join(share_subpath, dir_part, unique_base).replace('\\', '/')
            else:
                share_path_with_structure = os.path.join(share_subpath, unique_base).replace('\\', '/')
            share_dest_path = os.path.join(share_dir, share_path_with_structure)
            file_exists_in_share = os.path.exists(share_dest_path)
        elif share_dir:
            # Check with full directory structure in share_dir
            if dir_part:
                share_dest_path = os.path.join(share_dir, dir_part, unique_base)
            else:
                share_dest_path = os.path.join(share_dir, unique_base)
            file_exists_in_share = os.path.exists(share_dest_path)
        
        # If file doesn't exist in either location, we can use this name
        if not file_exists_in_upload and not file_exists_in_share:
            # Build the full relative path for logging (includes directory structure)
            if dir_part and counter == 0:
                full_relative_path_for_log = os.path.join(dir_part, unique_base).replace('\\', '/')
            elif dir_part:
                full_relative_path_for_log = os.path.join(dir_part, unique_base).replace('\\', '/')
            else:
                full_relative_path_for_log = unique_base
            
            return unique_base, full_path_upload, full_relative_path_for_log
        
        counter += 1


@uploads_bp.route("/upload", methods=["POST"])
def upload_file():
    if not session.get("logged_in"):
        return jsonify({"error": "Not logged in"}), 401
        
    # Ensure files are stored in project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    
    uploaded_files = request.files.getlist("file")
    if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ''):
        return jsonify({"error": "No files selected"}), 400
        
    # Get subpath from form data (for file uploads, subpath comes in form, not JSON)
    upload_subpath = request.form.get('subpath', '')
    
    successful_uploads = []
    errors = []
    failed_files_by_type = {}  # Track failed files by error type and extension
    
    for file in uploaded_files:
        if file:
            # filename from the browser can include the relative path for folder uploads
            filename = file.filename
            
            if not allowed_file(file.filename):
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'no extension'
                error_type = 'file_type_not_allowed'
                if error_type not in failed_files_by_type:
                    failed_files_by_type[error_type] = {}
                if ext not in failed_files_by_type[error_type]:
                    failed_files_by_type[error_type][ext] = []
                failed_files_by_type[error_type][ext].append(filename)
                errors.append(f"File type not allowed for: {filename}")
                continue

            if is_file_malicious(file.stream):
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'no extension'
                error_type = 'malicious_file'
                if error_type not in failed_files_by_type:
                    failed_files_by_type[error_type] = {}
                if ext not in failed_files_by_type[error_type]:
                    failed_files_by_type[error_type][ext] = []
                failed_files_by_type[error_type][ext].append(filename)
                errors.append(f"Malicious file detected: {filename}")
                continue
                
            # Security check to prevent path traversal attacks
            if '..' in filename.split('/') or '..' in filename.split('\\') or os.path.isabs(filename):
                errors.append(f"Invalid path in filename: '{filename}' was skipped.")
                continue
            
            # Get unique filename (handles indexing if file exists)
            # Check both upload directory and share directory (eventual destination)
            # Files are saved FLAT in uploads directory (no folder structure)
            # Use lock to prevent race conditions when checking for existing files
            try:
                share_dir = os.path.join(project_root, config.SHARE_FOLDER)
                with _log_lock:
                    flat_filename, save_path, full_relative_path = get_unique_filename(
                        upload_dir, 
                        filename, 
                        share_dir=share_dir,
                        share_subpath=upload_subpath,
                        save_flat=True  # Save files flat in uploads directory
                    )
            except Exception as e:
                errors.append(f"Could not generate unique filename for '{filename}'. Error: {e}")
                continue

            # Final security check to ensure the path doesn't escape the upload directory
            if not os.path.abspath(save_path).startswith(os.path.abspath(upload_dir)):
                errors.append(f"Invalid save path for file: '{filename}' was skipped.")
                continue

            try:
                # Save the file
                # Double-check file doesn't exist (handles extremely rare race condition)
                if os.path.exists(save_path):
                    # File was created between check and save, get next available unique name
                    with _log_lock:
                        flat_filename, save_path, full_relative_path = get_unique_filename(
                            upload_dir, 
                            filename,
                            share_dir=share_dir,
                            share_subpath=upload_subpath,
                            save_flat=True
                        )
                
                file.save(save_path)
                
                # Build the suggested path for approval
                # If filename has directory structure (folder upload), include it in the suggestion
                if '/' in filename or '\\' in filename:
                    # Full path including folder structure within the upload_subpath
                    final_path_suggestion = os.path.join(upload_subpath, full_relative_path).replace('\\', '/')
                else:
                    # Single file upload
                    final_path_suggestion = os.path.join(upload_subpath, filename).replace('\\', '/')
                
                # Get user_id from session, fallback to finding user by email if not in session
                user_id = session.get("user_id")
                if user_id is None:
                    user = User.find_by_email(session.get("email"))
                    user_id = user.user_id if user else None
                
                # Generate unique upload ID
                upload_id = get_next_upload_id()
                
                # Thread-safe logging to pending log
                # Format: upload_id, timestamp, email, user_id, flat_filename, suggested_full_path
                with _log_lock:
                    log_event(config.UPLOAD_PENDING_LOG_FILE, [
                        upload_id,  # Unique upload identifier
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        session.get("email"), 
                        user_id if user_id else '',  # Store user_id in log
                        flat_filename,  # Store flat filename (for finding file: "my file.whatever" or "my file_1.whatever")
                        final_path_suggestion  # Full suggested path including folder structure (for reconstruction)
                    ])
                
                successful_uploads.append(filename)  # Return original filename to user
            except Exception as e:
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'no extension'
                error_type = 'upload_error'
                if error_type not in failed_files_by_type:
                    failed_files_by_type[error_type] = {}
                if ext not in failed_files_by_type[error_type]:
                    failed_files_by_type[error_type][ext] = []
                failed_files_by_type[error_type][ext].append(filename)
                errors.append(f"Could not upload '{filename}'. Error: {e}")

    # Format errors based on count
    error_summary = None
    
    if errors and len(errors) > 5:
        # Group by file extension/suffix for errors > 5
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
            # Fallback if we don't have extension info
            error_summary = f"{len(errors)} files failed to upload"
    
    if successful_uploads:
        response = {
            "message": f"Successfully uploaded {len(successful_uploads)} file(s). Files are pending review.",
            "successful_uploads": successful_uploads,
            "count": len(successful_uploads)
        }
        if errors:
            if len(errors) <= 5:
                response["errors"] = errors
            else:
                response["errors"] = [error_summary]
                response["error_count"] = len(errors)
        return jsonify(response), 200
    else:
        if errors:
            if len(errors) <= 5:
                return jsonify({"error": "No files were uploaded", "errors": errors}), 400
            else:
                return jsonify({"error": "No files were uploaded", "errors": [error_summary], "error_count": len(errors)}), 400
        else:
            return jsonify({"error": "No files were uploaded", "errors": errors}), 400

@uploads_bp.route('/my_uploads')
def my_uploads():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    # Ensure files are read from project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    pending_log_path = os.path.join(project_root, config.UPLOAD_PENDING_LOG_FILE)
    completed_log_path = os.path.join(project_root, config.UPLOAD_COMPLETED_LOG_FILE)
    user_email = session.get('email')
    user_id = session.get('user_id')
    
    # Get user_id if not in session
    if user_id is None:
        user = User.find_by_email(user_email)
        user_id = user.user_id if user else None
    
    user_uploads = []

    declined_items = set()
    try:
        declined_log_path = os.path.join(project_root, config.DECLINED_UPLOAD_LOG_FILE)
        with open(declined_log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check by email for backward compatibility, or by user_id if available
                declined_user_id = row.get('user_id', '')
                if (row['email'] == user_email) or (declined_user_id and str(user_id) == declined_user_id):
                    # Store the declined filename (might be display path or flat filename)
                    declined_items.add(row['filename'])
    except FileNotFoundError:
        pass

    # Read from pending log
    try:
        with open(pending_log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 6:
                    upload_id, timestamp, email, row_user_id, flat_filename, full_path = row[0], row[1], row[2], row[3], row[4], row[5]
                    
                    # Filter by user_id if available, otherwise fallback to email
                    matches_user = False
                    if user_id and row_user_id:
                        matches_user = str(user_id) == row_user_id
                    else:
                        matches_user = email == user_email
                    
                    if matches_user:
                        # Check if file exists using flat filename
                        file_exists = os.path.exists(os.path.join(upload_dir, flat_filename))
                        
                        # Use full_path for display if available, otherwise use flat_filename
                        display_filename = full_path if full_path else flat_filename
                        
                        # Check status
                        if flat_filename in declined_items or display_filename in declined_items:
                            status = 'Declined'
                        elif file_exists:
                            status = 'Pending Review'
                        else:
                            status = 'Processing'  # File missing but still in pending log
                        
                        user_uploads.append({
                            'upload_id': upload_id,
                            'timestamp': timestamp,
                            'email': email,
                            'user_id': row_user_id if row_user_id else None,
                            'filename': display_filename,
                            'path': full_path if full_path else '',
                            'status': status
                        })
    except FileNotFoundError:
        pass

    # Read from completed log
    try:
        with open(completed_log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 7:
                    upload_id, original_timestamp, approval_timestamp, email, row_user_id, flat_filename, final_path = row[0], row[1], row[2], row[3], row[4], row[5], row[6]
                    
                    # Filter by user_id if available, otherwise fallback to email
                    matches_user = False
                    if user_id and row_user_id:
                        matches_user = str(user_id) == row_user_id
                    else:
                        matches_user = email == user_email
                    
                    if matches_user:
                        user_uploads.append({
                            'upload_id': upload_id,
                            'timestamp': original_timestamp,
                            'email': email,
                            'user_id': row_user_id if row_user_id else None,
                            'filename': final_path,
                            'path': final_path,
                            'status': 'Approved & Moved',
                            'approval_timestamp': approval_timestamp
                        })
    except FileNotFoundError:
        pass

    # Sort by timestamp (most recent first)
    user_uploads.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return jsonify(user_uploads), 200

@uploads_bp.route("/admin/uploads")
def admin_uploads():
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are read from project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    pending_log_path = os.path.join(project_root, config.UPLOAD_PENDING_LOG_FILE)
    all_uploads_list = []
    
    try:
        with open(pending_log_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            all_uploads_logged = list(reader)

        for row in reversed(all_uploads_logged):
            # New format: upload_id, timestamp, email, user_id, flat_filename, suggested_full_path
            if len(row) >= 6:
                upload_id, timestamp, email, user_id, flat_filename, suggested_full_path = row[0], row[1], row[2], row[3], row[4], row[5]
            else:
                # Skip malformed rows
                continue
            
            # Check if file still exists in upload directory (pending review)
            # Files are stored FLAT in uploads directory (no folder structure)
            full_file_path = os.path.join(upload_dir, flat_filename)
            
            # Only show files that still exist (pending approval)
            if os.path.exists(full_file_path):
                # Get user information if user_id is available
                user_info = None
                if user_id:
                    try:
                        user = User.find_by_email(email)
                        if user:
                            user_info = {
                                "id": user.user_id,
                                "email": user.email,
                                "role": user.role
                            }
                    except:
                        pass
                
                # Extract the folder structure from suggested_full_path for display
                # suggested_full_path contains: upload_subpath + folder_structure + filename
                if '/' in suggested_full_path:
                    display_filename = suggested_full_path
                else:
                    # Single file, no folder structure
                    display_filename = flat_filename
                
                all_uploads_list.append({
                    "upload_id": upload_id,  # Unique upload identifier
                    "timestamp": timestamp, 
                    "email": email,
                    "user_id": user_id if user_id else None,
                    "user": user_info,  # User info visible only to admins
                    "filename": display_filename,  # Full path including folder structure for display
                    "path": suggested_full_path,  # Where admin should approve it to (full path with structure)
                    "flat_filename": flat_filename  # Actual filename in uploads directory (for file lookup)
                })
                    
    except (FileNotFoundError, StopIteration):
        pass
        
    # Sort by timestamp (most recent first)
    final_uploads_list = sorted(all_uploads_list, key=lambda x: x['timestamp'], reverse=True)
    return jsonify(final_uploads_list), 200

@uploads_bp.route("/admin/move_upload/<path:filename>", methods=["POST"])
def move_upload(filename):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are in project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    pending_log_path = os.path.join(project_root, config.UPLOAD_PENDING_LOG_FILE)
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    target_path_str = data.get("target_path")
    if not target_path_str:
        return jsonify({"error": "Target path cannot be empty"}), 400

    # Look up the entry from pending log by upload_id or filename
    upload_id = data.get("upload_id")  # Try to get upload_id from request
    flat_filename = None
    pending_entry = None
    
    try:
        with open(pending_log_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reversed(list(reader)):
                if len(row) >= 6:
                    row_upload_id, timestamp, email, user_id, stored_flat, stored_path = row[0], row[1], row[2], row[3], row[4], row[5]
                    # Match by upload_id (preferred) or by filename/path
                    if (upload_id and str(row_upload_id) == str(upload_id)) or \
                       (stored_path == filename or stored_flat == filename):
                        pending_entry = row
                        flat_filename = stored_flat
                        upload_id = row_upload_id  # Use the found upload_id
                        break
    except (FileNotFoundError, StopIteration):
        pass
    
    # If lookup failed, assume filename is the flat filename
    if flat_filename is None:
        flat_filename = filename
    
    source_item = os.path.join(upload_dir, flat_filename)
    
    # Check if source file exists
    if not os.path.exists(source_item):
        return jsonify({"error": f'Source item "{flat_filename}" not found'}), 404
    
    # Build destination path
    # target_path_str already contains the full path with directory structure (e.g., "A/A/my file.whatever")
    # So we just need to join it with share_dir
    destination_path = os.path.join(share_dir, target_path_str)
    
    # Ensure parent directories exist (recreate the folder structure in share_dir)
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    
    # Check for conflicts in destination and get unique filename if needed
    if os.path.exists(destination_path):
        # File exists in destination, get unique filename
        # Ensure we don't check directories, only files
        if os.path.isfile(destination_path):
            dest_dir = os.path.dirname(destination_path)
            dest_base = os.path.basename(destination_path)
            # Calculate relative path from share_dir
            if dest_dir:
                rel_dir = os.path.relpath(dest_dir, share_dir)
                if rel_dir == '.':
                    rel_dir = ''
                dest_filename_with_path = os.path.join(rel_dir, dest_base).replace('\\', '/') if rel_dir else dest_base
            else:
                dest_filename_with_path = dest_base
            
            # Use get_unique_filename with share_dir as base (it handles subdirectories)
            # Note: save_flat=False to preserve directory structure in share_dir
            _, unique_dest_path, _ = get_unique_filename(share_dir, dest_filename_with_path, save_flat=False)
            destination_path = unique_dest_path
            # Update target_path_str to reflect the unique name for the response
            # Extract the relative path from share_dir
            rel_path = os.path.relpath(unique_dest_path, share_dir).replace('\\', '/')
            target_path_str = rel_path
    
    safe_destination = os.path.abspath(destination_path)
    if not safe_destination.startswith(os.path.abspath(share_dir)):
        return jsonify({"error": "Invalid target path"}), 400

    try:
        # Move the file (files are stored flat, so source_item is just the filename)
        shutil.move(source_item, destination_path)
        
        # Move entry from pending log to completed log
        if pending_entry and upload_id:
            # Extract data from pending entry before removing
            # Format: upload_id, timestamp, email, user_id, flat_filename, suggested_full_path
            entry_upload_id, original_timestamp, email, user_id, _, _ = pending_entry
            
            # Remove from pending log
            remove_from_pending_log(upload_id)
            
            # Add to completed log with approval timestamp
            # Format: upload_id, original_timestamp, approval_timestamp, email, user_id, flat_filename, final_path
            log_event(config.UPLOAD_COMPLETED_LOG_FILE, [
                entry_upload_id,
                original_timestamp,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Approval timestamp
                email,
                user_id if user_id else '',
                flat_filename,
                target_path_str  # Final approved path
            ])
        
        return jsonify({"message": f'Item "{filename}" has been successfully moved to "{target_path_str}".'}), 200
    except FileNotFoundError:
        return jsonify({"error": f'Source item "{flat_filename}" not found'}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred while moving the item: {e}"}), 500

@uploads_bp.route("/admin/decline_upload/<path:filename>", methods=["POST"])
def decline_upload(filename):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are in project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    pending_log_path = os.path.join(project_root, config.UPLOAD_PENDING_LOG_FILE)
    
    # Look up the entry from pending log
    upload_id = None
    flat_filename = None
    pending_entry = None
    
    data = request.get_json() or {}
    request_upload_id = data.get("upload_id")
    
    try:
        with open(pending_log_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reversed(list(reader)):
                if len(row) >= 6:
                    row_upload_id, timestamp, email, user_id, stored_flat, stored_path = row[0], row[1], row[2], row[3], row[4], row[5]
                    # Match by upload_id (preferred) or by filename/path
                    if (request_upload_id and str(row_upload_id) == str(request_upload_id)) or \
                       (stored_path == filename or stored_flat == filename):
                        pending_entry = row
                        flat_filename = stored_flat
                        upload_id = row_upload_id
                        break
    except (FileNotFoundError, StopIteration):
        pass
    
    # If lookup failed, assume filename is the flat filename
    if flat_filename is None:
        flat_filename = filename
    
    item_to_delete = os.path.join(upload_dir, flat_filename)
    
    user_email = data.get("email", "unknown")
    user_id = data.get("user_id")
    
    # Get email and user_id from pending entry if available
    if pending_entry:
        _, _, email_from_entry, user_id_from_entry, _, _ = pending_entry
        user_email = email_from_entry
        user_id = user_id_from_entry if user_id_from_entry else user_id
    
    # Get user_id if not provided
    if not user_id:
        user = User.find_by_email(user_email)
        user_id = user.user_id if user else None
    
    # Remove from pending log
    if upload_id:
        remove_from_pending_log(upload_id)
    
    # Log to declined log
    log_event(config.DECLINED_UPLOAD_LOG_FILE, [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        user_email, 
        user_id if user_id else '',  # Store user_id in declined log
        flat_filename  # Store flat filename for consistency
    ])

    try:
        if os.path.exists(item_to_delete):
            if os.path.isdir(item_to_delete):
                shutil.rmtree(item_to_delete)
            else:
                os.remove(item_to_delete)
            return jsonify({"message": f'Item "{filename}" has been declined and removed.'}), 200
        else:
            return jsonify({"error": f'Item "{filename}" was already removed.'}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred while declining the item: {e}"}), 500

@uploads_bp.route("/admin/edit_upload_path/", methods=["POST"])
def edit_upload_path():
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
    
    # Ensure files are in project root
    file_log_path = config.UPLOAD_COMPLETED_LOG_FILE
    
    # Get upload_id and new_path from request if not provided as parameters
    data = request.get_json() or {}
    request_upload_id = data.get("upload_id")
    request_new_path = data.get("new_path")[1:]
    
    if not request_upload_id:
        return jsonify({"error": "upload_id is required"}), 400
    
    if not request_new_path:
        return jsonify({"error": "new_path is required"}), 400
    
    rows = []
    found = False
    
    with _log_lock:
        try:
            # Read all rows
            with open(file_log_path, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rows = [header] if header else []
                for row in reader:
                    if len(row) >= 6 and row[0] == str(request_upload_id):  # upload_id is first column
                        # Update the path column (index 5)
                        old_path = row[6]
                        move_file(request_upload_id, old_path, request_new_path)
                        row[6] = request_new_path
                        found = True
                    rows.append(row)
            
            # Write back all rows with updated path
            if found:
                with open(file_log_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                return jsonify({"success": True,"message": f"Path updated for upload_id {request_upload_id}"}), 200
            else:
                return jsonify({"error": f"Upload ID {request_upload_id} not found in log"}), 404
        except FileNotFoundError:
            return jsonify({"success": False,"message": "Pending log file not found"}), 404
        except Exception as e:
            return jsonify({"error": f"An error occurred while updating the path: {e}"}), 500
        
def move_file(upload_id, old_path, new_path):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are in project root
    '''project_root = get_project_root()'''
    share_dir = config.SHARE_FOLDER
    source_item = os.path.join(share_dir, old_path).replace('\\', '/')
    destination_path = os.path.join(share_dir, new_path).replace('\\', '/')
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    # Look up the entry from pending log by upload_id or filename
    upload_id = ""  # keep for csv update
    
    
    # Check if source file exists
    if not os.path.exists(source_item):
        return jsonify({"error": f'Source item "{os.path.basename(old_path)}" not found'}), 404
    
    # Ensure parent directories exist (recreate the folder structure in share_dir)
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    
    # Check for conflicts in destination and get unique filename if needed
    if os.path.exists(destination_path):
        # File exists in destination, get unique filename
        # Ensure we don't check directories, only files
        if os.path.isfile(destination_path):
            dest_dir = os.path.dirname(destination_path)
            dest_base = os.path.basename(destination_path)
            # Calculate relative path from share_dir
            if dest_dir:
                rel_dir = os.path.relpath(dest_dir, share_dir)
                if rel_dir == '.':
                    rel_dir = ''
                dest_filename_with_path = os.path.join(rel_dir, dest_base).replace('\\', '/') if rel_dir else dest_base
            else:
                dest_filename_with_path = dest_base
            
            # Use get_unique_filename with share_dir as base (it handles subdirectories)
            # Note: save_flat=False to preserve directory structure in share_dir
            _, unique_dest_path, _ = get_unique_filename(share_dir, dest_filename_with_path, save_flat=False)
            destination_path = unique_dest_path
            # Update target_path_str to reflect the unique name for the response
            # Extract the relative path from share_dir
            rel_path = os.path.relpath(unique_dest_path, share_dir).replace('\\', '/')
            target_path_str = rel_path
    
    safe_destination = os.path.abspath(destination_path)
    if not safe_destination.startswith(os.path.abspath(share_dir)):
        return jsonify({"error": "Invalid target path"}), 400

    try:
        # Move the file (files are stored flat, so source_item is just the filename)
        shutil.move(source_item, destination_path)
        
        #place holder for loging move
        
        return jsonify({"message": f'Item "{new_path}" has been successfully moved to "{new_path}".'}), 200
    except FileNotFoundError:
        return jsonify({"error": f'Source item "{os.path.basename(old_path)}" not found'}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred while moving the item: {e}"}), 500
