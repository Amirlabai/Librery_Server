import os
import shutil
import zipfile
from io import BytesIO
from datetime import datetime
from flask import Blueprint, session, send_from_directory, send_file, jsonify, request
import csv

import config.config as config
from utils import log_event, get_project_root
from utils.logger_config import get_logger
from flask_cors import cross_origin


files_bp = Blueprint('files', __name__)
logger = get_logger(__name__)

@files_bp.route('/browse', defaults={'subpath': ''}, methods=["GET"])
@files_bp.route('/browse/<path:subpath>', methods=["GET"])
def downloads(subpath=''):
    logger.debug(f"Browse request received - Path: {subpath}, User: {session.get('email', 'unknown')}")
    if not session.get("logged_in"):
        logger.warning("Browse request failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    
    # Get project root (one level up from merkaz_backend directory)
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    upload_completed_log = os.path.join(share_dir,config.UPLOAD_COMPLETED_LOG_FILE)

    safe_subpath = os.path.normpath(subpath).replace('\\', '/')
    if safe_subpath == '.':
        safe_subpath = ''
        
    if '/.' in safe_subpath:
        logger.warning(f"Invalid path detected: {safe_subpath}")
        return jsonify({"error": "Invalid path"}), 404
        
    current_path = os.path.join(share_dir, safe_subpath)
    
    if not os.path.abspath(current_path).startswith(os.path.abspath(share_dir)):
        logger.warning(f"Access denied - Path traversal attempt: {safe_subpath}, User: {session.get('email', 'unknown')}")
        return jsonify({"error": "Access denied"}), 403

    items = []
    if os.path.exists(current_path) and os.path.isdir(current_path):
        folders = []
        files = []
        for item_name in os.listdir(current_path):
            if item_name.startswith('.'): continue
            
            item_path_os = os.path.join(current_path, item_name)
            item_path_url = os.path.join(safe_subpath, item_name).replace('\\', '/')
            
            with open(upload_completed_log, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rows = [header] if header else []
                for row in reader:
                    a = row[6]
                    b = item_path_url
                    if len(row) >= 6 and row[6] == item_path_url:  # upload_id is first column
                        # Update the path column (index 5)
                        item_id = row[0]
                        break
                    else:
                        item_id = "0"

            item_data = {"upload_id":item_id,
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
    cooldown_level = session.get("cooldown_index", 0) + 1

    logger.info(f"Browse completed - Path: {safe_subpath}, Files: {len(files)}, Folders: {len(folders)}, User: {session.get('email', 'unknown')}")
    return jsonify({
        "files": files,
        "folders": folders,
        "current_path": safe_subpath,
        "back_path": back_path,
        "is_admin": session.get('is_admin', False),
        "cooldown_level": cooldown_level
    }), 200


@files_bp.route("/delete/<path:item_path>", methods=["POST"])
def delete_item(item_path):
    admin_email = session.get('email', 'unknown')
    logger.info(f"Delete request received - Path: {item_path}, Admin: {admin_email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to delete - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    trash_dir = os.path.join(project_root, config.TRASH_FOLDER)

    source_path = os.path.join(share_dir, item_path)

    if not os.path.exists(source_path) or not source_path.startswith(share_dir):
        logger.warning(f"Delete failed - File/folder not found: {item_path}")
        return jsonify({"error": "File or folder not found"}), 404

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(item_path)
    dest_name = f"{timestamp}_{base_name}"
    dest_path = os.path.join(trash_dir, dest_name)

    try:
        shutil.move(source_path, dest_path)
        log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "DELETE", item_path])
        logger.info(f"Item deleted successfully - Path: {item_path}, Moved to trash: {dest_name}, Admin: {admin_email}")
        return jsonify({"message": f"Successfully moved '{base_name}' to trash."}), 200
    except Exception as e:
        logger.error(f"Error deleting item: {item_path}, Error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error deleting item: {e}"}), 500

@files_bp.route("/create_folder", methods=["POST"])
def create_folder():
    admin_email = session.get('email', 'unknown')
    logger.info(f"Create folder request received - Admin: {admin_email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to create folder - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json()
    if not data:
        logger.warning("Create folder request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400
    
    parent_path = data.get("parent_path", "")
    folder_name = data.get("folder_name", "").strip()
    logger.debug(f"Creating folder - Name: {folder_name}, Parent: {parent_path}")
    
    if not folder_name:
        logger.warning("Create folder failed - Empty folder name")
        return jsonify({"error": "Folder name cannot be empty."}), 400
    
    if '/' in folder_name or '\\' in folder_name or '..' in folder_name:
        logger.warning(f"Create folder failed - Invalid characters in name: {folder_name}")
        return jsonify({"error": "Invalid characters in folder name."}), 400
    
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    
    safe_parent_path = os.path.normpath(parent_path).replace('\\', '/')
    if safe_parent_path == '.':
        safe_parent_path = ''
    
    new_folder_path = os.path.join(share_dir, safe_parent_path, folder_name)
    
    if not os.path.abspath(new_folder_path).startswith(os.path.abspath(share_dir)):
        return jsonify({"error": "Invalid path."}), 400
    
    if os.path.exists(new_folder_path):
        return jsonify({"error": f"A folder or file named '{folder_name}' already exists."}), 409
    
    try:
        os.makedirs(new_folder_path)
        folder_path_url = os.path.join(safe_parent_path, folder_name).replace('\\', '/') if safe_parent_path else folder_name
        log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "CREATE_FOLDER", folder_path_url])
        logger.info(f"Folder created successfully - Path: {folder_path_url}, Admin: {admin_email}")
        return jsonify({"message": f"Folder '{folder_name}' created successfully."}), 200
    except Exception as e:
        logger.error(f"Error creating folder: {folder_name}, Error: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error creating folder: {e}"}), 500

