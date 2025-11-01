import os
import shutil
import zipfile
from io import BytesIO
from datetime import datetime
from flask import Blueprint, session, send_from_directory, send_file, jsonify, request

import config
from utils import log_event, get_project_root
from flask_cors import cross_origin


files_bp = Blueprint('files', __name__)

@files_bp.route('/browse', defaults={'subpath': ''}, methods=["GET"])
@files_bp.route('/browse/<path:subpath>', methods=["GET"])
def downloads(subpath=''):
    if not session.get("logged_in"):
        return jsonify({"error": "Not logged in"}), 401
    
    # Get project root (one level up from merkaz_backend directory)
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)

    safe_subpath = os.path.normpath(subpath).replace('\\', '/')
    if safe_subpath == '.':
        safe_subpath = ''
        
    if '/.' in safe_subpath:
        return jsonify({"error": "Invalid path"}), 404
        
    current_path = os.path.join(share_dir, safe_subpath)
    
    if not os.path.abspath(current_path).startswith(os.path.abspath(share_dir)):
        return jsonify({"error": "Access denied"}), 403

    items = []
    if os.path.exists(current_path) and os.path.isdir(current_path):
        folders = []
        files = []
        for item_name in os.listdir(current_path):
            if item_name.startswith('.'): continue
            
            item_path_os = os.path.join(current_path, item_name)
            item_path_url = os.path.join(safe_subpath, item_name).replace('\\', '/')
            
            item_data = {"name": item_name, "path": item_path_url}
            
            if os.path.isdir(item_path_os):
                item_data["is_folder"] = True
                folders.append(item_data)
            else:
                item_data["is_folder"] = False
                files.append(item_data)
        
        folders.sort(key=lambda x: x['name'].lower())
        files.sort(key=lambda x: x['name'].lower())
        
        items = folders + files
    
    back_path = os.path.dirname(safe_subpath).replace('\\', '/') if safe_subpath else None
    cooldown_level = session.get("cooldown_index", 0) + 1

    return jsonify({
        "items": items,
        "current_path": safe_subpath,
        "back_path": back_path,
        "is_admin": session.get('is_admin', False),
        "cooldown_level": cooldown_level
    }), 200


@files_bp.route("/delete/<path:item_path>", methods=["POST"])
def delete_item(item_path):
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
    
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    trash_dir = os.path.join(project_root, config.TRASH_FOLDER)

    source_path = os.path.join(share_dir, item_path)

    if not os.path.exists(source_path) or not source_path.startswith(share_dir):
        return jsonify({"error": "File or folder not found"}), 404

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(item_path)
    dest_name = f"{timestamp}_{base_name}"
    dest_path = os.path.join(trash_dir, dest_name)

    try:
        shutil.move(source_path, dest_path)
        log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "DELETE", item_path])
        return jsonify({"message": f"Successfully moved '{base_name}' to trash."}), 200
    except Exception as e:
        return jsonify({"error": f"Error deleting item: {e}"}), 500

@files_bp.route("/create_folder", methods=["POST"])
def create_folder():
    if not session.get("is_admin"):
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    parent_path = data.get("parent_path", "")
    folder_name = data.get("folder_name", "").strip()
    
    if not folder_name:
        return jsonify({"error": "Folder name cannot be empty."}), 400
    
    if '/' in folder_name or '\\' in folder_name or '..' in folder_name:
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
        return jsonify({"message": f"Folder '{folder_name}' created successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Error creating folder: {e}"}), 500

@files_bp.route("/download/file/<path:file_path>")
def download_file(file_path):
    if not session.get("logged_in"):
        return jsonify({"error": "Not logged in"}), 401
    log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "FILE", file_path])
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)

    directory, filename = os.path.split(file_path)
    safe_dir = os.path.join(share_dir, directory)
    if not safe_dir.startswith(share_dir) or not os.path.isdir(safe_dir):
        return jsonify({"error": "Access denied"}), 403
    return send_from_directory(safe_dir, filename, as_attachment=True)

@files_bp.route("/download/folder/<path:folder_path>")
def download_folder(folder_path):
    if not session.get("logged_in"):
        return jsonify({"error": "Not logged in"}), 401
    log_event(config.DOWNLOAD_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "FOLDER", folder_path])
    project_root = get_project_root()
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)

    absolute_folder_path = os.path.join(share_dir, folder_path)
    if not os.path.isdir(absolute_folder_path) or not absolute_folder_path.startswith(share_dir):
        return jsonify({"error": "Folder not found"}), 404
    
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(absolute_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zf.write(file_path, os.path.relpath(file_path, absolute_folder_path))
    memory_file.seek(0)
    return send_file(memory_file, download_name=f'{os.path.basename(folder_path)}.zip', as_attachment=True)

COOLDOWN_LEVELS = [0, 60, 300, 600, 1800, 3600]
@files_bp.route("/suggest", methods=["POST"])
def suggest():
    if not session.get("logged_in"):
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    suggestion_text = data.get("suggestion")
    if not suggestion_text:
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
            remaining = max(1, round((current_cooldown - elapsed_time) / 60))
            return jsonify({
                "error": f"You must wait another {remaining} minute(s) before submitting again.",
                "remaining_minutes": remaining
            }), 429
            
    log_event(config.SUGGESTION_LOG_FILE, [now.strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), suggestion_text])
    session["last_suggestion_time"] = now.isoformat()
    if cooldown_index < len(COOLDOWN_LEVELS) - 1:
        session["cooldown_index"] = cooldown_index + 1
    
    return jsonify({"message": "Thank you, your suggestion has been submitted!"}), 200
