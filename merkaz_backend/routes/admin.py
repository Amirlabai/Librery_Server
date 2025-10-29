from datetime import datetime
from flask import Blueprint, session, abort, jsonify, request, current_app, send_file

import config
from user import User
from utils import csv_to_xlsx_in_memory
from mailer import send_approval_email, send_denial_email
from routes.session_tracker import mark_user_online, mark_user_offline, active_sessions

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ========== METRICS ==========
@admin_bp.route("/metrics", methods=["GET"])
def admin_metrics():
    if not session.get("is_admin"):
        abort(403)

    mark_user_online()    

    log_files = [
        {"type": "session", "name": "Session Log (Login/Logout)", "description": "Track user login and failure events."},
        {"type": "download", "name": "Download Log (File/Folder/Delete)", "description": "Track all file, folder, and delete events."},
        {"type": "suggestion", "name": "Suggestion Log (User Feedback)", "description": "Records all user suggestions."},
    ]

    return jsonify(log_files), 200


# ========== USERS ==========
from datetime import datetime
from flask import Blueprint, session, abort, jsonify
import config
from user import User
from utils import csv_to_xlsx_in_memory
from mailer import send_approval_email, send_denial_email
from routes.session_tracker import mark_user_online, get_active_users

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route("/users", methods=["GET"])
def admin_users():
    if not session.get("is_admin"):
        abort(403)

    mark_user_online()

    all_users = User.get_all()
    users_list = []

    active_now = get_active_users()
    print("🟢 Active sessions right now:", active_now)

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

    return jsonify({
        "current_admin": session.get('email'),
        "users": users_list
    }), 200




# ========== PENDING ==========
@admin_bp.route("/pending", methods=["GET"])
def admin_pending():
    if not session.get("is_admin"):
        abort(403)

    pending_users = User.get_pending()


    users_list = [user.to_dict() if hasattr(user, "to_dict") else user for user in pending_users]

    return jsonify(users_list), 200


# ========== DENIED ==========
@admin_bp.route("/denied", methods=["GET"])
def admin_denied():
    if not session.get("is_admin"):
        abort(403)

    denied_users = User.get_denied()
    users_list = [user.to_dict() if hasattr(user, "to_dict") else user for user in denied_users]

    return jsonify(users_list), 200


# ========== APPROVE USER ==========
@admin_bp.route("/approve/<string:email>", methods=["POST"])
def approve_user(email):
    if not session.get("is_admin"):
        abort(403)

    pending_users = User.get_pending()
    user_to_approve = next((user for user in pending_users if user.email == email), None)

    if not user_to_approve:
        return jsonify({"error": f"User {email} not found in pending list"}), 404

    auth_users = User.get_all()
    user_to_approve.status = 'active'
    auth_users.append(user_to_approve)
    User.save_all(auth_users)

    remaining_pending = [user for user in pending_users if user.email != email]
    User.save_pending(remaining_pending)
    send_approval_email(current_app._get_current_object(), email)

    return jsonify({"message": f"User {email} approved successfully"}), 200


# ========== DENY USER ==========
@admin_bp.route("/deny/<string:email>", methods=["POST"])
def deny_user(email):
    if not session.get("is_admin"):
        abort(403)

    pending_users = User.get_pending()
    user_to_deny = next((user for user in pending_users if user.email == email), None)

    if not user_to_deny:
        return jsonify({"error": f"User {email} not found"}), 404

    denied_users = User.get_denied()
    denied_users.append(user_to_deny)
    User.save_denied(denied_users)

    remaining_pending = [user for user in pending_users if user.email != email]
    User.save_pending(remaining_pending)
    send_denial_email(current_app._get_current_object(), email)

    return jsonify({"message": f"User {email} has been denied"}), 200


# ========== RE-PEND USER ==========
@admin_bp.route("/re-pend/<string:email>", methods=["POST"])
def re_pend_user(email):
    if not session.get("is_admin"):
        abort(403)

    denied_users = User.get_denied()
    user_to_re_pend = next((user for user in denied_users if user.email == email), None)

    if not user_to_re_pend:
        return jsonify({"error": f"User {email} not found"}), 404

    pending_users = User.get_pending()
    pending_users.append(user_to_re_pend)
    User.save_pending(pending_users)

    remaining_denied = [user for user in denied_users if user.email != email]
    User.save_denied(remaining_denied)

    return jsonify({"message": f"User {email} moved back to pending"}), 200


# ========== TOGGLE ROLE ==========
@admin_bp.route("/toggle-role/<string:email>", methods=["POST"])
def toggle_role(email):
    if not session.get("is_admin"):
        abort(403)

    if email == session.get('email'):
        return jsonify({"error": "You cannot change your own admin status"}), 403

    users = User.get_all()
    user_found = False
    for user in users:
        if user.email == email:
            user.role = 'user' if user.is_admin else 'admin'
            user_found = True
            break

    if not user_found:
        return jsonify({"error": f"User {email} not found"}), 404

    User.save_all(users)
    return jsonify({"message": f"Successfully updated role for {email}"}), 200


# ========== TOGGLE STATUS ==========
@admin_bp.route("/toggle-status/<string:email>", methods=["POST"])
def toggle_status(email):
    if not session.get("is_admin"):
        abort(403)

    if email == session.get('email'):
        return jsonify({"error": "You cannot change your own status"}), 403

    users = User.get_all()
    user_found = False
    for user in users:
        if user.email == email:
            user.status = 'inactive' if user.is_active else 'active'
            user_found = True
            break

    if not user_found:
        return jsonify({"error": f"User {email} not found"}), 404

    User.save_all(users)
    return jsonify({"message": f"Successfully updated status for {email}"}), 200


# ========== DOWNLOAD METRICS XLSX ==========
@admin_bp.route("/metrics/download/<log_type>", methods=["GET"])
def download_metrics_xlsx(log_type):
    if not session.get("is_admin"):
        abort(403)

    log_map = {
        "session": (config.SESSION_LOG_FILE, "Session_Log"),
        "download": (config.DOWNLOAD_LOG_FILE, "Download_Log"),
        "suggestion": (config.SUGGESTION_LOG_FILE, "Suggestion_Log")
    }

    if log_type not in log_map:
        abort(404)

    csv_filepath, file_prefix = log_map[log_type]

    try:
        xlsx_data = csv_to_xlsx_in_memory(csv_filepath)
        download_name = f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return send_file(
            xlsx_data,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name=download_name,
            as_attachment=True
        )
    except FileNotFoundError:
        abort(404)
    except Exception as e:
        print(f"Error during XLSX conversion: {e}")
        abort(500)


# ========== HEARTBEAT ==========
@admin_bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    
    if "email" not in session:
        return jsonify({"error": "Not logged in"}), 401
    mark_user_online()
    return jsonify({"message": "Heartbeat received"}), 200
