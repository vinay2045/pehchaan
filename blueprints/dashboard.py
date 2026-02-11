from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User
from blueprints.forms import ProfileEditForm

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard - redirect to profile"""
    return redirect(url_for('dashboard.profile'))

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Edit profile page"""
    from utils.file_handler import handle_file_upload, delete_file
    from utils.security import check_username_availability
    from utils.qr_generator import generate_qr_code
    from models import slugify_username, Skill, SocialLink
    
    form = ProfileEditForm()
    
    if form.validate_on_submit():
        print(f"DEBUG: Profile Update Form Valid. Data: {form.data}")
        # Handle file uploads first
        if form.profile_image.data:
            if current_user.profile_image:
                delete_file(current_user.profile_image)
            filename = handle_file_upload(form.profile_image.data, 'profiles', max_size=5*1024*1024)
            if filename:
                current_user.profile_image = filename
        
        if form.banner_image.data:
            if current_user.banner_image:
                delete_file(current_user.banner_image)
            filename = handle_file_upload(form.banner_image.data, 'banners', max_size=5*1024*1024)
            if filename:
                current_user.banner_image = filename
        
        if form.resume.data:
            if current_user.resume_pdf:
                delete_file(current_user.resume_pdf)
            filename = handle_file_upload(form.resume.data, 'resumes', max_size=10*1024*1024)
            if filename:
                current_user.resume_pdf = filename
        
        # Update text fields
        current_user.full_name = form.full_name.data
        current_user.profile_tag = form.profile_tag.data
        current_user.tagline = form.tagline.data
        current_user.bio = form.bio.data
        
        # Handle skills for Individual users
        if current_user.role == 'individual':
            # Update skills - delete all and recreate
            Skill.query.filter_by(user_id=current_user.id).delete()
            skills_str = request.form.get('skills', '')
            if skills_str:
                for idx, skill_name in enumerate(skills_str.split(',')):
                    skill_name = skill_name.strip()
                    if skill_name:
                        skill = Skill(user_id=current_user.id, name=skill_name, order=idx)
                        db.session.add(skill)
            
            # Update social links - delete all and recreate
            SocialLink.query.filter_by(user_id=current_user.id).delete()
            idx = 0
            while f'social_platform_{idx}' in request.form:
                platform = request.form.get(f'social_platform_{idx}')
                url = request.form.get(f'social_url_{idx}')
                if platform and url:
                    link = SocialLink(user_id=current_user.id, platform=platform, url=url, order=idx)
                    db.session.add(link)
                idx += 1
        
        # Handle username change
        new_username = slugify_username(form.username.data)
        if new_username != current_user.username:
            available, message = check_username_availability(new_username)
            if available:
                current_user.username = new_username
                try:
                    generate_qr_code(new_username)
                except Exception as e:
                    print(f"Error regenerating QR code: {e}")
            else:
                flash(message, 'danger')
                return render_template('dashboard/profile.html', form=form)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.profile'))
    
    # Pre-fill form
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.username.data = current_user.username
        form.profile_tag.data = current_user.profile_tag
        form.tagline.data = current_user.tagline
        form.bio.data = current_user.bio
    
    if form.errors:
        print(f"DEBUG: Profile Form Errors: {form.errors}")
    
    return render_template('dashboard/profile.html', form=form)

# PROJECTS CRUD
@dashboard_bp.route('/projects')
@login_required
def projects():
    from models import Project
    from sqlalchemy.orm import joinedload
    if current_user.role != 'individual':
        flash('This section is only for Individual accounts.', 'warning')
        return redirect(url_for('dashboard.index'))
    projects = Project.query.filter_by(user_id=current_user.id).options(
        joinedload(Project.images),
        joinedload(Project.links)
    ).order_by(Project.order).all()
    return render_template('dashboard/projects.html', projects=projects)

@dashboard_bp.route('/projects/add', methods=['POST'])
@login_required
def add_project():
    from models import Project, ProjectImage
    from utils.file_handler import handle_file_upload
    
    project = Project(
        user_id=current_user.id,
        title=request.form.get('title'),
        description=request.form.get('description'),
        live_demo_url=request.form.get('demo_url'),
        github_url=request.form.get('github_url'),
        youtube_url=request.form.get('youtube_url')
    )
    
    # Store technologies as attribute (will be added to model later)
    technologies = request.form.get('technologies')
    if technologies:
        project._technologies = technologies
    
    db.session.add(project)
    db.session.commit()
    
    # Handle media: YouTube OR Image
    youtube_url = request.form.get('youtube_url')
    
    if youtube_url:
        project.youtube_url = youtube_url
        # Ignore images if YouTube URL is present
    else:
        project.youtube_url = None
        # Handle single image
        image = request.files.get('images') # Single file input
        if image and image.filename:
            filename = handle_file_upload(image, 'projects', max_size=5*1024*1024)
            if filename:
                db.session.add(ProjectImage(project_id=project.id, image_path=filename))
    
    db.session.commit()
    flash('Project added successfully!', 'success')
    return redirect(url_for('dashboard.projects'))

