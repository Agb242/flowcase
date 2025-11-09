#!/usr/bin/env python
"""
Development startup script for Flowcase/Nalabo
This script starts the Flask app directly without gunicorn for easier debugging
"""

import os
import sys
from __init__ import create_app, initialize_database_and_setup

# Set development environment
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Configuration for development
config = {
    'DEBUG': True,
    'TESTING': False,
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
}

# Create the Flask app
app = create_app(config)

# Initialize database and setup
with app.app_context():
    print("🚀 Initializing database and setup...")
    initialize_database_and_setup()
    print("✅ Database initialized")

if __name__ == '__main__':
    print("🌊 Starting Nalabo development server...")
    print("📍 Access the application at: http://localhost:5000")
    print("📍 Admin panel available at: http://localhost:5000/dashboard")
    print("🔑 Check logs for default credentials if this is first run")
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',  # Important: bind to all interfaces for Docker
        port=5000,
        debug=True,
        use_reloader=True
    )
