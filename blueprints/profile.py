from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import current_user
from models import db, User, Message
from blueprints.forms import ContactMessageForm
from app import limiter
import os
from config import Config

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/<username>')
def view_profile(username):
    """View public profile by username"""
    user = User.query.filter_by(username=username.lower()).first_or_404()
    
    # Check if account is soft-deleted
    if user.deleted_at:
        flash('This profile is not available.', 'warning')
        return redirect(url_for('main.index'))
    
    # Render appropriate template based on user role
    if user.role == 'individual':
        return render_template('public/individual_profile.html', user=user)
    else:
        return render_template('public/business_profile.html', user=user)

@profile_bp.after_request
def add_header(response):
    """Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@profile_bp.route('/<username>/contact', methods=['POST'])
@limiter.limit("3 per 15 minutes")
def contact(username):
    """Handle contact form submissions"""
    user = User.query.filter_by(username=username.lower()).first_or_404()
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    subject = request.form.get('subject')
    message_text = request.form.get('message')
    
    # Basic validation
    if not all([name, email, subject, message_text]):
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('profile.view_profile', username=username))
    
    # Create message
    message = Message(
        recipient_id=user.id,
        name=name,
        email=email,
        phone=phone,
        subject=subject,
        message=message_text
    )
    
    db.session.add(message)
    db.session.commit()
    
    flash('Your message has been sent successfully!', 'success')
    return redirect(url_for('profile.view_profile', username=username))

@profile_bp.route('/resume/<int:user_id>')
def download_resume(user_id):
    """Download user resume"""
    user = User.query.get_or_404(user_id)
    
    if not user.resume_pdf:
        flash('Resume not found.', 'warning')
        return redirect(url_for('profile.view_profile', username=user.username))
    
    # Build full path to resume
    resume_path = os.path.join(Config.UPLOAD_FOLDER, user.resume_pdf)
    
    if not os.path.exists(resume_path):
        flash('Resume file not found.', 'warning')
        return redirect(url_for('profile.view_profile', username=user.username))
    
    # Extract filename without path
    filename = os.path.basename(user.resume_pdf)
    
    return send_file(resume_path, as_attachment=True, download_name=f"{user.username}_resume.pdf")
