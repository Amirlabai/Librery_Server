import sys, os
import logging

from flask import Flask
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
import run_ngrok

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
    CORS(
        app,
        resources={r"/*": {
            "origins": ["http://localhost:4200"],
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }},
        supports_credentials=True
    )
    logger.info("CORS configured")

    # Register blueprints
    logger.debug("Registering blueprints")
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(admin_bp)
    logger.info("All blueprints registered successfully")

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
    create_file_with_header(config.AUTH_USER_DATABASE, ["id", "email", "password", "role", "status"])
    create_file_with_header(config.NEW_USER_DATABASE, ["id", "email", "password", "role", "status"])
    create_file_with_header(config.DENIED_USER_DATABASE, ["id", "email", "password", "role", "status"])
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
    
    logger.info("Starting server with Waitress on 0.0.0.0:8000")
    serve(app, host="0.0.0.0", port=8000)

