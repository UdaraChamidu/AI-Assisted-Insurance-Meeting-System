"""
Complete ElevenLabs text-to-speech integration with audio streaming.
"""

import requests
from config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Handles text-to-speech conversion using ElevenLabs API."""
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = settings.elevenlabs_voice_id or "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ) -> Optional[bytes]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert
            voice_id: Optional voice ID (uses default if not provided)
            model_id: Model to use
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)
        
        Returns:
            Audio bytes (MP3 format) or None if failed
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
            return None
        
        try:
            voice = voice_id or self.voice_id
            url = f"{self.base_url}/text-to-speech/{voice}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            audio_data = response.content
            logger.info(f"Generated {len(audio_data)} bytes of audio")
            
            return audio_data
        
        except requests.exceptions.Timeout:
            logger.error("ElevenLabs API timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"ElevenLabs API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"TTS failed: {str(e)}")
            return None
    
    def text_to_speech_stream(
        self,
        text: str,
        voice_id: Optional[str] = None
    ):
        """
        Stream text-to-speech audio (for real-time playback).
        
        Args:
            text: Text to convert
            voice_id: Optional voice ID
        
        Yields:
            Audio chunks
        """
        if not self.api_key:
            logger.warning("ElevenLabs API key not configured")
            return
        
        try:
            voice = voice_id or self.voice_id
            url = f"{self.base_url}/text-to-speech/{voice}/stream"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk
        
        except Exception as e:
            logger.error(f"TTS streaming failed: {str(e)}")
    
    def get_voices(self) -> Optional[list]:
        """
        Get available voices.
        
        Returns:
            List of voice objects
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/voices"
            headers = {"xi-api-key": self.api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("voices", [])
        
        except Exception as e:
            logger.error(f"Failed to get voices: {str(e)}")
            return None


# Global service instance
elevenlabs_service = ElevenLabsService()
