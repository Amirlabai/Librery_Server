# Development Guidelines

Guidelines and best practices for developing the Merkaz_lib backend.

## Code Style

### Python Style Guide

Follow PEP 8 Python style guide:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Maximum 100 characters
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Imports**: Group by standard library, third-party, local

### Example

```python
# Standard library
import os
import csv
from datetime import datetime

# Third-party
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

# Local
from models.user_entity import User
from utils import log_event
```

---

## Architecture Guidelines

### Layer Responsibilities

1. **Controllers**: HTTP handling only
   - Validate request format
   - Call services
   - Return responses
   - No business logic

2. **Services**: Business logic
   - Implement workflows
   - Validate business rules
   - Orchestrate operations
   - No HTTP concerns

3. **Repositories**: Data access
   - Abstract storage
   - Provide data methods
   - No business logic

4. **Models**: Entities
   - Data structure
   - Entity methods
   - Serialization

### Example: Adding a New Feature

**Step 1**: Define the model (if needed)
```python
# models/feature_entity.py
class Feature:
    def __init__(self, ...):
        # ...
    
    def to_dict(self):
        # ...
```

**Step 2**: Create repository
```python
# repositories/feature_repository.py
class FeatureRepository:
    @staticmethod
    def get_all():
        # ...
```

**Step 3**: Create service
```python
# services/feature_service.py
class FeatureService:
    @staticmethod
    def process_feature(data):
        # Business logic
        # ...
```

**Step 4**: Create controller
```python
# controllers/feature_controller.py
@feature_bp.route("/feature", methods=["POST"])
def create_feature():
    # Validate request
    # Call service
    # Return response
```

---

## Error Handling

### Consistent Error Format

Always return errors in this format:

```python
return jsonify({"error": "Error message"}), status_code
```

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (not logged in)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `409`: Conflict (duplicate, etc.)
- `429`: Too Many Requests
- `500`: Internal Server Error

### Example

```python
@route("/endpoint", methods=["POST"])
def endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    try:
        result = service.do_operation(data)
        return jsonify({"message": "Success", "data": result}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
```

---

## Security Best Practices

### Authentication

Always check authentication:

```python
if not session.get("logged_in"):
    return jsonify({"error": "Not logged in"}), 401
```

### Authorization

Check permissions:

```python
if not session.get("is_admin"):
    return jsonify({"error": "Access denied"}), 403
```

### Input Validation

Validate all inputs:

```python
# Email validation
if not email or '@' not in email:
    return jsonify({"error": "Invalid email"}), 400

# Path validation
if '..' in path or os.path.isabs(path):
    return jsonify({"error": "Invalid path"}), 400
```

### File Security

Always validate files:

```python
from utils.file_utils import allowed_file, is_file_malicious

if not allowed_file(filename):
    return jsonify({"error": "File type not allowed"}), 400

if is_file_malicious(file.stream):
    return jsonify({"error": "Malicious file detected"}), 400
```

### Path Traversal Protection

```python
# Ensure path stays within allowed directory
if not os.path.abspath(file_path).startswith(os.path.abspath(allowed_dir)):
    return jsonify({"error": "Access denied"}), 403
```

---

## Logging

### Log Important Events

```python
from utils import log_event
from datetime import datetime

log_event(
    config.SESSION_LOG_FILE,
    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email, "EVENT_TYPE"]
)
```

### Log Format

Always use consistent timestamp format:
```python
datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

### Thread-Safe Logging

For concurrent operations, use locks:

```python
import threading

_log_lock = threading.Lock()

with _log_lock:
    log_event(config.LOG_FILE, data)
```

---

## Testing

### Unit Tests

Test individual functions:

```python
def test_get_next_user_id():
    # Test ID generation
    id1 = get_next_user_id()
    id2 = get_next_user_id()
    assert id2 > id1
```

### Integration Tests

Test API endpoints:

```python
def test_login(client):
    response = client.post('/login', json={
        'email': 'user@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
```

### Test Structure

```
tests/
├── test_controllers/
├── test_services/
├── test_repositories/
└── test_utils/
```

---

## Code Organization

### File Structure

- One class/blueprint per file
- Related functions grouped together
- Helper functions at bottom of file

### Function Organization

```python
# Imports
# Constants
# Helper functions
# Main functions
# Blueprint routes
```

### Docstrings

Document all public functions:

```python
def process_upload(file):
    """
    Process and validate file upload.
    
    Args:
        file: File object to process
        
    Returns:
        Tuple of (success, error_message)
        
    Raises:
        ValueError: If file is invalid
    """
    # ...
```

---

## Performance

### Database Operations

- Batch operations when possible
- Use transactions for multiple writes
- Index frequently queried fields

### File Operations

- Use streaming for large files
- Clean up temporary files
- Use appropriate buffer sizes

### Caching

Consider caching for:
- User lookups
- Configuration values
- Computed values

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_by_email(email):
    # ...
```

---

## Migration Guide

### Adding New Fields

1. Update model class
2. Update CSV format (add column)
3. Update read/write methods
4. Handle backward compatibility

### Changing Data Format

1. Create migration script
2. Backup existing data
3. Run migration
4. Verify data integrity

---

## Debugging

### Debug Mode

Enable Flask debug mode (development only):

```python
app.run(debug=True)
```

### Logging

Add print statements or use logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.error("Error message")
```

### Common Issues

1. **Import Errors**: Check PYTHONPATH and virtual environment
2. **Path Issues**: Use `get_project_root()` consistently
3. **Encoding Issues**: Always use UTF-8
4. **Session Issues**: Check session configuration
5. **File Permissions**: Check file/directory permissions

---

## Git Workflow

### Branch Naming

- `feature/feature-name`: New features
- `bugfix/bug-name`: Bug fixes
- `hotfix/issue-name`: Urgent fixes
- `refactor/component-name`: Refactoring

### Commit Messages

Format: `type: description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

Example:
```
feat: Add file upload validation
fix: Resolve path traversal vulnerability
docs: Update API documentation
```

---

## Code Review Checklist

- [ ] Follows architecture patterns
- [ ] Has proper error handling
- [ ] Includes input validation
- [ ] Has security checks
- [ ] Logs important events
- [ ] Has docstrings
- [ ] Follows code style
- [ ] No hardcoded values
- [ ] Handles edge cases
- [ ] Thread-safe (if needed)

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Python Best Practices](https://docs.python-guide.org/writing/style/)
- [Security Best Practices](https://owasp.org/www-project-top-ten/)

---

## Getting Help

- Check existing code for patterns
- Review module documentation
- Check API reference
- Ask team members
- Review architecture documentation

