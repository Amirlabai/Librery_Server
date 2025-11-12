from datetime import datetime
from flask import Blueprint, session, jsonify, request, current_app, send_file

import config.config as config
from models.user_entity import User
from utils import csv_to_xlsx_in_memory, get_next_user_id
from utils.logger_config import get_logger
from services.mail_service import send_approval_email, send_denial_email
from services.auth_service import mark_user_online, mark_user_offline, get_active_users

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = get_logger(__name__)


# ========== METRICS ==========
@admin_bp.route("/metrics", methods=["GET"])
def admin_metrics():
    logger.debug("Admin metrics request received")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to metrics - User: {session.get('email', 'unknown')}")
        return jsonify({"error": "Access denied"}), 403

    mark_user_online()    
    logger.debug(f"Metrics requested by admin: {session.get('email')}")

    log_files = [
        {"type": "session", "name": "Session Log (Login/Logout)", "description": "Track user login and failure events."},
        {"type": "download", "name": "Download Log (File/Folder/Delete)", "description": "Track all file, folder, and delete events."},
        {"type": "suggestion", "name": "Suggestion Log (User Feedback)", "description": "Records all user suggestions."},
    ]

    logger.info(f"Metrics retrieved successfully by admin: {session.get('email')}")
    return jsonify(log_files), 200


# ========== USERS ==========
@admin_bp.route("/users", methods=["GET"])
def admin_users():
    logger.debug("Admin users list request received")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to users list - User: {session.get('email', 'unknown')}")
        return jsonify({"error": "Access denied"}), 403

    mark_user_online()

    all_users = User.get_all()
    users_list = []

    active_now = get_active_users()
    logger.debug(f"Active sessions: {active_now}")

    for user in all_users:
        user_dict = user.to_dict() if hasattr(user, "to_dict") else {
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "is_admin": getattr(user, "is_admin", False),
            "is_active": getattr(user, "is_active", False)
        }

        user_dict["online_status"] = user.email in active_now
        users_list.append(user_dict)

    logger.info(f"Users list retrieved by admin: {session.get('email')}, total users: {len(users_list)}")
    return jsonify({
        "current_admin": session.get('email'),
        "users": users_list
    }), 200




# ========== PENDING ==========
@admin_bp.route("/pending", methods=["GET"])
def admin_pending():
    logger.debug("Admin pending users request received")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to pending users - User: {session.get('email', 'unknown')}")
        return jsonify({"error": "Access denied"}), 403

    pending_users = User.get_pending()
    users_list = [user.to_dict() if hasattr(user, "to_dict") else user for user in pending_users]
    logger.info(f"Pending users retrieved by admin: {session.get('email')}, count: {len(users_list)}")

    return jsonify(users_list), 200


# ========== DENIED ==========
@admin_bp.route("/denied", methods=["GET"])
def admin_denied():
    logger.debug("Admin denied users request received")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to denied users - User: {session.get('email', 'unknown')}")
        return jsonify({"error": "Access denied"}), 403

    denied_users = User.get_denied()
    users_list = [user.to_dict() if hasattr(user, "to_dict") else user for user in denied_users]
    logger.info(f"Denied users retrieved by admin: {session.get('email')}, count: {len(users_list)}")

    return jsonify(users_list), 200


