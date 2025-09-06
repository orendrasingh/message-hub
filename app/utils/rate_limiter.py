"""
Rate limiting utilities
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def init_limiter(app):
    """Initialize rate limiter"""
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=app.config.get('RATELIMIT_DEFAULT', ["1000 per day", "200 per hour"]),
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    )
    return limiter
