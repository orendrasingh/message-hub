# Message Hub

A modern, web-based messaging platform for efficient bulk messaging campaigns with media support.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/message-hub.git
cd message-hub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python migrate.py

# Run the application
python run.py
```

Visit `http://localhost:5000` to access Message Hub.

## ✨ Features

- **Single & Bulk Messaging**: Send to individuals or launch campaigns to multiple contacts
- **Media Support**: Attach images, videos, and documents with automatic validation
- **Contact Management**: Import contacts via CSV, organize and manage contact lists
- **Campaign Analytics**: Track delivery status and campaign progress in real-time
- **User Authentication**: Secure multi-user system with role-based access
- **Rate Limiting**: Built-in protection against spam and API overuse

## 📋 Requirements

- Python 3.8+
- Evolution API server
- SQLite (default) or PostgreSQL/MySQL
- Modern web browser

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
EVOLUTION_API_URL=http://your-evolution-api-server:8080
EVOLUTION_API_KEY=your-api-key
```

### Evolution API Setup

1. Install and configure Evolution API
2. Create an instance for Message Hub
3. Connect WhatsApp through the app interface

## 📱 Usage

### Contact Management
- Import contacts via CSV upload
- Add contacts manually
- Organize and filter contact lists

### Single Messages
- Select contact from dropdown
- Compose message with personalization variables
- Attach multiple media files
- Send instantly

### Bulk Campaigns
- Choose recipient groups (all, pending, or selected contacts)
- Compose personalized messages using variables like `{name}`, `{first_name}`
- Attach media that will be sent to all recipients
- Configure delays between messages
- Monitor campaign progress in real-time

### Media Support
- **Images**: PNG, JPG, GIF, WebP (up to 10MB)
- **Videos**: MP4, AVI, MOV (up to 50MB)
- **Documents**: PDF, DOC, DOCX (up to 20MB)
- Multiple file upload with preview
- Automatic file validation and compression

## 📖 Documentation

For comprehensive documentation including API reference, deployment guides, and troubleshooting:

👉 **[Complete Documentation](DOCUMENTATION.md)**

## 🐳 Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Or build manually
docker build -t message-hub .
docker run -p 8000:8000 message-hub
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](DOCUMENTATION.md#contributing) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/message-hub/issues)
- **Documentation**: [Full Documentation](DOCUMENTATION.md)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/message-hub/discussions)

## 🔗 Links

- [Live Demo](https://demo.message-hub.com) (if available)
- [Evolution API Documentation](https://evolution-api.com)
- [Project Roadmap](https://github.com/yourusername/message-hub/projects)

---

**Made with ❤️ by the Message Hub Team**
