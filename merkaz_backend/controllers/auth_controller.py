import re
import csv
from datetime import datetime
from flask import Blueprint, request, session, current_app, jsonify
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash
import config.config as config
from models.user_entity import User
from utils import log_event, get_next_user_id
from utils.logger_config import get_logger
from services.mail_service import send_new_user_notification, send_password_reset_email
from services.auth_service import mark_user_online, mark_user_offline
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

def email_exists(email):
    """Checks if an email exists in auth, pending, or denied users."""
    return User.find_by_email(email) or User.find_pending_by_email(email) or User.find_denied_by_email(email)

@auth_bp.before_request
def before_request():
    """Reset the session timer with each request."""
    session.permanent = True
    logger.debug("Session timer reset")

@auth_bp.route("/login", methods=["POST"])
def api_login():
    logger.info("Login attempt received")
    data = request.get_json()
    if not data:
        logger.warning("Login request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")
    logger.debug(f"Login attempt for email: {email}")

    user = User.find_by_email(email)

    if not user or not user.check_password(password):
        logger.warning(f"Login failed for email: {email} - Invalid credentials")
        log_event(config.SESSION_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "LOGIN_FAIL"])
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        logger.warning(f"Login failed for email: {email} - Account inactive")
        return jsonify({"error": "Account inactive"}), 403

    session["logged_in"] = True
    session["email"] = user.email
    session["user_id"] = user.user_id  # Store user ID in session
    session["is_admin"] = user.is_admin
    logger.debug(f"Session created for user: {email}, user_id: {user.user_id}, is_admin: {user.is_admin}")

    mark_user_online()

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
    logger.info("Registration attempt received")
    data = request.get_json()
    if not data:
        logger.warning("Registration request missing JSON body")
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")
    logger.debug(f"Registration attempt for email: {email}")

    if email_exists(email):
        logger.warning(f"Registration failed for email: {email} - Email already exists")
        return jsonify({"error": "Email already registered or pending"}), 409

    if len(password) < 8:
        logger.warning(f"Registration failed for email: {email} - Password too short")
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    hashed_password = generate_password_hash(password)
    user_id = get_next_user_id()
    logger.debug(f"Generated user_id: {user_id} for new user: {email}")
    
    # Create new user with ID using factory method (polymorphic instantiation)
    new_user = User.create_user(email=email, password=hashed_password, role='user', status='pending', user_id=user_id)
    
    # Get existing pending users and append new user
    pending_users = User.get_pending()
    pending_users.append(new_user)
    User.save_pending(pending_users)
    logger.info(f"User registered successfully: {email}, user_id: {user_id}, status: pending")

    send_new_user_notification(current_app._get_current_object(), email)
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
    session.clear()
    logger.info(f"User logged out successfully: {email}")
    return jsonify({"message": "Logged out"}), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def api_forgot_password():
    logger.info("Password reset request received")
    data = request.get_json()
    email = data.get("email")
    logger.debug(f"Password reset requested for email: {email}")
    user = User.find_by_email(email)

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

    if len(password) < 8:
        logger.warning(f"Password reset failed for email: {email} - Password too short")
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    users = User.get_all()
    user_found = False
    for user in users:
        if user.email == email:
            user.password = generate_password_hash(password)
            user_found = True
            logger.debug(f"Password hash generated for user: {email}")
            break
    
    if user_found:
        User.save_all(users)
        logger.info(f"Password reset successful for user: {email}")
        return jsonify({"message": "Your password has been updated successfully."}), 200
    else:
        logger.error(f"Password reset failed - User not found in database: {email}")
        return jsonify({"error": "An error occurred. Please try again."}), 500

@auth_bp.route("/refresh-session", methods=["GET"])
@cross_origin(supports_credentials=True)
def refresh_session():
    """Refreshes the current user's session with latest data from database."""
    logger.debug("Session refresh request received")
    if not session.get("logged_in"):
        logger.warning("Session refresh failed - User not logged in")
        return jsonify({"error": "Not logged in"}), 401
    
    email = session.get("email")
    if not email:
        logger.warning("Session refresh failed - Invalid session")
        return jsonify({"error": "Session invalid"}), 401
    
    # Get latest user data from database
    user = User.find_by_email(email)
    if not user:
        logger.error(f"Session refresh failed - User not found: {email}")
        return jsonify({"error": "User not found"}), 404
    
    # Update session with latest data
    old_is_admin = session.get("is_admin", False)
    session["is_admin"] = user.is_admin
    session["user_id"] = user.user_id
    session["email"] = user.email
    
    if old_is_admin != user.is_admin:
        logger.info(f"Session refreshed - Role changed for user: {email}, new role: {'admin' if user.is_admin else 'user'}")
    else:
        logger.debug(f"Session refreshed for user: {email}, role: {'admin' if user.is_admin else 'user'}")
    
    return jsonify({
        "message": "Session refreshed",
        "email": user.email,
        "role": "admin" if user.is_admin else "user",
        "is_admin": user.is_admin,
        "is_active": user.is_active
    }), 200

