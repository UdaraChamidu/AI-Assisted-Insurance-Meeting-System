"""
Pydantic models for request/response schemas and data validation.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ParticipantRole(str, Enum):
    """Participant role in a session."""
    CUSTOMER = "customer"
    STAFF = "staff"


class SessionStatus(str, Enum):
    """Session lifecycle status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class BookingStatus(str, Enum):
    """Booking status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


# =============== Lead Models ===============

class LeadCreate(BaseModel):
    """Request to create a new lead."""
    phone_number: str = Field(..., description="Customer phone number")
    customer_name: Optional[str] = None
    notes: Optional[str] = None


class Lead(BaseModel):
    """Lead information."""
    id: str
    phone_number: str
    customer_name: Optional[str] = None
    notes: Optional[str] = None
    sms_sent: bool = False
    sms_sent_at: Optional[datetime] = None
    created_at: datetime


# =============== Booking Models ===============

class BookingCreate(BaseModel):
    """Request to create a booking."""
    lead_id: str
    customer_email: EmailStr
    scheduled_time: datetime
    duration_minutes: int = 30


class Booking(BaseModel):
    """Booking information."""
    id: str
    lead_id: str
    customer_email: str
    scheduled_time: datetime
    duration_minutes: int
    status: BookingStatus
    ms_booking_id: Optional[str] = None
    session_id: Optional[str] = None
    created_at: datetime


# =============== Session Models ===============

class SessionCreate(BaseModel):
    """Request to create a session."""
    booking_id: Optional[str] = None
    zoom_meeting_id: Optional[str] = None


class SessionParticipant(BaseModel):
    """Participant in a session."""
    role: ParticipantRole
    user_id: Optional[str] = None
    name: Optional[str] = None
    joined_at: datetime


class Session(BaseModel):
    """Session information."""
    id: str
    booking_id: Optional[str] = None
    zoom_meeting_id: Optional[str] = None
    zoom_meeting_password: Optional[str] = None
    status: SessionStatus
    participants: List[SessionParticipant] = []
    created_at: datetime
    expires_at: datetime
    ended_at: Optional[datetime] = None


# =============== Zoom Models ===============

class ZoomMeetingCreate(BaseModel):
    """Request to create a Zoom meeting."""
    topic: str = "Insurance Consultation"
    duration_minutes: int = 30
    session_id: str


class ZoomSignatureRequest(BaseModel):
    """Request to generate Zoom SDK signature."""
    meeting_number: str
    role: int = 0  # 0 for participant, 1 for host


class ZoomSignatureResponse(BaseModel):
    """Zoom SDK signature response."""
    signature: str
    sdk_key: str
    meeting_number: str
    password: Optional[str] = None


# =============== Transcription Models ===============

class TranscriptSegment(BaseModel):
    """A segment of transcribed speech."""
    text: str
    speaker: str  # "customer" or "staff"
    timestamp: datetime
    confidence: float = 1.0


class TranscriptQuery(BaseModel):
    """Query from transcript for AI processing."""
    session_id: str
    text: str
    speaker: str
    timestamp: datetime


# =============== AI/RAG Models ===============

class RAGQuery(BaseModel):
    """Query to the RAG system."""
    query: str
    session_id: Optional[str] = None
    top_k: int = 5


class RAGContext(BaseModel):
    """Retrieved context from RAG system."""
    chunks: List[Dict[str, Any]]
    query: str
    total_results: int


class AIResponse(BaseModel):
    """AI-generated response."""
    answer: str
    follow_up_question: Optional[str] = None
    confidence: float
    rag_context: Optional[RAGContext] = None
    timestamp: datetime


# =============== WebSocket Event Models ===============

class WSEvent(BaseModel):
    """WebSocket event base model."""
    event_type: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]


class TranscriptionEvent(WSEvent):
    """Transcription event sent via WebSocket."""
    event_type: str = "transcription.new"


class AIResponseEvent(WSEvent):
    """AI response event sent via WebSocket."""
    event_type: str = "ai.response"


class ParticipantJoinEvent(WSEvent):
    """Participant join event."""
    event_type: str = "session.join"


class ParticipantLeaveEvent(WSEvent):
    """Participant leave event."""
    event_type: str = "session.leave"


# =============== SMS Models ===============

class SMSRequest(BaseModel):
    """Request to send SMS."""
    to_phone_number: str
    booking_url: str
    customer_name: Optional[str] = None


class SMSResponse(BaseModel):
    """SMS send response."""
    success: bool
    message_sid: Optional[str] = None
    error: Optional[str] = None
