# file_utils.py

File validation and MIME type checking utilities.

## Location
`merkaz_backend/utils/file_utils.py`

## Functions

### `allowed_file(filename: str) -> bool`
Check if file extension is in allowed extensions list.

**Parameters:**
- `filename` (str): Filename to check

**Returns:**
- `bool`: True if file extension is in `config.ALLOWED_EXTENSIONS`

**Validation:**
- Checks if filename contains a dot (extension separator)
- Extracts extension and converts to lowercase
- Compares against whitelist in configuration

**Example:**
```python
allowed_file("document.pdf")  # True if 'pdf' in ALLOWED_EXTENSIONS
allowed_file("script.exe")    # False if 'exe' not in ALLOWED_EXTENSIONS
```

---

### `is_file_malicious(file_stream) -> bool`
Check if file is potentially malicious using magic number detection.

**Parameters:**
- `file_stream`: File stream object (must support `read()` and `seek()`)

**Returns:**
- `bool`: True if file is potentially malicious, False otherwise

**Security Checks:**
1. Reads first 2048 bytes for magic number analysis
2. Resets stream position to beginning
3. Uses `python-magic` to detect MIME type
4. Flags executables as potentially malicious

**Current Detection:**
- Executable files (MIME type contains "executable")

**Future Enhancements:**
- Can add more sophisticated checks
- Can check for specific file signatures
- Can validate against known malicious patterns

**Example:**
```python
with open("file.exe", "rb") as f:
    if is_file_malicious(f):
        print("File rejected: potentially malicious")
```

---

## Dependencies

- `magic` - Python-magic library for MIME type detection
- `config.config` - Configuration constants (ALLOWED_EXTENSIONS)

---

## Installation

For Windows:
```bash
pip install python-magic-bin
```

For Linux/Mac:
```bash
pip install python-magic
```

---

## Configuration

File extensions are configured in `config.config`:
- `ALLOWED_EXTENSIONS` - Set of allowed file extensions

