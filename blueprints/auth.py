from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from models import db, User, slugify_username
from blueprints.forms import IndividualSignupForm, BusinessSignupForm, LoginForm
from utils.qr_generator import generate_qr_code
from utils.security import check_username_availability
from app import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def signup():
    """Signup page for Individual and Business users"""
    individual_form = IndividualSignupForm()
    business_form = BusinessSignupForm()
    
    # Determine which form was submitted
    role = request.form.get('role', 'individual')
    
    if request.method == 'POST':
        if role == 'individual' and individual_form.validate_on_submit():
            # Process Individual signup
            username = slugify_username(individual_form.username.data)
            
            # Check username availability
            available, message = check_username_availability(username)
            if not available:
                flash(message, 'danger')
                return render_template('auth/signup.html', 
                                     individual_form=individual_form,
                                     business_form=business_form,
                                     active_tab='individual')
            
            # Check if email already exists
            if User.query.filter_by(email=individual_form.email.data).first():
                flash('This email is already registered. Please login or use a different email.', 'danger')
                return render_template('auth/signup.html',
                                     individual_form=individual_form,
                                     business_form=business_form,
                                     active_tab='individual')
            
            # Create new user
            user = User(
                email=individual_form.email.data,
                username=username,
                phone=individual_form.phone.data,
                role='individual'
            )
            user.set_password(individual_form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate QR code
            try:
                generate_qr_code(username)
            except Exception as e:
                print(f"Error generating QR code: {e}")
            
            # Auto-login user
            login_user(user)
            flash('Welcome to Pehchaan! Your account has been created.', 'success')
            return redirect(url_for('dashboard.index'))
        
        elif role == 'business' and business_form.validate_on_submit():
            # Process Business signup
            username = slugify_username(business_form.username.data)
            
            # Check username availability
            available, message = check_username_availability(username)
            if not available:
                flash(message, 'danger')
                return render_template('auth/signup.html',
                                     individual_form=individual_form,
                                     business_form=business_form,
                                     active_tab='business')
            
            # Determine if email or phone
            email_or_phone = business_form.email.data
            email = None
            phone = None
            
            if '@' in email_or_phone:
                email = email_or_phone
                # Check if email already exists
                if User.query.filter_by(email=email).first():
                    flash('This email is already registered. Please login or use a different email.', 'danger')
                    return render_template('auth/signup.html',
                                         individual_form=individual_form,
                                         business_form=business_form,
                                         active_tab='business')
            else:
                phone = email_or_phone
            
            # Create new user
            user = User(
                email=email,
                username=username,
                phone=phone or business_form.email.data,  # Fallback
                role='business',
                business_category=business_form.business_category.data,
                country=business_form.country.data,
                state=business_form.state.data,
                district=business_form.district.data
            )
            user.set_password(business_form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            # Generate QR code
            try:
                generate_qr_code(username)
            except Exception as e:
                print(f"Error generating QR code: {e}")
            
            # Auto-login user
            login_user(user)
            flash('Welcome to Pehchaan! Your business account has been created.', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            # Debug: Show form validation errors
            if role == 'business' and request.method == 'POST':
                for field, errors in business_form.errors.items():
                    for error in errors:
                        flash(f'{field}: {error}', 'danger')
    
    return render_template('auth/signup.html',
                         individual_form=individual_form,
                         business_form=business_form,
                         active_tab='individual')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per 15 minutes")
def login():
    """Login page"""
    form = LoginForm()
    
    if form.validate_on_submit():
        # Try to find user by email or username
        email_or_username = form.email_or_username.data
        user = User.query.filter(
            (User.email == email_or_username) |
            (User.username == email_or_username.lower())
        ).first()
        
        if user and user.check_password(form.password.data):
            # Check if account is soft-deleted
            if user.deleted_at:
                flash('This account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html', form=form)
            
            login_user(user)
            flash('Login successful! Welcome back.', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash('Invalid credentials. Please check your email/username and password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/check-username')
def check_username():
    """AJAX endpoint to check username availability"""
    username = request.args.get('username', '')
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    # Slugify username
    slugified = slugify_username(username)
    
    if not slugified or len(slugified) < 3:
        return jsonify({
            'available': False,
            'slugified': slugified,
            'message': 'Username must be at least 3 characters'
        })
    
    # Check availability
    available, message = check_username_availability(slugified)
    
    return jsonify({
        'available': available,
        'slugified': slugified,
        'message': message
    })
