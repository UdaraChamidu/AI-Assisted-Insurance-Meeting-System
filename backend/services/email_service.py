"""
Email service using standard SMTP (smtplib).
Supports Gmail, Outlook, and other standard SMTP providers.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.server = settings.smtp_server
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email or self.username
        
        if not self.username or not self.password:
            logger.warning("SMTP credentials not found. Email service disabled.")

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send an email using SMTP.
        """
        if not self.username or not self.password:
             logger.warning("Cannot send email: SMTP credentials missing")
             return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to server
            logger.info(f"Connecting to SMTP server: {self.server}:{self.port}")
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()  # Secure the connection
            
            # Login
            server.login(self.username, self.password)
            
            # Send
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {str(e)}")
            return False

    def send_booking_confirmation(
        self, 
        to_email: str, 
        customer_name: str, 
        booking_time: str, 
        join_url: str
    ):
        """
        Send booking confirmation email.
        """
        subject = "Confirming your Insurance Consultation"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">Appointment Confirmed</h2>
            <p>Hi {customer_name},</p>
            <p>Your insurance consultation has been confirmed.</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>📅 Date:</strong> {booking_time}</p>
                <p style="margin: 5px 0;"><strong>💻 Join Link:</strong> <a href="{join_url}">{join_url}</a></p>
            </div>
            
            <p>Please click the link above at the scheduled time to join the video call.</p>
            <p>Best regards,<br>Insurance Agent Team</p>
        </div>
        """
        
        return self.send_email(to_email, subject, html_content)

# Global instance
email_service = EmailService()
