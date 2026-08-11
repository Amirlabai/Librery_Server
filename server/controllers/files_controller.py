from flask import Blueprint, session, send_from_directory, send_file, jsonify, request
from utils.logger_config import get_logger
from services.file_service import FileService
from services.auth_service import AuthService, mark_user_online, is_user_admin
from utils.log_utils import log_event
from datetime import datetime
from flask_cors import cross_origin
from urllib.parse import quote
import config.config as config
from utils.path_utils import resolve_config_path
import json
import os
import csv

files_bp = Blueprint('files', __name__)
logger = get_logger(__name__)

@files_bp.before_request
def before_request():
    """Mark user as online and reset session timer with each request."""
    session.permanent = True
    if AuthService.get_current_email():
        mark_user_online()
    logger.debug("Session timer reset for files blueprint")

@files_bp.route('/browse', defaults={'subpath': ''}, methods=["GET"])
@files_bp.route('/browse/<path:subpath>', methods=["GET"])
def downloads(subpath=''):
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    user_email = AuthService.get_current_email() or "unknown"
    logger.debug(f"Browse request received, User: {user_email}")

    browse_data, error = FileService.browse_directory(subpath)
    
    if error:
        status_code = 403 if error == "Access denied" else 404
        logger.warning(f"Browse failed - {error} for path: {subpath}")
        return jsonify({"error": error}), status_code
    
    cooldown_level = session.get("cooldown_index", 0)
    logger.info(f"Browse completed - Path: {subpath}, Files: {len(browse_data['files'])}, Folders: {len(browse_data['folders'])}, User: {user_email}")
    
    return jsonify({
        **browse_data,
        "is_admin": is_user_admin(),
        "cooldown_level": cooldown_level
    }), 200


