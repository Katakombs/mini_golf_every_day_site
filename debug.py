#!/usr/bin/env python3
"""
Debug script - helps identify why API endpoints return 404
Upload this and visit: https://yourdomain.com/debug.py
"""

import sys
import os
import traceback

def main():
    """Debug the Flask app setup"""
    
    print("Content-Type: text/html\n")
    
    print("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini Golf Debug - API 404 Issues</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .success { color: green; }
            .error { color: red; }
            .warning { color: orange; }
            pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }
            code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🕵️ Mini Golf API Debug</h1>
    """)
    
    print(f"<h2>Current Directory & Files:</h2>")
    print(f"<p>Working Directory: <code>{os.getcwd()}</code></p>")
    
    # Check for required files
    required_files = ['passenger_wsgi.py', 'flask_app.py']
    print("<h3>Required Files:</h3>")
    for file in required_files:
        if os.path.exists(file):
            print(f"<p class='success'>✅ {file} - Found</p>")
        else:
            print(f"<p class='error'>❌ {file} - Missing</p>")
    
    # Test Flask import
    print("<h2>Flask Import Test:</h2>")
    try:
        import flask
        print(f"<p class='success'>✅ Flask version: {flask.__version__}</p>")
        
        # Test importing your app
        try:
            from flask_app import app
            print(f"<p class='success'>✅ flask_app.py imported successfully</p>")
            
            # Check app routes
            print(f"<h3>Registered Routes:</h3>")
            print(f"<pre>")
            for rule in app.url_map.iter_rules():
                print(f"{rule.rule} -> {rule.endpoint}")
            print(f"</pre>")
            
        except Exception as e:
            print(f"<p class='error'>❌ Error importing flask_app.py: {str(e)}</p>")
            print(f"<pre>{traceback.format_exc()}</pre>")
            
    except ImportError:
        print(f"<p class='error'>❌ Flask not available</p>")
    
    # Test WSGI setup
    print("<h2>WSGI Setup Test:</h2>")
    try:
        # Try to load the WSGI application
        sys.path.insert(0, os.getcwd())
        from passenger_wsgi import application
        print(f"<p class='success'>✅ WSGI application loaded</p>")
    except Exception as e:
        print(f"<p class='error'>❌ WSGI application error: {str(e)}</p>")
        print(f"<pre>{traceback.format_exc()}</pre>")
    
    # Environment info
    print(f"<h2>Environment Info:</h2>")
    print(f"<pre>")
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Environment Variables:")
    for key, value in os.environ.items():
        if 'PYTHON' in key or 'PATH' in key or 'WSGI' in key:
            print(f"  {key}={value}")
    print(f"</pre>")
    
    # Common solutions
    print(f"""
    <h2>🔧 Common Solutions for 404 API Errors:</h2>
    <ol>
        <li><strong>Restart Python App:</strong> Go to your hosting control panel and restart the Python application</li>
        <li><strong>Check App Root:</strong> Make sure your hosting points to the correct directory containing passenger_wsgi.py</li>
        <li><strong>Verify Startup File:</strong> Ensure passenger_wsgi.py is set as the startup file in your hosting control panel</li>
        <li><strong>Install Flask:</strong> Run <code>pip install flask --user</code> via SSH</li>
        <li><strong>File Permissions:</strong> Ensure passenger_wsgi.py and flask_app.py have correct permissions (644)</li>
        <li><strong>URL Structure:</strong> Some hosts require /public_html/api/status instead of /api/status</li>
    </ol>
    
    <h3>Test URLs to Try:</h3>
    <ul>
        <li><a href="/api/status">https://yourdomain.com/api/status</a></li>
        <li><a href="/public_html/api/status">https://yourdomain.com/public_html/api/status</a></li>
        <li><a href="/app/api/status">https://yourdomain.com/app/api/status</a></li>
    </ul>
    
    <h3>If Still Getting 404:</h3>
    <p>Your hosting might not be routing requests through the Flask app properly. Contact your hosting support with this debug info.</p>
    """)
    
    print("</body></html>")

if __name__ == "__main__":
    main()
