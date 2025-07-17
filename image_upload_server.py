#!/usr/bin/env python3
"""
Simple Image Upload Server
Standalone Flask server for handling image uploads without database dependencies
Can be used as a microservice alongside the main server
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """Simple image upload endpoint"""
    try:
        # Basic auth check (for production, integrate with your auth system)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or WebP'}), 400
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File size too large. Maximum 16MB allowed'}), 400
        
        # Generate secure filename with timestamp
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Return response
        return jsonify({
            'url': f'/uploads/{filename}',
            'filename': filename,
            'size': file_size
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Image upload failed: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/upload/status')
def upload_status():
    """Check upload service status"""
    return jsonify({
        'status': 'running',
        'upload_folder': UPLOAD_FOLDER,
        'max_file_size': f'{MAX_FILE_SIZE / 1024 / 1024}MB',
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

if __name__ == '__main__':
    print("Starting Simple Image Upload Server...")
    print(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"Max file size: {MAX_FILE_SIZE / 1024 / 1024}MB")
    print(f"Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
    print("Available at: http://localhost:5003")
    
    app.run(host='0.0.0.0', port=5003, debug=True)
