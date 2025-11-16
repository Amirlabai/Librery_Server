# Module `merkaz_backend/services/file_service.py`

File service - File management and validation.

## Classes

### `FileService`

Service for file management operations.

#### Methods

- `get_share_directory()`
  - Get the share directory path.

- `get_upload_directory()`
  - Get the upload directory path.

- `get_trash_directory()`
  - Get the trash directory path.

- `validate_file_extension(filename)`
  - Validate if file extension is allowed.
  - Arguments:
    - `filename`

- `validate_file_safety(file_stream)`
  - Validate if file is safe (not malicious).
  - Arguments:
    - `file_stream`

- `create_folder(folder_path)`
  - Create a folder at the specified path.
  - Arguments:
    - `folder_path`

- `delete_item(source_path, trash_path)`
  - Move an item to trash.
  - Arguments:
    - `source_path`
    - `trash_path`

- `create_zip_from_folder(folder_path)`
  - Create a ZIP file from a folder in memory.
  - Arguments:
    - `folder_path`

- `browse_directory(subpath)`
  - Browse a directory and return files/folders with metadata.
  - Arguments:
    - `subpath`

- `delete_item(item_path, email)`
  - Delete an item by moving it to trash.
  - Arguments:
    - `item_path`
    - `email`

- `create_folder(parent_path, folder_name, email)`
  - Create a new folder.
  - Arguments:
    - `parent_path`
    - `folder_name`
    - `email`

- `get_download_file_path(file_path)`
  - Get the directory and filename for file download.
  - Arguments:
    - `file_path`

- `get_file_mime_type(file_path)`
  - Get MIME type of a file.
  - Arguments:
    - `file_path`

- `is_previewable(file_path)`
  - Check if file can be previewed in browser.
  - Arguments:
    - `file_path`

- `get_preview_file_path(file_path)`
  - Get the directory and filename for file preview.
  - Arguments:
    - `file_path`

- `get_download_folder_path(folder_path)`
  - Get the absolute path for folder download.
  - Arguments:
    - `folder_path`

- `_get_pending_log_row_count()`
  - Get the current row count of upload_pending_log.csv (excluding header).

- `_check_and_trigger_cache_priming()`
  - Check if pending log hasn't changed in 1 minute and trigger cache priming.

- `_trigger_cache_priming()`
  - Trigger cache priming in a background thread.

- `monitor_pending_log_changes()`
  - Monitor upload_pending_log.csv for changes.
When row count hasn't changed for 1 minute, triggers cache priming.
Should be called after operations that modify the pending log.

- `prime_search_cache()`
  - Prime the search cache by reading upload_completed_log.csv and splitting it
into separate CSV files based on the first character of filenames (a-z).
Files starting with non-a-z characters are saved to misc.csv.

- `search_uploaded_files(query)`
  - Search for uploaded files in the upload_completed_log based on a query string
against the filename (column 6).
Returns a dict in the format similar to browse_directory() with file results.
  - Arguments:
    - `query`

- `submit_suggestion(suggestion_text, email, session_data)`
  - Submit a suggestion with cooldown management.
  - Arguments:
    - `suggestion_text`
    - `email`
    - `session_data`
