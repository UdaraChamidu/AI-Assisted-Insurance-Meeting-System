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
            staff_only=True  # Customer doesn't see transcription
        )
        
        # If customer is speaking, process for AI
        if speaker == 'customer' and len(text.strip()) > 10:
            # Process in background to not block
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
    Process customer query through RAG and AI.
    
    Args:
        session_id: Session identifier
        query: Customer's question
    """
    try:
        logger.info(f"Processing query: {query[:100]}")
        
        # Send "processing" status to staff
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='ai.processing',
            data={'query': query},
            staff_only=True
        )
        
        # Retrieve context from RAG
        rag_result = retriever_service.retrieve(query, top_k=5)
        
        # Send RAG context to staff
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='rag.context',
            data={
                'query': query,
                'chunks': rag_result['chunks'],
                'total_results': rag_result['total_results']
            },
            staff_only=True
        )
        
        # Generate AI response
        ai_response = gemini_service.generate_response(
            query=query,
            context_chunks=rag_result['chunks']
        )
        
        # Send AI response to staff only
        await connection_manager.broadcast_event(
            session_id=session_id,
            event_type='ai.response',
            data={
                'query': query,
                'answer': ai_response['answer'],
                'follow_up_question': ai_response.get('follow_up_question'),
                'confidence': ai_response['confidence'],
                'timestamp': datetime.utcnow().isoformat()
            },
            staff_only=True
        )
        
        # Generate voice response for customer (MANDATORY)
        from services.elevenlabs_service import elevenlabs_service
        audio_data = elevenlabs_service.text_to_speech(ai_response['answer'])
        
        if audio_data:
            # Send voice audio to customer via WebSocket
            await connection_manager.send_audio_to_customer(
                session_id=session_id,
                audio_data=audio_data
            )
            logger.info(f"Voice response sent to customer for query: {query[:50]}")
        else:
            logger.warning("Failed to generate voice response, customer will not hear AI")
        
        logger.info(f"AI response and voice sent for query: {query[:50]}")
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        
        # Send error to staff
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
