"""
Download repository - Manage download history.
"""
import os
import config.config as config
from utils.path_utils import get_project_root

class DownloadRepository:
    """Repository for download history operations."""
    
    @staticmethod
    def get_download_log_path():
        """Get the path to the download log file."""
        project_root = get_project_root()
        return os.path.join(project_root, config.DOWNLOAD_LOG_FILE)

