"""
File service - File management and validation.
"""
import os
import shutil
import zipfile
from io import BytesIO
from utils.file_utils import allowed_file, is_file_malicious
from utils.path_utils import get_project_root
import config.config as config

class FileService:
    """Service for file management operations."""
    
    @staticmethod
    def get_share_directory():
        """Get the share directory path."""
        project_root = get_project_root()
        return os.path.join(project_root, config.SHARE_FOLDER)
    
    @staticmethod
    def get_upload_directory():
        """Get the upload directory path."""
        project_root = get_project_root()
        return os.path.join(project_root, config.UPLOAD_FOLDER)
    
    @staticmethod
    def get_trash_directory():
        """Get the trash directory path."""
        project_root = get_project_root()
        return os.path.join(project_root, config.TRASH_FOLDER)
    
    @staticmethod
    def validate_file_extension(filename):
        """Validate if file extension is allowed."""
        return allowed_file(filename)
    
    @staticmethod
    def validate_file_safety(file_stream):
        """Validate if file is safe (not malicious)."""
        return not is_file_malicious(file_stream)
    
    @staticmethod
    def create_folder(folder_path):
        """Create a folder at the specified path."""
        os.makedirs(folder_path, exist_ok=True)
    
    @staticmethod
    def delete_item(source_path, trash_path):
        """Move an item to trash."""
        shutil.move(source_path, trash_path)
    
    @staticmethod
    def create_zip_from_folder(folder_path):
        """Create a ZIP file from a folder in memory."""
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zf.write(file_path, os.path.relpath(file_path, folder_path))
        memory_file.seek(0)
        return memory_file

