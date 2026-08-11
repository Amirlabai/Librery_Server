import os
import config.config as config

def get_project_root():
    """
    Determines the project root directory.
    If path_utils.py is in merkaz_backend/utils/, go up two levels to get project root.
    """
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(utils_dir)
    project_root = os.path.dirname(backend_dir)
    return project_root

def _get_project_root():
    """Private alias for backward compatibility."""
    return get_project_root()

def is_path_under(child: str, parent: str) -> bool:
    """Return True if child is inside parent after path normalization."""
    child_abs = os.path.abspath(child)
    parent_abs = os.path.abspath(parent)
    return child_abs.startswith(parent_abs + os.sep) or child_abs == parent_abs

def resolve_config_path(config_path: str) -> str:
    """Resolve a config path relative to project root when not absolute."""
    if not config_path:
        return config_path
    if os.path.isabs(config_path):
        return config_path
    return os.path.join(get_project_root(), config_path)

def get_root_search_cache_dir() -> str:
    """Search cache directory (letter CSV shards)."""
    cache_dir = getattr(config, 'ROOT_SEARCH_CACHE_DIR', None) or getattr(
        config, 'ROOT_SEARCH_CACHE_FILE', None
    )
    return resolve_config_path(cache_dir) if cache_dir else ''
