"""
Suggestion repository - Manage user suggestions.
"""
import os
import config.config as config
from utils.path_utils import get_project_root
from utils.logger_config import get_logger

logger = get_logger(__name__)

class SuggestionRepository:
    """Repository for suggestion log operations."""
    
    @staticmethod
    def get_suggestion_log_path():
        """Get the path to the suggestion log file."""
        project_root = get_project_root()
        path = os.path.join(project_root, config.SUGGESTION_LOG_FILE)
        logger.debug(f"Retrieved suggestion log path: {path}")
        return path

