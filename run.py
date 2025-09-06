"""
Main application runner for WhatsApp Message Hub
"""

import os
from app import create_app
from app.models import init_database

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        init_database(app.config['DB_PATH'])
    
    # Run application
    debug_mode = app.config.get('DEBUG', False)
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5001))
    
    print(f"Starting WhatsApp Message Hub on {host}:{port}")
    print(f"Debug mode: {debug_mode}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(debug=debug_mode, host=host, port=port)
