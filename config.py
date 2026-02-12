import os
from datetime import timedelta

class Config:
    """Flask application configuration"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-immediately'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///pehchaan.db'
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Upload folder configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PROFILE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'profiles')
    BANNER_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners')
    RESUME_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'resumes')
    PROJECT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'projects')
    EXPERIENCE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'experience')
    GALLERY_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'gallery')
    OTHER_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'others')
    SERVICE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'services')
    PREVIOUS_WORK_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'previous_work')
    QR_CODE_FOLDER = os.path.join(BASE_DIR, 'static', 'qr_codes')
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max request size
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
    ALLOWED_RESUME_EXTENSIONS = {'pdf'}
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', 24)))
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTF/CSRF configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    WTF_CSRF_SSL_STRICT = False  # Set to True in production with HTTPS
    
    # Rate limiting configuration (Flask-Limiter)
    RATELIMIT_STORAGE_URL = 'memory://'  # Use Redis in production
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Reserved usernames (case-insensitive)
    RESERVED_USERNAMES = {
        'login', 'signup', 'logout', 'dashboard', 'admin', 'api',
        'static', 'uploads', 'about', 'contact', 'help', 'support',
        'terms', 'privacy', 'settings', 'profile', 'user', 'users',
        'public', 'app', 'dev', 'test', 'staging', 'production',
        'www', 'mail', 'ftp', 'blog', 'shop', 'store', 'account',
        'billing', 'pay', 'payment', 'subscribe', 'download',
        'cdn', 'assets', 'media', 'images', 'css', 'js', 'fonts',
        'root', 'administrator', 'moderator', 'guest', 'pehchaan'
    }
