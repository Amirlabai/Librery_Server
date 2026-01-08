"""
Merkaz Server Application - Main entry point.
backend made by Amir Labay
frontend made by Yosef Nago
"""

import sys, os
import logging

from flask import Flask, jsonify, send_from_directory, send_file
from waitress import serve
from datetime import datetime, timedelta

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
from controllers.ee_controller import easter_egg_bp
import dev_toolkit.run_ngrok as run_ngrok

# Initialize logging
setup_logging(logging.DEBUG)
#setup_logging(logging.INFO)
logger = get_logger(__name__)

#lessgoo

def create_app():
    """Create and configure the Flask application."""
    logger.info("Creating Flask application")
    app = Flask(__name__)
    app.secret_key = config.SUPER_SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)
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
        "http://localhost:4200",
        "http://localhost:8000",  # Same port when serving Angular from Flask
        "http://127.0.0.1:4200",
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
    app.register_blueprint(easter_egg_bp, url_prefix="/api")
    logger.info("All blueprints registered successfully")
    
    # Configure static file serving for Angular build (AFTER API routes)
    project_root = get_project_root()
    frontend_dist_path = os.path.join(project_root, "merkaz-frontend", "dist", "angular", "browser")
    
    if os.path.exists(frontend_dist_path):
        logger.info(f"Angular build found at: {frontend_dist_path}")
        
        # Serve static files from Angular build directory
        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """Serve Angular assets."""
            return send_from_directory(os.path.join(frontend_dist_path, 'assets'), filename)
        
        # Serve other static files (JS, CSS, etc.) - catch-all for Angular SPA routes
        # This route is registered AFTER blueprints, so API routes take precedence
        @app.route('/<path:filename>')
        def serve_static(filename):
            """Serve static files from Angular build or fallback to index.html for SPA routes."""
            # List of API route prefixes to avoid serving as static files
            api_prefixes = ['login', 'register', 'browse', 'upload', 'admin', 'download', 
                           'delete', 'create_folder', 'suggest', 'my_uploads', 
                           'forgot-password', 'reset-password', 'logout', 'refresh-session']
            
            # If it matches an API route prefix, it should have been handled by blueprints
            # If we reach here, it's likely an Angular route or static file
            if any(filename.startswith(prefix) for prefix in api_prefixes):
                # This shouldn't happen if API routes are working, but serve index.html as fallback
                return send_file(os.path.join(frontend_dist_path, 'index.html'))
            
            # Check if it's a static file (has extension)
            if '.' in filename:
                try:
                    return send_from_directory(frontend_dist_path, filename)
                except:
                    # File not found, serve index.html for Angular routes
                    pass
            
            # For Angular routes (SPA), serve index.html
            return send_file(os.path.join(frontend_dist_path, 'index.html'))
        
        # Root route - serve Angular index.html
        @app.route("/", methods=["GET"])
        def serve_index():
            """Serve Angular application."""
            return send_file(os.path.join(frontend_dist_path, 'index.html'))
    else:
        logger.warning(f"Angular build not found at: {frontend_dist_path}")
        logger.warning("Run 'ng build' in merkaz-frontend directory first")
        
        # Fallback root route if build doesn't exist
        @app.route("/", methods=["GET"])
        def root():
            """Root endpoint to verify server is running."""
            return jsonify({
                "message": "Merkaz Server API",
                "status": "running",
                "note": "Angular build not found. Run 'ng build' in merkaz-frontend directory.",
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
    # Get project root (one level up from merkaz_backend directory)
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

    # Save the return json from FileService.browse_directory("") into the cache file
    try:
        from services.file_service import FileService
        import json

        root_browse_json, _ = FileService.browse_directory("")
        with open(config.ROOT_SEARCH_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(root_browse_json, f, ensure_ascii=False, indent=2)
        logger.info(f"Root search cache file created at {config.ROOT_SEARCH_CACHE_FILE}")
    except Exception as e:
        logger.error(f"Error initializing root search cache: {e}")

    app = create_app()

    app.config.update(
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True
    )
    
    logger.info("Starting server with Waitress on 0.0.0.0:8000")
    serve(app, host="0.0.0.0", port=8000)

