# Utility module exports
from .path_utils import get_project_root, _get_project_root
from .csv_utils import (
    create_file_with_header,
    csv_to_xlsx_in_memory,
    get_next_user_id,
    get_max_user_id_from_files,
    get_next_upload_id
)
from .log_utils import log_event
from .file_utils import allowed_file, is_file_malicious

# Backward compatibility - export commonly used functions at package level
__all__ = [
    'get_project_root',
    '_get_project_root',
    'create_file_with_header',
    'csv_to_xlsx_in_memory',
    'get_next_user_id',
    'get_max_user_id_from_files',
    'get_next_upload_id',
    'log_event',
    'allowed_file',
    'is_file_malicious'
]

