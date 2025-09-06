"""
WhatsApp Message Hub - A Flask application for managing WhatsApp campaigns
"""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os


def create_app(config_name=None):
    """Application factory pattern"""
    
    # Load environment variables
    load_dotenv()
    
    # Get the correct template and static directories
    import os
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    # Create Flask app with correct paths
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import config
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register context processors
    _register_context_processors(app)
    
    # Add security headers
    _add_security_headers(app)
    
    return app


def _init_extensions(app):
    """Initialize Flask extensions"""
    # Note: Rate limiter is initialized in individual route files
    # to avoid circular import issues
    pass


def _register_blueprints(app):
    """Register application blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.contacts import contacts_bp
    from app.routes.campaigns import campaigns_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(contacts_bp, url_prefix='/contacts')
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    app.register_blueprint(api_bp, url_prefix='/api')


def _register_error_handlers(app):
    """Register error handlers"""
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)


def _register_context_processors(app):
    """Register template context processors"""
    from app.utils.context_processors import register_context_processors
    register_context_processors(app)


def _add_security_headers(app):
    """Add security headers"""
    @app.after_request
    def add_security_headers(response):
        if hasattr(app.config, 'SECURITY_HEADERS'):
            for header, value in app.config['SECURITY_HEADERS'].items():
                response.headers[header] = value
        return response
