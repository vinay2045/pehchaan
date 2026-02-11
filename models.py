from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt
import re

db = SQLAlchemy()

def slugify_username(username):
    """Convert username to lowercase and sanitize"""
    # Convert to lowercase
    slug = username.lower().strip()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^a-z0-9-]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Replace multiple consecutive hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    return slug

class User(UserMixin, db.Model):
    """User model for both Individual and Business accounts"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # 'individual' or 'business'
    
    # Profile fields
    full_name = db.Column(db.String(100), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    banner_image = db.Column(db.String(255), nullable=True)
    profile_tag = db.Column(db.String(32), nullable=True)
    tagline = db.Column(db.String(150), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    resume_pdf = db.Column(db.String(255), nullable=True)
    
    # Business-specific fields
    business_category = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    maps_embed = db.Column(db.Text, nullable=True)
    whatsapp_number = db.Column(db.String(15), nullable=True)
    
    # Soft delete
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    skills = db.relationship('Skill', backref='user', lazy=True, cascade='all, delete-orphan')
    social_links = db.relationship('SocialLink', backref='user', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan', order_by='Project.order')
    experiences = db.relationship('Experience', backref='user', lazy=True, cascade='all, delete-orphan', order_by='Experience.order')
    gallery_images = db.relationship('GalleryImage', backref='user', lazy=True, cascade='all, delete-orphan', order_by='GalleryImage.order')
    education = db.relationship('Education', backref='user', lazy=True, cascade='all, delete-orphan', order_by='Education.order')
    others = db.relationship('Other', backref='user', lazy=True, cascade='all, delete-orphan', order_by='Other.order')
    services = db.relationship('Service', backref='user', lazy=True, cascade='all, delete-orphan', order_by='Service.order')
    previous_works = db.relationship('PreviousWork', backref='user', lazy=True, cascade='all, delete-orphan', order_by='PreviousWork.order')
    
    def set_password(self, password):
        """Hash and set password using bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Skill(db.Model):
    """Skills/Tools for Individual users"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SocialLink(db.Model):
    """Social media links for users"""
    __tablename__ = 'social_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # 'twitter', 'linkedin', 'github', 'custom', etc.
    url = db.Column(db.String(255), nullable=False)
    label = db.Column(db.String(50), nullable=True)  # For custom links
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    """Projects for Individual users"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    live_demo_url = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    youtube_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def youtube_id(self):
        """Extract YouTube ID from URL"""
        if not self.youtube_url:
            return None
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None

    
    # Relationships
    images = db.relationship('ProjectImage', backref='project', lazy=True, cascade='all, delete-orphan', order_by='ProjectImage.order')
    links = db.relationship('ProjectLink', backref='project', lazy=True, cascade='all, delete-orphan', order_by='ProjectLink.order')

class ProjectLink(db.Model):
    """Proof links/Additional links for projects"""
    __tablename__ = 'project_links'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

    
    @property
    def display_order(self):
        """Alias for order for backward compatibility"""
        return self.order
    
    @display_order.setter
    def display_order(self, value):
        """Setter for display_order property"""
        self.order = value
    
    @property
    def demo_url(self):
        """Alias for live_demo_url for backward compatibility"""
        return self.live_demo_url
    
    @demo_url.setter
    def demo_url(self, value):
        """Setter for demo_url property"""
        self.live_demo_url = value
    
    @property
    def technologies(self):
        """Get technologies as string (placeholder for now)"""
        return getattr(self, '_technologies', '')
    
    @technologies.setter
    def technologies(self, value):
        """Set technologies string"""
        self._technologies = value

class ProjectImage(db.Model):
    """Multiple images for a project"""
    __tablename__ = 'project_images'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Experience(db.Model):
    """Experience/Work history for Individual users"""
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.String(50), nullable=True)  # e.g., "Jan 2020" or "2020-01"
    end_date = db.Column(db.String(50), nullable=True)    # or "Present"
    youtube_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def company(self):
        """Alias for company_name for template compatibility"""
        return self.company_name
    
    @property
    def role(self):
        """Alias for position for template compatibility"""
        return self.position
    
    @property
    def display_order(self):
        """Alias for order for template sorting"""
        return self.order
    
    @property
    def youtube_id(self):
        """Extract YouTube ID from URL"""
        if not self.youtube_url:
            return None
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None

    
    # Relationships
    images = db.relationship('ExperienceImage', backref='experience', lazy=True, cascade='all, delete-orphan', order_by='ExperienceImage.order')
    links = db.relationship('ExperienceLink', backref='experience', lazy=True, cascade='all, delete-orphan', order_by='ExperienceLink.order')

