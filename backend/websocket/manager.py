"""
WebSocket connection manager for real-time communication.
"""

from fastapi import WebSocket
from typing import Dict, Set, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time events."""
    
    def __init__(self):
        # Store connections by session_id and role
        # Format: {session_id: {role: {websocket_objects}}}
        self._connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        role: str = "staff"
    ):
        """
        Accept and register a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            role: User role ('staff' or 'customer')
        """
        await websocket.accept()
        
        if session_id not in self._connections:
            self._connections[session_id] = {}
        
        if role not in self._connections[session_id]:
            self._connections[session_id][role] = set()
        
        self._connections[session_id][role].add(websocket)
        
        logger.info(f"Client connected: session={session_id}, role={role}")
    
    def disconnect(
        self,
        websocket: WebSocket,
        session_id: str,
        role: str = "staff"
    ):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            session_id: Session identifier
            role: User role
        """
        if session_id in self._connections:
            if role in self._connections[session_id]:
                self._connections[session_id][role].discard(websocket)
                
                # Clean up empty sets
                if not self._connections[session_id][role]:
                    del self._connections[session_id][role]
                
                # Clean up empty sessions
                if not self._connections[session_id]:
                    del self._connections[session_id]
        
        logger.info(f"Client disconnected: session={session_id}, role={role}")
    
    async def send_to_session(
        self,
        session_id: str,
        message: dict,
        role: Optional[str] = None
    ):
        """
        Send message to all connections in a session or specific role.
        
        Args:
            session_id: Session identifier
            message: Message data to send
            role: Optional role filter ('staff' or 'customer')
        """
        if session_id not in self._connections:
            return
        
        message_json = json.dumps(message)
        
        # Get target connections
        if role:
            # Send to specific role only
            connections = self._connections[session_id].get(role, set())
        else:
            # Send to all roles in session
            connections = set()
            for role_connections in self._connections[session_id].values():
                connections.update(role_connections)
        
        # Send to all target connections
        for connection in connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Failed to send message: {str(e)}")
    
    async def send_to_staff_only(
        self,
        session_id: str,
        message: dict
    ):
        """
        Send message only to staff members (AI responses, context, etc).
        
        Args:
            session_id: Session identifier
            message: Message data
        """
        await self.send_to_session(session_id, message, role="staff")
    
    async def send_audio_to_customer(
        self,
        session_id: str,
        audio_data: bytes
    ):
        """
        Send audio data to customer for voice playback.
        
        Args:
            session_id: Session identifier
            audio_data: Audio bytes (MP3 format)
        """
        import base64
        
        # Encode audio to base64 for JSON transmission
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        message = {
            'event_type': 'ai.voice_response',
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'audio': audio_base64,
                'format': 'mp3'
            }
        }
        
        # Send only to customer
        await self.send_to_session(session_id, message, role="customer")
        logger.info(f"Sent {len(audio_data)} bytes of audio to customer")
    
    async def broadcast_event(
        self,
        session_id: str,
        event_type: str,
        data: dict,
        staff_only: bool = False
    ):
        """
        Broadcast an event to session participants.
        
        Args:
            session_id: Session identifier
            event_type: Type of event
            data: Event data
            staff_only: If True, send only to staff
        """
        message = {
            'event_type': event_type,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        if staff_only:
            await self.send_to_staff_only(session_id, message)
        else:
            await self.send_to_session(session_id, message)
    
    def get_connection_count(
        self,
        session_id: Optional[str] = None
    ) -> int:
        """
        Get number of active connections.
        
        Args:
            session_id: Optional session filter
        
        Returns:
            Connection count
        """
        if session_id:
            if session_id in self._connections:
                return sum(
                    len(conns)
                    for conns in self._connections[session_id].values()
                )
            return 0
        else:
            # Total across all sessions
            return sum(
                len(conns)
                for session in self._connections.values()
                for conns in session.values()
            )


# Global connection manager instance
connection_manager = ConnectionManager()
