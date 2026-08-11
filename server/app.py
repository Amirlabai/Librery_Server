"""
Merkaz Server Application - Main entry point.
backend made by Amir Labay
frontend made by Yosef Nago
"""

import os
import logging
from urllib.parse import urlparse

from flask import Flask, jsonify, request, make_response, send_from_directory, send_file
from waitress import serve
from datetime import timedelta
from werkzeug.exceptions import NotFound

import config.config as config
from utils import create_file_with_header, get_project_root
from utils.logger_config import setup_logging, get_logger
from services.mail_service import mail

# Import and register blueprints
from controllers.auth_controller import auth_bp
from controllers.files_controller import files_bp
from controllers.uploads_controller import uploads_bp
from controllers.admin_controller import admin_bp
from dev_toolkit import run_ngrok

# Initialize logging
_debug = getattr(config, 'DEBUG', False)
setup_logging(logging.DEBUG if _debug else logging.INFO)
logger = get_logger(__name__)

_LOCAL_ORIGINS = frozenset({
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
})
_CORS_HOST_SUFFIXES = (
    ".vercel.app",
    ".ngrok-free.dev",
    ".ngrok-free.app",
    ".ngrok.dev",
    ".ngrok.app",
)


def _cors_origin_allowed(origin: str) -> bool:
    if not origin:
        return False
    origin = origin.rstrip("/")
    if origin in _LOCAL_ORIGINS:
        return True
    for extra in getattr(config, "CORS_EXTRA_ORIGINS", None) or []:
        if extra and origin == extra.rstrip("/"):
            return True
    host = (urlparse(origin).hostname or "").lower()
    if not host:
        return False
    return any(host == suf.lstrip(".") or host.endswith(suf) for suf in _CORS_HOST_SUFFIXES)


def _apply_cors_headers(response):
    origin = request.headers.get("Origin")
    if not origin or not _cors_origin_allowed(origin):
        return response
    response.headers["Access-Control-Allow-Origin"] = origin.rstrip("/")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    response.headers["Vary"] = "Origin"
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, ngrok-skip-browser-warning"
        )
        response.headers["Access-Control-Max-Age"] = "86400"
    return response


