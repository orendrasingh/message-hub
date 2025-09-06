"""
Authentication decorators and utilities
"""

from functools import wraps
from flask import session, redirect, url_for, request, current_app
from app.models import DatabaseManager
from app.services.auth import AuthService


def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Decorator to require user NOT to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current user from session"""
    if 'user_id' in session:
        # Initialize services
        db_manager = DatabaseManager(current_app.config['DB_PATH'])
        auth_service = AuthService(
            db_manager,
            current_app.config['EVOLUTION_API_URL'],
            current_app.config['EVOLUTION_GLOBAL_KEY']
        )
        return auth_service.get_user_by_id(session['user_id'])
    return None


def whatsapp_setup_required(f):
    """Decorator to require WhatsApp setup"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))
        
        if not user.instance_created:
            return redirect(url_for('main.setup_whatsapp'))
        elif not user.whatsapp_connected:
            return redirect(url_for('main.connect_whatsapp'))
        
        return f(*args, **kwargs)
    return decorated_function
