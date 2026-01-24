"""
Zoom service for meeting creation and SDK signature generation.
"""

import jwt
import time
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)


class ZoomService:
    """Handles Zoom meeting creation and SDK operations."""
    
    def __init__(self):
        self.account_id = settings.zoom_account_id
        self.client_id = settings.zoom_client_id
        self.client_secret = settings.zoom_client_secret
        self.sdk_key = settings.zoom_sdk_key
        self.sdk_secret = settings.zoom_sdk_secret
        self.base_url = "https://api.zoom.us/v2"
        self._oauth_token = None
        self._token_expires_at = 0

    def _get_oauth_token(self) -> Optional[str]:
        """Get or refresh Server-to-Server OAuth token."""
        if self._oauth_token and time.time() < self._token_expires_at:
            return self._oauth_token

        try:
            url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}"
            auth = (self.client_id, self.client_secret)
            
            response = requests.post(url, auth=auth)
            
            if response.status_code != 200:
                logger.error(f"Failed to get Zoom OAuth token: {response.text}")
                return None
                
            data = response.json()
            self._oauth_token = data['access_token']
            # Expires in 1 hour usually, set buffer of 5 mins
            self._token_expires_at = time.time() + data['expires_in'] - 300
            
            return self._oauth_token
        except Exception as e:
            logger.error(f"Error getting Zoom OAuth token: {str(e)}")
            return None

    def create_meeting(
        self,
        topic: str = "Insurance Consultation",
        duration_minutes: int = 30,
        start_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Zoom meeting.
        """
        # Check if Zoom S2S credentials are configured
        if not self.account_id or not self.client_id or not self.client_secret:
            logger.warning("Zoom S2S credentials not configured. Using mock meeting data.")
            return self._get_mock_meeting_data(topic, start_time, duration_minutes)

        try:
            token = self._get_oauth_token()
            if not token:
                logger.warning("Could not get OAuth token. Using mock data.")
                return self._get_mock_meeting_data(topic, start_time, duration_minutes)

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'topic': topic,
                'type': 1 if start_time is None else 2,
                'duration': duration_minutes,
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': True,
                    'mute_upon_entry': False,
                    'waiting_room': False,
                    'audio': 'both',
                    'auto_recording': 'cloud'
                }
            }
            
            if start_time:
                payload['start_time'] = start_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            response = requests.post(
                f'{self.base_url}/users/me/meetings',
                headers=headers,
                json=payload
            )
            
            if response.status_code != 201:
                logger.error(f"Zoom API Error: {response.text}")
                logger.warning("Falling back to mock meeting data")
                return self._get_mock_meeting_data(topic, start_time, duration_minutes)
            
            meeting_data = response.json()
            logger.info(f"Created Zoom meeting: {meeting_data.get('id')}")
            
            return {
                'meeting_id': str(meeting_data['id']),
                'meeting_password': meeting_data.get('password', ''),
                'join_url': meeting_data['join_url'],
                'start_url': meeting_data['start_url']
            }
            
        except Exception as e:
            logger.error(f"Failed to create Zoom meeting: {str(e)}")
            logger.warning("Falling back to mock meeting data due to error")
            return self._get_mock_meeting_data(topic, start_time, duration_minutes)

    def _get_mock_meeting_data(self, topic: str, start_time: Optional[datetime], duration: int):
        """Generate mock meeting data for testing/dev."""
        import random
        meeting_id = str(random.randint(1000000000, 9999999999))
        return {
            'meeting_id': meeting_id,
            'meeting_password': '123456',
            'join_url': f'https://zoom.us/j/{meeting_id}?pwd=123456',
            'start_url': f'https://zoom.us/s/{meeting_id}?pwd=123456'
        }
    
    def generate_sdk_signature(
        self,
        meeting_number: str,
        role: int = 0
    ) -> str:
        """
        Generate Zoom Meeting SDK JWT signature.
        For SDK v3.9.0+, the signature must include specific payload fields.
        """
        # Current timestamp
        iat = int(time.time())
        # Token expires in 2 hours
        exp = iat + 60 * 60 * 2

        # Payload for Zoom Meeting SDK
        payload = {
            'sdkKey': self.sdk_key,
            'mn': str(meeting_number),  # Meeting number as string
            'role': role,  # 0 = participant, 1 = host
            'iat': iat,
            'exp': exp,
            'appKey': self.sdk_key,  # For backward compatibility
            'tokenExp': exp
        }

        logger.info(f"Generating signature for meeting {meeting_number} with role {role}")
        logger.debug(f"Using SDK Key: {self.sdk_key[:10]}...")

        # Encode the JWT signature using HS256 algorithm
        signature = jwt.encode(payload, self.sdk_secret, algorithm='HS256')

        logger.info(f"Successfully generated SDK signature for meeting: {meeting_number}")

        return signature
    
    def get_meeting_details(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a Zoom meeting.
        """
        try:
            token = self._get_oauth_token()
            if not token:
                return None

            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(
                f'{self.base_url}/meetings/{meeting_id}',
                headers=headers
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get meeting details: {str(e)}")
            return None


# Global service instance
zoom_service = ZoomService()