def create_app():
    """Create Flask app: API blueprints + optional client/dist SPA."""
    logger.info("Creating Flask application")
    app = Flask(__name__)
    app.secret_key = config.SUPER_SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=config.SESSION_TIMEOUT_MINUTES)
    logger.debug(f"Session lifetime set to {app.config['PERMANENT_SESSION_LIFETIME']}")

    # --- Mail Configuration ---
    logger.debug("Configuring mail settings")
    app.config['MAIL_SERVER'] = config.MAIL_SERVER
    app.config['MAIL_PORT'] = config.MAIL_PORT
    app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
    app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
    mail.init_app(app)
    logger.info("Mail service initialized")

    @app.before_request
    def _cors_preflight():
        origin = request.headers.get("Origin")
        if origin:
            logger.debug(f"CORS Origin: {origin} {request.method} {request.path}")
        if request.method == "OPTIONS":
            return _apply_cors_headers(make_response(("", 204)))

    @app.after_request
    def _cors_after(response):
        return _apply_cors_headers(response)

    logger.info("CORS configured (localhost / ngrok / optional Vercel)")

    logger.debug("Registering blueprints")
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(admin_bp)
    logger.info("All blueprints registered successfully")

    project_root = get_project_root()
    frontend_dist_path = os.path.join(project_root, "client", "dist")

    if os.path.exists(frontend_dist_path):
        logger.info(f"Client build found at: {frontend_dist_path}")

        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            return send_from_directory(os.path.join(frontend_dist_path, 'assets'), filename)

        @app.route('/<path:filename>')
        def serve_static(filename):
            spa_routes = {
                'login', 'register', 'forgot-password', 'reset-password',
                'dashboard', 'metrics', 'users', 'pending', 'denied', 'uploads',
            }
            first_segment = filename.split('/', 1)[0]

            if '.' in first_segment or '.' in filename.rsplit('/', 1)[-1]:
                try:
                    return send_from_directory(frontend_dist_path, filename)
                except NotFound:
                    if first_segment in spa_routes or filename.startswith('dashboard/'):
                        return send_file(os.path.join(frontend_dist_path, 'index.html'))
                    return jsonify({"error": "Not found"}), 404

            if first_segment in spa_routes or filename.startswith('dashboard/'):
                return send_file(os.path.join(frontend_dist_path, 'index.html'))

            if request.accept_mimetypes.accept_html and request.method == 'GET':
                return send_file(os.path.join(frontend_dist_path, 'index.html'))

            return jsonify({"error": "Not found"}), 404

        @app.route("/", methods=["GET"])
        def serve_index():
            return send_file(os.path.join(frontend_dist_path, 'index.html'))
    else:
        logger.warning(f"Client build not found at: {frontend_dist_path}")
        logger.warning("Run 'npm run build' in client/ (no VITE_API_BASE_URL) then restart")

        @app.route("/", methods=["GET"])
        def root():
            return jsonify({
                "message": "Merkaz Server API",
                "status": "running",
                "note": "Client build not found. Run npm run build in client/ first.",
                "endpoints": {
                    "auth": "/login, /register, /logout, /forgot-password, /reset-password",
                    "files": "/browse, /download/file, /download/folder, /delete, /create_folder",
                    "uploads": "/upload, /my_uploads",
                    "admin": "/admin/metrics, /admin/users, /admin/pending"
                }
            }), 200

    return app

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting Merkaz Server (API + UI)")
    logger.info("=" * 60)

    run_ngrok.main()
    project_root = get_project_root()
    logger.debug(f"Project root: {project_root}")

    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    trash_dir = os.path.join(project_root, config.TRASH_FOLDER)
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)

    logger.debug("Creating required directories")
    if not os.path.exists(share_dir):
        os.makedirs(share_dir)
        logger.info(f"Created directory: {share_dir}")
    if not os.path.exists(trash_dir):
        os.makedirs(trash_dir)
        logger.info(f"Created directory: {trash_dir}")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        logger.info(f"Created directory: {upload_dir}")

    logger.debug("Initializing CSV log files")
    create_file_with_header(config.AUTH_USER_DATABASE, ["id", "email", "password", "role", "status", "is_boss_admin", "first_name", "last_name", "challenge"])
    create_file_with_header(config.NEW_USER_DATABASE, ["id", "email", "password", "role", "status", "is_boss_admin", "first_name", "last_name"])
    create_file_with_header(config.DENIED_USER_DATABASE, ["id", "email", "password", "role", "status", "is_boss_admin", "first_name", "last_name"])
    create_file_with_header(config.PASSWORD_RESET_DATABASE, ["email", "token", "timestamp"])
    create_file_with_header(config.SESSION_LOG_FILE, ["timestamp", "email", "event"])
    create_file_with_header(config.DOWNLOAD_LOG_FILE, ["timestamp", "email", "type", "path"])
    create_file_with_header(config.SUGGESTION_LOG_FILE, ["timestamp", "email", "suggestion"])
    create_file_with_header(config.UPLOAD_LOG_FILE, ["timestamp", "email", "user_id", "filename", "path"])  # Deprecated - kept for backward compatibility
    create_file_with_header(config.UPLOAD_PENDING_LOG_FILE, ["upload_id", "timestamp", "email", "user_id", "filename", "path"])
    create_file_with_header(config.UPLOAD_COMPLETED_LOG_FILE, ["upload_id", "original_timestamp", "approval_timestamp", "email", "user_id", "filename", "final_path"])
    create_file_with_header(config.DECLINED_UPLOAD_LOG_FILE, ["timestamp", "email", "user_id", "filename"])
    logger.info("All CSV log files initialized")

    app = create_app()

    _secure = getattr(config, 'SESSION_COOKIE_SECURE', False)
    app.config.update(
        SESSION_COOKIE_SAMESITE='None' if _secure else 'Lax',
        SESSION_COOKIE_SECURE=_secure
    )

    logger.info("Starting Waitress on 0.0.0.0:8000 (API + client/dist)")
    serve(app, host="0.0.0.0", port=8000)
