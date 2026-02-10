import re
from config import Config
from models import User
from datetime import datetime, timedelta

def is_reserved_username(username):
    """Check if username is in reserved list"""
    return username.lower() in Config.RESERVED_USERNAMES

def validate_username(username):
    """Validate username format and constraints"""
    if not username:
        return False, "Username is required"
    
    # Length check
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters"
    
    # Format check (alphanumeric + hyphens only)
    if not re.match(r'^[a-z0-9-]+$', username.lower()):
        return False, "Username can only contain lowercase letters, numbers, and hyphens"
    
    # Cannot start or end with hyphen
    if username.startswith('-') or username.endswith('-'):
        return False, "Username cannot start or end with a hyphen"
    
    # Cannot have consecutive hyphens
    if '--' in username:
        return False, "Username cannot have consecutive hyphens"
    
    # Reserved username check
    if is_reserved_username(username):
        return False, "This username is reserved"
    
    return True, "Username is valid"

def is_username_available(username):
    """Check if username is available (not taken and no soft-delete grace period)"""
    # Case-insensitive check
    existing_user = User.query.filter(User.username.ilike(username)).first()
    
    if not existing_user:
        return True
    
    # If user is soft-deleted, check grace period (30 days)
    if existing_user.deleted_at:
        grace_period = timedelta(days=30)
        if datetime.utcnow() - existing_user.deleted_at > grace_period:
            # Grace period expired, username can be reused
            return True
    
    return False

def check_username_availability(username):
    """Complete username validation and availability check"""
    # Format validation
    is_valid, message = validate_username(username)
    if not is_valid:
        return False, message
    
    # Availability check
    if not is_username_available(username):
        return False, "Username is already taken"
    
    return True, "Username is available"
