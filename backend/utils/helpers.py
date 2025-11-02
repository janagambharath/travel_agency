import random
import string
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from config import Config

def generate_booking_id():
    """Generate unique booking ID"""
    # Format: SRTA-YYYYMMDD-XXXXX
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=5))
    return f"SRTA-{date_str}-{random_str}"

def generate_invoice_number():
    """Generate invoice number"""
    # Format: INV-YYYYMMDD-XXXXX
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.digits, k=5))
    return f"INV-{date_str}-{random_str}"

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder='general'):
    """
    Save uploaded file and return filename
    
    Args:
        file: FileStorage object
        folder: Subfolder within uploads (e.g., 'licenses', 'vehicles', 'goods')
    
    Returns:
        Relative file path
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Add timestamp to filename to make it unique
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # Create upload folder if not exists
        upload_path = os.path.join(Config.UPLOAD_FOLDER, folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Return relative path
        return os.path.join(folder, unique_filename)
    
    return None

def format_phone(phone):
    """
    Format phone number to standard format
    Assumes Indian phone numbers
    """
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # Add +91 if not present
    if len(phone) == 10:
        return f"+91{phone}"
    elif len(phone) == 12 and phone.startswith('91'):
        return f"+{phone}"
    
    return phone

def calculate_commission(fare, percentage=10, min_commission=100, max_commission=300):
    """
    Calculate admin commission with min/max limits
    
    Args:
        fare: Total fare amount
        percentage: Commission percentage (default 10%)
        min_commission: Minimum commission amount
        max_commission: Maximum commission amount
    
    Returns:
        Commission amount
    """
    commission = fare * (percentage / 100)
    
    # Apply limits
    commission = max(min_commission, min(commission, max_commission))
    
    return round(commission, 2)

def get_time_slots(date=None):
    """
    Get available time slots for booking
    
    Args:
        date: Date for which to get slots (default: today)
    
    Returns:
        List of time slots
    """
    slots = []
    
    # Generate slots from 6 AM to 8 PM in 2-hour intervals
    start_hour = 6
    end_hour = 20
    interval = 2
    
    for hour in range(start_hour, end_hour, interval):
        time_str = f"{hour:02d}:00"
        slots.append({
            'value': time_str,
            'label': datetime.strptime(time_str, '%H:%M').strftime('%I:%M %p')
        })
    
    return slots

def get_goods_types():
    """Get list of available goods types"""
    return [
        {'value': 'cement', 'label_en': 'Cement', 'label_te': 'సిమెంట్'},
        {'value': 'bricks', 'label_en': 'Bricks', 'label_te': 'ఇటుకలు'},
        {'value': 'sand', 'label_en': 'Sand', 'label_te': 'ఇసుక'},
        {'value': 'gravel', 'label_en': 'Gravel', 'label_te': 'గులకరాళ్ళు'},
        {'value': 'furniture', 'label_en': 'Furniture', 'label_te': 'ఫర్నిచర్'},
        {'value': 'electronics', 'label_en': 'Electronics', 'label_te': 'ఎలక్ట్రానిక్స్'},
        {'value': 'household', 'label_en': 'Household Items', 'label_te': 'గృహ సామగ్రి'},
        {'value': 'machinery', 'label_en': 'Machinery', 'label_te': 'యంత్రాలు'},
        {'value': 'agricultural', 'label_en': 'Agricultural Goods', 'label_te': 'వ్యవసాయ సామాగ్రి'},
        {'value': 'food_items', 'label_en': 'Food Items', 'label_te': 'ఆహార పదార్థాలు'},
        {'value': 'textiles', 'label_en': 'Textiles', 'label_te': 'వస్త్రాలు'},
        {'value': 'others', 'label_en': 'Others', 'label_te': 'ఇతరాలు'}
    ]

def get_vehicle_types():
    """Get list of vehicle types"""
    return [
        {
            'value': 'mini_dcm',
            'label_en': 'Mini DCM',
            'label_te': 'మినీ DCM',
            'capacity': '1-2 tons'
        },
        {
            'value': 'standard_dcm',
            'label_en': 'Standard DCM',
            'label_te': 'స్టాండర్డ్ DCM',
            'capacity': '2-4 tons'
        },
        {
            'value': 'large_dcm',
            'label_en': 'Large DCM',
            'label_te': 'పెద్ద DCM',
            'capacity': '4-6 tons'
        }
    ]

def get_telangana_cities():
    """Get list of major cities in Telangana"""
    return [
        {'value': 'hyderabad', 'label_en': 'Hyderabad', 'label_te': 'హైదరాబాద్'},
        {'value': 'secunderabad', 'label_en': 'Secunderabad', 'label_te': 'సికింద్రాబాద్'},
        {'value': 'warangal', 'label_en': 'Warangal', 'label_te': 'వరంగల్'},
        {'value': 'nizamabad', 'label_en': 'Nizamabad', 'label_te': 'నిజామాబాద్'},
        {'value': 'khammam', 'label_en': 'Khammam', 'label_te': 'ఖమ్మం'},
        {'value': 'karimnagar', 'label_en': 'Karimnagar', 'label_te': 'కరీంనగర్'},
        {'value': 'mahbubnagar', 'label_en': 'Mahbubnagar', 'label_te': 'మహబూబ్‌నగర్'},
        {'value': 'nalgonda', 'label_en': 'Nalgonda', 'label_te': 'నల్గొండ'},
        {'value': 'adilabad', 'label_en': 'Adilabad', 'label_te': 'ఆదిలాబాద్'},
        {'value': 'medak', 'label_en': 'Medak', 'label_te': 'మేడక్'},
        {'value': 'ranga_reddy', 'label_en': 'Ranga Reddy', 'label_te': 'రంగా రెడ్డి'},
        {'value': 'sangareddy', 'label_en': 'Sangareddy', 'label_te': 'సంగారెడ్డి'}
    ]

def translate_text(text, target_lang='te'):
    """
    Placeholder for translation function
    In production, integrate with Google Translate API or similar
    
    Args:
        text: Text to translate
        target_lang: Target language code ('te' for Telugu, 'en' for English)
    
    Returns:
        Translated text
    """
    # For now, return original text
    # In production, implement actual translation
    return text

def format_currency(amount, currency='INR'):
    """Format amount as currency"""
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    return f"{amount:,.2f}"

def validate_phone(phone):
    """Validate Indian phone number"""
    phone = ''.join(filter(str.isdigit, phone))
    return len(phone) == 10 or (len(phone) == 12 and phone.startswith('91'))

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return text
    
    # Basic sanitization - remove potentially harmful characters
    dangerous_chars = ['<', '>', '"', "'", '/', '\\']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()
