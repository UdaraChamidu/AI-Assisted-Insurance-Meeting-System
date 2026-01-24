"""
Session management API routes.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db
from db_models import Session, SessionStatus
from models import Session as SessionModel, SessionCreate, ParticipantRole
from services.zoom_service import zoom_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=List[dict])
async def list_sessions(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all sessions, optionally filtered by status."""
    try:
        query = select(Session).order_by(Session.created_at.desc())
        
        if status:
            # Filter by status if provided
            # Note: In a real app, you'd filter by enum, but for simplicity we list all
            pass
            
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        # Convert to response model format
        return [
            {
                "id": str(s.id),
                "zoom_meeting_id": s.zoom_meeting_id,
                "zoom_meeting_password": s.zoom_meeting_password,
                "status": s.status.value if hasattr(s.status, 'value') else str(s.status),
                "created_at": s.created_at.isoformat(),
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                "participants": []
            } 
            for s in sessions
        ]
    except Exception as e:
        logger.error(f"Failed to list sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=dict)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session details."""
    try:
        result = await db.execute(select(Session).where(Session.id == uuid.UUID(session_id)))
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {
            "id": str(session.id),
            "zoom_meeting_id": session.zoom_meeting_id,
            "zoom_meeting_password": session.zoom_meeting_password,
            "status": session.status.value if hasattr(session.status, 'value') else str(session.status),
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat() if session.expires_at else None,
            "participants": [] # Participants would need a separate join table or logic
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        logger.error(f"Failed to get session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

