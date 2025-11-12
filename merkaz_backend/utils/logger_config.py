"""
Logging configuration module.
Sets up Python logging with timestamp, file, line number, and message format.
"""
import logging
import os
from datetime import datetime
import config.config as config
from utils.path_utils import get_project_root

def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the entire application.
    
    Args:
        log_level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    # Ensure logs directory exists
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, config.SERVER_LOGS_DIR)
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log file path with date
    log_filename = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create custom formatter with timestamp, file, line number, level, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # File handler - logs to file
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler - logs to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name (typically __name__)
    
    Returns:
        Logger instance configured with the module name
    """
    return logging.getLogger(name)

