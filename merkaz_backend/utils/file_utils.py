"""
File operations and MIME validation utilities.
"""
import magic
import config.config as config

def allowed_file(filename):
    """Check if file extension is in allowed extensions list."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def is_file_malicious(file_stream):
    """
    Checks the magic number of a file to determine if it's potentially malicious.
    """
    file_signature = file_stream.read(2048)  # Read the first 2048 bytes
    file_stream.seek(0)  # Reset stream position
    
    file_type = magic.from_buffer(file_signature, mime=True)

    # Add more sophisticated checks here if needed
    if "executable" in file_type:
        return True
    
    return False

