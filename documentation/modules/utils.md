# Utils Module Documentation

Utility functions and helpers used throughout the application.

## Overview

The utils module provides reusable utility functions organized by category. Each utility file handles a specific domain of operations.

## Files

### `path_utils.py`

Path and directory management utilities.

**Functions**:

#### `get_project_root()`
- **Purpose**: Get the project root directory
- **Logic**: Goes up two levels from `merkaz_backend/utils/` to project root
- **Returns**: Absolute path string
- **Usage**: Base path for all file operations

#### `_get_project_root()`
- **Purpose**: Private alias for backward compatibility
- **Returns**: Same as `get_project_root()`

**Example**:
```python
from utils.path_utils import get_project_root

root = get_project_root()
# Returns: /path/to/NagoAmir_Server
```

---

### `csv_utils.py`

CSV file operations and ID generation utilities.

**Functions**:

#### `create_file_with_header(filename, header)`
- **Purpose**: Create CSV file with header if it doesn't exist
- **Parameters**: 
  - `filename`: Relative path from project root
  - `header`: List of column names
- **Action**: Creates file with header row if missing
- **Uses**: `get_project_root()` for path resolution

#### `csv_to_xlsx_in_memory(csv_filepath)`
- **Purpose**: Convert CSV file to XLSX in memory
- **Parameters**: Absolute path to CSV file
- **Returns**: BytesIO object with XLSX data
- **Uses**: openpyxl library
- **Error Handling**: Returns error row if file not found

#### `get_next_user_id()`
- **Purpose**: Generate next unique user ID
- **Logic**:
  1. Scans all user CSV files for max ID
  2. Checks sequence file
  3. Uses maximum value
  4. Updates sequence file
- **Returns**: Integer user ID
- **Thread Safe**: Yes (file-based locking)

#### `get_max_user_id_from_files()`
- **Purpose**: Get maximum user ID from all user files
- **Returns**: Integer (0 if no users)
- **Usage**: Migration and validation

#### `get_next_upload_id()`
- **Purpose**: Generate next unique upload ID
- **Logic**:
  1. Reads sequence file
  2. Increments and updates
- **Returns**: Integer upload ID
- **Thread Safe**: Yes (file-based)

**Helper Functions** (private):
- `_get_id_sequence_file_path()`: Get user ID sequence file path
- `_get_upload_id_sequence_file_path()`: Get upload ID sequence file path

**Dependencies**: openpyxl (optional, for XLSX conversion)

---

### `log_utils.py`

Logging helper functions.

**Functions**:

#### `log_event(filename, data)`
- **Purpose**: Append row to CSV log file
- **Parameters**:
  - `filename`: Absolute path to log file
  - `data`: List of values for the row
- **Action**: Appends row to CSV file
- **Encoding**: UTF-8
- **Thread Safety**: Not thread-safe (caller must handle locking)

**Example**:
```python
from utils.log_utils import log_event
from datetime import datetime

log_event(
    config.SESSION_LOG_FILE,
    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user@example.com", "LOGIN_SUCCESS"]
)
```

**Note**: For thread-safe logging, use locks in calling code.

---

### `file_utils.py`

File operations and MIME validation utilities.

**Functions**:

#### `allowed_file(filename)`
- **Purpose**: Check if file extension is in allowed list
- **Parameters**: Filename string
- **Returns**: Boolean
- **Uses**: `config.ALLOWED_EXTENSIONS`
- **Logic**: Extracts extension and checks against whitelist

#### `is_file_malicious(file_stream)`
- **Purpose**: Check if file is potentially malicious
- **Parameters**: File stream (file-like object)
- **Returns**: Boolean (True if malicious)
- **Uses**: python-magic library
- **Logic**:
  1. Reads first 2048 bytes
  2. Checks MIME type
  3. Flags executables
- **Security**: Basic check, can be enhanced

**Example**:
```python
from utils.file_utils import allowed_file, is_file_malicious

if allowed_file("document.pdf"):
    if not is_file_malicious(file_stream):
        # Safe to process
        pass
```

**Dependencies**: python-magic (or python-magic-bin on Windows)

---

## Module Exports

The `utils/__init__.py` exports commonly used functions:

```python
from utils import (
    get_project_root,
    create_file_with_header,
    csv_to_xlsx_in_memory,
    get_next_user_id,
    get_next_upload_id,
    log_event,
    allowed_file,
    is_file_malicious
)
```

## Usage Patterns

### Path Resolution
```python
from utils.path_utils import get_project_root
import os

root = get_project_root()
file_path = os.path.join(root, "data", "users.csv")
```

### ID Generation
```python
from utils.csv_utils import get_next_user_id, get_next_upload_id

user_id = get_next_user_id()
upload_id = get_next_upload_id()
```

### File Validation
```python
from utils.file_utils import allowed_file, is_file_malicious

if allowed_file(filename):
    file.stream.seek(0)  # Reset stream
    if not is_file_malicious(file.stream):
        # Process file
        pass
```

### Logging
```python
from utils.log_utils import log_event
from datetime import datetime

log_event(
    config.SESSION_LOG_FILE,
    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "EVENT"]
)
```

### CSV Operations
```python
from utils.csv_utils import create_file_with_header, csv_to_xlsx_in_memory

# Create file
create_file_with_header(
    config.NEW_USER_DATABASE,
    ["id", "email", "password", "role", "status"]
)

# Convert to XLSX
xlsx_data = csv_to_xlsx_in_memory("/path/to/file.csv")
```

## Thread Safety

### Thread-Safe Functions
- `get_next_user_id()`: Uses file-based sequence
- `get_next_upload_id()`: Uses file-based sequence

### Not Thread-Safe
- `log_event()`: Caller must use locks
- `create_file_with_header()`: Should be called during initialization

## Error Handling

### File Not Found
- `csv_to_xlsx_in_memory()`: Returns XLSX with error row
- `get_next_user_id()`: Starts from 1 if no files exist
- `log_event()`: Creates file if doesn't exist (via append mode)

### Invalid Data
- ID generation functions handle invalid sequence files gracefully
- File validation returns False for invalid files

## Best Practices

1. **Use absolute paths** for file operations
2. **Reset file streams** after reading (for MIME checks)
3. **Use locks** for thread-safe logging
4. **Handle file not found** gracefully
5. **Validate inputs** before processing
6. **Use UTF-8 encoding** for CSV files
7. **Check return values** from utility functions

## Dependencies

### Required
- `os`: Path operations
- `csv`: CSV file operations
- `datetime`: Timestamp generation

### Optional
- `openpyxl`: XLSX conversion (csv_utils)
- `python-magic`: MIME type checking (file_utils)
- `io.BytesIO`: In-memory file operations

## Future Enhancements

### Enhanced File Validation
```python
def validate_file_comprehensive(file_stream, filename):
    # Check extension
    # Check MIME type
    # Check file size
    # Scan for viruses (if scanner available)
    pass
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_project_root():
    # Cache project root
    pass
```

### Async Operations
```python
async def log_event_async(filename, data):
    # Async logging
    pass
```

## Common Issues

### python-magic Installation
**Windows**: Use `python-magic-bin`
```bash
pip install python-magic-bin
```

**Linux**: Install system library first
```bash
sudo apt-get install libmagic1
```

### Path Issues
Always use `get_project_root()` for consistent path resolution across different execution contexts.

### Encoding Issues
All CSV operations use UTF-8 encoding. Ensure files are saved with UTF-8 encoding.

