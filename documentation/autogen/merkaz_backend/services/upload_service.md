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
