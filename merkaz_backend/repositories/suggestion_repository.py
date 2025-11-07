"""
Suggestion repository - Manage user suggestions.
"""
import os
import config.config as config
from utils.path_utils import get_project_root

class SuggestionRepository:
    """Repository for suggestion log operations."""
    
    @staticmethod
    def get_suggestion_log_path():
        """Get the path to the suggestion log file."""
        project_root = get_project_root()
        return os.path.join(project_root, config.SUGGESTION_LOG_FILE)

