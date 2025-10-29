import sys, os

from flask import Flask
from waitress import serve
from datetime import datetime, timedelta

import config
from utils import create_file_with_header
from mailer import mail
from flask_cors import CORS

# Import and register blueprints
from routes.auth import auth_bp
from routes.files import files_bp
from routes.uploads import uploads_bp
from routes.admin import admin_bp
import run_ngrok

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = config.SUPER_SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

    # --- Mail Configuration ---
    app.config['MAIL_SERVER'] = config.MAIL_SERVER
    app.config['MAIL_PORT'] = config.MAIL_PORT
    app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
    app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
    mail.init_app(app)

    CORS(
        app,
        resources={r"/*": {
            "origins": ["http://localhost:4200"],
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        }},
        supports_credentials=True
    )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == "__main__":
    #run_ngrok.main()
    # --- Directory and File Initialization ---
    # Get project root (one level up from merkaz_backend directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    share_dir = os.path.join(project_root, config.SHARE_FOLDER)
    trash_dir = os.path.join(project_root, config.TRASH_FOLDER)
    upload_dir = os.path.join(project_root, config.UPLOAD_FOLDER)

    if not os.path.exists(share_dir): os.makedirs(share_dir)
    if not os.path.exists(trash_dir): os.makedirs(trash_dir)
    if not os.path.exists(upload_dir): os.makedirs(upload_dir)

    # Create necessary CSV files with headers if they don't exist
    # User databases now include ID column
    create_file_with_header(config.AUTH_USER_DATABASE, ["id", "email", "password", "role", "status"])
    create_file_with_header(config.NEW_USER_DATABASE, ["id", "email", "password", "role", "status"])
    create_file_with_header(config.DENIED_USER_DATABASE, ["id", "email", "password", "role", "status"])
    create_file_with_header(config.PASSWORD_RESET_DATABASE, ["email", "token", "timestamp"])
    create_file_with_header(config.SESSION_LOG_FILE, ["timestamp", "email", "event"])
    create_file_with_header(config.DOWNLOAD_LOG_FILE, ["timestamp", "email", "type", "path"])
    create_file_with_header(config.SUGGESTION_LOG_FILE, ["timestamp", "email", "suggestion"])
    create_file_with_header(config.UPLOAD_LOG_FILE, ["timestamp", "email", "filename", "path"])
    create_file_with_header(config.DECLINED_UPLOAD_LOG_FILE, ["timestamp", "email", "filename"])

    app = create_app()
    


    print("Starting server with Waitress...")
    serve(app, host="0.0.0.0", port=8000)
