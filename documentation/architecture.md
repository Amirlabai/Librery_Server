# Architecture Overview

## System Architecture

The Merkaz_lib backend follows a **layered architecture** pattern, providing clear separation of concerns and maintainability.

```
┌─────────────────────────────────────────┐
│         Controllers (API Layer)         │
│  Handles HTTP requests and responses    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Services (Business Logic)        │
│  Implements business rules and workflows│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Repositories (Data Access)         │
│  Abstracts data storage operations      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Models (Entities)                │
│  Defines data structures and entities   │
└─────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Controllers Layer (`controllers/`)

**Purpose**: Handle HTTP requests and responses, route definitions

**Responsibilities**:
- Define API endpoints (Flask routes)
- Validate request data
- Call appropriate services
- Format and return responses
- Handle authentication/authorization checks

**Files**:
- `auth_controller.py` - Authentication endpoints (login, register, logout, password reset)
- `files_controller.py` - File browsing, downloading, folder management
- `uploads_controller.py` - File upload handling and approval workflow
- `admin_controller.py` - Admin dashboard endpoints

### 2. Services Layer (`services/`)

**Purpose**: Implement business logic and orchestrate operations

**Responsibilities**:
- Business rule validation
- Workflow orchestration
- Cross-cutting concerns (email, logging)
- Session management
- File validation and processing

**Files**:
- `auth_service.py` - Authentication and session management
- `file_service.py` - File operations and validation
- `upload_service.py` - Upload workflow and logging
- `admin_service.py` - Admin operations (approvals, user management)
- `mail_service.py` - Email sending and notifications

### 3. Repositories Layer (`repositories/`)

**Purpose**: Abstract data access operations

**Responsibilities**:
- Provide data access methods
- Handle file paths and data file operations
- Abstract storage implementation (currently CSV files)

**Files**:
- `user_repository.py` - User data access
- `upload_repository.py` - Upload log access
- `download_repository.py` - Download log access
- `session_repository.py` - Session log access
- `suggestion_repository.py` - Suggestion log access

### 4. Models Layer (`models/`)

**Purpose**: Define data structures and entity definitions

**Responsibilities**:
- Define entity classes
- Provide data serialization methods
- Handle entity-specific logic

**Files**:
- `user_entity.py` - User entity with authentication methods
- `upload_entity.py` - Upload entity definition
- `log_entity.py` - Base log entry structure

### 5. Utils Layer (`utils/`)

**Purpose**: Provide reusable utility functions

**Responsibilities**:
- Path management
- CSV operations
- Logging helpers
- File validation
- ID generation

**Files**:
- `path_utils.py` - Path and directory utilities
- `csv_utils.py` - CSV file operations and ID generation
- `log_utils.py` - Logging helper functions
- `file_utils.py` - File validation and MIME checking

## Data Flow

### Example: User Registration Flow

```
1. Client → POST /register
   ↓
2. auth_controller.api_register()
   - Validates request data
   - Checks if email exists
   ↓
3. auth_service (implicit)
   - Generates user ID
   ↓
4. User Entity
   - Creates user object
   ↓
5. User Repository / User Entity
   - Saves to pending users CSV
   ↓
6. mail_service
   - Sends notification to admins
   ↓
7. Response to Client
```

### Example: File Upload Flow

```
1. Client → POST /upload
   ↓
2. uploads_controller.upload_file()
   - Validates authentication
   ↓
3. file_utils / upload_service
   - Validates file type and safety
   - Generates unique filename
   ↓
4. File saved to uploads/ directory
   ↓
5. upload_service
   - Logs to pending upload log
   ↓
6. Response to Client
   ↓
7. Admin approves via /admin/move_upload
   ↓
8. File moved to files_to_share/
   ↓
9. Log moved to completed log
```

## Design Patterns

### 1. Repository Pattern
- Abstracts data access
- Allows easy switching between storage backends
- Centralizes data access logic

### 2. Service Layer Pattern
- Separates business logic from controllers
- Enables code reuse
- Makes testing easier

### 3. Entity Pattern
- Encapsulates data and behavior
- Provides methods for entity operations
- Handles serialization

## Security Architecture

### Authentication
- Session-based authentication
- 15-minute session timeout
- Password hashing with Werkzeug

### Authorization
- Role-based access control (Admin/User)
- Session-based authorization checks
- Admin-only endpoints protected

### File Security
- File type validation (extension whitelist)
- MIME type checking (magic number validation)
- Path traversal protection
- Unique filename generation

## Data Storage

### Current Implementation: CSV Files

**User Data**:
- `auth_users.csv` - Authenticated users
- `new_users.csv` - Pending registrations
- `denied_users.csv` - Denied registrations

**Logs**:
- `session_log.csv` - Login/logout events
- `download_log.csv` - File/folder downloads
- `suggestion_log.csv` - User suggestions
- `upload_pending_log.csv` - Pending uploads
- `upload_completed_log.csv` - Approved uploads
- `declined_log.csv` - Declined uploads

**Files**:
- `files_to_share/` - Approved shared files
- `uploads/` - Pending uploads (flat structure)
- `trash/` - Deleted files

## Session Management

- Flask sessions with server-side storage
- 15-minute timeout (configurable)
- Session data includes:
  - `logged_in`: Boolean
  - `email`: User email
  - `user_id`: Unique user ID
  - `is_admin`: Admin status
  - `cooldown_index`: Suggestion cooldown level

## Error Handling

- Consistent JSON error responses
- HTTP status codes:
  - `200`: Success
  - `400`: Bad Request
  - `401`: Unauthorized
  - `403`: Forbidden
  - `404`: Not Found
  - `409`: Conflict
  - `429`: Too Many Requests
  - `500`: Internal Server Error

## Future Improvements

1. **Database Migration**: Replace CSV with SQLite/PostgreSQL
2. **Caching**: Add Redis for session management
3. **File Storage**: Consider cloud storage (S3, Azure Blob)
4. **API Versioning**: Add versioning support
5. **Rate Limiting**: Implement rate limiting middleware
6. **Testing**: Add comprehensive unit and integration tests

