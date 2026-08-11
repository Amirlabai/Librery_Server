# Module `merkaz_backend/utils/logger_config.py`

Logging configuration module.
Sets up Python logging with timestamp, file, line number, and message format.

## Functions

### `setup_logging(log_level=logging.INFO)`

Configure logging for the entire application.

Args:
    log_level: Logging level (default: INFO)

Returns:
    Configured logger instance

**Arguments:**
- `log_level` (default: `logging.INFO`)

### `get_logger(name)`

Get a logger instance for a specific module.

Args:
    name: Module name (typically __name__)

Returns:
    Logger instance configured with the module name

**Arguments:**
- `name`
