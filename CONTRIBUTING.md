# Contributing to Message Hub

Thank you for your interest in contributing to Message Hub! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Setup](#development-setup)
5. [Coding Standards](#coding-standards)
6. [Pull Request Process](#pull-request-process)
7. [Issue Reporting](#issue-reporting)
8. [Feature Requests](#feature-requests)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and constructive in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of Flask web development
- Familiarity with SQLite and database concepts

### First Time Setup

1. **Fork the Repository**
   ```bash
   # Click the "Fork" button on GitHub, then:
   git clone https://github.com/yourusername/message-hub.git
   cd message-hub
   git remote add upstream https://github.com/original/message-hub.git
   ```

2. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**
   ```bash
   python migrate.py
   ```

5. **Run the Application**
   ```bash
   python run.py
   ```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Implement features or fix bugs
- **Documentation**: Improve guides, API docs, or comments
- **Testing**: Add or improve test coverage
- **Design**: UI/UX improvements and suggestions

### Contribution Workflow

1. **Create an Issue**: For bugs or feature requests
2. **Discussion**: Discuss the approach in the issue
3. **Implementation**: Create a branch and implement changes
4. **Testing**: Ensure all tests pass and add new tests
5. **Pull Request**: Submit PR with clear description
6. **Review**: Address feedback from maintainers
7. **Merge**: Your contribution becomes part of the project!

## Development Setup

### Project Structure

```
message-hub/
├── app/                     # Application code
│   ├── models/             # Database models
│   ├── routes/             # Route handlers
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── templates/              # HTML templates
├── static/                 # Static assets
├── tests/                  # Test files
├── migrations/             # Database migrations
└── docs/                   # Documentation
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_services.py

# Run with coverage
python -m pytest --cov=app --cov-report=html
```

### Database Migrations

```bash
# Create a new migration
python migrate.py create "Description of changes"

# Apply migrations
python migrate.py upgrade

# Rollback migration
python migrate.py downgrade
```

## Coding Standards

### Python Code Style

We follow PEP 8 guidelines with some modifications:

- **Line Length**: Maximum 88 characters
- **Imports**: Group standard library, third-party, and local imports
- **Naming**: Use descriptive names for variables and functions
- **Type Hints**: Use type hints for function parameters and returns

### Example Code Style

```python
from typing import List, Optional, Dict, Any
from datetime import datetime

from flask import request, jsonify
from app.models import Contact
from app.services.contact import ContactService


def create_contact(data: Dict[str, Any]) -> Optional[Contact]:
    """
    Create a new contact with validation.
    
    Args:
        data: Dictionary containing contact information
        
    Returns:
        Created contact object or None if validation fails
        
    Raises:
        ValidationError: If required fields are missing
    """
    if not data.get('name') or not data.get('phone'):
        raise ValidationError("Name and phone are required")
        
    contact = ContactService.create_contact(
        name=data['name'],
        phone=data['phone'],
        first_name=data.get('first_name', '')
    )
    
    return contact
```

### JavaScript Code Style

- Use modern ES6+ syntax
- Follow consistent naming conventions (camelCase)
- Add comments for complex logic
- Use async/await for promises

### HTML/CSS Guidelines

- Use semantic HTML elements
- Follow Bootstrap conventions
- Use CSS custom properties for theming
- Ensure responsive design
- Add proper accessibility attributes

## Pull Request Process

### Before Submitting

1. **Update Documentation**: Ensure README, API docs, and code comments are updated
2. **Add Tests**: Include tests for new features or bug fixes
3. **Check Code Style**: Run linting tools and fix any issues
4. **Test Thoroughly**: Run full test suite and manual testing
5. **Update Changelog**: Add entry describing your changes

### PR Guidelines

1. **Clear Title**: Use a descriptive title summarizing the change
2. **Detailed Description**: Explain what changes were made and why
3. **Link Issues**: Reference related issues using "Fixes #123" or "Closes #123"
4. **Screenshots**: Include screenshots for UI changes
5. **Breaking Changes**: Clearly document any breaking changes

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have performed manual testing

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information or context.
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Clear Title**: Summarize the issue
2. **Environment**: OS, Python version, browser
3. **Steps to Reproduce**: Detailed steps to recreate the issue
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Screenshots**: Visual evidence if applicable
7. **Error Messages**: Full error messages and stack traces

### Bug Report Template

```markdown
**Environment:**
- OS: [e.g., Windows 10, macOS 11.6, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Browser: [e.g., Chrome 95.0, Firefox 93.0]
- Message Hub Version: [e.g., 1.2.0]

**Description:**
A clear description of what the bug is.

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior:**
A clear description of what you expected to happen.

**Actual Behavior:**
A clear description of what actually happened.

**Screenshots:**
If applicable, add screenshots to help explain your problem.

**Error Messages:**
```
Paste any error messages here
```

**Additional Context:**
Add any other context about the problem here.
```

## Feature Requests

### Guidelines for Feature Requests

1. **Check Existing Issues**: Search for similar requests first
2. **Clear Use Case**: Explain the problem this feature would solve
3. **Detailed Description**: Provide comprehensive details
4. **Consider Alternatives**: Mention alternative solutions considered
5. **Implementation Ideas**: Suggest how it might be implemented

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions or features you've considered.

**Use Cases**
Describe specific use cases where this feature would be helpful.

**Implementation Ideas**
If you have ideas on how this could be implemented, please share them.

**Additional Context**
Add any other context or screenshots about the feature request here.
```

## Development Guidelines

### Adding New Features

1. **Create Feature Branch**: `git checkout -b feature/feature-name`
2. **Plan Implementation**: Break down into smaller tasks
3. **Write Tests First**: Consider test-driven development
4. **Implement Feature**: Follow coding standards
5. **Update Documentation**: Include usage examples
6. **Test Thoroughly**: Manual and automated testing

### Database Changes

1. **Create Migration**: Use migration script for schema changes
2. **Backward Compatibility**: Ensure migrations are reversible
3. **Test Migrations**: Test on fresh database and with existing data
4. **Document Changes**: Update schema documentation

### API Changes

1. **Versioning**: Consider API versioning for breaking changes
2. **Documentation**: Update API documentation
3. **Backward Compatibility**: Maintain compatibility when possible
4. **Testing**: Add comprehensive API tests

## Review Process

### Code Review Checklist

**Functionality**
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance considerations

**Code Quality**
- [ ] Code is readable and well-documented
- [ ] Follows project coding standards
- [ ] No code duplication
- [ ] Appropriate abstractions

**Testing**
- [ ] Tests cover new functionality
- [ ] Tests are meaningful and reliable
- [ ] All tests pass
- [ ] Manual testing performed

**Documentation**
- [ ] Code is properly commented
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] README updated if needed

### Review Timeline

- **Initial Review**: Within 2-3 business days
- **Follow-up Reviews**: Within 24-48 hours
- **Final Approval**: After all feedback addressed

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check existing documentation first
- **Code Comments**: Look at inline code documentation

### Communication Guidelines

- Be respectful and professional
- Provide context and details
- Use clear, descriptive titles
- Search existing issues before creating new ones
- Follow up on your contributions

## Recognition

We value all contributions to Message Hub! Contributors will be:

- Listed in the project's contributors
- Mentioned in release notes for significant contributions
- Invited to join the core contributor team for sustained contributions

## Questions?

If you have questions about contributing, please:

1. Check this document first
2. Search existing GitHub issues and discussions
3. Create a new discussion on GitHub
4. Reach out to maintainers if needed

Thank you for contributing to Message Hub! 🚀
