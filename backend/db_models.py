"""
SQLAlchemy database models.
"""

from sqlalchemy import Column, String, Boolean, Integer, Float, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "ADMIN"
    AGENT = "AGENT"


class SessionStatus(str, enum.Enum):
    """Session status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class BookingStatus(str, enum.Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ParticipantRole(str, enum.Enum):
    """Participant role enumeration."""
    CUSTOMER = "customer"
    STAFF = "staff"


# ==================== MODELS ====================

class User(Base):
    """Staff user model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.AGENT)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions_participated = relationship("SessionParticipant", back_populates="user")


class Lead(Base):
    """Customer lead model."""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(50), nullable=False)
    customer_name = Column(String(255))
    notes = Column(Text)
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    bookings = relationship("Booking", back_populates="lead")


class Booking(Base):
    """Meeting booking model."""
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"))
    customer_email = Column(String(255), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING)
    ms_booking_id = Column(String(255))  # Microsoft Bookings ID
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lead = relationship("Lead", back_populates="bookings")
    session = relationship("Session")


class Session(Base):
    """Meeting session model."""
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zoom_meeting_id = Column(String(255))
    zoom_meeting_password = Column(String(255))
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)

    # Relationships
    booking = relationship("Booking", foreign_keys="[Booking.session_id]", uselist=False)
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    transcripts = relationship("Transcript", back_populates="session", cascade="all, delete-orphan")
    ai_responses = relationship("AIResponse", back_populates="session", cascade="all, delete-orphan")


class SessionParticipant(Base):
    """Session participant model."""
    __tablename__ = "session_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(SQLEnum(ParticipantRole), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    name = Column(String(255))
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="participants")
    user = relationship("User", back_populates="sessions_participated")


class Transcript(Base):
    """Conversation transcript model."""
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    speaker = Column(String(50), nullable=False)  # customer, staff, speaker_0, etc.
    text = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="transcripts")


class AIResponse(Base):
    """AI-generated response model."""
    __tablename__ = "ai_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    follow_up_question = Column(Text)
    confidence = Column(Float, default=0.75)
    rag_context = Column(Text)  # JSON string of retrieved context
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="ai_responses")
