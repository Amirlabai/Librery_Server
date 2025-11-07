# Models Module Documentation

The models layer defines entity classes and data structures used throughout the application.

## Overview

Models represent domain entities and encapsulate both data and behavior. They provide methods for entity operations and serialization.

## Files

### `user_entity.py`

User entity class with authentication and data management methods.

**Class**: `User`

**Properties**:
- `user_id`: Integer or None - Unique user identifier
- `email`: String - User email address
- `password`: String - Hashed password (Werkzeug)
- `role`: String - User role ('user' or 'admin')
- `status`: String - User status ('active', 'inactive', 'pending', 'denied')

**Computed Properties**:
- `is_admin`: Boolean - True if role is 'admin'
- `is_active`: Boolean - True if status is 'active'

**Methods**:

#### `__init__(email, password, role='user', status='active', user_id=None)`
- **Purpose**: Initialize user object
- **Parameters**: All user attributes

#### `check_password(password_to_check)`
- **Purpose**: Verify password against stored hash
- **Parameters**: Plain text password
- **Returns**: Boolean
- **Uses**: Werkzeug `check_password_hash()`

#### `find_by_email(email)` (static)
- **Purpose**: Find user in authenticated users database
- **Returns**: User object or None
- **Uses**: `get_all()` and filters by email

#### `get_all()` (static)
- **Purpose**: Get all authenticated users
- **Returns**: List of User objects
- **Reads**: `config.AUTH_USER_DATABASE` CSV file

#### `save_all(users)` (static)
- **Purpose**: Save all authenticated users
- **Parameters**: List of User objects
- **Writes**: `config.AUTH_USER_DATABASE` CSV file
- **Format**: id,email,password,role,status

#### `get_admin_emails()` (static)
- **Purpose**: Get all admin email addresses
- **Returns**: List of email strings

#### `find_pending_by_email(email)` (static)
- **Purpose**: Find user in pending users database
- **Returns**: User object or None

#### `get_pending()` (static)
- **Purpose**: Get all pending users
- **Returns**: List of User objects
- **Reads**: `config.NEW_USER_DATABASE` CSV file

#### `save_pending(users)` (static)
- **Purpose**: Save all pending users
- **Parameters**: List of User objects
- **Writes**: `config.NEW_USER_DATABASE` CSV file

#### `find_denied_by_email(email)` (static)
- **Purpose**: Find user in denied users database
- **Returns**: User object or None

#### `get_denied()` (static)
- **Purpose**: Get all denied users
- **Returns**: List of User objects
- **Reads**: `config.DENIED_USER_DATABASE` CSV file

#### `save_denied(users)` (static)
- **Purpose**: Save all denied users
- **Parameters**: List of User objects
- **Writes**: `config.DENIED_USER_DATABASE` CSV file

#### `_read_users_from_file(filepath)` (static, private)
- **Purpose**: Helper to read users from CSV file
- **Handles**: Both old format (no ID) and new format (with ID)
- **Returns**: List of User objects

#### `_save_users_to_file(filepath, users)` (static, private)
- **Purpose**: Helper to write users to CSV file
- **Format**: Always writes with ID column (new format)

#### `to_dict()`
- **Purpose**: Serialize user to dictionary
- **Returns**: Dictionary with user data
- **Format**:
  ```python
  {
      "id": 1,
      "email": "user@example.com",
      "role": "user",
      "status": "active",
      "is_admin": False,
      "is_active": True
  }
  ```

**CSV Format**:
```csv
id,email,password,role,status
1,user@example.com,pbkdf2:sha256:...,user,active
```

**Backward Compatibility**: Handles CSV files without ID column (old format)

---

### `upload_entity.py`

Upload entity definition.

**Class**: `Upload`

**Properties**:
- `upload_id`: String - Unique upload identifier
- `timestamp`: String - Upload timestamp
- `email`: String - User email who uploaded
- `user_id`: String or None - User ID
- `filename`: String - Filename
- `path`: String - File path
- `status`: String - Upload status ('pending', 'approved', 'declined')

**Methods**:

#### `__init__(upload_id, timestamp, email, user_id, filename, path, status='pending')`
- **Purpose**: Initialize upload object

#### `to_dict()`
- **Purpose**: Serialize upload to dictionary
- **Returns**: Dictionary with upload data
- **Format**:
  ```python
  {
      'upload_id': '1',
      'timestamp': '2024-01-15 10:30:00',
      'email': 'user@example.com',
      'user_id': '5',
      'filename': 'document.pdf',
      'path': 'folder/document.pdf',
      'status': 'pending'
  }
  ```

**Note**: Currently used as data structure. Future: Add methods for upload operations.

---

### `log_entity.py`

Base log entry structure.

**Class**: `LogEntry`

**Properties**:
- `timestamp`: String - Log entry timestamp
- `email`: String - User email
- `event_type`: String - Type of event
- `details`: Dictionary - Additional event details

**Methods**:

#### `__init__(timestamp, email, event_type, details=None)`
- **Purpose**: Initialize log entry

#### `to_dict()`
- **Purpose**: Serialize log entry to dictionary
- **Returns**: Dictionary with log data
- **Format**:
  ```python
  {
      'timestamp': '2024-01-15 10:30:00',
      'email': 'user@example.com',
      'event_type': 'LOGIN_SUCCESS',
      'details': {}
  }
  ```

**Note**: Base class for log entries. Can be extended for specific log types.

---

## Entity Patterns

### Serialization Pattern
```python
def to_dict(self):
    return {
        "id": self.id,
        "name": self.name,
        # ... other fields
    }
```

### Static Factory Methods
```python
@staticmethod
def find_by_email(email):
    users = User.get_all()
    return next((u for u in users if u.email == email), None)
```

### Property Pattern
```python
@property
def is_admin(self):
    return self.role == 'admin'
```

## Data Formats

### User CSV Format
```csv
id,email,password,role,status
1,user@example.com,pbkdf2:sha256:...,user,active
```

### Upload Log Format
```csv
upload_id,timestamp,email,user_id,filename,path
1,2024-01-15 10:30:00,user@example.com,5,document.pdf,folder/document.pdf
```

## Best Practices

1. **Encapsulate data and behavior** in entity classes
2. **Use properties** for computed values
3. **Provide serialization methods** (to_dict)
4. **Handle backward compatibility** for data migrations
5. **Validate data** in entity methods
6. **Keep entities focused** on single responsibility
7. **Use static methods** for factory/query operations

## Dependencies

- `werkzeug.security`: Password hashing
- `csv`: CSV file operations
- `config.config`: Configuration values

## Future Enhancements

### Validation
Add validation methods:
```python
def validate_email(self):
    import re
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', self.email)
```

### Relationships
Add relationship methods:
```python
def get_uploads(self):
    # Get all uploads by this user
    pass
```

### Events
Add event handlers:
```python
def on_status_change(self, old_status, new_status):
    # Handle status change
    pass
```

## Usage Examples

### Create User
```python
from werkzeug.security import generate_password_hash
from models.user_entity import User

user = User(
    email="user@example.com",
    password=generate_password_hash("password123"),
    role="user",
    status="active",
    user_id=1
)
```

### Find User
```python
user = User.find_by_email("user@example.com")
if user and user.check_password("password123"):
    print("Login successful")
```

### Serialize User
```python
user_dict = user.to_dict()
# Returns: {"id": 1, "email": "...", ...}
```

### Save Users
```python
users = User.get_all()
users.append(new_user)
User.save_all(users)
```

