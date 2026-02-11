from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL
from utils.validators import PhoneNumber, YouTubeURL

class IndividualSignupForm(FlaskForm):
    """Signup form for Individual users"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=30, message='Username must be between 3 and 30 characters')
    ])
    phone = StringField('Phone Number', validators=[
        DataRequired(message='Phone number is required'),
        PhoneNumber(message='Invalid phone number format')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    country = SelectField('Country', validators=[
        DataRequired(message='Country is required')
    ], choices=[
        ('', 'Select Country'),
        ('india', 'India')
    ])
    state = SelectField('State', 
        validators=[Optional()],
        choices=[('', 'Select State')],
        validate_choice=False  # Dynamically populated via JavaScript
    )
    district = SelectField('District',
        validators=[Optional()],
        choices=[('', 'Select District')],
        validate_choice=False  # Dynamically populated via JavaScript
    )

class BusinessSignupForm(FlaskForm):
    """Signup form for Business users"""
    email = StringField('Email or Phone', validators=[
        DataRequired(message='Email or phone is required')
    ])
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=30, message='Username must be between 3 and 30 characters')
    ])
    business_category = SelectField('Business Category', validators=[
        DataRequired(message='Business category is required')
    ], choices=[
        ('', 'Select Category'),
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurant'),
        ('cafe', 'Cafe'),
        ('grocery', 'Grocery Store'),
        ('electronics', 'Electronics Shop'),
        ('construction', 'Construction Company'),
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('pharmacy', 'Pharmacy'),
        ('salon', 'Salon'),
        ('spa', 'Spa'),
        ('clothing', 'Clothing Store'),
        ('jewelry', 'Jewelry Store'),
        ('coaching', 'Coaching Center'),
        ('school', 'School'),
        ('real_estate', 'Real Estate'),
        ('photography', 'Photography Studio'),
        ('event_management', 'Event Management'),
        ('consulting', 'Consulting Firm'),
        ('law_firm', 'Law Firm'),
        ('ca_firm', 'CA Firm'),
        ('gym', 'Gym'),
        ('fitness', 'Fitness Center'),
        ('automobile', 'Automobile Showroom'),
        ('printing', 'Printing Press'),
        ('stationery', 'Stationery Shop'),
        ('bakery', 'Bakery'),
        ('sweet_shop', 'Sweet Shop'),
        ('flower_shop', 'Flower Shop'),
        ('pet_shop', 'Pet Shop'),
        ('other', 'Other')
    ])
    country = SelectField('Country', validators=[
        DataRequired(message='Country is required')
    ], choices=[
        ('', 'Select Country'),
        ('india', 'India')
    ])
    state = SelectField('State', 
        validators=[Optional()],
        choices=[('', 'Select State')],
        validate_choice=False  # Dynamically populated via JavaScript
    )
    district = SelectField('District',
        validators=[Optional()],
        choices=[('', 'Select District')],
        validate_choice=False  # Dynamically populated via JavaScript
    )
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters')
    ])

class LoginForm(FlaskForm):
    """Login form for all users"""
    email_or_username = StringField('Email or Username', validators=[
        DataRequired(message='Email or username is required')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])

class ProfileEditForm(FlaskForm):
    """Edit profile form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(max=100)
    ])
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=30)
    ])
    profile_tag = StringField('Profile Tag', validators=[
        Optional(),
        Length(max=255)
    ])
    tagline = StringField('Tagline', validators=[
        Optional(),
        Length(max=150)
    ])
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=2000)
    ])
    # File uploads
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images allowed')
    ])
    banner_image = FileField('Banner Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images allowed')
    ])
    resume = FileField('Resume (PDF)', validators=[
        FileAllowed(['pdf'], 'Only PDF files allowed')
    ])

class ContactMessageForm(FlaskForm):
    """Contact form for public profiles"""
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(max=100)
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    phone = StringField('Phone', validators=[
        Optional(),
        PhoneNumber()
    ])
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required'),
        Length(max=200)
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(min=10, max=2000, message='Message must be between 10 and 2000 characters')
    ])
