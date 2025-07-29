#!/bin/bash

echo "🧹 Clearing Python cache files..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "🔄 Restarting server..."
touch passenger_wsgi.py

echo "✅ Cache cleared and server restarted"
echo "📝 The encoding fix should now be active" 