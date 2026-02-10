import re
from wtforms.validators import ValidationError

def validate_youtube_url(url):
    """Extract YouTube video ID from URL"""
    if not url:
        return None
    
    # Patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def validate_phone_number(phone):
    """Validate phone number format (Indian + international)"""
    if not phone:
        return True  # Optional field
    
    # Remove spaces, hyphens, parentheses
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Indian format: 10 digits or +91 followed by 10 digits
    if re.match(r'^\+?91?[6-9]\d{9}$', clean_phone):
        return True
    
    # International format: + followed by 7-15 digits
    if re.match(r'^\+\d{7,15}$', clean_phone):
        return True
    
    return False

class YouTubeURL:
    """Custom validator for YouTube URLs"""
    def __init__(self, message=None):
        if not message:
            message = 'Invalid YouTube URL'
        self.message = message
    
    def __call__(self, form, field):
        if field.data:
            video_id = validate_youtube_url(field.data)
            if not video_id:
                raise ValidationError(self.message)

class PhoneNumber:
    """Custom validator for phone numbers"""
    def __init__(self, message=None):
        if not message:
            message = 'Invalid phone number format'
        self.message = message
    
    def __call__(self, form, field):
        if field.data:
            if not validate_phone_number(field.data):
                raise ValidationError(self.message)
