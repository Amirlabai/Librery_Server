"""
Merkaz Server Application - Main entry point.
backend made by Amir Labay
frontend made by Yosef Nago
"""

import os
import logging

from flask import Flask, jsonify, request, send_from_directory, send_file
from werkzeug.exceptions import NotFound
from waitress import serve
from datetime import timedelta

import config.config as config
from utils import create_file_with_header, get_project_root
from utils.logger_config import setup_logging, get_logger
from services.mail_service import mail
from flask_cors import CORS

# Import and register blueprints
from controllers.auth_controller import auth_bp
from controllers.files_controller import files_bp
from controllers.uploads_controller import uploads_bp
from controllers.admin_controller import admin_bp

# Initialize logging
_debug = getattr(config, 'DEBUG', False)
setup_logging(logging.DEBUG if _debug else logging.INFO)
logger = get_logger(__name__)

def create_app():
    """Create and configure the Flask application."""
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

    logger.debug("Configuring CORS")
    # When serving Angular from Flask, CORS is less restrictive (same origin)
    # Still allow ngrok and dev origins for flexibility
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        r"https://.*\.ngrok-free\.dev",
        r"https://.*\.ngrok-free\.app",
        r"https://.*\.ngrok\.dev",
        r"https://.*\.ngrok\.app"
    ]
    CORS(
        app,
        resources={r"/*": {
            "origins": allowed_origins,
            "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }},
        supports_credentials=True
    )
    logger.info("CORS configured")
    
    # Register blueprints (API routes) FIRST - before static file routes
    logger.debug("Registering blueprints")
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(admin_bp)
    logger.info("All blueprints registered successfully")
    
    # Configure static file serving for Angular build (AFTER API routes)
    project_root = get_project_root()
    frontend_dist_path = os.path.join(project_root, "client", "dist")
    
    if os.path.exists(frontend_dist_path):
        logger.info(f"Client build found at: {frontend_dist_path}")
        
        # Serve static files from Angular build directory
        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """Serve Angular assets."""
            return send_from_directory(os.path.join(frontend_dist_path, 'assets'), filename)
        
        # Catch-all for SPA routes / static files. Registered AFTER blueprints so
        # real API handlers win when they match. Do not 404 SPA paths that share
        # prefixes with APIs (e.g. /uploads vs /upload, /login page vs POST /login).
        @app.route('/<path:filename>')
        def serve_static(filename):
            """Serve static files from client build or fallback to index.html for SPA routes."""
            spa_routes = {
                'login', 'register', 'forgot-password', 'reset-password',
                'dashboard', 'metrics', 'users', 'pending', 'denied', 'uploads',
            }
            first_segment = filename.split('/', 1)[0]

            # Prefer static assets when the path looks like a file.
            if '.' in first_segment or '.' in filename.rsplit('/', 1)[-1]:
                try:
                    return send_from_directory(frontend_dist_path, filename)
                except NotFound:
                    if first_segment in spa_routes or filename.startswith('dashboard/'):
                        return send_file(os.path.join(frontend_dist_path, 'index.html'))
                    return jsonify({"error": "Not found"}), 404

            # Client-side routes always get the SPA shell.
            if first_segment in spa_routes or filename.startswith('dashboard/'):
                return send_file(os.path.join(frontend_dist_path, 'index.html'))

            # Browser navigations that miss both API and SPA: still serve SPA.
            if request.accept_mimetypes.accept_html and request.method == 'GET':
                return send_file(os.path.join(frontend_dist_path, 'index.html'))

            return jsonify({"error": "Not found"}), 404
        
        # Root route - serve Angular index.html
        @app.route("/", methods=["GET"])
        def serve_index():
            """Serve Angular application."""
            return send_file(os.path.join(frontend_dist_path, 'index.html'))
    else:
        logger.warning(f"Client build not found at: {frontend_dist_path}")
        logger.warning("Run 'npm run build' in client directory first")
        
        # Fallback root route if build doesn't exist
        @app.route("/", methods=["GET"])
        def root():
            """Root endpoint to verify server is running."""
            return jsonify({
                "message": "Merkaz Server API",
                "status": "running",
                "note": "Client build not found. Run 'npm run build' in client directory first.",
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
    logger.info("Starting Merkaz Server Application")
    logger.info("=" * 60)
    
    #run_ngrok.main()
    # --- Directory and File Initialization ---
    # Get project root (one level up from server directory)
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

    # Create necessary CSV files with headers if they don't exist
    logger.debug("Initializing CSV log files")
    # User databases now include ID column
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
    
    logger.info("Starting server with Waitress on 0.0.0.0:8000")
    serve(app, host="0.0.0.0", port=8000)

