<p align="center"><a href="https://turbocat.ro" target="_blank"><img src="https://github.com/ideacatlab/simple-mailship/blob/main/.github/images/logo.png?raw=true" width="400"></a></p>

**Professional Python SMTP HTML Mailer for Sequential Email Campaigns**

Simple MailShip is a powerful, yet easy-to-use Python application designed to send professional HTML emails sequentially via SMTP. Built with simplicity and reliability in mind, it provides a robust solution for email marketing campaigns, newsletters, notifications, and automated email communications.

Whether you're running a small business, managing a newsletter, or need to send personalized emails to a large list of recipients, Simple MailShip offers the flexibility and features you need while maintaining professional email standards and deliverability best practices.

## ✨ Key Features

- **📧 HTML Email Templates**: Beautiful, responsive email templates with Jinja2 templating support
- **🔄 Sequential Sending**: Send emails one by one with customizable rate limiting to avoid spam filters
- **🔒 Secure SMTP**: Support for SSL/TLS encryption with Gmail, Outlook, and custom SMTP servers
- **📊 Multiple Authentication**: SSL (port 465), STARTTLS (port 587), and no-auth configurations
- **📋 JSON Contact Lists**: Load recipients from JSON files with flexible data structure support
- **🎯 Template Variables**: Dynamic content insertion using recipient data
- **📱 Mobile-Friendly**: Responsive email templates that work across all devices and email clients
- **🛡️ Email Validation**: Built-in email address validation and duplicate removal
- **⚡ Rate Limiting**: Configurable sending rates to comply with SMTP provider limits
- **🧪 Test Mode**: Dry-run capability and single email testing
- **📁 Preview Generation**: Save HTML previews of rendered emails before sending
- **🔧 Environment Configuration**: Secure credential management via .env files

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- SMTP server credentials (Gmail App Password recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ideacatlab/simple-mailship.git
   cd simple-mailship
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your SMTP credentials
   nano .env  # or use your preferred editor
   ```

5. **Send your first test email**
   ```bash
   python mailer.py --test your-email@example.com
   ```

## ⚙️ Configuration

### Environment Variables

Simple MailShip uses environment variables for configuration. Copy `.env.example` to `.env` and customize the following settings:

#### SMTP Server Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` | No |
| `SMTP_PORT` | SMTP server port | `465` | No |
| `SMTP_USE_SSL` | Use SSL connection | `true` | No |
| `SMTP_USERNAME` | Your email address | - | **Yes** |
| `SMTP_PASSWORD` | Your email password/app password | - | **Yes** |

#### Email Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FROM_NAME` | Display name for sender | `SMTP_USERNAME` | No |
| `SUBJECT` | Default email subject | - | No |
| `REPLY_TO` | Reply-to email address | - | No |
| `TEMPLATE_PATH` | Path to HTML template | `./templates/example.html` | No |
| `RATE_PER_MIN` | Emails per minute limit | - | No |

### SMTP Port Configuration

Simple MailShip supports multiple SMTP configurations:

#### SSL Connection (Recommended)
- **Port**: 465
- **Security**: SSL/TLS encryption from start
- **Configuration**: `SMTP_PORT=465` and `SMTP_USE_SSL=true`
- **Best for**: Gmail, most secure option

#### STARTTLS Connection
- **Port**: 587
- **Security**: Starts unencrypted, then upgrades to TLS
- **Configuration**: `SMTP_PORT=587` and `SMTP_USE_SSL=false`
- **Best for**: Outlook, some corporate servers

#### No Authentication (Development Only)
- **Port**: 25 or custom
- **Security**: No encryption (not recommended for production)
- **Configuration**: `SMTP_PORT=25` and `SMTP_USE_SSL=false`
- **Best for**: Local testing, development servers

### Gmail Setup

For Gmail users, follow these steps:

1. **Enable 2-Factor Authentication** on your Google Account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Use the 16-character app password** as `SMTP_PASSWORD`
4. **Set your full Gmail address** as `SMTP_USERNAME`

## 📋 Usage Examples

### Command Line Interface

Simple MailShip provides a comprehensive command-line interface with the following options:

```bash
python mailer.py [OPTIONS]
```

#### Required Arguments (choose one):
- `--test EMAIL`: Send a single test email to the specified address
- `--list JSON_FILE`: Send emails to all recipients in the JSON file

#### Optional Arguments:
- `--subject SUBJECT`: Override the default email subject
- `--from-name NAME`: Override the sender display name
- `--reply-to EMAIL`: Set a custom reply-to address
- `--rate FLOAT`: Set rate limit in emails per minute
- `--dry-run`: Preview what would be sent without actually sending
- `--save-previews DIR`: Save HTML previews to specified directory
- `--verbose`: Enable detailed logging

### Basic Examples

#### Send a Test Email
```bash
python mailer.py --test john@example.com
```

#### Send to Contact List
```bash
python mailer.py --list contacts/subscribers.json
```

#### Send with Custom Subject and Rate Limiting
```bash
python mailer.py --list contacts/newsletter.json --subject "Monthly Newsletter" --rate 10
```

#### Dry Run with Preview Generation
```bash
python mailer.py --list contacts/campaign.json --dry-run --save-previews ./previews
```

#### Send with Custom Reply-To
```bash
python mailer.py --list contacts/support.json --reply-to support@company.com --verbose
```

### JSON Contact File Format

Simple MailShip supports flexible JSON formats for contact lists:

#### Simple List Format
```json
[
  {
    "email": "john@example.com",
    "name": "John Doe",
    "company": "Acme Corp"
  },
  {
    "email": "jane@example.com",
    "name": "Jane Smith",
    "location": "New York"
  }
]
```

#### Nested Object Format
```json
{
  "data": [
    {
      "email": "subscriber1@example.com",
      "first_name": "Alice",
      "last_name": "Johnson",
      "subscription_date": "2024-01-15"
    }
  ]
}
```

#### Supported Container Keys
- `items`
- `results`
- `data`

#### Email Field Recognition
Simple MailShip automatically detects email addresses using these field names (case-insensitive):
- `email`
- `e-mail`
- `mail`

### Template Variables

All JSON fields are available as template variables in your HTML templates:

```html
<h1>Hello {{name}}!</h1>
<p>Thank you for joining us from {{location}}.</p>
<p>Your email: {{email}}</p>
```

## 🎨 Email Templates

### Template Structure

Simple MailShip uses Jinja2 templating engine, allowing for dynamic content insertion and conditional logic in your HTML emails.

#### Basic Template Example
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{subject}}</title>
</head>
<body>
    <h1>Hello {{name|default('Valued Customer')}}!</h1>
    <p>This is a personalized message for {{email}}.</p>
    
    {% if company %}
    <p>We see you're from {{company}}. That's great!</p>
    {% endif %}
    
    <p>Best regards,<br>The Team</p>
