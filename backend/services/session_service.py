"""
Session management service.
Handles session lifecycle, participant tracking, and session state.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import uuid
from models import (
    Session, SessionCreate, SessionStatus, SessionParticipant,
    ParticipantRole
)
from config import settings


class SessionService:
    """Manages meeting sessions."""
    
    def __init__(self):
        # In-memory storage (use Redis in production)
        self._sessions: Dict[str, Session] = {}
        
    def create_session(
        self,
        booking_id: Optional[str] = None,
        zoom_meeting_id: Optional[str] = None,
        zoom_meeting_password: Optional[str] = None
    ) -> Session:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=settings.session_expiry_hours)
        
        session = Session(
            id=session_id,
            booking_id=booking_id,
            zoom_meeting_id=zoom_meeting_id,
            zoom_meeting_password=zoom_meeting_password,
            status=SessionStatus.PENDING,
            participants=[],
            created_at=now,
            expires_at=expires_at
        )
        
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        session = self._sessions.get(session_id)
        if session:
            # Check if expired
            if datetime.utcnow() > session.expires_at:
                session.status = SessionStatus.EXPIRED
        return session
    
    def list_sessions(
        self,
        status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """List all sessions, optionally filtered by status."""
        sessions = list(self._sessions.values())
        if status:
            sessions = [s for s in sessions if s.status == status]
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    
    def add_participant(
        self,
        session_id: str,
        role: ParticipantRole,
        user_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[Session]:
        """Add a participant to a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Check if participant already exists
        for p in session.participants:
            if p.role == role and p.user_id == user_id:
                return session  # Already joined
        
        participant = SessionParticipant(
            role=role,
            user_id=user_id,
            name=name,
            joined_at=datetime.utcnow()
        )
        
        session.participants.append(participant)
        
        # Update session status to active if both participants joined
        if len(session.participants) >= 1:
            session.status = SessionStatus.ACTIVE
        
        return session
    
    def remove_participant(
        self,
        session_id: str,
        role: ParticipantRole,
        user_id: Optional[str] = None
    ) -> Optional[Session]:
        """Remove a participant from a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        session.participants = [
            p for p in session.participants
            if not (p.role == role and p.user_id == user_id)
        ]
        
        return session
    
    def end_session(self, session_id: str) -> Optional[Session]:
        """End a session."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        session.status = SessionStatus.COMPLETED
        session.ended_at = datetime.utcnow()
        
        return session
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        now = datetime.utcnow()
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if now > session.expires_at
        ]
        
        for sid in expired_ids:
            self._sessions[sid].status = SessionStatus.EXPIRED
        
        return len(expired_ids)


# Global service instance
session_service = SessionService()
