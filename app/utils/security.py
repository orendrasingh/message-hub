"""
Security utilities for safe redirects and validation
"""

import re
from typing import Optional
from urllib.parse import urlparse, urljoin
from flask import request, url_for


def is_safe_url(target: str) -> bool:
    """
    Check if a URL is safe for redirect (prevents open redirect attacks)
    """
    if not target:
        return False
    
    try:
        # Parse the target URL
        parsed = urlparse(target)
        
        # Only allow relative URLs or URLs on the same host
        if parsed.netloc and parsed.netloc != request.host:
            return False
        
        # Check for dangerous patterns
        if re.search(r'[<>"\']', target):
            return False
        
        # Must start with / for relative URLs
        if not target.startswith('/'):
            return False
        
        # Prevent javascript: and data: URLs
        if target.lower().startswith(('javascript:', 'data:', 'vbscript:')):
            return False
        
        return True
    except Exception:
        return False


def safe_redirect_url(target: Optional[str] = None, fallback_endpoint: str = 'main.dashboard') -> str:
    """
    Safely redirect to a target URL or fallback endpoint
    """
    if target and is_safe_url(target):
        return target
    
    # Fallback to safe endpoint
    return url_for(fallback_endpoint)