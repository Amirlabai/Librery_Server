import os
import csv
import shutil
import magic
from datetime import datetime
from flask import Blueprint, session, abort, jsonify, request, current_app, send_file


import config
from utils import log_event, get_project_root
from user import User

uploads_bp = Blueprint('uploads', __name__)

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
    
    for file in uploaded_files:
        if file:
            if not allowed_file(file.filename):
                errors.append(f"File type not allowed for {file.filename}")
                continue

            if is_file_malicious(file.stream):
                errors.append(f"Malicious file detected: {file.filename}")
                continue
                
            # filename from the browser can include the relative path for folder uploads
            filename = file.filename
            
            # Security check to prevent path traversal attacks
            if '..' in filename.split('/') or '..' in filename.split('\\') or os.path.isabs(filename):
                errors.append(f"Invalid path in filename: '{filename}' was skipped.")
                continue
            
            save_path = os.path.join(upload_dir, filename)

            # Final security check to ensure the path doesn't escape the upload directory
            if not os.path.abspath(save_path).startswith(os.path.abspath(upload_dir)):
                errors.append(f"Invalid save path for file: '{filename}' was skipped.")
                continue

            try:
                # Create parent directories if they don't exist
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)
                
                # The suggested path for the file after admin approval
                final_path_suggestion = os.path.join(upload_subpath, filename).replace('\\', '/')
                
                # Get user_id from session, fallback to finding user by email if not in session
                user_id = session.get("user_id")
                if user_id is None:
                    user = User.find_by_email(session.get("email"))
                    user_id = user.user_id if user else None
                
                log_event(config.UPLOAD_LOG_FILE, [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    session.get("email"), 
                    user_id,  # Store user_id in log
                    filename, 
                    final_path_suggestion
                ])
                successful_uploads.append(filename)
            except Exception as e:
                errors.append(f"Could not upload '{filename}'. Error: {e}")

    if successful_uploads:
        response = {
            "message": f"Successfully uploaded {len(successful_uploads)} file(s). Files are pending review.",
            "successful_uploads": successful_uploads,
            "count": len(successful_uploads)
        }
        if errors:
            response["errors"] = errors
        return jsonify(response), 200
    else:
        return jsonify({"error": "No files were uploaded", "errors": errors}), 400

@uploads_bp.route('/my_uploads')
def my_uploads():
    if not session.get('logged_in'):
        return jsonify({"error": "Not logged in"}), 401

    # Ensure files are read from project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    user_email = session.get('email')
    user_id = session.get('user_id')
    
    # Get user_id if not in session
    if user_id is None:
        user = User.find_by_email(user_email)
        user_id = user.user_id if user else None
    
    user_uploads = []

    declined_items = set()
    try:
        with open(config.DECLINED_UPLOAD_LOG_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check by email for backward compatibility, or by user_id if available
                declined_user_id = row.get('user_id', '')
                if (row['email'] == user_email) or (declined_user_id and str(user_id) == declined_user_id):
                    declined_items.add(row['filename'])
    except FileNotFoundError:
        pass

    try:
        with open(config.UPLOAD_LOG_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filter by user_id if available, otherwise fallback to email
                row_user_id = row.get('user_id', '')
                matches_user = False
                
                if user_id and row_user_id:
                    # New format: match by user_id
                    matches_user = str(user_id) == row_user_id
                else:
                    # Old format or missing user_id: match by email
                    matches_user = row['email'] == user_email
                
                if matches_user:
                    full_relative_path = row['filename']
                    top_level_item = full_relative_path.split('/')[0].split('\\')[0]

                    if top_level_item in declined_items:
                        row['status'] = 'Declined'
                    elif os.path.exists(os.path.join(upload_dir, full_relative_path)):
                        row['status'] = 'Pending Review'
                    else:
                        row['status'] = 'Approved & Moved'
                    user_uploads.append(row)
    except FileNotFoundError:
        pass

    user_uploads.reverse()
    return jsonify(user_uploads), 200

@uploads_bp.route("/admin/uploads")
def admin_uploads():
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are read from project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    grouped_uploads = {}
    
    try:
        with open(config.UPLOAD_LOG_FILE, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            all_uploads_logged = list(reader)

        for row in reversed(all_uploads_logged):
            # Handle both old format (4 cols) and new format (5 cols with user_id)
            if len(row) >= 5:
                # New format: timestamp, email, user_id, filename, path
                timestamp, email, user_id, relative_path, suggested_full_path = row[0], row[1], row[2], row[3], row[4]
            else:
                # Old format: timestamp, email, filename, path
                timestamp, email, relative_path, suggested_full_path = row[0], row[1], row[2], row[3]
                user_id = None
            
            top_level_item = relative_path.split('/')[0].split('\\')[0]

            if top_level_item not in grouped_uploads:
                if os.path.exists(os.path.join(upload_dir, top_level_item)):
                    is_part_of_dir_upload = '/' in relative_path or '\\' in relative_path
                    final_approval_path = os.path.dirname(suggested_full_path) if is_part_of_dir_upload else suggested_full_path
                    
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
                    
                    grouped_uploads[top_level_item] = {
                        "timestamp": timestamp, 
                        "email": email,
                        "user_id": user_id if user_id else None,
                        "user": user_info,  # User info visible only to admins
                        "filename": top_level_item,
                        "path": final_approval_path
                    }
    except (FileNotFoundError, StopIteration):
        pass
        
    final_uploads_list = sorted(list(grouped_uploads.values()), key=lambda x: x['timestamp'])
    return jsonify(final_uploads_list), 200

@uploads_bp.route("/admin/move_upload/<path:filename>", methods=["POST"])
def move_upload(filename):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are in project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    target_path_str = data.get("target_path")
    if not target_path_str:
        return jsonify({"error": "Target path cannot be empty"}), 400

    source_item = os.path.join(upload_dir, filename)
    destination_path = os.path.join(share_dir, target_path_str)
    
    safe_destination = os.path.abspath(destination_path)
    if not safe_destination.startswith(os.path.abspath(share_dir)):
        return jsonify({"error": "Invalid target path"}), 400

    try:
        os.makedirs(os.path.dirname(safe_destination), exist_ok=True)
        shutil.move(source_item, safe_destination)
        return jsonify({"message": f'Item "{filename}" has been successfully moved to "{target_path_str}".'}), 200
    except FileNotFoundError:
        return jsonify({"error": f'Source item "{filename}" not found'}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred while moving the item: {e}"}), 500

@uploads_bp.route("/admin/decline_upload/<path:filename>", methods=["POST"])
def decline_upload(filename):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
        
    # Ensure files are in project root
    project_root = get_project_root()
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)
    item_to_delete = os.path.join(upload_dir, filename)
    
    data = request.get_json() or {}
    user_email = data.get("email", "unknown")
    user_id = data.get("user_id")
    
    # Get user_id if not provided in request
    if not user_id:
        user = User.find_by_email(user_email)
        user_id = user.user_id if user else None
    
    log_event(config.DECLINED_UPLOAD_LOG_FILE, [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        user_email, 
        user_id if user_id else '',  # Store user_id in declined log
        filename
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
