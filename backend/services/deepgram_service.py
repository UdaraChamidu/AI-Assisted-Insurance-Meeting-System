"""
Deepgram service for real-time speech-to-text transcription.
Updated for Deepgram SDK v3.
"""

from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from config import settings
import logging
import asyncio
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)


class DeepgramService:
    """Handles real-time audio transcription using Deepgram SDK v3."""
    
    def __init__(self):
        self.api_key = settings.deepgram_api_key
        # v3 uses DeepgramClient
        self.client = DeepgramClient(self.api_key)
        self._connections: Dict[str, Any] = {}
        self._on_transcript_callbacks: Dict[str, Callable] = {}

    def is_connected(self, session_id: str) -> bool:
        """Check if a session has an active Deepgram connection."""
        return session_id in self._connections
    
    async def start_transcription(
        self,
        session_id: str,
        on_transcript: Callable[[str, str, float], None],
        language: str = "en-US"
    ):
        """
        Start real-time transcription for a session.
        """
        print(f"DEBUG: DeepgramService.start_transcription called for {session_id}")
        try:
            # 1. Store callback and current loop for this session
            self._on_transcript_callbacks[session_id] = on_transcript
            loop = asyncio.get_running_loop() # Capture the main loop

            # ... (rest of configuration) ...
            print("DEBUG: Configuring LiveOptions")
            options = LiveOptions(
                model="nova-2",
                language=language,
                smart_format=True,
                interim_results=True,
                punctuate=True,
                diarize=True,
                utterance_end_ms=1000
            )

            # ... (callbacks) ...
            service = self  # Capture the DeepgramService instance
            
            # 4. Initialize Connection
            print("DEBUG: Creating Deepgram connection object", flush=True)
            dg_connection = self.client.listen.live.v("1")
            
            # ... (register listeners) ...
            def on_message(_, result, **kwargs):
                print(f"DEBUG: on_message callback triggered!", flush=True)
                service._handle_transcript_event(session_id, result, loop)
            
            def on_error(_, error, **kwargs):
                print(f"DEBUG: Deepgram Error: {error}", flush=True)
                logger.error(f"Deepgram Error for session {session_id}: {error}")
            
            def on_close(_, close, **kwargs):
                print(f"DEBUG: Deepgram Connection closed for session {session_id}", flush=True)
                logger.info(f"Deepgram Connection closed for session {session_id}")
                if session_id in service._connections:
                    del service._connections[session_id]

            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)
            dg_connection.on(LiveTranscriptionEvents.Close, on_close)
            
            print("DEBUG: Starting connection...")
            if dg_connection.start(options) is False:
                print("DEBUG: dg_connection.start() returned False")
                raise Exception("Failed to start Deepgram connection")

            # Store connection
            self._connections[session_id] = dg_connection
            print(f"DEBUG: Deepgram connection started and stored for {session_id}")
            logger.info(f"Started Deepgram v3 transcription for session: {session_id}")

        except Exception as e:
            print(f"DEBUG: Exception in start_transcription: {e}")
            logger.error(f"Failed to start transcription: {str(e)}")
            if session_id in self._connections:
                del self._connections[session_id]
            raise

    def _handle_transcript_event(self, session_id, result, loop):
        """Internal handler for parsing Deepgram results."""
        try:
            callback = self._on_transcript_callbacks.get(session_id)
            if not callback:
                return

            if result.channel and result.channel.alternatives:
                alternative = result.channel.alternatives[0]
                transcript = alternative.transcript
                confidence = alternative.confidence
                
                if transcript and len(transcript.strip()) > 0:
                    # Determine speaker
                    speaker = "customer" # Default
                    
                    logging.info(f"Transcript [{session_id}]: {transcript}")
                    print(f"DEBUG: Dispatching transcript to WebSocket: {transcript[:30]}...")
                    
                    # Run callback on the main loop
                    if loop and callback:
                        asyncio.run_coroutine_threadsafe(
                            callback(transcript, speaker, confidence),
                            loop
                        )
            
        except Exception as e:
            logger.error(f"Error handling transcript event: {e}")
            print(f"DEBUG Error handling transcript: {e}")

    async def send_audio(self, session_id: str, audio_data: bytes):
        """Send audio bytes to Deepgram."""
        connection = self._connections.get(session_id)
        if connection:
            try:
                # v3 uses send()
                connection.send(audio_data)
            except Exception as e:
                logger.error(f"Failed to send audio to Deepgram: {str(e)}")
        else:
            # Auto-start if missing? 
            # Or just warn users they didn't join properly?
            logger.warning(f"No Deepgram connection found for session: {session_id}")

    async def stop_transcription(self, session_id: str):
        """Stop transcription."""
        connection = self._connections.get(session_id)
        if connection:
            try:
                connection.finish()
                del self._connections[session_id]
                if session_id in self._on_transcript_callbacks:
                    del self._on_transcript_callbacks[session_id]
                logger.info(f"Stopped transcription for session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to stop transcription: {str(e)}")

# Global service instance
deepgram_service = DeepgramService()
