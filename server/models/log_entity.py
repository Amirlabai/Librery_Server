"""
Base log record structure.
Represents a generic log entry for various activity types.
"""
from datetime import datetime
from typing import Optional

class LogEntry:
    def __init__(self, timestamp: str, email: str, event_type: str, 
                 details: Optional[dict] = None):
        self.timestamp = timestamp
        self.email = email
        self.event_type = event_type
        self.details = details or {}
    
    def to_dict(self):
        """Returns a dictionary representation of the log entry."""
        return {
            'timestamp': self.timestamp,
            'email': self.email,
            'event_type': self.event_type,
            'details': self.details
        }

