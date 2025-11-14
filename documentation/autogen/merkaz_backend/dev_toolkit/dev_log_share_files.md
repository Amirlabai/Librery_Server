# Module `merkaz_backend/dev_toolkit/dev_log_share_files.py`

Development script to log all server share files that are not already logged.
Assigns upload IDs to files that don't have them yet.

This script should be run from the project root directory.

## Functions

### `get_share_folder()`

Get the share folder path.

### `get_upload_completed_log_file()`

Get the upload completed log file path.

### `get_upload_id_sequence_file()`

Get the upload ID sequence file path.

### `get_max_upload_id_from_logs()`

Get the maximum upload ID from completed log and sequence file.

### `get_next_upload_id()`

Get the next upload ID, ensuring it's higher than any existing ID.

### `get_logged_paths()`

Get a set of all final_paths that are already logged.

### `log_file_to_completed(upload_id, file_path, relative_path, filename)`

Log a file to the completed upload log.

**Arguments:**
- `upload_id`
- `file_path`
- `relative_path`
- `filename`

### `scan_and_log_share_files()`

Scan all files in the share directory and log them if not already logged.
