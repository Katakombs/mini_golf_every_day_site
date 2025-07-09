#!/usr/bin/env python3
"""
WSGI entry point for Mini Golf Every Day website
This file is required for shared hosting deployment
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app and expose it as 'application' for WSGI
from server import app

# WSGI servers expect this variable to be named 'application'
application = app

if __name__ == "__main__":
    # For local testing only
    app.run(debug=True, host='0.0.0.0', port=8000)
