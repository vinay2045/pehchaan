from flask import Flask

from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from models import db, User
from config import Config
import os

# Initialize extensions
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "100 per hour"]
)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create upload directories
    upload_dirs = [
        Config.PROFILE_UPLOAD_FOLDER,
        Config.BANNER_UPLOAD_FOLDER,
        Config.RESUME_UPLOAD_FOLDER,
        Config.PROJECT_UPLOAD_FOLDER,
        Config.EXPERIENCE_UPLOAD_FOLDER,
        Config.GALLERY_UPLOAD_FOLDER,
        Config.OTHER_UPLOAD_FOLDER,
        Config.SERVICE_UPLOAD_FOLDER,
        Config.PREVIOUS_WORK_UPLOAD_FOLDER,
        Config.QR_CODE_FOLDER
    ]
    
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Register blueprints
    from blueprints.main import main_bp
    from blueprints.auth import auth_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.profile import profile_bp
    from blueprints.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
