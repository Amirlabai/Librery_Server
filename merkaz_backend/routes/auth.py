import re
import csv
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash, jsonify
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash
import config
from user import User
from utils import log_event
from mailer import send_new_user_notification, send_password_reset_email
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
    session["is_admin"] = user.is_admin
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
    with open(config.NEW_USER_DATABASE, mode='a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([email, hashed_password, 'user'])

    send_new_user_notification(current_app._get_current_object(), email)
    return jsonify({"message": "Registration successful. Pending admin approval."}), 201

@auth_bp.route("/logout")
def logout():
    log_event(config.SESSION_LOG_FILE, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), session.get("email", "unknown"), "LOGOUT"])
    session.clear()
    return redirect(url_for("auth.login"))

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


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    s = URLSafeTimedSerializer(config.TOKEN_SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiration
    except (SignatureExpired, BadTimeSignature):
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form["password"]
        # Add password validation logic here (same as registration)
        users = User.get_all()
        user_found = False
        for user in users:
            if user.email == email:
                user.password = generate_password_hash(password)
                user_found = True
                break
        
        if user_found:
            User.save_all(users)
            flash("Your password has been updated successfully.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("An error occurred. Please try again.", "error")

    return render_template("reset_password.html", token=token)