class ExperienceImage(db.Model):
    """Multiple images for experience"""
    __tablename__ = 'experience_images'
    
    id = db.Column(db.Integer, primary_key=True)
    experience_id = db.Column(db.Integer, db.ForeignKey('experiences.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExperienceLink(db.Model):
    """Proof links for experience"""
    __tablename__ = 'experience_links'
    
    id = db.Column(db.Integer, primary_key=True)
    experience_id = db.Column(db.Integer, db.ForeignKey('experiences.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

class Education(db.Model):
    """Education history for Individual users"""
    __tablename__ = 'education'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    institute_name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False) # e.g. BTech, MTech, School
    start_date = db.Column(db.String(50), nullable=True)
    end_date = db.Column(db.String(50), nullable=True)
    grade = db.Column(db.String(50), nullable=True) # Percentage or CGPA
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GalleryImage(db.Model):
    """Gallery images for users"""
    __tablename__ = 'gallery_images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Other(db.Model):
    """Achievements, certifications, custom items"""
    __tablename__ = 'others'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    achieved_date = db.Column(db.String(50), nullable=True)  # e.g., "2024" or "Jan 2024"
    youtube_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def youtube_id(self):
        """Extract YouTube ID from URL"""
        if not self.youtube_url:
            return None
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None

    
    # Relationships
    images = db.relationship('OtherImage', backref='other', lazy=True, cascade='all, delete-orphan', order_by='OtherImage.order')
    links = db.relationship('OtherLink', backref='other', lazy=True, cascade='all, delete-orphan', order_by='OtherLink.order')

class OtherImage(db.Model):
    """Multiple images for other items"""
    __tablename__ = 'other_images'
    
    id = db.Column(db.Integer, primary_key=True)
    other_id = db.Column(db.Integer, db.ForeignKey('others.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OtherLink(db.Model):
    """Links for other items"""
    __tablename__ = 'other_links'
    
    id = db.Column(db.Integer, primary_key=True)
    other_id = db.Column(db.Integer, db.ForeignKey('others.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

class Service(db.Model):
    """Services for Business users"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    price_range = db.Column(db.String(50), nullable=True)
    youtube_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def youtube_id(self):
        """Extract YouTube ID from URL"""
        if not self.youtube_url:
            return None
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None

    
    # Relationships
    images = db.relationship('ServiceImage', backref='service', lazy=True, cascade='all, delete-orphan', order_by='ServiceImage.order')

class ServiceImage(db.Model):
    """Multiple images for service"""
    __tablename__ = 'service_images'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PreviousWork(db.Model):
    """Previous work/portfolio for Business users"""
    __tablename__ = 'previous_works'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price_range = db.Column(db.String(50), nullable=True)
    youtube_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def youtube_id(self):
        """Extract YouTube ID from URL"""
        if not self.youtube_url:
            return None
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'embed\/([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None

    
    # Relationships
    images = db.relationship('PreviousWorkImage', backref='previous_work', lazy=True, cascade='all, delete-orphan', order_by='PreviousWorkImage.order')
    links = db.relationship('PreviousWorkLink', backref='previous_work', lazy=True, cascade='all, delete-orphan', order_by='PreviousWorkLink.order')

class PreviousWorkImage(db.Model):
    """Multiple images for previous work"""
    __tablename__ = 'previous_work_images'
    
    id = db.Column(db.Integer, primary_key=True)
    previous_work_id = db.Column(db.Integer, db.ForeignKey('previous_works.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PreviousWorkLink(db.Model):
    """Links for previous work"""
    __tablename__ = 'previous_work_links'
    
    id = db.Column(db.Integer, primary_key=True)
    previous_work_id = db.Column(db.Integer, db.ForeignKey('previous_works.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, default=0)

class Message(db.Model):
    """Contact form submissions"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Recipient
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
