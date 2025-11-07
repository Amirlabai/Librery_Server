"""
Session repository - Handle session logs.
"""
import os
import config.config as config
from utils.path_utils import get_project_root

class SessionRepository:
    """Repository for session log operations."""
    
    @staticmethod
    def get_session_log_path():
        """Get the path to the session log file."""
        project_root = get_project_root()
        return os.path.join(project_root, config.SESSION_LOG_FILE)

