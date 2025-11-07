import os
import csv
from io import BytesIO
import config.config as config
from .path_utils import get_project_root, _get_project_root

try:
    from openpyxl.workbook import Workbook
except ImportError:
    print("Warning: openpyxl not found. Excel export will not work. Run 'pip install openpyxl'.")
    class Workbook: pass

def create_file_with_header(filename, header):
    """Creates a file with a header if it doesn't exist."""
    project_root = get_project_root()
    filename = os.path.join(project_root, filename)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(header)
        print(f"Created file: {filename}")

def csv_to_xlsx_in_memory(csv_filepath):
    """Converts a CSV file to an XLSX file in memory (BytesIO)."""
    if 'Workbook' not in globals():
        raise RuntimeError("openpyxl library is missing.")
    wb = Workbook()
    ws = wb.active
    ws.title = os.path.basename(csv_filepath).replace('.csv', '').title()
    try:
        with open(csv_filepath, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                ws.append(row)
    except FileNotFoundError:
        ws.append(["Error", "File Not Found"])
    memory_file = BytesIO()
    wb.save(memory_file)
    memory_file.seek(0)
    return memory_file

def _get_id_sequence_file_path():
    """
    Returns the absolute path to the user_id_sequence.txt file.
    """
    project_root = _get_project_root()
    return os.path.join(project_root, config.ID_SEQUENCE_FILE)

def get_next_user_id():
    """
    Generates and returns the next unique user ID.
    Tracks the sequence in a persistent file to ensure uniqueness across restarts.
    
    Logic:
    1. First, scan all user CSV files to find the maximum existing ID
    2. If user_id_sequence.txt exists, compare with stored value and use the higher one
    3. If user_id_sequence.txt doesn't exist but users exist, use max_id + 1 from users
    4. Update the sequence file with the next ID to assign
    """
    project_root = _get_project_root()
    sequence_file_path = _get_id_sequence_file_path()
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(sequence_file_path), exist_ok=True)
    
    # STEP 1: Check all user databases to find the maximum existing ID
    # This ensures we always retrieve the last ID from existing users
    max_id = 0
    user_files = [
        os.path.join(project_root, config.AUTH_USER_DATABASE),
        os.path.join(project_root, config.NEW_USER_DATABASE),
        os.path.join(project_root, config.DENIED_USER_DATABASE)
    ]
    
    for filepath in user_files:
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                # Check if ID column exists (first column should be 'id')
                if header and len(header) > 0 and header[0].lower() == 'id':
                    for row in reader:
                        if row and len(row) > 0:
                            try:
                                user_id = int(row[0])
                                max_id = max(max_id, user_id)
                            except (ValueError, IndexError):
                                continue
        except FileNotFoundError:
            continue
    
    # STEP 2: Determine the next ID to assign
    # Start with max_id + 1 from existing users (ensures no conflicts)
    next_id = max_id + 1
    
    # STEP 3: Check if sequence file exists and compare with stored value
    # If sequence file has a higher value, use that instead
    try:
        if os.path.exists(sequence_file_path):
            with open(sequence_file_path, mode='r', encoding='utf-8') as f:
                stored_id = int(f.read().strip())
                # Use the maximum of stored_id or max_id + 1 to ensure consistency
                next_id = max(stored_id, max_id + 1)
    except (FileNotFoundError, ValueError, IOError):
        # If file doesn't exist or is invalid, next_id is already set to max_id + 1
        pass
    
    # STEP 4: Update sequence file with the next ID to assign
    next_id_to_store = next_id + 1
    try:
        with open(sequence_file_path, mode='w', encoding='utf-8') as f:
            f.write(str(next_id_to_store))
    except IOError as e:
        # Log warning but don't fail - we can still return the ID
        print(f"Warning: Could not update sequence file: {e}")
    
    return next_id

def get_max_user_id_from_files():
    """
    Scans all user CSV files and returns the maximum ID found.
    Useful for migration and validation.
    Uses absolute paths based on project root.
    """
    project_root = _get_project_root()
    max_id = 0
    user_files = [
        os.path.join(project_root, config.AUTH_USER_DATABASE),
        os.path.join(project_root, config.NEW_USER_DATABASE),
        os.path.join(project_root, config.DENIED_USER_DATABASE)
    ]
    
    for filepath in user_files:
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header and len(header) > 0 and header[0].lower() == 'id':
                    for row in reader:
                        if row and len(row) > 0:
                            try:
                                user_id = int(row[0])
                                max_id = max(max_id, user_id)
                            except (ValueError, IndexError):
                                continue
        except FileNotFoundError:
            continue
    
    return max_id

def _get_upload_id_sequence_file_path():
    """
    Returns the absolute path to the upload_id_sequence.txt file.
    """
    project_root = _get_project_root()
    return os.path.join(project_root, config.UPLOAD_ID_SEQUENCE_FILE)

def get_next_upload_id():
    """
    Generates and returns the next unique upload ID.
    Uses a sequence file to ensure uniqueness across restarts.
    """
    project_root = _get_project_root()
    sequence_file_path = _get_upload_id_sequence_file_path()
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(sequence_file_path), exist_ok=True)
    
    # Read current sequence or start at 1
    next_id = 1
    try:
        if os.path.exists(sequence_file_path):
            with open(sequence_file_path, mode='r', encoding='utf-8') as f:
                stored_id = int(f.read().strip())
                next_id = stored_id
    except (FileNotFoundError, ValueError, IOError):
        # If file doesn't exist or is invalid, start at 1
        pass
    
    # Update sequence file with the next ID to assign
    next_id_to_store = next_id + 1
    try:
        with open(sequence_file_path, mode='w', encoding='utf-8') as f:
            f.write(str(next_id_to_store))
    except IOError as e:
        # Log warning but don't fail - we can still return the ID
        print(f"Warning: Could not update upload sequence file: {e}")
    
    return next_id