</body>
</html>
```

#### Advanced Template Features

**Conditional Content**:
```html
{% if user_type == 'premium' %}
<div class="premium-content">
    <h2>Exclusive Premium Content</h2>
</div>
{% else %}
<div class="standard-content">
    <h2>Standard Content</h2>
</div>
{% endif %}
```

**Loops and Lists**:
```html
{% if products %}
<ul>
{% for product in products %}
    <li>{{product.name}} - ${{product.price}}</li>
{% endfor %}
</ul>
{% endif %}
```

**Filters and Formatting**:
```html
<p>Welcome {{name|title}}!</p>
<p>Member since: {{join_date|strftime('%B %d, %Y')}}</p>
<p>Total orders: {{order_count|default(0)}}</p>
```

### Email Client Compatibility

The included example template is designed for maximum compatibility:

- **Inline CSS**: All styles are inlined for better email client support
- **Table-based Layout**: Uses HTML tables for consistent rendering
- **Mobile Responsive**: Adapts to different screen sizes
- **Dark Mode Support**: Includes dark mode media queries
- **Outlook Compatibility**: Special handling for Microsoft Outlook

### Template Best Practices

1. **Use Inline CSS**: Email clients strip out `<style>` tags
2. **Table Layouts**: More reliable than div-based layouts
3. **Web-Safe Fonts**: Stick to Arial, Helvetica, Georgia, Times
4. **Alt Text**: Always include alt text for images
5. **Test Across Clients**: Preview in Gmail, Outlook, Apple Mail
6. **Keep It Simple**: Complex layouts may break in some clients

## 🔧 Advanced Configuration

### Rate Limiting

Control sending speed to avoid triggering spam filters:

```bash
# Send 6 emails per minute (10-second intervals)
python mailer.py --list contacts.json --rate 6

