"""
Input validation and sanitization utilities
"""

import re
import os
from typing import Any, Dict, List, Optional
from werkzeug.datastructures import FileStorage


def sanitize_input(data: Any) -> Any:
    """Basic input sanitization"""
    if isinstance(data, str):
        # Remove potential XSS characters
        data = data.replace('<', '&lt;').replace('>', '&gt;')
        data = data.replace('"', '&quot;').replace("'", '&#x27;')
        data = data.replace('&', '&amp;')  # Should be done last
    return data


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits_only) <= 15


def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    if not password:
        return {'valid': False, 'errors': ['Password is required']}
    
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    
    return {'valid': len(errors) == 0, 'errors': errors}


def validate_csv_file(filename: str) -> bool:
    """Validate CSV file extension"""
    if not filename:
        return False
    
    allowed_extensions = {'csv', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def sanitize_csv_content(content: str) -> str:
    """Sanitize CSV content"""
    # Remove any potential script tags or harmful content
    content = re.sub(r'<script.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<.*?>', '', content)  # Remove any HTML tags
    return content


def validate_message_template(template: str) -> Dict[str, Any]:
    """Validate message template"""
    if not template:
        return {'valid': False, 'errors': ['Message template is required']}
    
    errors = []
    
    if len(template.strip()) == 0:
        errors.append('Message template cannot be empty')
    
    if len(template) > 4096:  # WhatsApp message limit
        errors.append('Message template is too long (max 4096 characters)')
    
    # Check for valid placeholders
    valid_placeholders = ['{name}', '{phone}']
    invalid_placeholders = re.findall(r'\{[^}]+\}', template)
    invalid_placeholders = [p for p in invalid_placeholders if p not in valid_placeholders]
    
    if invalid_placeholders:
        errors.append(f'Invalid placeholders: {", ".join(invalid_placeholders)}. Valid placeholders: {", ".join(valid_placeholders)}')
    
    return {'valid': len(errors) == 0, 'errors': errors}


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file has allowed extension"""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_media_file(file: FileStorage, max_size: int, allowed_extensions: set) -> Dict[str, Any]:
    """Validate uploaded media file"""
    if not file:
        return {'valid': False, 'errors': ['No file provided']}
    
    if not file.filename:
        return {'valid': False, 'errors': ['No filename provided']}
    
    errors = []
    
    # Check file extension
    if not allowed_file(file.filename, allowed_extensions):
        errors.append(f'Invalid file type. Allowed types: {", ".join(allowed_extensions)}')
    
    # Check file size (Note: this requires the file to be saved first to get accurate size)
    # For now, we'll rely on the browser and do additional checks after upload
    
    # Check filename for security
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        errors.append('Invalid filename')
    
    return {'valid': len(errors) == 0, 'errors': errors}


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except (OSError, IOError):
        return 0


def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}
    return allowed_file(filename, image_extensions)


def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    video_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', '3gp'}
    return allowed_file(filename, video_extensions)


def get_media_type(filename: str) -> str:
    """Get media type from filename"""
    if is_image_file(filename):
        return 'image'
    elif is_video_file(filename):
        return 'video'
    else:
        return 'unknown'
