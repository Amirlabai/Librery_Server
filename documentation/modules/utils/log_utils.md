# log_utils.py

Logging helper functions for CSV-based activity logs.

## Location
`merkaz_backend/utils/log_utils.py`

## Functions

### `log_event(filename: str, data: list) -> None`
Append a new row to a specified CSV log file.

**Parameters:**
- `filename` (str): Absolute path to CSV log file
- `data` (list): List of values to write as a row

**Actions:**
- Creates directory structure if needed
- Opens file in append mode
- Writes data as CSV row with UTF-8 encoding
- Uses newline='' for cross-platform compatibility

**Thread Safety:**
- **Not thread-safe** - Use `threading.Lock()` in calling code for concurrent access

**Example:**
```python
from utils.log_utils import log_event
from datetime import datetime

log_event(
    "/path/to/log.csv",
    [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user@example.com",
        "LOGIN_SUCCESS"
    ]
)
```

**Usage Pattern:**
```python
import threading
from utils.log_utils import log_event

_log_lock = threading.Lock()

def safe_log_event(filename, data):
    with _log_lock:
        log_event(filename, data)
```

---

## Dependencies

- `csv` - CSV file operations
- `os` - Directory creation
- `utils.path_utils` - Project root path resolution

---

## Log File Format

All log files use CSV format with UTF-8 encoding:
- **Delimiter:** Comma
- **Encoding:** UTF-8
- **Newlines:** Platform-agnostic (newline='')

**Common Log Files:**
- Session log: `timestamp,email,event`
- Download log: `timestamp,email,type,path`
- Suggestion log: `timestamp,email,suggestion`
- Upload log: `timestamp,email,user_id,filename,path`

