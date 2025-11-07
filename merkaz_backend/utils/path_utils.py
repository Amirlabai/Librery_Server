import os
import config.config as config

def get_project_root():
    """
    Determines the project root directory.
    If path_utils.py is in merkaz_backend/utils/, go up two levels to get project root.
    """
    # Get the directory where path_utils.py is located (merkaz_backend/utils/)
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to get merkaz_backend/
    backend_dir = os.path.dirname(utils_dir)
    # Go up one more level to get project root
    project_root = os.path.dirname(backend_dir)
    return project_root

def _get_project_root():
    """
    Private alias for backward compatibility.
    """
    return get_project_root()

