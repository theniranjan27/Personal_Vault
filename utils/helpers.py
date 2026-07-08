import re
import uuid
import base64
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

def generate_id() -> str:
    return str(uuid.uuid4())

def sanitize_input(input_string: str, max_length: int = 5000) -> str:
    if not input_string:
        return ''
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', input_string)
    
    # Remove script tags content
    sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.DOTALL)
    
    # Remove extra whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Truncate if too long
    return sanitized[:max_length]

def format_datetime(dt: datetime, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    if not dt:
        return ''
    return dt.strftime(format)

def format_relative_time(dt: datetime) -> str:
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f'{years} year{"s" if years > 1 else ""} ago'
    elif diff.days > 30:
        months = diff.days // 30
        return f'{months} month{"s" if months > 1 else ""} ago'
    elif diff.days > 0:
        return f'{diff.days} day{"s" if diff.days > 1 else ""} ago'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    else:
        return 'Just now'

def mask_sensitive_value(value: str, visible_chars: int = 4, mask_char: str = 'x') -> str:
    if not value:
        return ''
    
    if len(value) <= visible_chars:
        return mask_char * len(value)
    
    visible_part = value[-visible_chars:]
    masked_part = mask_char * (len(value) - visible_chars)
    return masked_part + visible_part

def format_aadhaar(aadhaar: str) -> str:
    if not aadhaar:
        return ''
    cleaned = re.sub(r'[^0-9]', '', aadhaar)
    if len(cleaned) == 12:
        return f'{cleaned[0:4]}-{cleaned[4:8]}-{cleaned[8:12]}'
    return aadhaar

def format_pan(pan: str) -> str:
    if not pan:
        return ''
    pan = pan.upper()
    if len(pan) == 10:
        return f'{pan[0:5]}{pan[5:9]}{pan[9]}'
    return pan

def format_account_number(account: str, visible_chars: int = 4) -> str:
    if not account:
        return ''
    cleaned = re.sub(r'[^0-9]', '', account)
    if len(cleaned) <= visible_chars:
        return cleaned
    return 'x' * (len(cleaned) - visible_chars) + cleaned[-visible_chars:]

def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def base64_encode(data: str) -> str:
    return base64.b64encode(data.encode()).decode()

def base64_decode(data: str) -> str:
    return base64.b64decode(data.encode()).decode()

def is_valid_uuid(uuid_string: str) -> bool:
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix

def extract_tags(text: str) -> list:
    if not text:
        return []
    tags = re.findall(r'#(\w+)', text)
    return list(set(tags))

def get_file_extension(filename: str) -> str:
    if not filename:
        return ''
    parts = filename.rsplit('.', 1)
    return parts[-1].lower() if len(parts) > 1 else ''

def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    ext = get_file_extension(filename)
    return ext in allowed_extensions

def dict_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = dict_merge(result[key], value)
        else:
            result[key] = value
    return result