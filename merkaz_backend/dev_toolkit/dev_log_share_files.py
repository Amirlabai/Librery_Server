#!/usr/bin/env python3
"""
Development script to log all server share files that are not already logged.
Assigns upload IDs to files that don't have them yet.

This script should be run from the project root directory.
"""

import os
import csv
import sys
from datetime import datetime

# Import get_project_root and config from repository
# Import directly from file to avoid utils/__init__.py dependencies
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)

# First, load path_utils with mocked config to avoid circular import
import types
import importlib.util

_mock_config = types.ModuleType('config')
_mock_config.config = types.ModuleType('config.config')
sys.modules['config'] = _mock_config
sys.modules['config.config'] = _mock_config.config

# Import path_utils directly
_path_utils_file = os.path.join(_backend_dir, 'utils', 'path_utils.py')
_path_utils_spec = importlib.util.spec_from_file_location("path_utils", _path_utils_file)
_path_utils = importlib.util.module_from_spec(_path_utils_spec)
_path_utils_spec.loader.exec_module(_path_utils)

get_project_root = _path_utils.get_project_root

# Create a mock utils module with path_utils to avoid utils/__init__.py imports
_utils_module = types.ModuleType('utils')
_utils_module.path_utils = _path_utils
sys.modules['utils'] = _utils_module
sys.modules['utils.path_utils'] = _path_utils

# Now import config - it will use the already-loaded path_utils via utils.path_utils
_config_file = os.path.join(_backend_dir, 'config', 'config.py')
_config_spec = importlib.util.spec_from_file_location("config.config", _config_file)
_config_module = importlib.util.module_from_spec(_config_spec)
_config_spec.loader.exec_module(_config_module)
sys.modules['config.config'] = _config_module

# Use config constants instead of manually constructing paths
def get_share_folder():
    """Get the share folder path."""
    project_root = get_project_root()
    return os.path.join(project_root, _config_module.SHARE_FOLDER)


def get_upload_completed_log_file():
    """Get the upload completed log file path."""
    project_root = get_project_root()
    return os.path.join(project_root, _config_module.UPLOAD_COMPLETED_LOG_FILE)


def get_upload_id_sequence_file():
    """Get the upload ID sequence file path."""
    project_root = get_project_root()
    return os.path.join(project_root, _config_module.UPLOAD_ID_SEQUENCE_FILE)


def get_max_upload_id_from_logs():
    """Get the maximum upload ID from completed log and sequence file."""
    max_id = 0
    
    # Check completed log for max ID
    completed_log_path = get_upload_completed_log_file()
    try:
        with open(completed_log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header
            for row in reader:
                if row and len(row) > 0:
                    try:
                        upload_id = int(row[0])
                        max_id = max(max_id, upload_id)
                    except (ValueError, IndexError):
                        continue
    except FileNotFoundError:
        pass
    
    # Check sequence file
    sequence_file_path = get_upload_id_sequence_file()
    try:
        if os.path.exists(sequence_file_path):
            with open(sequence_file_path, 'r', encoding='utf-8') as f:
                stored_id = int(f.read().strip())
                max_id = max(max_id, stored_id - 1)  # stored_id is next to assign, so subtract 1
    except (FileNotFoundError, ValueError, IOError):
        pass
    
    return max_id


def get_next_upload_id():
    """Get the next upload ID, ensuring it's higher than any existing ID."""
    sequence_file_path = get_upload_id_sequence_file()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(sequence_file_path), exist_ok=True)
    
    # Get max ID from logs
    max_id = get_max_upload_id_from_logs()
    
    # Next ID is max_id + 1
    next_id = max_id + 1
    
    # Update sequence file
    try:
        with open(sequence_file_path, 'w', encoding='utf-8') as f:
            f.write(str(next_id + 1))  # Store next ID to assign after this one
    except IOError as e:
        print(f"Warning: Could not update upload sequence file: {e}")
    
    return next_id


def get_logged_paths():
    """Get a set of all final_paths that are already logged."""
    completed_log_path = get_upload_completed_log_file()
    logged_paths = set()
    
    try:
        with open(completed_log_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header
            for row in reader:
                if len(row) >= 7:
                    logged_paths.add(row[6])  # final_path is column 6
    except FileNotFoundError:
        pass
    
    return logged_paths


def log_file_to_completed(upload_id, file_path, relative_path, filename):
    """Log a file to the completed upload log."""
    completed_log_path = get_upload_completed_log_file()
    
    # Ensure file exists with header
    if not os.path.exists(completed_log_path):
        os.makedirs(os.path.dirname(completed_log_path), exist_ok=True)
        with open(completed_log_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['upload_id', 'original_timestamp', 'approval_timestamp', 'email', 'user_id', 'filename', 'final_path'])
    
    # Get file modification time as original timestamp
    try:
        mtime = os.path.getmtime(file_path)
        original_timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
    except OSError:
        original_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    approval_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the entry
    with open(completed_log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            upload_id,
            original_timestamp,
            approval_timestamp,
            '',  # email - unknown for existing files
            '',  # user_id - unknown for existing files
            filename,
            relative_path
        ])


def scan_and_log_share_files():
    """Scan all files in the share directory and log them if not already logged."""
    share_dir = get_share_folder()
    
    if not os.path.exists(share_dir):
        print(f"Error: Share directory does not exist: {share_dir}")
        return
    
    print(f"Scanning share directory: {share_dir}")
    print("-" * 60)
    
    # Get already logged paths
    logged_paths = get_logged_paths()
    print(f"Found {len(logged_paths)} files already logged.")
    
    # Scan all files
    files_to_log = []
    for root, dirs, files in os.walk(share_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in files:
            # Skip hidden files
            if filename.startswith('.'):
                continue
            
            file_path = os.path.join(root, filename)
            
            # Get relative path from share_dir
            relative_path = os.path.relpath(file_path, share_dir).replace('\\', '/')
            
            # Check if already logged
            if relative_path not in logged_paths:
                files_to_log.append((file_path, relative_path, filename))
    
    print(f"Found {len(files_to_log)} files that need to be logged.")
    print("-" * 60)
    
    if not files_to_log:
        print("All files are already logged. Nothing to do.")
        return
    
    # Log each file
    logged_count = 0
    for file_path, relative_path, filename in files_to_log:
        try:
            upload_id = get_next_upload_id()
            log_file_to_completed(upload_id, file_path, relative_path, filename)
            print(f"✓ Logged: {relative_path} (ID: {upload_id})")
            logged_count += 1
        except Exception as e:
            print(f"✗ Error logging {relative_path}: {e}")
    
    print("-" * 60)
    print(f"Successfully logged {logged_count} out of {len(files_to_log)} files.")


if __name__ == "__main__":
    print("=" * 60)
    print("Share Files Logging Script")
    print("=" * 60)
    print()
    
    try:
        scan_and_log_share_files()
        print()
        print("Script completed successfully.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

