"""
Twilio SMS service for sending booking links to customers.
"""

from twilio.rest import Client
from config import settings
from models import SMSRequest, SMSResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TwilioService:
    """Handles SMS sending via Twilio."""
    
    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.from_number = settings.twilio_phone_number
    
    def send_booking_sms(
        self,
        to_phone_number: str,
        booking_url: str,
        customer_name: Optional[str] = None,
        description: Optional[str] = None,
        meeting_id: str = "",
        passcode: str = ""
    ) -> SMSResponse:
        """
        Send SMS with booking link to customer.
        
        Args:
            to_phone_number: Customer phone number
            booking_url: Microsoft Bookings URL
            customer_name: Optional customer name for personalization
            description: Optional description/notes to include in message
        
        Returns:
            SMSResponse with success status and message SID
        """
        try:
            # Construct message
            greeting = f"Hi {customer_name}" if customer_name else "Hello"
            
            # Build message body
            message_parts = [f"{greeting},\n"]
            
            # Add description if provided
            if description:
                message_parts.append(f"{description}\n\n")
            else:
                message_parts.append("Thank you for your interest in our insurance services.\n\n")
            
            # Add booking link and credentials
            message_parts.append(
                f"Please use the link below to schedule your consultation:\n\n"
                f"{booking_url}\n\n"
                f"Meeting ID: {meeting_id}\n"
                f"Passcode: {passcode}\n\n"
                f"We look forward to speaking with you!"
            )
            
            message_body = "".join(message_parts)
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone_number
            )
            
            logger.info(f"SMS sent to {to_phone_number}: {message.sid}")
            
            return SMSResponse(
                success=True,
                message_sid=message.sid
            )
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone_number}: {str(e)}")
            return SMSResponse(
                success=False,
                error=str(e)
            )
    
    def send_reminder_sms(
        self,
        to_phone_number: str,
        meeting_time: str,
        join_url: str,
        customer_name: Optional[str] = None
    ) -> SMSResponse:
        """
        Send meeting reminder with join link.
        
        Args:
            to_phone_number: Customer phone number
            meeting_time: Formatted meeting time
            join_url: Meeting join URL
            customer_name: Optional customer name
        
        Returns:
            SMSResponse with success status
        """
        try:
            greeting = f"Hi {customer_name}" if customer_name else "Hello"
            message_body = (
                f"{greeting},\n\n"
                f"Reminder: Your insurance consultation is scheduled for {meeting_time}.\n\n"
                f"Join the meeting here:\n{join_url}\n\n"
                f"See you soon!"
            )
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone_number
            )
            
            logger.info(f"Reminder SMS sent to {to_phone_number}: {message.sid}")
            
            return SMSResponse(
                success=True,
                message_sid=message.sid
            )
            
        except Exception as e:
            logger.error(f"Failed to send reminder to {to_phone_number}: {str(e)}")
            return SMSResponse(
                success=False,
                error=str(e)
            )


# Global service instance
twilio_service = TwilioService()
