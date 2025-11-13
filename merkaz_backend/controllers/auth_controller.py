import re
import csv
from datetime import datetime
from flask import Blueprint, request, session, current_app, jsonify
from flask_cors import cross_origin
import config.config as config
from utils import log_event
from utils.logger_config import get_logger
from services.mail_service import send_new_user_notification, send_password_reset_email
from services.auth_service import AuthService, mark_user_online, mark_user_offline
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

@auth_bp.before_request
def before_request():
    """Reset the session timer with each request."""
    session.permanent = True
    logger.debug("Session timer reset")

@auth_bp.route("/login", methods=["POST"])
def api_login():
    logger.info("Login request received")
    data = request.get_json()
    if not data:
        logger.warning("Login request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")
    logger.debug(f"Login attempt for email: {email}")

    user, error = AuthService.login(email, password)
    
    if error:
        logger.warning(f"Login failed - {error} for email: {email}")
        log_event(config.SESSION_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "LOGIN_FAIL"])
        return jsonify({"error": error}), 401 if error == "Invalid credentials" else 403

    log_event(config.SESSION_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "LOGIN_SUCCESS"])
    logger.info(f"Login successful for user: {email}, role: {'admin' if user.is_admin else 'user'}")

    return jsonify({
        "message": "Login successful",
        "email": user.email,
        "role": "admin" if user.is_admin else "user",
        "token": "mock-token"
    }), 200

@auth_bp.route("/register", methods=["POST"])
def api_register():
    logger.info("Registration request received")
    data = request.get_json()
    if not data:
        logger.warning("Registration request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")
    logger.debug(f"Registration attempt for email: {email}")

    new_user, error = AuthService.register(email, password)
    
    if error:
        status_code = 409 if error == "Email already registered or pending" else 400
        logger.warning(f"Registration failed - {error} for email: {email}")
        return jsonify({"error": error}), status_code

    send_new_user_notification(current_app._get_current_object(), email)
    logger.info(f"Registration successful - Email: {email}, user_id: {new_user.user_id}")
    return jsonify({"message": "Registration successful. Pending admin approval."}), 201

@auth_bp.route("/logout", methods=["POST"])
@cross_origin(supports_credentials=True)
def logout():
    email = session.get("email", "unknown")
    logger.info(f"Logout request for user: {email}")
    log_event(
        config.SESSION_LOG_FILE,
        [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "LOGOUT"]
    )
    mark_user_offline()
    AuthService.clear_session()
    logger.info(f"User logged out successfully: {email}")
    return jsonify({"message": "Logged out"}), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def api_forgot_password():
    logger.info("Password reset request received")
    data = request.get_json()
    email = data.get("email")
    logger.debug(f"Password reset requested for email: {email}")
    user = AuthService.find_user_by_email(email)

    if not user:
        logger.warning(f"Password reset failed - Email not found: {email}")
        return jsonify({"error": "Email not found"}), 404

    s = URLSafeTimedSerializer(config.TOKEN_SECRET_KEY)
    token = s.dumps(email, salt='password-reset-salt')
    logger.debug(f"Password reset token generated for email: {email}")
    send_password_reset_email(current_app._get_current_object(), email, token)
    logger.info(f"Password reset email sent to: {email}")

    return jsonify({"message": "Password reset link sent"}), 200


@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    logger.info("Password reset attempt received")
    s = URLSafeTimedSerializer(config.TOKEN_SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiration
        logger.debug(f"Password reset token validated for email: {email}")
    except (SignatureExpired, BadTimeSignature) as e:
        logger.warning(f"Password reset failed - Invalid or expired token: {str(e)}")
        return jsonify({"error": "The password reset link is invalid or has expired."}), 400

    data = request.get_json()
    if not data:
        logger.warning("Password reset request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400

    password = data.get("password")
    if not password:
        logger.warning(f"Password reset failed for email: {email} - Password not provided")
        return jsonify({"error": "Password is required"}), 400

    success, error = AuthService.reset_password(email, password)
    
    if error:
        status_code = 400 if "Password must be at least" in error else 500
        logger.warning(f"Password reset failed - {error} for email: {email}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Password reset successful for user: {email}")
    return jsonify({"message": "Your password has been updated successfully."}), 200

@auth_bp.route("/refresh-session", methods=["GET"])
@cross_origin(supports_credentials=True)
def refresh_session():
    """Refreshes the current user's session with latest data from database."""
    logger.debug("Session refresh request received")
    if not session.get("logged_in"):
        logger.warning("Session refresh failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    
    user_data, error = AuthService.refresh_session()
    
    if error:
        status_code = 401 if "Session invalid" in error else 404
        logger.warning(f"Session refresh failed - {error}")
        return jsonify({"error": error}), status_code
    
    logger.info(f"Session refreshed successfully - Email: {user_data['email']}")
    return jsonify({
        "message": "Session refreshed",
        **user_data
    }), 200

