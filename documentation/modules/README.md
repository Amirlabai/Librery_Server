# Module Documentation

This directory contains detailed documentation for each Python module in the backend.

## Structure

```
modules/
├── controllers/          # Controller layer documentation
│   ├── auth_controller.md
│   ├── files_controller.md
│   ├── uploads_controller.md
│   └── admin_controller.md
│
├── services/             # Service layer documentation
│   ├── auth_service.md
│   ├── file_service.md
│   ├── upload_service.md
│   ├── admin_service.md
│   └── mail_service.md
│
├── repositories/         # Repository layer documentation
│   ├── user_repository.md
│   ├── upload_repository.md
│   ├── download_repository.md
│   ├── session_repository.md
│   └── suggestion_repository.md
│
├── models/              # Model/Entity documentation
│   ├── user_entity.md
│   ├── upload_entity.md
│   └── log_entity.md
│
└── utils/               # Utility module documentation
    ├── path_utils.md
    ├── csv_utils.md
    ├── log_utils.md
    └── file_utils.md
```

## Documentation Format

Each module documentation file includes:

1. **Location** - File path
2. **Overview** - Purpose and responsibilities
3. **Classes/Functions** - Detailed documentation for each:
   - Parameters
   - Return values
   - Usage examples
   - Error handling
4. **Dependencies** - Required modules and libraries
5. **Usage Examples** - Code examples where applicable

## Quick Links

### Controllers
- [Authentication Controller](controllers/auth_controller.md) - Login, registration, password reset
- [Files Controller](controllers/files_controller.md) - File browsing, downloads, folder management
- [Uploads Controller](controllers/uploads_controller.md) - File uploads and approval workflow
- [Admin Controller](controllers/admin_controller.md) - Admin dashboard and user management

### Services
- [Auth Service](services/auth_service.md) - Session handling and user tracking
- [File Service](services/file_service.md) - File management operations
- [Upload Service](services/upload_service.md) - Upload workflow logic
- [Admin Service](services/admin_service.md) - Admin operations
- [Mail Service](services/mail_service.md) - Email notifications

### Repositories
- [User Repository](repositories/user_repository.md) - User data access
- [Upload Repository](repositories/upload_repository.md) - Upload log management
- [Download Repository](repositories/download_repository.md) - Download history
- [Session Repository](repositories/session_repository.md) - Session logs
- [Suggestion Repository](repositories/suggestion_repository.md) - User suggestions

### Models
- [User Entity](models/user_entity.md) - User data model
- [Upload Entity](models/upload_entity.md) - Upload data model
- [Log Entity](models/log_entity.md) - Log entry model

### Utils
- [Path Utils](utils/path_utils.md) - Path management
- [CSV Utils](utils/csv_utils.md) - CSV operations and ID generation
- [Log Utils](utils/log_utils.md) - Logging helpers
- [File Utils](utils/file_utils.md) - File validation

