from flask import Blueprint, session, jsonify, request
from utils.logger_config import get_logger
from services.upload_service import UploadService
from repositories.user_repository import UserRepository

uploads_bp = Blueprint('uploads', __name__)
logger = get_logger(__name__)


@uploads_bp.route("/upload", methods=["POST"])
def upload_file():
    logger.info("Upload request received")
    if not session.get("logged_in"):
        logger.warning("Upload failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    
    uploaded_files = request.files.getlist("file")
    if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ''):
        logger.warning("Upload failed - No files selected")
        return jsonify({"error": "No files selected"}), 400
    
    upload_subpath = request.form.get('subpath', '')
    email = session.get("email")
    user_id = session.get("user_id")
    
    if user_id is None:
        user = UserRepository.find_by_email(email)
        user_id = user.user_id if user else None
    
    successful_uploads, errors, failed_files_by_type, error_summary = UploadService.upload_files(
        uploaded_files, upload_subpath, email, user_id
    )
    
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
        logger.info(f"Upload completed successfully - Files: {len(successful_uploads)}, User: {email}")
        return jsonify(response), 200
    else:
        if errors:
            if len(errors) <= 5:
                logger.warning(f"Upload failed - No files uploaded, Errors: {len(errors)}, User: {email}")
                return jsonify({"error": "No files were uploaded", "errors": errors}), 400
            else:
                logger.warning(f"Upload failed - No files uploaded, Errors: {len(errors)}, User: {email}")
                return jsonify({"error": "No files were uploaded", "errors": [error_summary], "error_count": len(errors)}), 400
        else:
            logger.warning(f"Upload failed - No files uploaded, User: {email}")
            return jsonify({"error": "No files were uploaded", "errors": errors}), 400

@uploads_bp.route('/my_uploads')
def my_uploads():
    logger.debug("My uploads request received")
    if not session.get('logged_in'):
        logger.warning("My uploads failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    
    user_email = session.get('email')
    user_id = session.get('user_id')
    
    if user_id is None:
        user = UserRepository.find_by_email(user_email)
        user_id = user.user_id if user else None
    
    user_uploads = UploadService.get_my_uploads(user_email, user_id)
    logger.info(f"Retrieved {len(user_uploads)} uploads for user: {user_email}")
    return jsonify(user_uploads), 200

@uploads_bp.route("/admin/uploads")
def admin_uploads():
    logger.debug("Admin uploads request received")
    if not session.get("is_admin"):
        logger.warning("Admin uploads failed - Access denied")
        return jsonify({"error": "Access denied"}), 403
    
    all_uploads_list = UploadService.get_admin_uploads()
    logger.info(f"Retrieved {len(all_uploads_list)} pending uploads for admin review")
    return jsonify(all_uploads_list), 200

@uploads_bp.route("/admin/move_upload/<path:filename>", methods=["POST"])
def move_upload(filename):
    admin_email = session.get("email", "unknown")
    logger.info(f"Move upload request - File: {filename}, Admin: {admin_email}")
    if not session.get("is_admin"):
        logger.warning(f"Move upload failed - Access denied, User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json()
    if not data:
        logger.warning("Move upload failed - Missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400
    
    target_path_str = data.get("target_path")
    if not target_path_str:
        logger.warning("Move upload failed - Target path empty")
        return jsonify({"error": "Target path cannot be empty"}), 400
    
    upload_id = data.get("upload_id")
    
    success, error = UploadService.move_upload(upload_id, filename, target_path_str, admin_email)
    
    if error:
        status_code = 404 if "not found" in error.lower() else 400
        logger.warning(f"Move upload failed - {error} for file: {filename}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Upload moved successfully - File: {filename}, Target: {target_path_str}, Admin: {admin_email}")
    return jsonify({"message": f'Item "{filename}" has been successfully moved to "{target_path_str}".'}), 200

@uploads_bp.route("/admin/decline_upload/<path:filename>", methods=["POST"])
def decline_upload(filename):
    admin_email = session.get("email", "unknown")
    logger.info(f"Decline upload request - File: {filename}, Admin: {admin_email}")
    if not session.get("is_admin"):
        logger.warning(f"Decline upload failed - Access denied, User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json() or {}
    upload_id = data.get("upload_id")
    user_email = data.get("email", "unknown")
    user_id = data.get("user_id")
    
    success, error = UploadService.decline_upload(upload_id, filename, user_email, user_id)
    
    if error:
        status_code = 404 if "already removed" in error.lower() else 500
        logger.warning(f"Decline upload failed - {error} for file: {filename}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Upload declined successfully - File: {filename}, Admin: {admin_email}")
    return jsonify({"message": f'Item "{filename}" has been declined and removed.'}), 200

@uploads_bp.route("/admin/edit_upload_path/", methods=["POST"])
def edit_upload_path():
    admin_email = session.get("email", "unknown")
    logger.info(f"Edit upload path request - Admin: {admin_email}")
    if not session.get("is_admin"):
        logger.warning(f"Edit upload path failed - Access denied, User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403
    
    data = request.get_json() or {}
    request_upload_id = data.get("upload_id")
    request_new_path = data.get("new_path", "")
    
    if not request_upload_id:
        logger.warning("Edit upload path failed - upload_id required")
        return jsonify({"error": "upload_id is required"}), 400
    
    if not request_new_path:
        logger.warning("Edit upload path failed - new_path required")
        return jsonify({"error": "new_path is required"}), 400
    
    # Remove leading slash if present
    if request_new_path.startswith('/'):
        request_new_path = request_new_path[1:]
    
    success, error = UploadService.edit_upload_path(request_upload_id, request_new_path)
    
    if error:
        status_code = 404 if "not found" in error.lower() else 500
        logger.warning(f"Edit upload path failed - {error} for ID: {request_upload_id}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Upload path updated successfully - ID: {request_upload_id}, Admin: {admin_email}")
    return jsonify({"success": True, "message": f"Path updated for upload_id {request_upload_id}"}), 200
