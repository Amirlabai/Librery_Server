# Module `merkaz_backend/services/upload_service.py`

Upload service - File upload logic and workflow.

## Classes

### `UploadService`

Service for upload operations.

#### Methods

- `get_upload_directory()`
  - Get the upload directory path.

- `validate_file(file)`
  - Validate a file for upload.
  - Arguments:
    - `file`

- `get_next_upload_id()`
  - Get the next unique upload ID.

- `log_pending_upload(upload_id, email, user_id, filename, path)`
  - Log a pending upload to the pending log.
  - Arguments:
    - `upload_id`
    - `email`
    - `user_id`
    - `filename`
    - `path`

- `log_completed_upload(upload_id, original_timestamp, email, user_id, filename, final_path)`
  - Log a completed upload to the completed log.
  - Arguments:
    - `upload_id`
    - `original_timestamp`
    - `email`
    - `user_id`
    - `filename`
    - `final_path`

- `log_declined_upload(email, user_id, filename)`
  - Log a declined upload.
  - Arguments:
    - `email`
    - `user_id`
    - `filename`

- `get_unique_filename(upload_dir, filename, share_dir=None, share_subpath='', save_flat=True)`
  - Generates a unique filename by appending _1, _2, etc. if a file with the same name exists.
Checks in both the upload directory and the share directory (eventual destination).

For folder uploads: saves files flat in uploads directory but preserves path in metadata.

Args:
    upload_dir: Base upload directory
    filename: Original filename (may include relative path for folder uploads)
    share_dir: Optional base share directory to check for conflicts
    share_subpath: Optional subpath in share directory where file will eventually be placed
    save_flat: If True, save files flat (no directory structure) in upload_dir

Returns:
    Tuple of (flat_filename_for_storage, full_save_path, full_relative_path_for_log)
  - Arguments:
    - `upload_dir`
    - `filename`
    - `share_dir` (default: `None`)
    - `share_subpath` (default: `''`)
    - `save_flat` (default: `True`)

- `remove_from_pending_log(upload_id)`
  - Remove an entry from the pending log by upload_id.
  - Arguments:
    - `upload_id`

- `upload_files(uploaded_files, upload_subpath, email, user_id)`
  - Process multiple file uploads.
  - Arguments:
    - `uploaded_files`
    - `upload_subpath`
    - `email`
    - `user_id`

- `get_my_uploads(email, user_id)`
  - Get all uploads for a specific user.
  - Arguments:
    - `email`
    - `user_id`

- `get_admin_uploads()`
  - Get all pending uploads for admin review.

- `move_upload(upload_id, filename, target_path_str, email)`
  - Move an upload from pending to approved location.
  - Arguments:
    - `upload_id`
    - `filename`
    - `target_path_str`
    - `email`

- `decline_upload(upload_id, filename, email, user_id)`
  - Decline an upload and remove it.
  - Arguments:
    - `upload_id`
    - `filename`
    - `email`
    - `user_id`

- `move_file_for_edit(upload_id, old_path, new_path)`
  - Move a file from old_path to new_path in the share directory.
  - Arguments:
    - `upload_id`
    - `old_path`
    - `new_path`

- `edit_upload_path(upload_id, new_path)`
  - Edit the path of a completed upload and move the file.
  - Arguments:
    - `upload_id`
    - `new_path`

- `edit_folder_path(upload_id, new_path, old_path)`
  - Edit the path of a folder and move the folder, updating all nested files/folders in log.
  - Arguments:
    - `upload_id`
    - `new_path`
    - `old_path`
