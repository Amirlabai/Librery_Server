"""
Auth service - Authentication and session handling.
"""
from flask import session, g
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash

from repositories.user_repository import UserRepository
from models.user_entity import User
from utils.logger_config import get_logger
from utils import get_next_user_id
from services import jwt_service, session_state_store
import config.config as config

logger = get_logger(__name__)

session_timeout_minutes = config.SESSION_TIMEOUT_MINUTES


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def login(email, password):
        """Authenticate a user and create session."""
        email = User._normalize_email(email)
        logger.info(f"Login attempt for email: {email}")
        user = UserRepository.find_by_email(email)

        if not user or not user.check_password(password):
            logger.warning(f"Login failed - Invalid credentials for email: {email}")
            return None, "Invalid credentials"

        if not user.is_active:
            logger.warning(f"Login failed - Account inactive for email: {email}")
            return None, "Account inactive"

        session_state_store.clear_invalidation(email)
        AuthService.create_session(user)
        session_state_store.mark_online(email)
        logger.info(f"Login successful - User: {email}, Role: {'admin' if user.is_admin else 'user'}")
        return user, None

    @staticmethod
    def register(email, password, first_name, last_name):
        """Register a new user."""
        email = User._normalize_email(email)
        logger.info(f"Registration attempt for email: {email}")

        if AuthService.email_exists(email):
            logger.warning(f"Registration failed - Email already exists: {email}")
            return None, "Email already registered or pending"

        if len(password) < 8:
            logger.warning(f"Registration failed - Password too short for email: {email}")
            return None, "Password must be at least 8 characters long"

        hashed_password = generate_password_hash(password)
        user_id = get_next_user_id()
        new_user = UserRepository.create_user(
            email=email, password=hashed_password, role='user', status='pending',
            user_id=user_id, first_name=first_name, last_name=last_name
        )

        pending_users = UserRepository.get_pending()
        pending_users.append(new_user)
        UserRepository.save_pending(pending_users)
        logger.info(f"User registered successfully - Email: {email}, user_id: {user_id}")
        return new_user, None

    @staticmethod
    def reset_password(email, new_password):
        """Reset a user's password."""
        email = User._normalize_email(email)
        logger.info(f"Password reset attempt for email: {email}")

        if len(new_password) < 8:
            return False, "Password must be at least 8 characters long"

        users = UserRepository.get_all()
        user_found = False
        for user in users:
            if user.email == email:
                user.password = generate_password_hash(new_password)
                user_found = True
                break

        if not user_found:
            return False, "User not found"

        UserRepository.save_all(users)
        session_state_store.bump_token_version(email)
        logger.info(f"Password reset successful for user: {email}")
        return True, None

    @staticmethod
    def refresh_session():
        """Refresh the current user's session with latest data from database."""
        email = AuthService.get_current_email()
        if not email:
            return None, "Session invalid"

        if not AuthService.is_session_valid():
            AuthService.clear_session()
            return None, "Session has been terminated. Please log in again."

        user = UserRepository.find_by_email(email)
        if not user:
            return None, "User not found"

        AuthService.create_session(user)
        return {
            "email": user.email,
            "role": "admin" if user.is_admin else "user",
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "full_name": user.full_name,
            "username": user.username,
            "is_boss_admin": user.is_boss_admin,
            "challenge": user.challenge,
            "token": jwt_service.issue_token(user),
        }, None

    @staticmethod
    def create_session(user):
        """Create a session for the given user."""
        session["logged_in"] = True
        session["email"] = user.email
        session["user_id"] = user.user_id
        session["is_admin"] = user.is_admin
        session["challenge"] = user.challenge

    @staticmethod
    def clear_session():
        """Clear the current session."""
        email = session.get("email", "unknown")
        session.clear()
        if email and email != "unknown":
            session_state_store.mark_offline(email)

    @staticmethod
    def invalidate_user_session(email):
        """Invalidate all sessions for a specific user by email."""
        logger.info(f"Invalidating sessions for user: {email}")
        session_state_store.bump_token_version(email)
        session_state_store.mark_offline(email)

    @staticmethod
    def is_session_valid():
        """Check if the current session is valid (not invalidated)."""
        email = AuthService.get_current_email()
        if not email:
            return False
        if session_state_store.is_invalidated(email):
            return False
        token = jwt_service.get_bearer_token()
        if token:
            return jwt_service.validate_token(token) is not None
        return bool(session.get("logged_in", False))

    @staticmethod
    def validate_and_clear_if_invalidated():
        """Validate session; clear if invalidated."""
        if not session.get("logged_in") and not jwt_service.get_bearer_token():
            return True, None

        if not AuthService.is_session_valid():
            email = session.get("email", "unknown")
            logger.warning(f"Session terminated for user: {email}")
            AuthService.clear_session()
            return False, "Session has been terminated. Please log in again."

        return True, None

    @staticmethod
    def get_current_email():
        """Resolve current user email from JWT or Flask session."""
        token = jwt_service.get_bearer_token()
        if token:
            claims = jwt_service.validate_token(token)
            if claims:
                return claims.get("sub")
        return session.get("email")

    @staticmethod
    def require_auth():
        """Populate g.current_user_email or return (False, error)."""
        email = AuthService.get_current_email()
        if not email:
            return False, "Not logged in"
        is_valid, err = AuthService.validate_and_clear_if_invalidated()
        if not is_valid:
            return False, err
        g.current_user_email = email
        return True, None

    @staticmethod
    def find_user_by_email(email):
        return UserRepository.find_by_email(email)

    @staticmethod
    def email_exists(email):
        return (
            UserRepository.find_by_email(email)
            or UserRepository.find_pending_by_email(email)
            or UserRepository.find_denied_by_email(email)
        )

    @staticmethod
    def is_user_boss_admin(email):
        return UserRepository.is_user_boss_admin(email)

    @staticmethod
    def is_outside_user(email):
        """Check if a user is an outside user (username part, case-insensitive)."""
        import csv
        import os
        try:
            target_user = email.split('@')[0].lower()
            source = config.OUTSIDE_USERS_DATABASE_SOURCE
            if not source or not os.path.isfile(source):
                return False
            with open(source, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if row:
                        csv_user = row[0].split('@')[0].lower()
                        if csv_user == target_user:
                            return True
            return False
        except FileNotFoundError:
            return False

    @staticmethod
    def build_login_response(user):
        """Build login JSON payload including JWT."""
        token = jwt_service.issue_token(user)
        return {
            "message": "Login successful",
            "email": user.email,
            "role": "admin" if user.is_admin else "user",
            "full_name": user.full_name,
            "challenge": user.challenge,
            "username": user.username,
            "token": token,
        }


def mark_user_online():
    email = AuthService.get_current_email()
    if email:
        session_state_store.mark_online(email)


def mark_user_offline():
    email = session.get("email")
    if email:
        session_state_store.mark_offline(email)


def cleanup_expired_sessions():
    session_state_store.cleanup_expired(session_timeout_minutes)


def get_active_users():
    cleanup_expired_sessions()
    return session_state_store.list_active()


def is_user_authenticated():
    return AuthService.get_current_email() is not None


def is_user_admin():
    if session.get("is_admin"):
        return True
    token = jwt_service.get_bearer_token()
    if token:
        claims = jwt_service.validate_token(token)
        return claims and claims.get("role") == "admin"
    return False


def get_current_user_email():
    return AuthService.get_current_email()


def get_current_user_id():
    return session.get("user_id")