@dashboard_bp.route('/projects/<int:project_id>')
@login_required
def get_project(project_id):
    from models import Project
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': project.id,
        'title': project.title,
        'description': project.description,
        'demo_url': project.live_demo_url or '',
        'github_url': project.github_url or '',
        'youtube_url': project.youtube_url or '',
        'technologies': getattr(project, '_technologies', '') or ''
    })

@dashboard_bp.route('/projects/edit', methods=['POST'])
@login_required
def edit_project():
    from models import Project, ProjectImage
    from utils.file_handler import handle_file_upload
    
    project_id = request.form.get('project_id')
    print(f"DEBUG: Editing Project ID: {project_id}")
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    project.title = request.form.get('title')
    project.description = request.form.get('description')
    project.live_demo_url = request.form.get('demo_url')
    project.github_url = request.form.get('github_url')
    project.youtube_url = request.form.get('youtube_url')
    
    # Store technologies
    technologies = request.form.get('technologies')
    if technologies:
        project._technologies = technologies
    
    # Handle media: YouTube OR Image
    youtube_url = request.form.get('youtube_url')
    
    if youtube_url:
        project.youtube_url = youtube_url
        # Remove existing images if switching to YouTube
        for img in project.images:
            from utils.file_handler import delete_file
            delete_file(img.image_path)
            db.session.delete(img)
    else:
        project.youtube_url = None
        # Handle new image upload
        image = request.files.get('images')
        if image and image.filename:
            # Remove existing images to enforce single image policy
            for img in project.images:
                from utils.file_handler import delete_file
                delete_file(img.image_path)
                db.session.delete(img)
            
            # Save new image
            filename = handle_file_upload(image, 'projects', max_size=5*1024*1024)
            if filename:
                db.session.add(ProjectImage(project_id=project.id, image_path=filename))
    
    db.session.commit()
    flash('Project updated successfully!', 'success')
    return redirect(url_for('dashboard.projects'))

@dashboard_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    from models import Project
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True})

# OTHER ROUTES
@dashboard_bp.route('/experience')
@login_required
def experience():
    from models import Experience
    from sqlalchemy.orm import joinedload
    if current_user.role != 'individual':
        flash('This section is only for Individual accounts.', 'warning')
        return redirect(url_for('dashboard.index'))
    experiences = Experience.query.filter_by(user_id=current_user.id).options(
        joinedload(Experience.images),
        joinedload(Experience.links)
    ).order_by(Experience.order).all()
    return render_template('dashboard/experience.html', experiences=experiences)

@dashboard_bp.route('/experience/add', methods=['POST'])
@login_required
def add_experience():
    from models import Experience, ExperienceImage, ExperienceLink
    from utils.file_handler import handle_file_upload
    
    exp = Experience(
        user_id=current_user.id,
        company_name=request.form.get('company_name'),
        position=request.form.get('position'),
        description=request.form.get('description'),
        start_date=request.form.get('start_date'),
        end_date=request.form.get('end_date') or 'Present'
        # youtube_url removed per user request
    )
    
    db.session.add(exp)
    db.session.commit()
    
    # Images removed per user request
    # images = request.files.getlist('images') ...
    
    # Handle proof links
    idx = 0
    while f'link_label_{idx}' in request.form:
        label = request.form.get(f'link_label_{idx}')
        url = request.form.get(f'link_url_{idx}')
        if label and url:
            db.session.add(ExperienceLink(experience_id=exp.id, label=label, url=url, order=idx))
        idx += 1
    
    db.session.commit()
    flash('Experience added successfully!', 'success')
    return redirect(url_for('dashboard.experience'))

@dashboard_bp.route('/experience/<int:exp_id>')
@login_required
def get_experience(exp_id):
    from models import Experience
    exp = Experience.query.filter_by(id=exp_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': exp.id,
        'company_name': exp.company_name,
        'position': exp.position,
        'description': exp.description or '',
        'start_date': exp.start_date or '',
        'end_date': exp.end_date or 'Present',
        'youtube_url': exp.youtube_url or '',
        'links': [{'label': link.label, 'url': link.url} for link in exp.links]
    })

