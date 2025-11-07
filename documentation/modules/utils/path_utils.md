# path_utils.py

Path management and directory resolution utilities.

## Location
`merkaz_backend/utils/path_utils.py`

## Functions

### `get_project_root() -> str`
Get the project root directory.

**Returns:**
- `str`: Absolute path to project root directory

**Logic:**
1. Gets directory where `path_utils.py` is located (`merkaz_backend/utils/`)
2. Goes up one level to `merkaz_backend/`
3. Goes up one more level to project root

**Example Path Resolution:**
```
Project Root: /path/to/NagoAmir_Server/
├── merkaz_backend/
│   └── utils/
│       └── path_utils.py  ← This file
```

**Returns:** `/path/to/NagoAmir_Server/`

**Usage:**
```python
from utils.path_utils import get_project_root

project_root = get_project_root()
data_dir = os.path.join(project_root, "merkaz_server/data")
```

---

### `_get_project_root() -> str`
Private alias for backward compatibility.

**Returns:**
- `str`: Same as `get_project_root()`

**Note:**
- Internal function, use `get_project_root()` instead

---

## Dependencies

- `os` - Path operations

---

## Usage Pattern

All file operations should use `get_project_root()` as the base path to ensure consistent path resolution regardless of where the script is executed:

```python
from utils.path_utils import get_project_root
import os

project_root = get_project_root()
config_file = os.path.join(project_root, "merkaz_server/data/users.csv")
```

