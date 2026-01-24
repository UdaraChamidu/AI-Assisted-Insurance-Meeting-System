"""
Deepgram service for real-time speech-to-text transcription.
"""

from deepgram import Deepgram
from config import settings
import logging
import asyncio
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


class DeepgramService:
    """Handles real-time audio transcription using Deepgram."""
    
    def __init__(self):
        self.api_key = settings.deepgram_api_key
        self.deepgram = Deepgram(self.api_key)
        self._connections: Dict[str, Any] = {}
    
    async def start_transcription(
        self,
        session_id: str,
        on_transcript: Callable[[str, str, float], None],
        language: str = "en-US"
    ):
        """
        Start real-time transcription for a session.
        
        Args:
            session_id: Unique session identifier
            on_transcript: Callback function(text, speaker, confidence)
            language: Language code for transcription 
        """
        try:
            # Configure transcription options
            options = {
                'punctuate': True,
                'interim_results': True,
                'language': language,
                'model': 'nova-2',
                'smart_format': True,
                'diarize': True,  # Speaker diarization
                'utterance_end_ms': 1000
            }
            
            # Create live transcription connection
            connection = self.deepgram.transcription.live(options)
            
            # Handle transcript events
            def handle_transcript(data):
                """Process incoming transcript data."""
                try:
                    if data.get('is_final'):
                        channel = data['channel']
                        alternatives = channel['alternatives']
                        
                        if alternatives:
                            transcript = alternatives[0]['transcript']
                            confidence = alternatives[0]['confidence']
                            
                            # Determine speaker (simplified - use diarization in production)
                            speaker = "customer"  # Default to customer
                            if 'speaker' in alternatives[0]:
                                speaker_id = alternatives[0]['speaker']
                                speaker = f"speaker_{speaker_id}"
                            
                            if transcript.strip():
                                on_transcript(transcript, speaker, confidence)
                                logger.info(f"Transcript [{speaker}]: {transcript}")
                
                except Exception as e:
                    logger.error(f"Error processing transcript: {str(e)}")
            
            # Register event handler
            connection.registerHandler(
                connection.event.CLOSE,
                lambda c: logger.info(f"Connection closed for session {session_id}")
            )
            connection.registerHandler(
                connection.event.TRANSCRIPT_RECEIVED,
                handle_transcript
            )
            
            # Store connection
            self._connections[session_id] = connection
            
            logger.info(f"Started transcription for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to start transcription: {str(e)}")
            raise
    
    async def send_audio(
        self,
        session_id: str,
        audio_data: bytes
    ):
        """
        Send audio data for transcription.
        
        Args:
            session_id: Session identifier
            audio_data: Raw audio bytes (PCM16, 16kHz recommended)
        """
        connection = self._connections.get(session_id)
        if connection:
            try:
                connection.send(audio_data)
            except Exception as e:
                logger.error(f"Failed to send audio: {str(e)}")
    
    async def stop_transcription(self, session_id: str):
        """
        Stop transcription for a session.
        
        Args:
            session_id: Session identifier
        """
        connection = self._connections.get(session_id)
        if connection:
            try:
                connection.finish()
                del self._connections[session_id]
                logger.info(f"Stopped transcription for session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to stop transcription: {str(e)}")


# Global service instance
deepgram_service = DeepgramService()
