# Repositories Module Documentation

The repositories layer abstracts data access operations, providing a clean interface for data storage and retrieval.

## Overview

Repositories handle all data access operations, abstracting the underlying storage implementation (currently CSV files). This allows for easy migration to databases in the future.

## Files

### `user_repository.py`

User data access repository.

**Class**: `UserRepository`

**Methods** (all static):

#### `find_by_email(email)`
- **Purpose**: Find user by email in authenticated users
- **Returns**: User object or None
- **Delegates**: `User.find_by_email()`

#### `find_pending_by_email(email)`
- **Purpose**: Find user by email in pending users
- **Returns**: User object or None

#### `find_denied_by_email(email)`
- **Purpose**: Find user by email in denied users
- **Returns**: User object or None

#### `get_all()`
- **Purpose**: Get all authenticated users
- **Returns**: List of User objects

#### `save_all(users)`
- **Purpose**: Save all authenticated users
- **Parameters**: List of User objects

#### `get_pending()`
- **Purpose**: Get all pending users
- **Returns**: List of User objects

#### `save_pending(users)`
- **Purpose**: Save all pending users
- **Parameters**: List of User objects

#### `get_denied()`
- **Purpose**: Get all denied users
- **Returns**: List of User objects

#### `save_denied(users)`
- **Purpose**: Save all denied users
- **Parameters**: List of User objects

#### `get_admin_emails()`
- **Purpose**: Get all admin email addresses
- **Returns**: List of email strings

**Note**: Currently delegates to User entity methods. Future implementation could add caching or database access.

---

### `upload_repository.py`

Upload log data access repository.

**Class**: `UploadRepository`

**Methods** (all static):

#### `get_pending_log_path()`
- **Purpose**: Get absolute path to pending upload log
- **Returns**: String path

#### `get_completed_log_path()`
- **Purpose**: Get absolute path to completed upload log
- **Returns**: String path

#### `get_declined_log_path()`
- **Purpose**: Get absolute path to declined upload log
- **Returns**: String path

#### `read_pending_uploads()`
- **Purpose**: Read all pending uploads from log
- **Returns**: List of dictionaries with upload data
- **Format**:
  ```python
  {
      'upload_id': '1',
      'timestamp': '2024-01-15 10:30:00',
      'email': 'user@example.com',
      'user_id': '5',
      'filename': 'document.pdf',
      'path': 'folder/document.pdf'
  }
  ```

#### `read_completed_uploads()`
- **Purpose**: Read all completed uploads from log
- **Returns**: List of dictionaries with upload data
- **Format**:
  ```python
  {
      'upload_id': '1',
      'original_timestamp': '2024-01-15 10:30:00',
      'approval_timestamp': '2024-01-15 11:00:00',
      'email': 'user@example.com',
      'user_id': '5',
      'filename': 'document.pdf',
      'final_path': 'folder/document.pdf'
  }
  ```

**Error Handling**: Returns empty list if file not found

---

### `download_repository.py`

Download log data access repository.

**Class**: `DownloadRepository`

**Methods** (all static):

#### `get_download_log_path()`
- **Purpose**: Get absolute path to download log
- **Returns**: String path

**Note**: Currently provides path only. Future implementation could add read/write methods.

---

### `session_repository.py`

Session log data access repository.

**Class**: `SessionRepository`

**Methods** (all static):

#### `get_session_log_path()`
- **Purpose**: Get absolute path to session log
- **Returns**: String path

**Note**: Currently provides path only. Future implementation could add read/write methods.

---

### `suggestion_repository.py`

Suggestion log data access repository.

**Class**: `SuggestionRepository`

**Methods** (all static):

#### `get_suggestion_log_path()`
- **Purpose**: Get absolute path to suggestion log
- **Returns**: String path

**Note**: Currently provides path only. Future implementation could add read/write methods.

---

## Repository Pattern Benefits

1. **Abstraction**: Hides storage implementation details
2. **Testability**: Easy to mock for testing
3. **Flexibility**: Easy to switch storage backends
4. **Centralization**: Single point for data access logic

## Current Implementation

### CSV-Based Storage

All repositories currently work with CSV files:
- User data: CSV files in `merkaz_server/data/`
- Logs: CSV files in `merkaz_server/logs/`

### Path Resolution

Repositories use `path_utils.get_project_root()` to resolve absolute paths from relative paths in config.

## Future Enhancements

### Database Migration

Repositories can be extended to use databases:

```python
class UserRepository:
    @staticmethod
    def find_by_email(email):
        # Current: CSV-based
        return User.find_by_email(email)
        
        # Future: Database-based
        # return db.session.query(User).filter_by(email=email).first()
```

### Caching

Add caching layer:

```python
@lru_cache(maxsize=100)
def find_by_email(email):
    return User.find_by_email(email)
```

### Query Methods

Add more query methods:
- `find_by_id(user_id)`
- `find_by_role(role)`
- `find_active_users()`
- `count_users()`

## Usage Examples

### In Services

```python
from repositories.user_repository import UserRepository

# Find user
user = UserRepository.find_by_email("user@example.com")

# Get all users
users = UserRepository.get_all()

# Save users
UserRepository.save_all(users)
```

### In Controllers

```python
from repositories.upload_repository import UploadRepository

# Get pending uploads
pending = UploadRepository.read_pending_uploads()
```

## Best Practices

1. **Keep repositories stateless** (use static methods)
2. **Return consistent data structures**
3. **Handle file not found gracefully**
4. **Abstract storage details** from callers
5. **Provide path methods** for flexibility
6. **Document data formats** in docstrings

## Dependencies

- `utils.path_utils`: Path resolution
- `config.config`: Configuration values
- `models.user_entity`: User entity (for user_repository)
- `csv`: CSV file operations (internal)

## Error Handling

Repositories handle errors gracefully:
- File not found: Returns empty list or None
- Invalid data: Skips invalid rows
- No exceptions thrown: Callers handle None/empty results

