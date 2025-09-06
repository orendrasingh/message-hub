"""
Routes initialization
"""

from .auth import auth_bp
from .main import main_bp
from .contacts import contacts_bp
from .campaigns import campaigns_bp
from .api import api_bp

__all__ = [
    'auth_bp',
    'main_bp', 
    'contacts_bp',
    'campaigns_bp',
    'api_bp'
]
