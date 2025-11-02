import os
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config
from PIL import Image
import io

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_file(file, folder='general', compress=True, max_size=(1920, 1080)):
    """
    Save uploaded file with optional compression
    
    Args:
        file: FileStorage object from request
        folder: Subfolder name (e.g., 'licenses', 'vehicles', 'goods')
        compress: Whether to compress images
        max_size: Maximum dimensions for compressed images (width, height)
    
    Returns:
        Relative file path or None if failed
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to make unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # Create upload directory if not exists
        upload_path = os.path.join(Config.UPLOAD_FOLDER, folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(upload_path, unique_filename)
        
        # Check if it's an image and compression is enabled
        if compress and ext.lower() in ['.jpg', '.jpeg', '.png']:
            # Open and compress image
            image = Image.open(file)
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            # Resize if larger than max_size
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save compressed image
            if ext.lower() == '.png':
                image.save(file_path, 'PNG', optimize=True)
            else:
                image.save(file_path, 'JPEG', quality=85, optimize=True)
        else:
            # Save file as-is
            file.save(file_path)
        
        # Return relative path
        return os.path.join(folder, unique_filename)
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def delete_file(file_path):
    """
    Delete a file from the filesystem
    
    Args:
        file_path: Relative path to the file
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        full_path = os.path.join(Config.UPLOAD_FOLDER, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def get_file_url(file_path):
    """
    Get full URL for a file
    
    Args:
        file_path: Relative path to file
    
    Returns:
        Full URL to access the file
    """
    if not file_path:
        return None
    
    # In production, this should return the full URL
    # For now, return relative path
    return f"/uploads/{file_path}"

def validate_file_size(file, max_size_mb=16):
    """
    Validate file size
    
    Args:
        file: FileStorage object
        max_size_mb: Maximum size in megabytes
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # Seek to end to get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    except Exception as e:
        print(f"Error validating file size: {e}")
        return False

def process_image(file, output_format='JPEG', quality=85):
    """
    Process and optimize image
    
    Args:
        file: FileStorage object or file path
        output_format: Output format ('JPEG', 'PNG', 'WEBP')
        quality: Quality for JPEG/WEBP (1-100)
    
    Returns:
        BytesIO object with processed image
    """
    try:
        image = Image.open(file)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            if output_format == 'JPEG':
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            else:
                image = image.convert('RGBA')
        
        # Create output buffer
        output = io.BytesIO()
        
        # Save with optimization
        if output_format == 'JPEG':
            image.save(output, format='JPEG', quality=quality, optimize=True)
        elif output_format == 'PNG':
            image.save(output, format='PNG', optimize=True)
        elif output_format == 'WEBP':
            image.save(output, format='WEBP', quality=quality)
        
        output.seek(0)
        return output
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def create_thumbnail(file_path, size=(300, 300)):
    """
    Create thumbnail from image
    
    Args:
        file_path: Path to original image
        size: Thumbnail size (width, height)
    
    Returns:
        Path to thumbnail or None
    """
    try:
        full_path = os.path.join(Config.UPLOAD_FOLDER, file_path)
        
        if not os.path.exists(full_path):
            return None
        
        # Open image
        image = Image.open(full_path)
        
        # Create thumbnail
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create thumbnail path
        name, ext = os.path.splitext(file_path)
        thumb_path = f"{name}_thumb{ext}"
        thumb_full_path = os.path.join(Config.UPLOAD_FOLDER, thumb_path)
        
        # Save thumbnail
        image.save(thumb_full_path, optimize=True, quality=85)
        
        return thumb_path
    
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return None
