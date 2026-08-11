"""
Download repository - Manage download history.
"""
import os
import config.config as config
from utils.path_utils import get_project_root
from utils.logger_config import get_logger

logger = get_logger(__name__)

class DownloadRepository:
    """Repository for download history operations."""
    
    @staticmethod
    def get_download_log_path():
        """Get the path to the download log file."""
        project_root = get_project_root()
        path = os.path.join(project_root, config.DOWNLOAD_LOG_FILE)
        logger.debug(f"Retrieved download log path: {path}")
        return path

