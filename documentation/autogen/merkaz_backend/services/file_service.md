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
