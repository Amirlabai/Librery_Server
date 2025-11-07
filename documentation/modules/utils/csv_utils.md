# csv_utils.py

CSV file operations and ID generation utilities.

## Location
`merkaz_backend/utils/csv_utils.py`

## Functions

### `create_file_with_header(filename: str, header: list) -> None`
Create a CSV file with a header if it doesn't exist.

**Parameters:**
- `filename` (str): Relative path to CSV file (from project root)
- `header` (list): List of column names

**Actions:**
- Creates directory structure if needed
- Creates file with header row if file doesn't exist
- Prints confirmation message

**Example:**
```python
create_file_with_header("data/users.csv", ["id", "email", "password"])
```

---

### `csv_to_xlsx_in_memory(csv_filepath: str) -> BytesIO`
Convert a CSV file to an XLSX file in memory.

**Parameters:**
- `csv_filepath` (str): Absolute path to CSV file

**Returns:**
- `BytesIO`: In-memory XLSX file object (seeked to position 0)

**Features:**
- Creates Excel workbook with single sheet
- Sheet name derived from CSV filename
- Handles missing files gracefully (adds error row)

**Dependencies:**
- Requires `openpyxl` library

**Example:**
```python
xlsx_data = csv_to_xlsx_in_memory("/path/to/log.csv")
# Send as download response
return send_file(xlsx_data, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
```

---

### `get_next_user_id() -> int`
Generate the next unique user ID.

**Returns:**
- `int`: Next available user ID

**Logic:**
1. Scans all user CSV files (auth, pending, denied) to find maximum existing ID
2. Checks sequence file (`user_id_sequence.txt`) if it exists
3. Uses the higher value between max file ID and stored sequence
4. Updates sequence file with next ID to assign
5. Returns the next available ID

**Thread Safety:**
- File-based locking ensures uniqueness
- Handles concurrent access safely

**Example:**
```python
new_user_id = get_next_user_id()  # Returns 1, 2, 3, etc.
```

---

### `get_max_user_id_from_files() -> int`
Scan all user CSV files and return the maximum ID found.

**Returns:**
- `int`: Maximum user ID found in all user files (0 if none found)

**Usage:**
- Useful for migration and validation
- Helps ensure ID consistency

**Scans:**
- `auth_users.csv`
- `new_users.csv`
- `denied_users.csv`

---

### `get_next_upload_id() -> int`
Generate the next unique upload ID.

**Returns:**
- `int`: Next available upload ID

**Logic:**
1. Reads sequence file (`upload_id_sequence.txt`)
2. Increments and stores next ID
3. Returns current ID

**Thread Safety:**
- File-based sequence tracking
- Handles concurrent uploads

**Example:**
```python
upload_id = get_next_upload_id()  # Returns 1, 2, 3, etc.
```

---

## Private Functions

### `_get_id_sequence_file_path() -> str`
Get absolute path to user ID sequence file.

**Returns:**
- `str`: Absolute path to `user_id_sequence.txt`

---

### `_get_upload_id_sequence_file_path() -> str`
Get absolute path to upload ID sequence file.

**Returns:**
- `str`: Absolute path to `upload_id_sequence.txt`

---

## Dependencies

- `openpyxl` - Optional, for XLSX conversion
- `csv` - CSV file operations
- `io.BytesIO` - In-memory file handling
- `utils.path_utils` - Project root path resolution
- `config.config` - Configuration constants

---

## File Locations

Sequence files are stored in project root:
- `merkaz_server/data/user_id_sequence.txt`
- `merkaz_server/data/upload_id_sequence.txt`

