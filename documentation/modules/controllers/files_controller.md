# files_controller.py

Files controller handling file browsing, downloading, folder management, and suggestion submission.

## Location
`merkaz_backend/controllers/files_controller.py`

## Blueprint
`files_bp` - Registered at root level

## Routes

### `GET /browse` or `GET /browse/<path:subpath>`
Browse directory endpoint.

**URL Parameters:**
- `subpath` (optional): Directory path to browse (default: root)

**Response (200):**
```json
{
  "items": [
    {
      "upload_id": "123",
      "name": "filename.txt",
      "path": "path/to/file",
      "is_folder": false
    }
  ],
  "current_path": "path/to",
  "back_path": "path",
  "is_admin": false,
  "cooldown_level": 1
}
```

**Errors:**
- `401` - Not logged in
- `404` - Invalid path
- `403` - Access denied

**Features:**
- Path traversal protection
- Upload ID tracking for files
- Sorted folders and files
- Cooldown level tracking

---

### `GET /download/file/<path:item_path>`
Download a file endpoint.

**URL Parameters:**
- `item_path` (str): Path to file relative to share directory

**Response:**
- File download with appropriate MIME type

**Errors:**
- `401` - Not logged in
- `403` - Access denied
- `404` - File not found

**Logs:**
- `FILE` event to download log

---

### `GET /download/folder/<path:item_path>`
Download folder as ZIP endpoint.

**URL Parameters:**
- `item_path` (str): Path to folder relative to share directory

**Response:**
- ZIP file download

**Errors:**
- `401` - Not logged in
- `404` - Folder not found

**Logs:**
- `FOLDER` event to download log

---

### `POST /create_folder`
Create new folder endpoint (admin only).

**Request Body:**
```json
{
  "parent_path": "optional/parent",
  "folder_name": "New Folder"
}
```

**Response (200):**
```json
{
  "message": "Folder 'New Folder' created successfully."
}
```

**Errors:**
- `403` - Access denied (not admin)
- `400` - Missing JSON body, empty folder name, or invalid characters
- `409` - Folder or file already exists
- `500` - Error creating folder

**Validations:**
- Folder name cannot contain `/`, `\`, or `..`
- Path must be within share directory

**Logs:**
- `CREATE_FOLDER` event to download log

---

### `POST /delete/<path:item_path>`
Delete file or folder endpoint (admin only).

**URL Parameters:**
- `item_path` (str): Path to item relative to share directory

**Response (200):**
```json
{
  "message": "Successfully moved 'filename.txt' to trash."
}
```

**Errors:**
- `403` - Access denied (not admin)
- `404` - File or folder not found
- `500` - Error deleting item

**Actions:**
- Moves item to trash directory with timestamp prefix
- Logs deletion event

**Logs:**
- `DELETE` event to download log

---

### `POST /suggest`
Submit suggestion endpoint with cooldown system.

**Request Body:**
```json
{
  "suggestion": "I suggest a dark mode feature."
}
```

**Response (200):**
```json
{
  "message": "Thank you, your suggestion has been submitted!"
}
```

**Errors:**
- `401` - Not logged in
- `400` - Missing JSON body or suggestion text required
- `429` - Cooldown active (must wait X minutes)

**Cooldown System:**
- Progressive cooldown: 1 min, 2 min, 4 min, 8 min, 16 min, 30 min
- Stored in session as `cooldown_index`
- Cooldown resets after 30 minutes

**Logs:**
- Suggestion text to suggestion log

---

## Security Features

- **Path Traversal Protection:** Validates paths to prevent directory traversal attacks
- **Access Control:** Admin-only endpoints check `is_admin` session flag
- **Path Validation:** Ensures all paths stay within share directory boundaries

---

## Dependencies

- `flask.Blueprint` - Route organization
- `flask.session` - Session management
- `zipfile` - ZIP archive creation
- `shutil` - File operations
- `utils` - Logging and path utilities
- `config.config` - Configuration constants

