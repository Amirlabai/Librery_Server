# Module `merkaz_backend/models/log_entity.py`

Base log record structure.
Represents a generic log entry for various activity types.

## Classes

### `LogEntry`

No description provided.

#### Methods

- `__init__(self, timestamp: str, email: str, event_type: str, details: Optional[dict]=None)`
  - No description provided.
  - Arguments:
    - `self`
    - `timestamp` : `str`
    - `email` : `str`
    - `event_type` : `str`
    - `details` : `Optional[dict]` (default: `None`)

- `to_dict(self)`
  - Returns a dictionary representation of the log entry.
  - Arguments:
    - `self`
