"""
WebSocket event handlers for processing real-time events.
"""

from typing import Dict, Any
from datetime import datetime
from websocket.manager import connection_manager
from services.gemini_service import gemini_service
from rag.retriever import retriever_service
import logging
import asyncio

logger = logging.getLogger(__name__)


async def handle_transcription_event(
    session_id: str,
    transcript_data: Dict[str, Any]
):
    """
    Handle incoming transcription event.
    Sends to staff and processes for AI if from customer.
    
    Args:
        session_id: Session identifier
        transcript_data: Transcript information
    """
    try:
        text = transcript_data.get('text', '')
        speaker = transcript_data.get('speaker', 'customer')
        
        # Send transcription to staff
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='transcription.new',
            data=transcript_data,
            staff_only=True
        )
        
        # Trigger AI on valid text (Relaxed speaker check for testing)
        if len(text.strip()) > 10:
            # Process in background
            asyncio.create_task(
                process_customer_query(session_id, text)
            )
    
    except Exception as e:
        logger.error(f"Error handling transcription: {str(e)}")


async def process_customer_query(
    session_id: str,
    query: str
):
    """
    Process query through RAG and AI.
    """
    try:
        logger.info(f"Processing query: {query[:100]}")
        
        # 1. Notify Staff: Processing
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='ai.processing',
            data={'query': query},
            staff_only=True
        )
        
        # 2. RAG Retrieval (Optional / Try-Except)
        context_chunks = []
        try:
            rag_result = retriever_service.retrieve(query, top_k=3)
            context_chunks = rag_result.get('chunks', [])
            
            # Send RAG context to staff
            await connection_manager.broadcast_event(
                session_id=session_id,
                event_type='rag.context',
                data={
                    'query': query,
                    'chunks': context_chunks,
                    'total_results': rag_result.get('total_results', 0)
                },
                staff_only=True
            )
        except Exception as e:
            logger.warning(f"RAG Retrieval failed (skipping): {e}")

        # 3. Generate AI Response (Gemini)
        ai_response = gemini_service.generate_response(
            query=query,
            context_chunks=context_chunks
        )
        
        # 4. Send AI Answer to Staff
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='ai.response',
            data={
                'query': query,
                'answer': ai_response['answer'],
                'text': ai_response['answer'], # Added for frontend compatibility
                'follow_up_question': ai_response.get('follow_up_question'),
                'confidence': ai_response['confidence'],
                'timestamp': datetime.utcnow().isoformat()
            },
            staff_only=False
        )
        
        # 5. Voice Generation (Optional / Try-Except)
        try:
            from services.elevenlabs_service import elevenlabs_service
            audio_data = elevenlabs_service.text_to_speech(ai_response['answer'])
            
            if audio_data:
                await connection_manager.send_audio_to_customer(
                    session_id=session_id,
                    audio_data=audio_data
                )
                logger.info("Voice response sent")
        except Exception as e:
            logger.warning(f"Voice generation failed (skipping): {e}")
            
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='ai.error',
            data={'error': str(e)},
            staff_only=True
        )


async def handle_participant_join(
    session_id: str,
    participant_data: Dict[str, Any]
):
    """
    Handle participant join event.
    
    Args:
        session_id: Session identifier
        participant_data: Participant information
    """
    try:
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='session.participant_joined',
            data=participant_data,
            staff_only=False  # Both can see
        )
    except Exception as e:
        logger.error(f"Error handling participant join: {str(e)}")


async def handle_participant_leave(
    session_id: str,
    participant_data: Dict[str, Any]
):
    """
    Handle participant leave event.
    
    Args:
        session_id: Session identifier
        participant_data: Participant information
    """
    try:
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='session.participant_left',
            data=participant_data,
            staff_only=False
        )
    except Exception as e:
        logger.error(f"Error handling participant leave: {str(e)}")


async def handle_start_transcription(session_id: str):
    """
    Start transcription for a session (Idempotent).
    """
    try:
        from services.deepgram_service import deepgram_service
        
        # Check if already connected
        print(f"DEBUG: Checking if already connected for {session_id}", flush=True)
        if deepgram_service.is_connected(session_id):
            print(f"DEBUG: Already connected, skipping startup for {session_id}", flush=True)
            return

        print(f"DEBUG: Not connected, starting new connection for {session_id}", flush=True)
        
        # Callback to handle new transcripts
        async def on_transcript(text, speaker, confidence):
            # Construct transcript data
            data = {
                "text": text,
                "speaker": speaker,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
                "is_final": True
            }
            # Process via existing handler
            await handle_transcription_event(session_id, data)

        # Start Deepgram
        await deepgram_service.start_transcription(
            session_id=session_id,
            on_transcript=on_transcript
        )
        logger.info(f"Transcription service started for session {session_id}")

    except Exception as e:
        logger.error(f"Failed to start transcription handler: {e}")
