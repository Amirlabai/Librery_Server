# Backend Documentation

Welcome to the Merkaz_lib backend documentation. This documentation provides comprehensive information about the backend architecture, API endpoints, modules, and development guidelines.

## Table of Contents

1. [Architecture Overview](./architecture.md)
2. [API Reference](./api-reference.md)
3. [Module Documentation](./modules/)
   - [Controllers](./modules/controllers.md)
   - [Services](./modules/services.md)
   - [Repositories](./modules/repositories.md)
   - [Models](./modules/models.md)
   - [Utils](./modules/utils.md)
4. [Configuration Guide](./configuration.md)
5. [Setup & Installation](./setup.md)
6. [Development Guidelines](./development.md)

## Quick Start

1. **Installation**: See [Setup Guide](./setup.md)
2. **Configuration**: See [Configuration Guide](./configuration.md)
3. **API Usage**: See [API Reference](./api-reference.md)
4. **Architecture**: See [Architecture Overview](./architecture.md)

## Project Structure

```
merkaz_backend/
├── app.py                        # Main application entry point
├── config/
│   └── config.py                 # Application configuration
├── controllers/                  # API endpoints (Flask routes)
│   ├── auth_controller.py
│   ├── files_controller.py
│   ├── uploads_controller.py
│   └── admin_controller.py
├── services/                     # Business logic layer
│   ├── auth_service.py
│   ├── file_service.py
│   ├── upload_service.py
│   ├── admin_service.py
│   └── mail_service.py
├── repositories/                 # Data access layer
│   ├── user_repository.py
│   ├── upload_repository.py
│   ├── download_repository.py
│   ├── session_repository.py
│   └── suggestion_repository.py
├── models/                       # Entity definitions
│   ├── user_entity.py
│   ├── upload_entity.py
│   └── log_entity.py
└── utils/                        # Utility functions
    ├── file_utils.py
    ├── csv_utils.py
    ├── log_utils.py
    └── path_utils.py
```

## Key Features

- **Layered Architecture**: Clean separation of concerns with controllers, services, repositories, and models
- **User Authentication**: Session-based authentication with role-based access control
- **File Management**: Upload, download, browse, and manage files with admin approval workflow
- **Admin Dashboard**: User management, upload approvals, and system metrics
- **Email Notifications**: Automated emails for user approvals, denials, and password resets
- **Activity Logging**: Comprehensive logging for sessions, downloads, uploads, and suggestions

## Technology Stack

- **Framework**: Flask (Python)
- **Server**: Waitress (WSGI server)
- **Data Storage**: CSV files
- **Email**: Flask-Mail with Gmail SMTP
- **Security**: Werkzeug password hashing, session management
- **File Validation**: python-magic for MIME type checking

## Getting Help

For specific documentation:
- API endpoints: [API Reference](./api-reference.md)
- Code structure: [Architecture Overview](./architecture.md)
- Module details: [Module Documentation](./modules/)
- Configuration: [Configuration Guide](./configuration.md)