@dashboard_bp.route('/experience/edit', methods=['POST'])
@login_required
def edit_experience():
    from models import Experience, ExperienceImage, ExperienceLink
    from utils.file_handler import handle_file_upload
    
    exp_id = request.form.get('exp_id')
    print(f"DEBUG: Editing Experience ID: {exp_id}")
    exp = Experience.query.filter_by(id=exp_id, user_id=current_user.id).first_or_404()
    
    exp.company_name = request.form.get('company_name')
    exp.position = request.form.get('position')
    exp.description = request.form.get('description')
    exp.start_date = request.form.get('start_date')
    exp.end_date = request.form.get('end_date') or 'Present'
    # exp.youtube_url removed
    
    # Images removed per user request
    
    # Update proof links - delete all and recreate
    ExperienceLink.query.filter_by(experience_id=exp.id).delete()
    idx = 0
    while f'link_label_{idx}' in request.form:
        label = request.form.get(f'link_label_{idx}')
        url = request.form.get(f'link_url_{idx}')
        if label and url:
            db.session.add(ExperienceLink(experience_id=exp.id, label=label, url=url, order=idx))
        idx += 1
    
    db.session.commit()
    flash('Experience updated successfully!', 'success')
    return redirect(url_for('dashboard.experience'))

@dashboard_bp.route('/experience/<int:exp_id>/delete', methods=['POST'])
@login_required
def delete_experience(exp_id):
    from models import Experience
    exp = Experience.query.filter_by(id=exp_id, user_id=current_user.id).first_or_404()
    db.session.delete(exp)
    db.session.commit()
    return jsonify({'success': True})

    db.session.commit()
    return jsonify({'success': True})

@dashboard_bp.route('/education')
@login_required
def education():
    from models import Education
    if current_user.role != 'individual':
        flash('This section is only for Individual accounts.', 'warning')
        return redirect(url_for('dashboard.index'))
    education_items = Education.query.filter_by(user_id=current_user.id).order_by(Education.order).all()
    return render_template('dashboard/education.html', education_items=education_items)

@dashboard_bp.route('/education/add', methods=['POST'])
@login_required
def add_education():
    from models import Education
    
    edu = Education(
        user_id=current_user.id,
        institute_name=request.form.get('institute_name'),
        course=request.form.get('course'),
        start_date=request.form.get('start_date'),
        end_date=request.form.get('end_date') or 'Present',
        grade=request.form.get('grade'),
        description=request.form.get('description')
    )
    
    db.session.add(edu)
    db.session.commit()
    
    flash('Education added successfully!', 'success')
    return redirect(url_for('dashboard.education'))

@dashboard_bp.route('/education/<int:edu_id>')
@login_required
def get_education(edu_id):
    from models import Education
    edu = Education.query.filter_by(id=edu_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': edu.id,
        'institute_name': edu.institute_name,
        'course': edu.course,
        'start_date': edu.start_date or '',
        'end_date': edu.end_date or 'Present',
        'grade': edu.grade or '',
        'description': edu.description or ''
    })

@dashboard_bp.route('/education/edit', methods=['POST'])
@login_required
def edit_education():
    from models import Education
    
    edu_id = request.form.get('edu_id')
    print(f"DEBUG: Editing Education ID: {edu_id}")
    print(f"DEBUG: Form Data: {request.form}")
    
    edu = Education.query.filter_by(id=edu_id, user_id=current_user.id).first_or_404()
    print(f"DEBUG: Found Education Object: {edu}")
    
    edu.institute_name = request.form.get('institute_name')
    edu.course = request.form.get('course')
    edu.start_date = request.form.get('start_date')
    edu.end_date = request.form.get('end_date') or 'Present'
    edu.grade = request.form.get('grade')
    edu.description = request.form.get('description')
    
    db.session.commit()
    flash('Education updated successfully!', 'success')
    return redirect(url_for('dashboard.education'))

@dashboard_bp.route('/education/<int:edu_id>/delete', methods=['POST'])
@login_required
def delete_education(edu_id):
    from models import Education
    edu = Education.query.filter_by(id=edu_id, user_id=current_user.id).first_or_404()
    db.session.delete(edu)
    db.session.commit()
    return jsonify({'success': True})

@dashboard_bp.route('/gallery')
@login_required
def gallery():
    from models import GalleryImage
    images = GalleryImage.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/gallery.html', images=images)

@dashboard_bp.route('/gallery/upload', methods=['POST'])
@login_required
def upload_gallery_image():
    from models import GalleryImage
    from utils.file_handler import handle_file_upload
    
    images = request.files.getlist('images')
    for img in images:
        if img and img.filename:
            filename = handle_file_upload(img, 'gallery', max_size=5*1024*1024)
            if filename:
                db.session.add(GalleryImage(user_id=current_user.id, image_path=filename))
    
    db.session.commit()
    flash('Images uploaded successfully!', 'success')
    return redirect(url_for('dashboard.gallery'))

