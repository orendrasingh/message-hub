"""
Error handlers for the application
"""

from flask import render_template, request, jsonify, current_app
import traceback
import logging


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log the actual error for debugging (but don't expose to user)
        current_app.logger.error(f"Internal Server Error: {str(error)}")
        current_app.logger.error(f"Request URL: {request.url}")
        current_app.logger.error(f"Request Method: {request.method}")
        current_app.logger.error(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        current_app.logger.error(f"IP Address: {request.remote_addr}")
        
        # In debug mode, show detailed error; in production, show generic message
        if app.debug:
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        if request.content_type == 'application/json':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        # Log security-related 403 errors
        current_app.logger.warning(f"403 Forbidden: {request.url} - IP: {request.remote_addr}")
        
        if request.content_type == 'application/json':
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        # Log rate limiting events
        current_app.logger.warning(f"Rate limit exceeded: {request.url} - IP: {request.remote_addr}")
        
        if request.content_type == 'application/json':
            return jsonify({'error': 'Rate limit exceeded', 'retry_after': str(e.retry_after)}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Catch all unhandled exceptions"""
        # Log the exception with full details
        current_app.logger.error(f"Unhandled Exception: {str(e)}")
        current_app.logger.error(f"Request URL: {request.url}")
        current_app.logger.error(f"Request Method: {request.method}")
        current_app.logger.error(f"IP Address: {request.remote_addr}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return generic error to user (never expose internal details)
        if request.content_type == 'application/json':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
