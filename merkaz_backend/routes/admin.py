from datetime import datetime
from flask import Blueprint, render_template, session, abort, redirect, url_for, flash, send_file, current_app

import config
from user import User
from utils import csv_to_xlsx_in_memory
from mailer import send_approval_email, send_denial_email

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route("/metrics")
def admin_metrics():
    if not session.get("is_admin"): abort(403)
    log_files = [
        {"type": "session", "name": "Session Log (Login/Logout)", "description": "Track user login and failure events."},
        {"type": "download", "name": "Download Log (File/Folder/Delete)", "description": "Track all file, folder, and delete events."},
        {"type": "suggestion", "name": "Suggestion Log (User Feedback)", "description": "Records all user suggestions."},
    ]
    return render_template("admin_metrics.html", log_files=log_files)

@admin_bp.route("/users")
def admin_users():
    if not session.get("is_admin"): abort(403)
    all_users = User.get_all()
    return render_template("admin_users.html", users=all_users, current_user_email=session.get('email'))

@admin_bp.route("/pending")
def admin_pending():
    if not session.get("is_admin"): abort(403)
    pending_users = User.get_pending()
    return render_template("admin_pending.html", users=pending_users)

@admin_bp.route("/denied")
def admin_denied():
    if not session.get("is_admin"): abort(403)
    denied_users = User.get_denied()
    return render_template("admin_denied.html", users=denied_users)

@admin_bp.route("/approve/<string:email>", methods=["POST"])
def approve_user(email):
    if not session.get("is_admin"): abort(403)
    pending_users = User.get_pending()
    user_to_approve = next((user for user in pending_users if user.email == email), None)

    if user_to_approve:
        auth_users = User.get_all()
        user_to_approve.status = 'active'
        auth_users.append(user_to_approve)
        User.save_all(auth_users)

        remaining_pending = [user for user in pending_users if user.email != email]
        User.save_pending(remaining_pending)
        send_approval_email(current_app._get_current_object(), email)
        flash(f"User {email} has been approved.", "success")
    else:
        flash(f"Could not find pending user {email}.", "error")
    return redirect(url_for('admin.admin_pending'))

@admin_bp.route("/deny/<string:email>", methods=["POST"])
def deny_user(email):
    if not session.get("is_admin"): abort(403)
    pending_users = User.get_pending()
    user_to_deny = next((user for user in pending_users if user.email == email), None)

    if user_to_deny:
        denied_users = User.get_denied()
        denied_users.append(user_to_deny)
        User.save_denied(denied_users)

        remaining_pending = [user for user in pending_users if user.email != email]
        User.save_pending(remaining_pending)
        send_denial_email(current_app._get_current_object(), email)
        flash(f"Registration for {email} has been denied.", "success")
    else:
        flash(f"Could not find pending user {email}.", "error")
    return redirect(url_for('admin.admin_pending'))

@admin_bp.route("/re_pend/<string:email>", methods=["POST"])
def re_pend_user(email):
    if not session.get("is_admin"): abort(403)
    denied_users = User.get_denied()
    user_to_re_pend = next((user for user in denied_users if user.email == email), None)

    if user_to_re_pend:
        pending_users = User.get_pending()
        pending_users.append(user_to_re_pend)
        User.save_pending(pending_users)

        remaining_denied = [user for user in denied_users if user.email != email]
        User.save_denied(remaining_denied)
        flash(f"User {email} has been moved back to pending.", "success")
    else:
        flash(f"Could not find denied user {email}.", "error")
    return redirect(url_for('admin.admin_denied'))

@admin_bp.route("/toggle_role/<string:email>", methods=["POST"])
def toggle_role(email):
    if not session.get("is_admin"): abort(403)
    if email == session.get('email'):
        flash("For security, you cannot change your own admin status.", "error")
        return redirect(url_for('admin.admin_users'))
    users = User.get_all()
    user_found = False
    for user in users:
        if user.email == email:
            user.role = 'user' if user.is_admin else 'admin'
            user_found = True
            break
    if user_found:
        User.save_all(users)
        flash(f"Successfully updated role for {email}.", "success")
    else:
        flash(f"Could not find user {email}.", "error")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route("/toggle_status/<string:email>", methods=["POST"])
def toggle_status(email):
    if not session.get("is_admin"): abort(403)
    if email == session.get('email'):
        flash("You cannot change your own status.", "error")
        return redirect(url_for('admin.admin_users'))
    users = User.get_all()
    user_found = False
    for user in users:
        if user.email == email:
            user.status = 'inactive' if user.is_active else 'active'
            user_found = True
            break
    if user_found:
        User.save_all(users)
        flash(f"Successfully updated status for {email}.", "success")
    else:
        flash(f"Could not find user {email}.", "error")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route("/metrics/download/<log_type>")
def download_metrics_xlsx(log_type):
    if not session.get("is_admin"): abort(403)
    log_map = {
        "session": (config.SESSION_LOG_FILE, "Session_Log"),
        "download": (config.DOWNLOAD_LOG_FILE, "Download_Log"),
        "suggestion": (config.SUGGESTION_LOG_FILE, "Suggestion_Log")
    }
    if log_type not in log_map: return abort(404)
    
    csv_filepath, file_prefix = log_map[log_type]
    try:
        xlsx_data = csv_to_xlsx_in_memory(csv_filepath)
        download_name = f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(xlsx_data, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         download_name=download_name, as_attachment=True)
    except FileNotFoundError:
        return abort(404)
    except Exception as e:
        print(f"Error during XLSX conversion: {e}")
        return abort(500)
