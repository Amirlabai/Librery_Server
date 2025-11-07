import re
import csv
from datetime import datetime
from flask import Blueprint, request, session, current_app, jsonify
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash
import config.config as config
from models.user_entity import User
from utils import log_event, get_next_user_id
from services.mail_service import send_new_user_notification, send_password_reset_email
from services.auth_service import mark_user_online, mark_user_offline
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

auth_bp = Blueprint('auth', __name__)

def email_exists(email):
    """Checks if an email exists in auth, pending, or denied users."""
    return User.find_by_email(email) or User.find_pending_by_email(email) or User.find_denied_by_email(email)

@auth_bp.before_request
def before_request():
    """Reset the session timer with each request."""
    session.permanent = True

@auth_bp.route("/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400


    email = data.get("email")
    password = data.get("password")


    user = User.find_by_email(email)

    if not user or not user.check_password(password):
        log_event(config.SESSION_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "LOGIN_FAIL"])
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account inactive"}), 403


    session["logged_in"] = True
    session["email"] = user.email
    session["user_id"] = user.user_id  # Store user ID in session
    session["is_admin"] = user.is_admin

    mark_user_online()

    log_event(config.SESSION_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "LOGIN_SUCCESS"])

    return jsonify({
        "message": "Login successful",
        "email": user.email,
        "role": "admin" if user.is_admin else "user",
        "token": "mock-token"
    }), 200

@auth_bp.route("/register", methods=["POST"])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    email = data.get("email")
    password = data.get("password")

    if email_exists(email):
        return jsonify({"error": "Email already registered or pending"}), 409

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    hashed_password = generate_password_hash(password)
    user_id = get_next_user_id()
    
    # Create new user with ID
    new_user = User(email=email, password=hashed_password, role='user', status='pending', user_id=user_id)
    
    # Get existing pending users and append new user
    pending_users = User.get_pending()
    pending_users.append(new_user)
    User.save_pending(pending_users)

    send_new_user_notification(current_app._get_current_object(), email)
    return jsonify({"message": "Registration successful. Pending admin approval."}), 201

@auth_bp.route("/logout", methods=["POST"])
@cross_origin(supports_credentials=True)
def logout():
    log_event(
        config.SESSION_LOG_FILE,
        [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "LOGOUT"]
    )
    mark_user_offline()
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def api_forgot_password():
    data = request.get_json()
    email = data.get("email")
    user = User.find_by_email(email)

    if not user:
        return jsonify({"error": "Email not found"}), 404

    s = URLSafeTimedSerializer(config.TOKEN_SECRET_KEY)
    token = s.dumps(email, salt='password-reset-salt')
    send_password_reset_email(current_app._get_current_object(), email, token)

    return jsonify({"message": "Password reset link sent"}), 200


@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    s = URLSafeTimedSerializer(config.TOKEN_SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiration
    except (SignatureExpired, BadTimeSignature):
        return jsonify({"error": "The password reset link is invalid or has expired."}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    password = data.get("password")
    if not password:
        return jsonify({"error": "Password is required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    users = User.get_all()
    user_found = False
    for user in users:
        if user.email == email:
            user.password = generate_password_hash(password)
            user_found = True
            break
    
    if user_found:
        User.save_all(users)
        return jsonify({"message": "Your password has been updated successfully."}), 200
    else:
        return jsonify({"error": "An error occurred. Please try again."}), 500

