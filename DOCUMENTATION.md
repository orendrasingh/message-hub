# Message Hub - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [User Guide](#user-guide)
6. [API Documentation](#api-documentation)
7. [Development Guide](#development-guide)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## Overview

Message Hub is a modern, web-based messaging platform that enables businesses and individuals to send personalized messages with media attachments to multiple contacts efficiently. Built with Flask and integrated with Evolution API, it provides a comprehensive solution for bulk messaging campaigns.

### Key Capabilities
- **Single & Bulk Messaging**: Send messages to individual contacts or launch campaigns to multiple recipients
- **Media Support**: Attach images, videos, and documents with automatic format validation
- **Contact Management**: Import, organize, and manage contact lists with CSV support
- **Campaign Analytics**: Track message delivery status and campaign progress
- **User Authentication**: Secure multi-user system with role-based access
- **Rate Limiting**: Built-in protection against spam and API overuse

## Features

### 🚀 Core Messaging Features

#### Single Message Sending
- Send personalized messages to individual contacts
- Support for multiple media attachments (images, videos, documents)
- Real-time message status tracking
- Template variables for personalization (`{name}`, `{first_name}`, `{phone}`)

#### Bulk Campaign Management
- Create and manage bulk messaging campaigns
- Contact selection options:
  - All contacts
  - Pending contacts only (excludes previously messaged)
  - Custom contact selection
- Campaign progress monitoring
- Configurable message delays to prevent rate limiting

#### Media Management
- **Supported Formats**:
  - Images: PNG, JPG, GIF, WebP (up to 10MB)
  - Videos: MP4, AVI, MOV (up to 50MB)
  - Documents: PDF, DOC, DOCX (up to 20MB)
- Multiple file upload with drag-and-drop interface
- Automatic file validation and size checking
- Image/video preview with thumbnail generation
- Bulk media removal and management

#### Contact Management
- CSV import with automatic field mapping
- Manual contact addition and editing
- Contact categorization and filtering
- Duplicate detection and prevention
- Export contact lists

### 🔐 Security & Authentication

#### User Management
- Secure user registration and login
- Password reset functionality
- Session management with timeout
- Role-based access control

#### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting on API endpoints
- Secure file upload handling

### 📊 Analytics & Monitoring

#### Campaign Analytics
- Real-time delivery status tracking
- Success/failure rate monitoring
- Campaign progress visualization
- Message history and logs

#### System Monitoring
- Error logging and tracking
- Performance metrics
- API usage monitoring
- Database optimization

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- SQLite (included with Python)
- Evolution API server
- Modern web browser

### Quick Start

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/message-hub.git
cd message-hub
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize Database**
```bash
python migrate.py
```

6. **Run the Application**
```bash
python run.py
```

### Detailed Installation

#### Step 1: System Requirements
Ensure your system meets the following requirements:
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 2GB RAM
- **Storage**: At least 1GB free space
- **Network**: Internet connection for API integration

#### Step 2: Environment Setup
Create and configure your environment:

```bash
# Create project directory
mkdir message-hub-project
cd message-hub-project

# Clone repository
git clone https://github.com/yourusername/message-hub.git
cd message-hub

# Create virtual environment
python -m venv message-hub-env
source message-hub-env/bin/activate  # Unix/macOS
# OR
message-hub-env\Scripts\activate  # Windows
```

#### Step 3: Dependencies Installation
Install required packages:

```bash
# Upgrade pip
pip install --upgrade pip

# Install application dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 4: Configuration
Set up your environment variables:

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env
```

Required environment variables:
```env
# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///whatsapp.db

# Evolution API
EVOLUTION_API_URL=http://your-evolution-api-server:8080
EVOLUTION_API_KEY=your-api-key

# File Upload
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=uploads

# Email (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | - | Yes |
| `DEBUG` | Debug mode | False | No |
| `DATABASE_URL` | Database connection string | sqlite:///whatsapp.db | No |
| `EVOLUTION_API_URL` | Evolution API server URL | - | Yes |
| `EVOLUTION_API_KEY` | Evolution API authentication key | - | Yes |
| `MAX_CONTENT_LENGTH` | Maximum file upload size (bytes) | 52428800 | No |
| `UPLOAD_FOLDER` | Directory for uploaded files | uploads | No |
| `MAIL_SERVER` | SMTP server for emails | - | No |
| `MAIL_PORT` | SMTP port | 587 | No |
| `MAIL_USERNAME` | Email username | - | No |
| `MAIL_PASSWORD` | Email password | - | No |

### Evolution API Setup

1. **Install Evolution API**
   Follow the Evolution API documentation to set up your API server.

2. **Create Instance**
   ```bash
   curl -X POST http://your-server:8080/instance/create \
     -H "Content-Type: application/json" \
     -d '{"instanceName": "message-hub"}'
   ```

3. **Connect WhatsApp**
   - Open Message Hub in your browser
   - Navigate to WhatsApp Connection
   - Scan the QR code with your WhatsApp

### Database Configuration

The application uses SQLite by default, but supports other databases:

#### PostgreSQL
```env
DATABASE_URL=postgresql://username:password@localhost/message_hub
```

#### MySQL
```env
DATABASE_URL=mysql://username:password@localhost/message_hub
```

#### Custom Configuration
Edit `app/config.py` for advanced database settings.

## User Guide

### Getting Started

#### 1. Account Setup
1. **Registration**
   - Visit the application URL
   - Click "Register" on the landing page
   - Fill in your details (name, email, password)
   - Click "Create Account"

2. **Login**
   - Enter your email and password
   - Click "Login"
   - You'll be redirected to the dashboard

#### 2. WhatsApp Connection
1. **Initial Setup**
   - From the dashboard, click "Connect WhatsApp"
   - Follow the setup wizard
   - Scan the QR code with your WhatsApp mobile app
   - Wait for connection confirmation

2. **Connection Status**
   - Green indicator: Connected and ready
   - Yellow indicator: Connecting...
   - Red indicator: Disconnected or error

### Contact Management

#### Importing Contacts

1. **CSV Format**
   Your CSV file should have the following columns:
   ```csv
   name,phone,first_name
   John Doe,+1234567890,John
   Jane Smith,+1987654321,Jane
   ```

2. **Import Process**
   - Navigate to "Contacts" → "Upload Contacts"
   - Select your CSV file
   - Map columns to fields
   - Click "Import Contacts"
   - Review import summary

#### Manual Contact Entry
1. Go to "Contacts" → "Add Contact"
2. Fill in contact details:
   - **Name**: Full name (required)
   - **Phone**: International format (+1234567890)
   - **First Name**: Used for personalization
3. Click "Save Contact"

#### Contact Management
- **View All**: Browse your contact list with search and filtering
- **Edit**: Update contact information
- **Delete**: Remove contacts (with confirmation)
- **Export**: Download contact list as CSV

### Single Message Sending

#### Basic Message
1. **Navigate**: Dashboard → "Send Single Message"
2. **Select Contact**: Choose from dropdown or type to search
3. **Compose Message**: 
   - Enter your message text
   - Use variables: `{name}`, `{first_name}`, `{phone}`
   - Example: "Hi {first_name}, this is a test message!"
4. **Send**: Click "Send Message"

#### Message with Media
1. **Follow Basic Steps** (above)
2. **Attach Media**:
   - Click the media upload area
   - Select multiple files (Ctrl/Cmd + click)
   - Supported formats appear below
   - Preview thumbnails will appear
3. **Media Options**:
   - Remove individual files using the X button
   - Add caption to media (optional)
4. **Send**: Click "Send Message"

### Bulk Campaign Management

#### Creating a Campaign

1. **Setup**
   - Navigate to "Send Bulk Messages"
   - Choose recipient option:
     - **Pending Contacts Only**: Excludes previously messaged contacts
     - **All Contacts**: Sends to all contacts (may resend)
     - **Selected Contacts**: Choose specific contacts

2. **Contact Selection** (if "Selected Contacts" chosen)
   - Individual selection: Check specific contacts
   - Select All: Use "Select All" button
   - Select None: Use "Select None" button
   - Search: Use search box to filter contacts

3. **Message Composition**
   - **Text Message**: Enter your message
   - **Variables**: Use `{name}`, `{first_name}`, `{phone}` for personalization
   - **Media**: Attach multiple files (same as single send)
   - **Caption**: When media is attached, text becomes caption for first media file

4. **Campaign Settings**
   - **Delay Between Messages**: Recommended 2-5 seconds to avoid rate limiting
   - **Campaign Name**: Auto-generated or custom

5. **Launch Campaign**
   - Review all settings
   - Click "Send Bulk Messages"
   - Monitor progress on campaign status page

#### Campaign Monitoring

1. **Real-time Progress**
   - View active campaigns on dashboard
   - Progress bar shows completion percentage
   - Status indicators: Pending, In Progress, Completed, Failed

2. **Detailed Analytics**
   - Click on campaign to view details
   - Message delivery status per contact
   - Success/failure rates
   - Error logs and troubleshooting

#### Campaign Best Practices

1. **Message Timing**
   - Send during business hours
   - Consider recipient time zones
   - Avoid late night/early morning

2. **Content Guidelines**
   - Keep messages concise and relevant
   - Use personalization variables
   - Include clear call-to-action
   - Respect privacy and preferences

3. **Rate Limiting**
   - Use recommended delays (2-5 seconds)
   - Monitor for delivery failures
   - Split large campaigns across multiple days

### Media Management

#### Supported File Types

| Type | Formats | Max Size | Notes |
|------|---------|----------|-------|
| Images | PNG, JPG, JPEG, GIF, WebP | 10MB | Auto-compressed if needed |
| Videos | MP4, AVI, MOV, WMV | 50MB | Thumbnails generated |
| Documents | PDF, DOC, DOCX, TXT | 20MB | Icons displayed |

#### Upload Process
1. **Single File**: Click to select one file
2. **Multiple Files**: 
   - Hold Ctrl (Windows) or Cmd (Mac)
   - Click each file you want
   - Or select first file, hold Shift, select last file for range

#### Media Preview
- **Images**: Thumbnail previews with full-size view on click
- **Videos**: Thumbnail with play icon (preview not supported in browser)
- **Documents**: File icon with filename and size

#### Managing Attachments
- **Remove**: Click X button on individual files
- **Replace**: Remove existing and upload new files
- **Reorder**: Drag and drop to change order (first image becomes main thumbnail)

### Message Templates and Variables

#### Available Variables
- `{name}`: Full contact name
- `{first_name}`: First name only
- `{phone}`: Phone number

#### Template Examples

**Basic Greeting**
```
Hi {first_name}! Welcome to our service.
```

**Appointment Reminder**
```
Hello {name}, this is a reminder for your appointment tomorrow at 2 PM. Please confirm by replying to this message.
```

**Promotional Message**
```
Hi {first_name}! 🎉 Special offer just for you! Get 20% off your next purchase. Use code: SAVE20
```

**Follow-up Message**
```
Hi {name}, thank you for your interest in our services. Please feel free to contact us at {phone} if you have any questions.
```

## API Documentation

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully",
  "user_id": 123
}
```

#### POST /auth/login
Authenticate user and create session.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "redirect": "/dashboard"
}
```

### Contact Management Endpoints

#### GET /api/contacts
Retrieve user's contacts with pagination.

**Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `search` (optional): Search term

**Response:**
```json
{
  "contacts": [
    {
      "id": 1,
      "name": "John Doe",
      "phone": "+1234567890",
      "first_name": "John",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

#### POST /api/contacts
Create a new contact.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "phone": "+1987654321",
  "first_name": "Jane"
}
```

### Messaging Endpoints

#### POST /api/send-single
Send a single message.

**Request Body (Form Data):**
- `contact_id`: Contact ID
- `message`: Message text
- `media_files`: Media files (optional, multiple)

**Response:**
```json
{
  "success": true,
  "message": "Message sent successfully",
  "message_id": "msg_123"
}
```

#### POST /api/send-bulk
Start a bulk messaging campaign.

**Request Body (Form Data):**
- `send_to`: "all", "pending", or "selected"
- `selected_contacts`: Contact IDs (if send_to is "selected")
- `message`: Message text
- `delay`: Delay between messages in seconds
- `media_files`: Media files (optional, multiple)

**Response:**
```json
{
  "success": true,
  "message": "Campaign started successfully",
  "campaign_id": "camp_123"
}
```

### Campaign Monitoring Endpoints

#### GET /api/campaign/{campaign_id}/status
Get campaign progress and status.

**Response:**
```json
{
  "campaign_id": "camp_123",
  "status": "in_progress",
  "total_contacts": 100,
  "sent_count": 75,
  "failed_count": 2,
  "pending_count": 23,
  "progress_percentage": 75.0,
  "started_at": "2024-01-01T10:00:00Z",
  "estimated_completion": "2024-01-01T10:15:00Z"
}
```

## Development Guide

### Project Structure

```
message-hub/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   │   └── __init__.py
│   ├── routes/              # Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main application routes
│   │   ├── api.py           # API endpoints
│   │   ├── contacts.py      # Contact management
│   │   └── campaigns.py     # Campaign management
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication service
│   │   ├── contact.py       # Contact management service
│   │   ├── campaign.py      # Campaign management service
│   │   ├── whatsapp.py      # WhatsApp API integration
│   │   └── email.py         # Email service
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── auth.py          # Authentication utilities
│       ├── validators.py    # Input validation
│       ├── rate_limiter.py  # Rate limiting
│       ├── media.py         # Media handling
│       └── error_handlers.py # Error handling
├── templates/               # Jinja2 templates
├── static/                  # Static assets (CSS, JS, images)
├── uploads/                 # User uploaded files
├── logs/                    # Application logs
├── migrations/              # Database migrations
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── migrate.py              # Database migration script
└── README.md               # Project documentation
```

### Setting Up Development Environment

1. **Fork and Clone**
```bash
git clone https://github.com/yourusername/message-hub.git
cd message-hub
```

2. **Create Development Branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Install Development Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. **Run in Development Mode**
```bash
export FLASK_ENV=development
export DEBUG=True
python run.py
```

### Adding New Features

#### 1. Database Models
Create new models in `app/models/`:
```python
# app/models/new_model.py
from app import db
from datetime import datetime

class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

#### 2. Services
Create business logic in `app/services/`:
```python
# app/services/new_service.py
from app.models.new_model import NewModel
from app import db

class NewService:
    @staticmethod
    def create_item(name):
        item = NewModel(name=name)
        db.session.add(item)
        db.session.commit()
        return item
    
    @staticmethod
    def get_all_items():
        return NewModel.query.all()
```

#### 3. Routes
Add routes in `app/routes/`:
```python
# app/routes/new_routes.py
from flask import Blueprint, request, jsonify
from app.services.new_service import NewService

bp = Blueprint('new', __name__)

@bp.route('/api/new-items', methods=['GET'])
def get_items():
    items = NewService.get_all_items()
    return jsonify([item.to_dict() for item in items])

@bp.route('/api/new-items', methods=['POST'])
def create_item():
    data = request.get_json()
    item = NewService.create_item(data['name'])
    return jsonify(item.to_dict()), 201
```

#### 4. Templates
Create templates in `templates/`:
```html
<!-- templates/new_feature.html -->
{% extends "base.html" %}

{% block title %}New Feature{% endblock %}

{% block content %}
<div class="container">
    <h1>New Feature</h1>
    <!-- Your content here -->
</div>
{% endblock %}
```

### Testing

#### Unit Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_services.py

# Run with coverage
python -m pytest --cov=app
```

#### Manual Testing
1. **Start Development Server**
```bash
python run.py
```

2. **Test API Endpoints**
```bash
# Test with curl
curl -X POST http://localhost:5000/api/contacts \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "phone": "+1234567890"}'
```

### Code Standards

#### Python Style Guide
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document functions with docstrings
- Maximum line length: 88 characters

#### Example:
```python
from typing import List, Optional

def process_contacts(contact_list: List[dict]) -> Optional[dict]:
    """
    Process a list of contacts and return summary.
    
    Args:
        contact_list: List of contact dictionaries
        
    Returns:
        Dictionary with processing summary or None if empty
    """
    if not contact_list:
        return None
        
    processed = []
    for contact in contact_list:
        # Process contact
        processed.append(contact)
        
    return {
        'total': len(processed),
        'contacts': processed
    }
```

#### JavaScript Style Guide
- Use modern ES6+ syntax
- Follow consistent naming conventions
- Document complex functions
- Use async/await for promises

### Database Migrations

#### Creating Migrations
```bash
# Generate migration file
python migrate.py create "Add new table"

# Apply migrations
python migrate.py upgrade

# Rollback migration
python migrate.py downgrade
```

#### Migration Example
```python
# migrations/001_add_new_table.py
def upgrade():
    """Add new table."""
    cursor.execute('''
        CREATE TABLE new_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def downgrade():
    """Remove new table."""
    cursor.execute('DROP TABLE IF EXISTS new_table')
```

## Deployment

### Production Setup

#### 1. Server Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum
- **OS**: Ubuntu 20.04 LTS or CentOS 8

#### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and tools
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Install Node.js (for frontend build tools)
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 3. Application Setup
```bash
# Create application user
sudo useradd -m -s /bin/bash messageuser

# Switch to application user
sudo su - messageuser

# Clone and setup application
git clone https://github.com/yourusername/message-hub.git
cd message-hub

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Setup environment
cp .env.example .env
# Edit .env with production settings
```

#### 4. Environment Configuration
```env
# Production settings
DEBUG=False
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://user:pass@localhost/messagedb

# Security settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=3600
```

#### 5. Database Setup
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE messagedb;
CREATE USER messageuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE messagedb TO messageuser;
\q

# Run migrations
python migrate.py
```

#### 6. Gunicorn Configuration
```bash
# Create gunicorn config
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
user = "messageuser"
group = "messageuser"
EOF
```

#### 7. Supervisor Configuration
```bash
# Create supervisor config
sudo tee /etc/supervisor/conf.d/messagehub.conf << 'EOF'
[program:messagehub]
command=/home/messageuser/message-hub/venv/bin/gunicorn --config gunicorn.conf.py run:app
directory=/home/messageuser/message-hub
user=messageuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/messagehub.log
EOF

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start messagehub
```

#### 8. Nginx Configuration
```bash
# Create nginx config
sudo tee /etc/nginx/sites-available/messagehub << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 64M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/messageuser/message-hub/static;
        expires 30d;
    }

    location /uploads {
        alias /home/messageuser/message-hub/uploads;
        expires 1d;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/messagehub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. SSL Setup (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/messagedb
      - EVOLUTION_API_URL=http://evolution:8080
    depends_on:
      - db
      - evolution
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=messagedb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  evolution:
    image: davidsongomes/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      - SERVER_PORT=8080

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

volumes:
  postgres_data:
```

### Monitoring & Maintenance

#### Log Management
```bash
# View application logs
sudo tail -f /var/log/messagehub.log

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Rotate logs
sudo logrotate /etc/logrotate.d/messagehub
```

#### Performance Monitoring
```bash
# Monitor application
sudo supervisorctl status messagehub

# Monitor database
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Monitor system resources
htop
df -h
free -h
```

#### Backup Strategy
```bash
# Database backup
sudo -u postgres pg_dump messagedb > backup_$(date +%Y%m%d_%H%M%S).sql

# Application backup
tar -czf messagehub_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /home/messageuser/message-hub \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=*.pyc
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Symptoms:**
- Server returns 500 error
- Application logs show import errors
- Dependencies missing

**Solutions:**
```bash
# Check Python version
python --version

# Verify virtual environment
which python
which pip

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check environment variables
env | grep FLASK
```

#### 2. Database Connection Issues

**Symptoms:**
- Database connection errors
- Migration failures
- Data not saving

**Solutions:**
```bash
# Check database status
sudo systemctl status postgresql

# Test database connection
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://user:pass@localhost/db')
print('Connection successful')
"

# Reset database
python migrate.py reset
python migrate.py
```

#### 3. WhatsApp Connection Problems

**Symptoms:**
- QR code not appearing
- Connection timeouts
- Message sending failures

**Solutions:**
```bash
# Check Evolution API status
curl http://localhost:8080/instance/list

# Restart Evolution API
sudo docker restart evolution-api

# Check network connectivity
ping evolution-api-server.com
```

#### 4. File Upload Issues

**Symptoms:**
- Large files failing to upload
- Media not displaying
- Upload timeouts

**Solutions:**
```bash
# Check file permissions
ls -la uploads/
chmod 755 uploads/

# Increase upload limits
# In nginx.conf:
client_max_body_size 64M;

# In application config:
MAX_CONTENT_LENGTH = 67108864  # 64MB
```

#### 5. Performance Issues

**Symptoms:**
- Slow page loads
- High CPU/memory usage
- Database timeouts

**Solutions:**
```bash
# Monitor resources
htop
iotop

# Check database performance
sudo -u postgres psql messagedb -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
"

# Optimize database
sudo -u postgres psql messagedb -c "VACUUM ANALYZE;"
```

### Debug Mode

Enable debug mode for detailed error messages:

```python
# In run.py or config.py
DEBUG = True
FLASK_ENV = 'development'

# Enable SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Bad Request | Check request format and required fields |
| 401 | Unauthorized | Verify authentication credentials |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify URL and resource existence |
| 413 | Payload Too Large | Reduce file size or increase limits |
| 429 | Too Many Requests | Implement rate limiting |
| 500 | Internal Server Error | Check application logs |
| 502 | Bad Gateway | Check upstream service connectivity |
| 503 | Service Unavailable | Check service status |

### Getting Help

1. **Check Logs**: Always start by checking application and system logs
2. **GitHub Issues**: Report bugs and request features on GitHub
3. **Documentation**: Review this documentation for configuration details
4. **Community**: Join our community discussions
5. **Professional Support**: Contact for enterprise support options

## Contributing

We welcome contributions to Message Hub! Here's how to get started:

### Getting Started

1. **Fork the Repository**
   - Click "Fork" on the GitHub repository page
   - Clone your fork locally

2. **Set Up Development Environment**
   ```bash
   git clone https://github.com/orendrasingh/message-hub.git
   cd message-hub
   ```

3. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Development Workflow

1. **Make Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features

2. **Test Your Changes**
   ```bash
   # Run unit tests
   python -m pytest
   
   # Run manual tests
   python run.py
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create Pull Request on GitHub
   - Describe your changes clearly
   - Link any related issues

### Code Standards

#### Commit Messages
Follow conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

#### Code Quality
- Write clear, self-documenting code
- Add comments for complex logic
- Follow PEP 8 for Python code
- Use meaningful variable names
- Keep functions small and focused

#### Testing
- Write unit tests for new features
- Ensure existing tests pass
- Test edge cases and error conditions
- Include integration tests where appropriate

### Areas for Contribution

1. **Features**
   - Message scheduling
   - Advanced analytics
   - Template management
   - Integration with other platforms

2. **Documentation**
   - API documentation
   - User guides
   - Video tutorials
   - Translation

3. **Testing**
   - Unit tests
   - Integration tests
   - Performance tests
   - Security testing

4. **Infrastructure**
   - Docker improvements
   - CI/CD pipeline
   - Monitoring tools
   - Performance optimization

### License

Message Hub is released under the MIT License. By contributing, you agree that your contributions will be licensed under the same license.

---

## Support

For support, bug reports, or feature requests:

- **GitHub Issues**: https://github.com/orendrasingh/message-hub/issues
- **Documentation**: This file and inline code comments
- **Community**: GitHub Discussions
- **Email**: support@message-hub.com (for enterprise users)

---

**Message Hub** - Simplifying bulk messaging for everyone.
