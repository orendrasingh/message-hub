"""
Template context processors
"""

from flask import g, session
from app.utils.auth import get_current_user


def register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def inject_user():
        """Inject current user into templates"""
        return dict(current_user=get_current_user())
    
    @app.context_processor
    def inject_globals():
        """Inject global variables into templates"""
        return dict(
            app_name="WhatsApp Message Hub",
            app_version="1.0.0"
        )
