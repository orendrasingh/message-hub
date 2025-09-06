"""
Error handlers for the application
"""

from flask import render_template, request, jsonify


def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.content_type == 'application/json':
            return jsonify({'error': 'Rate limit exceeded'}), 429
        return render_template('errors/429.html'), 429
