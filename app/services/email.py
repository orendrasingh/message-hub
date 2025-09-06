"""
Email service for password reset and notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any


class EmailService:
    """Email service for sending emails"""
    
    def __init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password
    
    def send_password_reset(self, to_email: str, reset_url: str) -> Dict[str, Any]:
        """Send password reset email"""
        if not self.email_address or not self.email_password:
            return {'success': False, 'error': 'Email configuration not set'}
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"WhatsApp Message Hub <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = "Password Reset - WhatsApp Message Hub"
            
            body = f"""
            Hi,
            
            You requested a password reset for your WhatsApp Message Hub account.
            
            Click the link below to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this reset, please ignore this email.
            
            Best regards,
            WhatsApp Message Hub Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            return {'success': True, 'message': 'Reset email sent successfully'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to send email: {str(e)}'}
    
    def send_welcome_email(self, to_email: str, name: str) -> Dict[str, Any]:
        """Send welcome email to new users"""
        if not self.email_address or not self.email_password:
            return {'success': False, 'error': 'Email configuration not set'}
        
        try:
            msg = MIMEMultipart()
            msg['From'] = f"WhatsApp Message Hub <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = "Welcome to WhatsApp Message Hub!"
            
            body = f"""
            Hi {name},
            
            Welcome to WhatsApp Message Hub! Your account has been created successfully.
            
            You can now:
            - Set up your WhatsApp connection
            - Import and manage your contacts
            - Send bulk WhatsApp campaigns
            - Track your message delivery
            
            Get started by logging in and connecting your WhatsApp account.
            
            Best regards,
            WhatsApp Message Hub Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            return {'success': True, 'message': 'Welcome email sent successfully'}
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to send email: {str(e)}'}
