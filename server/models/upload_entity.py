"""
Upload entity definition.
Represents a file upload with its metadata.
"""
from datetime import datetime
from typing import Optional

class Upload:
    def __init__(self, upload_id: str, timestamp: str, email: str, user_id: Optional[str], 
                 filename: str, path: str, status: str = 'pending'):
        self.upload_id = upload_id
        self.timestamp = timestamp
        self.email = email
        self.user_id = user_id
        self.filename = filename
        self.path = path
        self.status = status  # 'pending', 'approved', 'declined'
    
    def to_dict(self):
        """Returns a dictionary representation of the upload."""
        return {
            'upload_id': self.upload_id,
            'timestamp': self.timestamp,
            'email': self.email,
            'user_id': self.user_id,
            'filename': self.filename,
            'path': self.path,
            'status': self.status
        }

