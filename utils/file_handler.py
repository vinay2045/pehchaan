import os
import uuid
import re
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'pdf':
        return ext in Config.ALLOWED_RESUME_EXTENSIONS
    
    return False

def sanitize_filename(filename):
    """Sanitize filename and add UUID to prevent conflicts"""
    # Get file extension
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
    else:
        name, ext = filename, ''
    
    # Secure the name part
    name = secure_filename(name)
    
    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex[:12]}_{name}"
    
    if ext:
        return f"{unique_name}.{ext.lower()}"
    return unique_name

def save_file(file, folder, file_type='image'):
    """Save uploaded file securely"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename, file_type):
        raise ValueError(f"Invalid file type. Allowed: {Config.ALLOWED_IMAGE_EXTENSIONS if file_type == 'image' else Config.ALLOWED_RESUME_EXTENSIONS}")
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    max_size = Config.MAX_IMAGE_SIZE if file_type == 'image' else Config.MAX_PDF_SIZE
    if file_size > max_size:
        raise ValueError(f"File size exceeds maximum allowed size of {max_size / (1024 * 1024)}MB")
    
    # Sanitize and save
    filename = sanitize_filename(file.filename)
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    
    return filename

def delete_file(filename):
    """Delete file if it exists (filename is relative to static/uploads/)"""
    try:
        if filename:
            # Build full path from static/uploads/
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")
    return False

def handle_file_upload(file, subfolder, max_size=None):
    """
    Handle file upload with validation
    
    Args:
        file: FileStorage object from form
        subfolder: Subfolder name (e.g., 'profiles', 'banners', 'resumes')
        max_size: Maximum file size in bytes
    
    Returns:
        Relative filename (e.g., 'profiles/abc123_photo.jpg') or None
    """
    if not file or file.filename == '':
        return None
    
    # Determine file type
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    file_type = 'pdf' if ext == 'pdf' else 'image'
    
    if not allowed_file(file.filename, file_type):
        raise ValueError(f"Invalid file type")
    
    # Check file size
    if max_size:
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum allowed")
    
    # Create subfolder if it doesn't exist
    upload_path = os.path.join(Config.UPLOAD_FOLDER, subfolder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Sanitize and save
    filename = sanitize_filename(file.filename)
    filepath = os.path.join(upload_path, filename)
    file.save(filepath)
    
    # Return relative path from uploads folder
    return os.path.join(subfolder, filename).replace('\\', '/')
