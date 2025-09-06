#!/bin/bash

# Production cleanup and optimization script for Message Hub

echo "🧹 Cleaning up for production deployment..."

# Remove development files
echo "Removing development files..."
rm -f *.log
rm -f *.sqlite3-journal
rm -f nohup.out
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf *.egg-info

# Clean up uploads directory
echo "Cleaning uploads directory..."
mkdir -p uploads
find uploads/ -name "*.tmp" -delete 2>/dev/null || true

# Create necessary directories
echo "Creating production directories..."
mkdir -p logs
mkdir -p uploads

# Set proper permissions
echo "Setting file permissions..."
chmod 755 .
chmod 644 *.py
chmod 644 *.txt
chmod 644 *.md
chmod 755 *.sh
chmod 644 templates/*.html
chmod 600 .env 2>/dev/null || echo "Note: .env file not found (normal for first run)"

# Check for security issues
echo "🔍 Security check..."

if [ -f ".env" ]; then
    if grep -q "your-" .env; then
        echo "⚠️  WARNING: Default values found in .env file!"
        echo "Please update all 'your-*' values with actual configuration"
    else
        echo "✅ .env file appears to be configured"
    fi
else
    echo "⚠️  .env file not found - will be created from .env.example on first run"
fi

# Check required files
echo "📋 Checking required files..."
required_files=("run.py" "app/config.py" "requirements.txt" "migrate.py")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING!"
    fi
done

# Check template files
echo "📋 Checking template files..."
required_templates=("dashboard.html" "login.html" "register.html" "upload_contacts.html" "bulk_send_new.html" "send_single.html")
for template in "${required_templates[@]}"; do
    if [ -f "templates/$template" ]; then
        echo "✅ templates/$template"
    else
        echo "❌ templates/$template - MISSING!"
    fi
done

# Database check
if [ -f "whatsapp.db" ]; then
    size=$(du -h whatsapp.db | cut -f1)
    echo "✅ Database exists (Size: $size)"
else
    echo "ℹ️  Database will be created on first run"
fi

echo ""
echo "🎉 Production cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and edit with your configuration"
echo "2. Ensure Evolution API is running"
echo "3. Run: ./start_production.sh"
echo ""
echo "For development, run: ./start_development.sh"
