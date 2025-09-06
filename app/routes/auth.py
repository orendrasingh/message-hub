"""
Authentication routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from datetime import timedelta

from app.models import DatabaseManager
from app.services.auth import AuthService
from app.services.email import EmailService
from app.utils.auth import anonymous_required, get_current_user
from app.utils.validators import validate_email, validate_password, sanitize_input

auth_bp = Blueprint('auth', __name__)


def get_services():
    """Get service instances"""
    db_manager = DatabaseManager(current_app.config['DB_PATH'])
    auth_service = AuthService(
        db_manager,
        current_app.config['EVOLUTION_API_URL'], 
        current_app.config['EVOLUTION_GLOBAL_KEY']
    )
    email_service = EmailService(
        current_app.config['SMTP_SERVER'],
        current_app.config['SMTP_PORT'],
        current_app.config['EMAIL_ADDRESS'],
        current_app.config['EMAIL_PASSWORD']
    )
    return auth_service, email_service


@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    """User login"""
    if request.method == 'POST':
        email = sanitize_input(request.form.get('username', ''))  # Form uses 'username' field
        password = request.form.get('password', '')
        remember = request.form.get('remember_me') == 'on'
        
        # Validation
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('login.html')
        
        # Authenticate user
        auth_service, _ = get_services()
        user = auth_service.authenticate_user(email, password)
        
        if user:
            # Create session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['evolution_instance_name'] = user.evolution_instance_name
            session['evolution_api_key'] = user.evolution_api_key
            
            # Set session expiry
            if remember:
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False
                current_app.permanent_session_lifetime = timedelta(hours=24)
            
            # Create session record
            auth_service.create_session(user.id, remember)
            
            flash('Login successful!', 'success')
            
            # Redirect based on setup status
            if not user.instance_created:
                return redirect(url_for('main.setup_whatsapp'))
            elif not user.whatsapp_connected:
                return redirect(url_for('main.connect_whatsapp'))
            else:
                # Check for next parameter
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    """User registration"""
    if request.method == 'POST':
        first_name = sanitize_input(request.form.get('first_name', '').strip())
        last_name = sanitize_input(request.form.get('last_name', '').strip())
        username = sanitize_input(request.form.get('username', '').strip())
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Determine name
        if first_name or last_name:
            name = f"{first_name} {last_name}".strip()
        else:
            name = username
        
        # Validation
        if not name:
            flash('Please provide your name or username', 'error')
            return render_template('register.html')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        password_validation = validate_password(password)
        if not password_validation['valid']:
            for error in password_validation['errors']:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create user
        auth_service, email_service = get_services()
        result = auth_service.create_user(name, email, password)
        
        if result['success']:
            # Send welcome email (optional, don't fail if it doesn't work)
            try:
                email_service.send_welcome_email(email, name)
            except Exception as e:
                print(f"Failed to send welcome email: {e}")
            
            flash('Registration successful! Please login and setup your WhatsApp connection.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Registration failed: {result["error"]}', 'error')
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    if 'user_id' in session:
        auth_service, _ = get_services()
        auth_service.delete_session(session['user_id'])
    
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@anonymous_required
def forgot_password():
    """Forgot password"""
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', ''))
        
        if not email:
            flash('Email is required', 'error')
            return render_template('forgot_password.html')
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return render_template('forgot_password.html')
        
        auth_service, email_service = get_services()
        user = auth_service.get_user_by_email(email)
        
        if user:
            token = auth_service.create_reset_token(user.id)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            result = email_service.send_password_reset(email, reset_url)
            if result['success']:
                flash('Password reset email sent! Check your inbox.', 'success')
            else:
                flash('Failed to send reset email. Please try again.', 'error')
        else:
            # Don't reveal if email exists
            flash('If the email exists, a reset link has been sent.', 'info')
        
        return redirect(url_for('auth.forgot_password'))
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@anonymous_required
def reset_password(token):
    """Reset password with token"""
    auth_service, _ = get_services()
    user_id = auth_service.verify_reset_token(token)
    
    if not user_id:
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        password_validation = validate_password(password)
        if not password_validation['valid']:
            for error in password_validation['errors']:
                flash(error, 'error')
            return render_template('reset_password.html', token=token)
        
        if auth_service.update_password(user_id, password):
            auth_service.mark_reset_token_used(token)
            flash('Password updated successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Failed to update password. Please try again.', 'error')
    
    return render_template('reset_password.html', token=token)
