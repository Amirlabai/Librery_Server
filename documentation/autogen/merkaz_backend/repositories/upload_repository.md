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

- `read_declined_uploads()`
  - Read all declined uploads from the log file.

- `find_pending_by_id(upload_id)`
  - Find a pending upload by upload_id.
  - Arguments:
    - `upload_id`

- `find_pending_by_filename(filename)`
  - Find pending uploads by filename or path.
  - Arguments:
    - `filename`

- `remove_from_pending(upload_id)`
  - Remove an entry from the pending log by upload_id.
  - Arguments:
    - `upload_id`

- `update_completed_path(upload_id, new_path)`
  - Update the path of a completed upload.
  - Arguments:
    - `upload_id`
    - `new_path`
