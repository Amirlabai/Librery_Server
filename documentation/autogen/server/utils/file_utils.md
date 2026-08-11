# Module `merkaz_backend/utils/file_utils.py`

File operations and MIME validation utilities.

## Functions

### `allowed_file(filename)`

Check if file extension is in allowed extensions list (includes both regular and video extensions).

**Arguments:**
- `filename`

### `is_video_file(filename)`

Check if file is a video based on extension.

**Arguments:**
- `filename`

### `is_file_malicious(file_stream)`

Checks the magic number of a file to determine if it's potentially malicious.

**Arguments:**
- `file_stream`