# ========== APPROVE USER ==========
@admin_bp.route("/approve/<string:email>", methods=["POST"])
def approve_user(email):
    admin_email = session.get('email', 'unknown')
    logger.info(f"User approval request received - Admin: {admin_email}, User to approve: {email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to approve user - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403

    pending_users = User.get_pending()
    user_to_approve = next((user for user in pending_users if user.email == email), None)

    if not user_to_approve:
        logger.warning(f"User approval failed - User {email} not found in pending list")
        return jsonify({"error": f"User {email} not found in pending list"}), 404

    # Ensure user has an ID (for backward compatibility with old data)
    if user_to_approve.user_id is None:
        user_to_approve.user_id = get_next_user_id()
        logger.debug(f"Assigned user_id {user_to_approve.user_id} to user {email}")

    auth_users = User.get_all()
    user_to_approve.status = 'active'
    auth_users.append(user_to_approve)
    User.save_all(auth_users)
    logger.debug(f"User {email} added to authenticated users")

    remaining_pending = [user for user in pending_users if user.email != email]
    User.save_pending(remaining_pending)
    logger.debug(f"User {email} removed from pending list")
    
    send_approval_email(current_app._get_current_object(), email)
    logger.info(f"User {email} approved successfully by admin: {admin_email}")

    return jsonify({"message": f"User {email} approved successfully"}), 200


# ========== DENY USER ==========
@admin_bp.route("/deny/<string:email>", methods=["POST"])
def deny_user(email):
    admin_email = session.get('email', 'unknown')
    logger.info(f"User denial request received - Admin: {admin_email}, User to deny: {email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to deny user - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403

    pending_users = User.get_pending()
    user_to_deny = next((user for user in pending_users if user.email == email), None)

    if not user_to_deny:
        logger.warning(f"User denial failed - User {email} not found in pending list")
        return jsonify({"error": f"User {email} not found"}), 404

    # Ensure user has an ID (for backward compatibility with old data)
    if user_to_deny.user_id is None:
        user_to_deny.user_id = get_next_user_id()
        logger.debug(f"Assigned user_id {user_to_deny.user_id} to user {email}")

    denied_users = User.get_denied()
    denied_users.append(user_to_deny)
    User.save_denied(denied_users)
    logger.debug(f"User {email} added to denied users")

    remaining_pending = [user for user in pending_users if user.email != email]
    User.save_pending(remaining_pending)
    logger.debug(f"User {email} removed from pending list")
    
    send_denial_email(current_app._get_current_object(), email)
    logger.info(f"User {email} denied successfully by admin: {admin_email}")

    return jsonify({"message": f"User {email} has been denied"}), 200


# ========== RE-PEND USER ==========
@admin_bp.route("/re-pend/<string:email>", methods=["POST"])
def re_pend_user(email):
    admin_email = session.get('email', 'unknown')
    logger.info(f"Re-pend user request received - Admin: {admin_email}, User: {email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to re-pend user - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403

    denied_users = User.get_denied()
    user_to_re_pend = next((user for user in denied_users if user.email == email), None)

    if not user_to_re_pend:
        logger.warning(f"Re-pend failed - User {email} not found in denied list")
        return jsonify({"error": f"User {email} not found"}), 404

    # Ensure user has an ID (for backward compatibility with old data)
    if user_to_re_pend.user_id is None:
        user_to_re_pend.user_id = get_next_user_id()
        logger.debug(f"Assigned user_id {user_to_re_pend.user_id} to user {email}")

    pending_users = User.get_pending()
    pending_users.append(user_to_re_pend)
    User.save_pending(pending_users)
    logger.debug(f"User {email} moved to pending list")

    remaining_denied = [user for user in denied_users if user.email != email]
    User.save_denied(remaining_denied)
    logger.debug(f"User {email} removed from denied list")
    logger.info(f"User {email} moved back to pending by admin: {admin_email}")

    return jsonify({"message": f"User {email} moved back to pending"}), 200


# ========== TOGGLE ROLE ==========
@admin_bp.route("/toggle-role/<string:email>", methods=["POST"])
def toggle_role(email):
    admin_email = session.get('email', 'unknown')
    logger.info(f"Toggle role request received - Admin: {admin_email}, User: {email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to toggle role - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403

    if email == session.get('email'):
        logger.warning(f"Toggle role failed - Admin {admin_email} attempted to change own role")
        return jsonify({"error": "You cannot change your own admin status"}), 403

    try:
        updated_user = User.toggle_role(email)
        logger.info(f"Role toggled successfully - User: {email}, New role: {updated_user.role}, Admin: {admin_email}")
        # Return updated user info so frontend can refresh if it's the current user
        return jsonify({
            "message": f"Successfully updated role for {email}",
            "updated_user": {
                "email": updated_user.email,
                "role": updated_user.role,
                "is_admin": updated_user.is_admin
            }
        }), 200
    except ValueError as e:
        logger.error(f"Toggle role failed - User {email} not found: {str(e)}")
        return jsonify({"error": str(e)}), 404


# ========== TOGGLE STATUS ==========
@admin_bp.route("/toggle-status/<string:email>", methods=["POST"])
def toggle_status(email):
    admin_email = session.get('email', 'unknown')
    logger.info(f"Toggle status request received - Admin: {admin_email}, User: {email}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to toggle status - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403

    if email == session.get('email'):
        logger.warning(f"Toggle status failed - Admin {admin_email} attempted to change own status")
        return jsonify({"error": "You cannot change your own status"}), 403

    try:
        updated_user = User.toggle_status(email)
        logger.info(f"Status toggled successfully - User: {email}, New status: {updated_user.status}, Admin: {admin_email}")
        return jsonify({"message": f"Successfully updated status for {email}"}), 200
    except ValueError as e:
        logger.error(f"Toggle status failed - User {email} not found: {str(e)}")
        return jsonify({"error": str(e)}), 404


# ========== DOWNLOAD METRICS XLSX ==========
@admin_bp.route("/metrics/download/<log_type>", methods=["GET"])
def download_metrics_xlsx(log_type):
    admin_email = session.get('email', 'unknown')
    logger.info(f"Metrics download request received - Admin: {admin_email}, Log type: {log_type}")
    if not session.get("is_admin"):
        logger.warning(f"Access denied to download metrics - User: {admin_email}")
        return jsonify({"error": "Access denied"}), 403

    log_map = {
        "session": (config.SESSION_LOG_FILE, "Session_Log"),
        "download": (config.DOWNLOAD_LOG_FILE, "Download_Log"),
        "suggestion": (config.SUGGESTION_LOG_FILE, "Suggestion_Log"),
        "upload": (config.UPLOAD_LOG_FILE, "Upload_Log"),
        "declined": (config.DECLINED_UPLOAD_LOG_FILE, "Declined_Upload_Log"),
    }

    if log_type not in log_map:
        logger.warning(f"Invalid log type requested: {log_type}")
        return jsonify({"error": "Invalid log type"}), 404

    csv_filepath, file_prefix = log_map[log_type]
    logger.debug(f"Converting log file to XLSX: {csv_filepath}")

    try:
        xlsx_data = csv_to_xlsx_in_memory(csv_filepath)
        download_name = f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        logger.info(f"Metrics file generated successfully - Type: {log_type}, Admin: {admin_email}")

        return send_file(
            xlsx_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name=download_name,
            as_attachment=True
        )
    except FileNotFoundError:
        logger.error(f"Log file not found: {csv_filepath}")
        return jsonify({"error": "Log file not found"}), 404
    except Exception as e:
        logger.error(f"Error during XLSX conversion: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error during XLSX conversion: {e}"}), 500


# ========== HEARTBEAT ==========
@admin_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    logger.debug("Heartbeat request received")
    if "email" not in session:
        logger.warning("Heartbeat failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    mark_user_online()
    logger.debug(f"Heartbeat processed for user: {session.get('email')}")
    return jsonify({"message": "Heartbeat received"}), 200
