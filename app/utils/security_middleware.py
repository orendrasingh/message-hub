"""
Security middleware and additional security measures
"""

from flask import request, g, current_app
import time
from functools import wraps
from typing import Dict, Any


class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Security checks before each request"""
        g.start_time = time.time()
        
        # Basic rate limiting checks
        self._check_request_size()
        self._validate_user_agent()
    
    def after_request(self, response):
        """Security headers and cleanup after each request"""
        # Add security headers if not in production config
        if not hasattr(current_app.config, 'SECURITY_HEADERS'):
            self._add_default_security_headers(response)
        
        # Log suspicious requests
        self._log_suspicious_activity()
        
        return response
    
    def _check_request_size(self):
        """Check request size to prevent DoS"""
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
        if request.content_length and request.content_length > max_size:
            from flask import abort
            abort(413)  # Request Entity Too Large
    
    def _validate_user_agent(self):
        """Basic user agent validation"""
        user_agent = request.headers.get('User-Agent', '')
        
        # Block obviously malicious user agents
        suspicious_patterns = [
            'sqlmap', 'nikto', 'nmap', 'masscan', 'nessus',
            'burp', 'acunetix', 'appscan', 'w3af'
        ]
        
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            current_app.logger.warning(f"Suspicious user agent detected: {user_agent} from {request.remote_addr}")
            from flask import abort
            abort(403)
    
    def _add_default_security_headers(self, response):
        """Add default security headers"""
        default_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        for header, value in default_headers.items():
            if header not in response.headers:
                response.headers[header] = value
    
    def _log_suspicious_activity(self):
        """Log potentially suspicious activity"""
        # Log slow requests
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            if duration > 10:  # Requests taking more than 10 seconds
                current_app.logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.2f}s from {request.remote_addr}"
                )


def require_api_key(f):
    """Decorator to require API key for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            from flask import jsonify
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key (implement your own validation logic)
        if not _validate_api_key(api_key):
            from flask import jsonify
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def _validate_api_key(api_key: str) -> bool:
    """Validate API key - implement your own logic"""
    # This is a placeholder - implement proper API key validation
    # You might want to store API keys in database with proper hashing
    return len(api_key) >= 32  # Basic validation


def log_security_event(event_type: str, details: Dict[str, Any]):
    """Log security events for monitoring"""
    current_app.logger.warning(
        f"Security Event: {event_type} - "
        f"IP: {request.remote_addr} - "
        f"User-Agent: {request.headers.get('User-Agent', 'Unknown')} - "
        f"Details: {details}"
    )


def detect_sql_injection(input_string: str) -> bool:
    """Basic SQL injection pattern detection"""
    if not input_string:
        return False
    
    # Common SQL injection patterns
    sql_patterns = [
        r"union\s+select", r"or\s+1\s*=\s*1", r"drop\s+table",
        r"insert\s+into", r"delete\s+from", r"update\s+set",
        r"exec\s*\(", r"execute\s*\(", r"sp_", r"xp_",
        r"--", r"/\*", r"\*/", r"char\s*\(", r"nchar\s*\(",
        r"varchar\s*\(", r"nvarchar\s*\(", r"alter\s+table",
        r"create\s+table", r"drop\s+database", r"backup\s+database"
    ]
    
    input_lower = input_string.lower()
    for pattern in sql_patterns:
        if re.search(pattern, input_lower):
            return True
    
    return False


def detect_xss_attempt(input_string: str) -> bool:
    """Basic XSS attempt detection"""
    if not input_string:
        return False
    
    # Common XSS patterns
    xss_patterns = [
        r"<script", r"javascript:", r"vbscript:", r"onload\s*=",
        r"onerror\s*=", r"onmouseover\s*=", r"onclick\s*=",
        r"onfocus\s*=", r"onblur\s*=", r"onchange\s*=",
        r"onsubmit\s*=", r"onkeyup\s*=", r"onkeydown\s*=",
        r"alert\s*\(", r"confirm\s*\(", r"prompt\s*\(",
        r"document\s*\.", r"window\s*\.", r"eval\s*\("
    ]
    
    input_lower = input_string.lower()
    for pattern in xss_patterns:
        if re.search(pattern, input_lower):
            return True
    
    return False


import re