@dashboard_bp.route('/gallery/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_gallery_image(image_id):
    from models import GalleryImage
    from utils.file_handler import delete_file
    
    image = GalleryImage.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    delete_file(image.image_path)
    db.session.delete(image)
    db.session.commit()
    return jsonify({'success': True})

@dashboard_bp.route('/others')
@login_required
def others():
    from models import Other
    from sqlalchemy.orm import joinedload
    items = Other.query.filter_by(user_id=current_user.id).options(
        joinedload(Other.images),
        joinedload(Other.links)
    ).order_by(Other.order).all()
    return render_template('dashboard/others.html', items=items)

@dashboard_bp.route('/others/add', methods=['POST'])
@login_required
def add_other():
    from models import Other, OtherImage, OtherLink
    from utils.file_handler import handle_file_upload
    
    item = Other(
        user_id=current_user.id,
        title=request.form.get('title'),
        description=request.form.get('description'),
        achieved_date=request.form.get('achieved_date'),
        youtube_url=request.form.get('youtube_url')
    )
    
    db.session.add(item)
    db.session.commit()
    
    # Handle media: YouTube OR Image
    youtube_url = request.form.get('youtube_url')
    
    if youtube_url:
        item.youtube_url = youtube_url
    else:
        item.youtube_url = None
        # Handle single image
        image = request.files.get('images')
        if image and image.filename:
            filename = handle_file_upload(image, 'others', max_size=5*1024*1024)
            if filename:
                db.session.add(OtherImage(other_id=item.id, image_path=filename))
    
    # Handle proof links
    idx = 0
    while f'link_label_{idx}' in request.form:
        label = request.form.get(f'link_label_{idx}')
        url = request.form.get(f'link_url_{idx}')
        if label and url:
            db.session.add(OtherLink(other_id=item.id, label=label, url=url, order=idx))
        idx += 1
    
    db.session.commit()
    flash('Achievement added successfully!', 'success')
    return redirect(url_for('dashboard.others'))

@dashboard_bp.route('/others/<int:item_id>')
@login_required
def get_other(item_id):
    from models import Other
    item = Other.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': item.id,
        'title': item.title,
        'description': item.description or '',
        'achieved_date': item.achieved_date or '',
        'youtube_url': item.youtube_url or '',
        'links': [{'label': link.label, 'url': link.url} for link in item.links]
    })

@dashboard_bp.route('/others/edit', methods=['POST'])
@login_required
def edit_other():
    from models import Other, OtherImage, OtherLink
    from utils.file_handler import handle_file_upload
    
    item_id = request.form.get('item_id')
    print(f"DEBUG: Editing Other ID: {item_id}")
    item = Other.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    item.title = request.form.get('title')
    item.description = request.form.get('description')
    item.achieved_date = request.form.get('achieved_date')
    item.youtube_url = request.form.get('youtube_url')
    
    # Handle media: YouTube OR Image
    youtube_url = request.form.get('youtube_url')
    
    if youtube_url:
        item.youtube_url = youtube_url
        # Remove existing images if switching to YouTube
        for img in item.images:
            from utils.file_handler import delete_file
            delete_file(img.image_path)
            db.session.delete(img)
    else:
        item.youtube_url = None
        # Handle new image upload
        image = request.files.get('images')
        if image and image.filename:
            # Remove existing images to enforce single image policy
            for img in item.images:
                from utils.file_handler import delete_file
                delete_file(img.image_path)
                db.session.delete(img)
            
            # Save new image
            filename = handle_file_upload(image, 'others', max_size=5*1024*1024)
            if filename:
                db.session.add(OtherImage(other_id=item.id, image_path=filename))
    
    # Update proof links - delete all and recreate
    OtherLink.query.filter_by(other_id=item.id).delete()
    idx = 0
    while f'link_label_{idx}' in request.form:
        label = request.form.get(f'link_label_{idx}')
        url = request.form.get(f'link_url_{idx}')
        if label and url:
            db.session.add(OtherLink(other_id=item.id, label=label, url=url, order=idx))
        idx += 1
    
    db.session.commit()
    flash('Achievement updated successfully!', 'success')
    return redirect(url_for('dashboard.others'))

@dashboard_bp.route('/others/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_other(item_id):
    from models import Other
    item = Other.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@dashboard_bp.route('/messages')
@login_required
def messages():
    from models import Message
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    return render_template('dashboard/messages.html', messages=messages)

@dashboard_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    from models import Message
    message = Message.query.filter_by(id=message_id, recipient_id=current_user.id).first_or_404()
    message.is_read = True
    db.session.commit()
    return jsonify({'success': True})

@dashboard_bp.route('/services')
@login_required
def services():
    if current_user.role != 'business':
        flash('This section is only for Business accounts.', 'warning')
        return redirect(url_for('dashboard.index'))
    return render_template('dashboard/services.html')

@dashboard_bp.route('/previous-work')
@login_required
def previous_work():
    if current_user.role != 'business':
        flash('This section is only for Business accounts.', 'warning')
        return redirect(url_for('dashboard.index'))
    return render_template('dashboard/previous_work.html')
