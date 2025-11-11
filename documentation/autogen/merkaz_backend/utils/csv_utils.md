# Module `merkaz_backend/utils/csv_utils.py`

## Functions

### `create_file_with_header(filename, header)`

Creates a file with a header if it doesn't exist.

**Arguments:**
- `filename`
- `header`

### `csv_to_xlsx_in_memory(csv_filepath)`

Converts a CSV file to an XLSX file in memory (BytesIO).

**Arguments:**
- `csv_filepath`

### `_get_id_sequence_file_path()`

Returns the absolute path to the user_id_sequence.txt file.

### `get_next_user_id()`

Generates and returns the next unique user ID.
Tracks the sequence in a persistent file to ensure uniqueness across restarts.

Logic:
1. First, scan all user CSV files to find the maximum existing ID
2. If user_id_sequence.txt exists, compare with stored value and use the higher one
3. If user_id_sequence.txt doesn't exist but users exist, use max_id + 1 from users
4. Update the sequence file with the next ID to assign

### `get_max_user_id_from_files()`

Scans all user CSV files and returns the maximum ID found.
Useful for migration and validation.
Uses absolute paths based on project root.

### `_get_upload_id_sequence_file_path()`

Returns the absolute path to the upload_id_sequence.txt file.

### `get_next_upload_id()`

Generates and returns the next unique upload ID.
Uses a sequence file to ensure uniqueness across restarts.
