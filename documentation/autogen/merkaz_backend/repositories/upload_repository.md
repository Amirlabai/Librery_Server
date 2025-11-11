# Module `merkaz_backend/repositories/upload_repository.py`

Upload repository - Manage upload logs and data.

## Classes

### `UploadRepository`

Repository for upload data operations.

#### Methods

- `get_pending_log_path()`
  - Get the path to the pending upload log file.

- `get_completed_log_path()`
  - Get the path to the completed upload log file.

- `get_declined_log_path()`
  - Get the path to the declined upload log file.

- `read_pending_uploads()`
  - Read all pending uploads from the log file.

- `read_completed_uploads()`
  - Read all completed uploads from the log file.
