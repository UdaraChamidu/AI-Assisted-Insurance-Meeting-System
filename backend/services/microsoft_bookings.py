"""
Complete Microsoft Bookings OAuth integration.
"""

from msal import ConfidentialClientApplication
from config import settings
from typing import Optional, Dict, Any
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MicrosoftBookingsService:
    """Handles Microsoft Bookings integration via Graph API."""
    
    def __init__(self):
        self.client_id = settings.ms_client_id
        self.client_secret = settings.ms_client_secret
        self.tenant_id = settings.ms_tenant_id
        self.business_id = settings.ms_booking_business_id
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        
        # Create MSAL app
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """
        Get OAuth authorization URL for admin consent.
        
        Args:
            redirect_uri: Redirect URI after consent
        
        Returns:
            Authorization URL
        """
        return self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
    
    def get_access_token_from_code(
        self,
        code: str,
        redirect_uri: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in auth request
        
        Returns:
            Token response with access_token and refresh_token
        """
        try:
            result = self.app.acquire_token_by_authorization_code(
                code=code,
                scopes=self.scopes,
                redirect_uri=redirect_uri
            )
            
            if "access_token" in result:
                logger.info("Successfully acquired access token")
                return result
            else:
                logger.error(f"Failed to get token: {result.get('error_description')}")
                return None
        
        except Exception as e:
            logger.error(f"Token exchange failed: {str(e)}")
            return None
    
    def get_access_token(self) -> Optional[str]:
        """
        Get access token using client credentials flow.
        
        Returns:
            Access token string
        """
        try:
            result = self.app.acquire_token_for_client(scopes=self.scopes)
            
            if "access_token" in result:
                return result["access_token"]
            else:
                logger.error(f"Failed to get token: {result.get('error_description')}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            return None
    
    def create_booking(
        self,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        start_time: datetime,
        duration_minutes: int = 30,
        notes: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a booking via Microsoft Bookings API.
        
        Args:
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone
            start_time: Booking start time
            duration_minutes: Duration in minutes
            notes: Optional notes
        
        Returns:
            Booking details or None
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Calculate end time
            from datetime import timedelta
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            # Booking payload
            payload = {
                "customerName": customer_name,
                "customerEmailAddress": customer_email,
                "customerPhone": customer_phone,
                "startDateTime": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "UTC"
                },
                "endDateTime": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "UTC"
                },
                "customerNotes": notes
            }
            
            # Create booking
            url = f"{self.graph_endpoint}/bookingBusinesses/{self.business_id}/appointments"
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            booking_data = response.json()
            logger.info(f"Created booking: {booking_data.get('id')}")
            
            return booking_data
        
        except Exception as e:
            logger.error(f"Failed to create booking: {str(e)}")
            return None
    
    def get_booking(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Get booking details.
        
        Args:
            booking_id: Microsoft Bookings ID
        
        Returns:
            Booking details
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            url = f"{self.graph_endpoint}/bookingBusinesses/{self.business_id}/appointments/{booking_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Failed to get booking: {str(e)}")
            return None
    
    def send_booking_email(
        self,
        customer_email: str,
        customer_name: str,
        meeting_time: str,
        join_url: str
    ) -> bool:
        """
        Send booking confirmation email with join link.
        
        Args:
            customer_email: Customer email
            customer_name: Customer name
            meeting_time: Formatted meeting time
            join_url: Custom join URL
        
        Returns:
            True if successful
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Email content
            email_body = f"""
            <html>
            <body>
                <h2>Your Insurance Consultation is Confirmed</h2>
                <p>Hello {customer_name},</p>
                <p>Your consultation is scheduled for <strong>{meeting_time}</strong>.</p>
                <p>To join the meeting, please click the link below at the scheduled time:</p>
                <p><a href="{join_url}" style="background-color: #4CAF50; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;">Join Meeting</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{join_url}</p>
                <p>We look forward to speaking with you!</p>
                <p>Best regards,<br>Insurance Team</p>
            </body>
            </html>
            """
            
            payload = {
                "message": {
                    "subject": "Your Insurance Consultation - Meeting Link",
                    "body": {
                        "contentType": "HTML",
                        "content": email_body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": customer_email
                            }
                        }
                    ]
                },
                "saveToSentItems": "false"
            }
            
            # Send email via Graph API
            url = f"{self.graph_endpoint}/me/sendMail"
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            logger.info(f"Sent booking email to {customer_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False


# Global service instance
ms_bookings_service = MicrosoftBookingsService()