# Very conservative rate (30-second intervals)
python mailer.py --list contacts.json --rate 2
```

### Custom SMTP Providers

#### Outlook/Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

#### Yahoo Mail
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_SSL=false
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

#### Custom SMTP Server
```env
SMTP_HOST=mail.yourcompany.com
SMTP_PORT=465
SMTP_USE_SSL=true
SMTP_USERNAME=noreply@yourcompany.com
SMTP_PASSWORD=your-password
```

### Error Handling

Simple MailShip includes robust error handling:

- **Configuration Errors**: Missing or invalid environment variables
- **Template Errors**: Jinja2 template syntax or missing template files
- **SMTP Errors**: Authentication failures, connection issues
- **Email Validation**: Invalid email addresses are automatically skipped
- **Rate Limiting**: Automatic delays between emails

### Logging and Monitoring

Enable verbose logging for detailed information:

```bash
python mailer.py --list contacts.json --verbose
```

Output includes:
- Configuration validation
- Template rendering status
- SMTP connection details
- Email sending progress
- Error messages and warnings
- Summary statistics

## 🧪 Testing and Development

### Dry Run Mode

Test your configuration without sending emails:

```bash
python mailer.py --list contacts.json --dry-run --save-previews ./test-previews
```

This will:
- Validate your configuration
- Load and parse contact lists
- Render email templates
- Save HTML previews
- Show what would be sent

### Preview Generation

Generate HTML previews for review:

```bash
python mailer.py --list contacts.json --save-previews ./previews --dry-run
```

Previews are saved as:
- `preview_test.html` (for test emails)
- `preview_email@domain.com.html` (for list emails)

### Single Email Testing

Test with a single recipient:

```bash
python mailer.py --test your-email@example.com --save-previews ./test
```

## 🤝 Contributing

We welcome contributions from developers of all skill levels! Simple MailShip is an open-source project, and we're excited to collaborate with the community.

### How to Contribute

#### Reporting Issues
- **Bug Reports**: Use GitHub Issues to report bugs
- **Feature Requests**: Suggest new features or improvements
- **Documentation**: Help improve our documentation

#### Contributing Code
1. **Fork the Repository**
   ```bash
   git fork https://github.com/ideacatlab/simple-mailship.git
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   python -m pytest tests/
   python mailer.py --test your-email@example.com --dry-run
   ```

5. **Submit a Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all tests pass

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/simple-mailship.git
cd simple-mailship

# Create development environment
python -m venv dev-env
source dev-env/bin/activate  # or dev-env\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if available

# Run tests
python -m pytest tests/
```

### Code Style Guidelines

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Document functions and classes with clear docstrings
- **Error Handling**: Include appropriate error handling and logging
- **Testing**: Write tests for new features and bug fixes

### Areas for Contribution

We're particularly interested in contributions for:

- **Email Template Library**: Additional professional email templates
- **SMTP Provider Presets**: Configuration presets for popular email providers
- **Advanced Features**: Attachment support, email tracking, analytics
- **Testing**: Improved test coverage and integration tests
- **Documentation**: Tutorials, examples, and improved documentation
- **Performance**: Optimization for large email lists
- **Security**: Enhanced security features and best practices

## 📄 License

Simple MailShip is released under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🏢 About TurboCat

Simple MailShip is created and maintained by [TurboCat](https://turbocat.ro/), a web development company specializing in custom software solutions and digital transformation.

**TurboCat Services:**
- 🌐 Web Development & Design
- ⚙️ Custom Software Development  
- ☁️ Infrastructure Management
- 📈 SEO & Digital Marketing
- 🎨 UI/UX Design
- 🔧 Technical Consulting & Support

Visit [turbocat.ro](https://turbocat.ro/) to learn more about our services and how we can help transform your digital presence.

## 🆘 Support

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check this README and code comments
- **Community**: Join discussions in GitHub Discussions

### Common Issues

#### Gmail Authentication Errors
- Ensure 2-Factor Authentication is enabled
- Use App Password, not your regular password
- Check that "Less secure app access" is disabled

#### Template Not Found
- Verify `TEMPLATE_PATH` in your `.env` file
- Ensure the template file exists and is readable
- Use absolute paths if relative paths don't work

#### SMTP Connection Issues
- Verify SMTP host and port settings
- Check firewall and network connectivity
- Try different ports (465 for SSL, 587 for STARTTLS)

#### Rate Limiting
- Reduce sending rate with `--rate` parameter
- Check your SMTP provider's sending limits
- Consider using dedicated email service for large volumes

---

**Made with ❤️ by [TurboCat](https://turbocat.ro/)**

*Transform your email communication with Simple MailShip - the professional Python SMTP solution.*
