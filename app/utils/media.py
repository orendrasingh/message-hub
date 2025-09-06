"""
Media upload and management utilities
"""

import os
import uuid
import shutil
from typing import Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app

from app.utils.validators import validate_media_file, get_file_size, get_media_type


def ensure_media_directory():
    """Ensure media upload directory exists"""
    media_dir = current_app.config.get('MEDIA_FOLDER')
    if media_dir and not os.path.exists(media_dir):
        os.makedirs(media_dir, exist_ok=True)
    return media_dir


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    if not original_filename:
        return str(uuid.uuid4())
    
    # Secure the filename
    filename = secure_filename(original_filename)
    name, ext = os.path.splitext(filename)
    
    # Generate unique name
    unique_name = f"{uuid.uuid4()}{ext}"
    return unique_name


def save_media_file(file: FileStorage) -> Dict[str, Any]:
    """Save uploaded media file and return file info"""
    try:
        # Ensure media directory exists
        media_dir = ensure_media_directory()
        if not media_dir:
            return {'success': False, 'error': 'Media directory not configured'}
        
        # Get allowed extensions and size limits
        allowed_extensions = current_app.config.get('ALLOWED_MEDIA_EXTENSIONS', set())
        max_image_size = current_app.config.get('MAX_IMAGE_SIZE', 10 * 1024 * 1024)
        max_video_size = current_app.config.get('MAX_VIDEO_SIZE', 50 * 1024 * 1024)
        
        # Determine media type and size limit
        media_type = get_media_type(file.filename)
        max_size = max_image_size if media_type == 'image' else max_video_size
        
        # Validate file
        validation = validate_media_file(file, max_size, allowed_extensions)
        if not validation['valid']:
            return {'success': False, 'error': '; '.join(validation['errors'])}
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(media_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Check file size after saving
        file_size = get_file_size(file_path)
        if file_size > max_size:
            # Remove the file if it's too large
            os.remove(file_path)
            return {
                'success': False, 
                'error': f'File too large. Maximum size: {max_size // (1024*1024)}MB'
            }
        
        # Return file info
        return {
            'success': True,
            'filename': unique_filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': file_size,
            'media_type': media_type,
            'relative_path': os.path.join('uploads', 'media', unique_filename)
        }
        
    except Exception as e:
        return {'success': False, 'error': f'Error saving file: {str(e)}'}


def delete_media_file(filename: str) -> bool:
    """Delete media file"""
    try:
        media_dir = current_app.config.get('MEDIA_FOLDER')
        if not media_dir:
            return False
        
        file_path = os.path.join(media_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_media_url(filename: str) -> str:
    """Get URL for media file"""
    if not filename:
        return ""
    
    # Return relative path that can be served by Flask
    return f"/uploads/media/{filename}"


def cleanup_old_media_files(max_age_days: int = 7):
    """Clean up old media files older than specified days"""
    try:
        media_dir = current_app.config.get('MEDIA_FOLDER')
        if not media_dir or not os.path.exists(media_dir):
            return
        
        import time
        max_age_seconds = max_age_days * 24 * 60 * 60
        current_time = time.time()
        
        for filename in os.listdir(media_dir):
            file_path = os.path.join(media_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    
    except Exception as e:
        current_app.logger.error(f"Error cleaning up media files: {e}")


def convert_to_base64_url(file_path: str) -> Optional[str]:
    """Convert media file to base64 data URL for Evolution API"""
    try:
        import base64
        import mimetypes
        
        if not os.path.exists(file_path):
            return None
        
        # Read and encode file
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
            # Return full data URL format for Evolution API
            return f"data:application/octet-stream;base64,{base64_data}"
    
    except Exception as e:
        current_app.logger.error(f"Error converting file to base64: {e}")
        return None


def save_multiple_media_files(files_list) -> Dict[str, Any]:
    """Save multiple uploaded media files and return file info list"""
    try:
        if not files_list:
            return {'success': True, 'files': []}
        
        # Ensure media directory exists
        media_dir = ensure_media_directory()
        if not media_dir:
            return {'success': False, 'error': 'Media directory not configured'}
        
        # Get allowed extensions and size limits
        allowed_extensions = current_app.config.get('ALLOWED_MEDIA_EXTENSIONS', set())
        max_image_size = current_app.config.get('MAX_IMAGE_SIZE', 10 * 1024 * 1024)
        max_video_size = current_app.config.get('MAX_VIDEO_SIZE', 50 * 1024 * 1024)
        
        saved_files = []
        errors = []
        
        for file in files_list:
            if not file or not file.filename:
                continue
                
            # Determine media type and size limit
            media_type = get_media_type(file.filename)
            max_size = max_image_size if media_type == 'image' else max_video_size
            
            # Validate file
            validation = validate_media_file(file, max_size, allowed_extensions)
            if not validation['valid']:
                errors.append(f"{file.filename}: {'; '.join(validation['errors'])}")
                continue
            
            # Generate unique filename
            unique_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(media_dir, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Check file size after saving
            file_size = get_file_size(file_path)
            if file_size > max_size:
                # Remove the file if it's too large
                os.remove(file_path)
                errors.append(f"{file.filename}: File too large. Maximum size: {max_size // (1024*1024)}MB")
                continue
            
            # Add to saved files list
            saved_files.append({
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_path': file_path,
                'file_size': file_size,
                'media_type': media_type,
                'relative_path': os.path.join('uploads', 'media', unique_filename)
            })
        
        if errors and not saved_files:
            return {'success': False, 'errors': errors}
        elif errors and saved_files:
            return {'success': True, 'files': saved_files, 'warnings': errors}
        else:
            return {'success': True, 'files': saved_files}
        
    except Exception as e:
        return {'success': False, 'error': f'Error saving files: {str(e)}'}


def convert_multiple_files_to_base64(file_paths: list) -> list:
    """Convert multiple media files to base64 strings"""
    base64_files = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            base64_data = convert_to_base64_only(file_path)
            if base64_data:
                media_type = get_media_type(os.path.basename(file_path))
                base64_files.append({
                    'base64': base64_data,
                    'media_type': media_type,
                    'filename': os.path.basename(file_path)
                })
    return base64_files


def convert_to_base64_only(file_path: str) -> Optional[str]:
    """Convert media file to base64 string only (no data URL prefix)"""
    try:
        import base64
        
        if not os.path.exists(file_path):
            return None
        
        # Read and encode file
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
            return base64_data
    
    except Exception as e:
        current_app.logger.error(f"Error converting file to base64: {e}")
        return None
    """Convert media file to base64 string only (no data URL prefix)"""
    try:
        import base64
        
        if not os.path.exists(file_path):
            return None
        
        # Read and encode file
        with open(file_path, 'rb') as f:
            file_data = f.read()
            base64_data = base64.b64encode(file_data).decode('utf-8')
            return base64_data
    
    except Exception as e:
        current_app.logger.error(f"Error converting file to base64: {e}")
        return None