@files_bp.route("/delete/<path:item_path>", methods=["POST"])
def delete_item(item_path):
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    admin_email = AuthService.get_current_email() or "unknown"
    logger.info(f"Delete request received - Path: {item_path}, Admin: {admin_email}")
    if not is_user_admin():
        logger.warning(f"Access denied to delete - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    base_name = os.path.basename(item_path)
    success, error = FileService.delete_item(item_path, admin_email)
    
    if error:
        status_code = 404 if "not found" in error.lower() else 500
        logger.warning(f"Delete failed - {error} for path: {item_path}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Item deleted successfully - Path: {item_path}, Admin: {admin_email}")
    return jsonify({"message": f"Successfully moved '{base_name}' to trash."}), 200

@files_bp.route("/create_folder", methods=["POST"])
def create_folder():
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    admin_email = AuthService.get_current_email() or "unknown"
    logger.info(f"Create folder request received - Admin: {admin_email}")
    if not is_user_admin():
        logger.warning(f"Access denied to create folder - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json()
    if not data:
        logger.warning("Create folder request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400
    
    parent_path = data.get("parent_path", "")
    folder_name = data.get("folder_name", "").strip()
    logger.debug(f"Creating folder - Name: {folder_name}, Parent: {parent_path}")
    
    success, error = FileService.create_folder(parent_path, folder_name, admin_email)
    
    if error:
        status_code = 400 if "cannot be empty" in error or "Invalid" in error else (409 if "already exists" in error else 500)
        logger.warning(f"Create folder failed - {error} for name: {folder_name}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Folder created successfully - Name: {folder_name}, Admin: {admin_email}")
    return jsonify({"message": f"Folder '{folder_name}' created successfully."}), 200

@files_bp.route("/download/file/<path:file_path>")
def download_file(file_path):
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    user_email = AuthService.get_current_email() or "unknown"
    logger.info(f"File download request - Path: {file_path}, User: {user_email}")

    log_event(resolve_config_path(config.DOWNLOAD_LOG_FILE), [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_email, "FILE", file_path])
    
    safe_dir, filename, error = FileService.get_download_file_path(file_path)
    
    if error:
        logger.warning(f"File download failed - {error} for path: {file_path}, User: {user_email}")
        return jsonify({"error": error}), 403
    
    logger.debug(f"File download successful - File: {filename}, User: {user_email}")
    return send_from_directory(safe_dir, filename, as_attachment=True)

@files_bp.route("/download/folder/<path:folder_path>")
def download_folder(folder_path):
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    user_email = AuthService.get_current_email() or "unknown"
    logger.info(f"Folder download request - Path: {folder_path}, User: {user_email}")

    log_event(resolve_config_path(config.DOWNLOAD_LOG_FILE), [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_email, "FOLDER", folder_path])
    
    absolute_folder_path, error = FileService.get_download_folder_path(folder_path)
    
    if error:
        logger.warning(f"Folder download failed - {error} for path: {folder_path}")
        return jsonify({"error": error}), 404
    
    memory_file = FileService.create_zip_from_folder(absolute_folder_path)
    logger.debug(f"Folder download successful - Folder: {folder_path}, User: {user_email}")
    return send_file(memory_file, download_name=f'{os.path.basename(folder_path)}.zip', as_attachment=True)

@files_bp.route("/preview/<path:file_path>")
def preview_file(file_path):
    """Preview a file in the browser (without forcing download)."""
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    user_email = AuthService.get_current_email() or "unknown"
    logger.info(f"File preview request - Path: {file_path}, User: {user_email}")
    
    safe_dir, filename, mime_type, error = FileService.get_preview_file_path(file_path)
    
    if error:
        logger.warning(f"File preview failed - {error} for path: {file_path}, User: {user_email}")
        return jsonify({"error": error}), 403 if error == "Access denied" else 404
    
    logger.debug(f"File preview successful - File: {filename}, MIME: {mime_type}, User: {user_email}")
    # Send file without attachment flag so browser can preview it
    # IMPORTANT: as_attachment=False ensures inline display, not download
    response = send_from_directory(safe_dir, filename, mimetype=mime_type, as_attachment=False)
    
    # Force Content-Disposition to inline to prevent downloads
    # Add headers to allow preview with proper Unicode encoding for filenames
    # Use RFC 2231 encoding for non-ASCII characters to avoid Waitress latin-1 encoding errors
    try:
        # Check if filename contains non-ASCII characters
        try:
            filename.encode('ascii')
            # Filename is ASCII-safe - use standard format
            response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
        except UnicodeEncodeError:
            # Filename contains non-ASCII characters - use RFC 2231 encoding
            # Format: filename*=UTF-8''encoded_filename
            filename_utf8_encoded = quote(filename, safe='')
            response.headers['Content-Disposition'] = f"inline; filename*=UTF-8''{filename_utf8_encoded}"
    except Exception as e:
        # Fallback: set inline without filename if encoding fails
        logger.warning(f"Error encoding filename for Content-Disposition header: {e}")
        response.headers['Content-Disposition'] = 'inline'
    
    # Ensure Content-Type is set correctly
    if mime_type:
        response.headers['Content-Type'] = mime_type
    
    # Add headers to allow embedding in iframes/objects
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Allow embedding in same origin (for preview modal)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    return response

@files_bp.route("/search", methods=["GET"])
def search():
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401

    user_email = AuthService.get_current_email() or "unknown"
    logger.info(f"Search request received - User: {user_email}")
    search_query = request.args.get("q", "")
    folder_path = request.args.get("folder_path", "")
    search_results, error = FileService.search_uploaded_files(search_query,folder_path)

    if error:
        logger.warning(f"Search failed - {error} for query: {search_query}, User: {user_email}")
        return jsonify({"error": error}), 404

    logger.info(f"Search completed - Query: {search_query}, Results: {len(search_results)}, User: {user_email}")
    cooldown_level = session.get("cooldown_index", 0)

    return jsonify({**search_results,
        "is_admin": is_user_admin(),
        "cooldown_level": cooldown_level
    }), 200

@files_bp.route("/suggest", methods=["POST"])
def suggest():
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    user_email = AuthService.get_current_email() or "unknown"
    logger.debug(f"Suggestion submission request - User: {user_email}")
    
    data = request.get_json()
    if not data:
        logger.warning("Suggestion submission missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400
    
    suggestion_text = data.get("suggestion")
    
    success, error = FileService.submit_suggestion(suggestion_text, user_email, session)
    
    if error:
        if "wait another" in error:
            # Extract remaining minutes from error message for response
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', error)
            remaining = float(match.group(1)) if match else 1
            logger.warning(f"Suggestion submission failed - Cooldown active, User: {user_email}")
            return jsonify({
                "error": error,
                "remaining_minutes": remaining
            }), 429
        logger.warning(f"Suggestion submission failed - {error}, User: {user_email}")
        return jsonify({"error": error}), 400
    
    logger.info(f"Suggestion submitted successfully - User: {user_email}")
    return jsonify({"message": "Thank you, your suggestion has been submitted!"}), 200

@files_bp.route("/useful_links", methods=["GET"])
def get_useful_links():
    """Get useful links from CSV file."""
    ok, error_msg = AuthService.require_auth()
    if not ok:
        return jsonify({"error": error_msg}), 401
    user_email = AuthService.get_current_email() or "unknown"
    logger.debug(f"Useful links request - User: {user_email}")
    
    try:
        useful_links_list = []
        useful_links_path = config.USEFUL_LINKS_FILE
        with open(useful_links_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 4 or row[0] == "url":
                    logger.warning(f"Invalid row in useful links file: {row}")
                    continue
                useful_links_list.append({
                    "url": row[0],
                    "title": row[1],
                    "description": row[2],
                    "dir": row[3]
                })
        
        logger.debug(f"Useful links retrieved successfully - Count: {len(useful_links_list) if isinstance(useful_links_list, list) else 0}, User: {user_email}")
        return jsonify(useful_links_list), 200
    except Exception as e:
        logger.error(f"Error reading useful links file: {e}")
        return jsonify({"error": "Failed to read useful links file"}), 500