@files_bp.route("/download/file/<path:file_path>")
def download_file(file_path):
    user_email = session.get("email", "unknown")
    logger.info(f"File download request - Path: {file_path}, User: {user_email}")
    if not session.get("logged_in"):
        logger.warning("File download failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_email, "FILE", file_path])
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)

    directory, filename = os.path.split(file_path)
    safe_dir = os.path.join(share_dir, directory)
    if not safe_dir.startswith(share_dir) or not os.path.isdir(safe_dir):
        logger.warning(f"File download access denied - Path: {file_path}, User: {user_email}")
        return jsonify({"error": "Access denied"}), 403
    logger.debug(f"File download successful - File: {filename}, User: {user_email}")
    return send_from_directory(safe_dir, filename, as_attachment=True)

@files_bp.route("/download/folder/<path:folder_path>")
def download_folder(folder_path):
    user_email = session.get("email", "unknown")
    logger.info(f"Folder download request - Path: {folder_path}, User: {user_email}")
    if not session.get("logged_in"):
        logger.warning("Folder download failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_email, "FOLDER", folder_path])
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)

    absolute_folder_path = os.path.join(share_dir, folder_path)
    if not os.path.isdir(absolute_folder_path) or not absolute_folder_path.startswith(share_dir):
        logger.warning(f"Folder download failed - Folder not found: {folder_path}")
        return jsonify({"error": "Folder not found"}), 404
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(absolute_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, os.path.relpath(file_path, absolute_folder_path))
    memory_file.seek(0)
    logger.debug(f"Folder download successful - Folder: {folder_path}, User: {user_email}")
    return send_file(memory_file, download_name=f'{os.path.basename(folder_path)}.zip', as_attachment=True)

COOLDOWN_LEVELS = [0, 60, 300, 600, 1800, 3600]
@files_bp.route("/suggest", methods=["POST"])
def suggest():
    user_email = session.get("email", "unknown")
    logger.debug(f"Suggestion submission request - User: {user_email}")
    if not session.get("logged_in"):
        logger.warning("Suggestion submission failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    if not data:
        logger.warning("Suggestion submission missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400
    
    suggestion_text = data.get("suggestion")
    if not suggestion_text:
        logger.warning(f"Suggestion submission failed - Empty suggestion text, User: {user_email}")
        return jsonify({"error": "Suggestion text is required"}), 400
    
    now = datetime.now()
    last_suggestion_time_str = session.get("last_suggestion_time")
    cooldown_index = session.get("cooldown_index", 0)
    
    if last_suggestion_time_str:
        last_suggestion_time = datetime.fromisoformat(last_suggestion_time_str)
        if last_suggestion_time.date() < now.date() and cooldown_index > 0:
            cooldown_index = 0
            session["cooldown_index"] = 0
        elapsed_time = (now - last_suggestion_time).total_seconds()
        current_cooldown = COOLDOWN_LEVELS[cooldown_index]
        if elapsed_time < current_cooldown:
            remaining = max(1, (current_cooldown - elapsed_time) / 60)
            if remaining == 1:
                remaining_str = str(int(current_cooldown - elapsed_time)) + " seconds"
            else:
                remaining_str = str(int(remaining)) + " minutes"
            return jsonify({
                "error": f"You must wait another {remaining_str} before submitting again.",
                "remaining_minutes": remaining
            }), 429
            
    log_event(config.SUGGESTION_LOG_FILE, [now.strftime("%Y-%m-%d %H:%M:%S"), user_email, suggestion_text])
    logger.info(f"Suggestion submitted successfully - User: {user_email}, Cooldown: {COOLDOWN_LEVELS[cooldown_index]}s")
    session["last_suggestion_time"] = now.isoformat()
    if cooldown_index < len(COOLDOWN_LEVELS) - 1:
        session["cooldown_index"] = cooldown_index + 1
    
    return jsonify({"message": "Thank you, your suggestion has been submitted!"}), 200
