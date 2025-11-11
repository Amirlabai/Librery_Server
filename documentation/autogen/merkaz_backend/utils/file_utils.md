# Module `merkaz_backend/utils/file_utils.py`

File operations and MIME validation utilities.

## Functions

### `allowed_file(filename)`

Check if file extension is in allowed extensions list.

**Arguments:**
- `filename`

### `is_file_malicious(file_stream)`

Checks the magic number of a file to determine if it's potentially malicious.

**Arguments:**
- `file_stream`
