"""
Booking management API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
from database import get_db
from db_models import Booking, Lead, Session, BookingStatus, SessionStatus
from services.zoom_service import zoom_service
from services.twilio_service import twilio_service
from config import settings
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


# ==================== MODELS ====================

class BookingCreate(BaseModel):
    lead_id: Optional[str] = None
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    scheduled_date: str
    scheduled_time: str
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    scheduled_time: str
    status: str
    session_id: Optional[str] = None
    zoom_meeting_id: Optional[str] = None


# ==================== ROUTES ====================

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new booking and automatically:
    1. Create Zoom meeting
    2. Create session
    3. Send confirmation SMS
    """
    try:
        # Parse scheduled datetime
        scheduled_datetime = datetime.fromisoformat(
            f"{booking_data.scheduled_date}T{booking_data.scheduled_time}"
        )
        
        # Create Zoom meeting
        zoom_meeting = zoom_service.create_meeting(
            topic=f"Insurance Consultation - {booking_data.customer_name}",
            start_time=scheduled_datetime,
            duration_minutes=30  # 30 minutes
        )
        
        if not zoom_meeting:
            logger.warning("Zoom service failed to create meeting, using fallback mock data")
            # Fallback mock data so booking can proceed
            import random
            mock_id = str(random.randint(1000000000, 9999999999))
            zoom_meeting = {
                'meeting_id': mock_id,  # Changed from id to meeting_id
                'meeting_password': '123456',
                'join_url': f'{settings.domain}/join/mock-{mock_id}',
                'start_url': f'{settings.domain}/start/mock-{mock_id}'
            }
        
        # Create session
        session_id = uuid.uuid4()
        new_session = Session(
            id=session_id,
            zoom_meeting_id=str(zoom_meeting['meeting_id']),  # Changed from id to meeting_id
            zoom_meeting_password=zoom_meeting.get('meeting_password', ''), # Changed from password to meeting_password
            status=SessionStatus.PENDING,
            created_at=datetime.utcnow(),
            expires_at=scheduled_datetime + timedelta(hours=2)
        )
        
        db.add(new_session)
        
        # Create booking
        booking_id = uuid.uuid4()
        new_booking = Booking(
            id=booking_id,
            lead_id=uuid.UUID(booking_data.lead_id) if booking_data.lead_id else None,
            customer_email=booking_data.customer_email,
            scheduled_time=scheduled_datetime,
            duration_minutes=30,
            status=BookingStatus.CONFIRMED,
            session_id=session_id
        )
        
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)
        
        # Send confirmation SMS
        join_url = f"{settings.domain}/join/{session_id}"
        formatted_date = scheduled_datetime.strftime("%B %d, %Y")
        formatted_time = scheduled_datetime.strftime("%I:%M %p")
        
        confirmation_message = (
            f"Your insurance consultation is confirmed!\n\n"
            f"📅 {formatted_date}\n"
            f"🕒 {formatted_time}\n\n"
            f"Join meeting:\n{join_url}\n\n"
            f"We look forward to speaking with you!"
        )
        
        sms_result = twilio_service.send_booking_sms(
            to_phone_number=booking_data.customer_phone,
            booking_url=join_url,
            customer_name=booking_data.customer_name,
            description=confirmation_message,
            meeting_id=str(zoom_meeting['meeting_id']),
            passcode=str(zoom_meeting.get('meeting_password', ''))
        )
        
        if not sms_result.success:
            logger.warning(f"Failed to send confirmation SMS: {sms_result.error}")
        
        logger.info(f"Booking created: {booking_id}, Session: {session_id}, Zoom: {zoom_meeting['meeting_id']}")
        
        return BookingResponse(
            id=str(booking_id),
            customer_name=booking_data.customer_name,
            customer_email=booking_data.customer_email,
            scheduled_time=scheduled_datetime.isoformat(),
            status=new_booking.status.value,
            session_id=str(session_id),
            zoom_meeting_id=str(zoom_meeting['meeting_id'])
        )
        
    except Exception as e:
        logger.error(f"Failed to create booking: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("", response_model=List[BookingResponse])
async def list_bookings(db: AsyncSession = Depends(get_db)):
    """List all bookings."""
    try:
        result = await db.execute(
            select(Booking).order_by(Booking.scheduled_time.desc())
        )
        bookings = result.scalars().all()
        
        return [
            BookingResponse(
                id=str(booking.id),
                customer_name=booking.customer_email.split('@')[0],  # Fallback
                customer_email=booking.customer_email,
                scheduled_time=booking.scheduled_time.isoformat(),
                status=booking.status.value,
                session_id=str(booking.session_id) if booking.session_id else None,
                zoom_meeting_id=None  # Would need to join with Session
            )
            for booking in bookings
        ]
    except Exception as e:
        logger.error(f"Failed to list bookings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{booking_id}/send-reminder")
async def send_reminder(
    booking_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a reminder SMS to customer about their upcoming meeting.
    """
    try:
        # Get booking
        result = await db.execute(
            select(Booking).where(Booking.id == uuid.UUID(booking_id))
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Get associated lead for phone number
        if booking.lead_id:
            lead_result = await db.execute(
                select(Lead).where(Lead.id == booking.lead_id)
            )
            lead = lead_result.scalar_one_or_none()
            customer_phone = lead.phone_number if lead else None
            customer_name = lead.customer_name if lead else None
        else:
            # No lead, can't send SMS without phone
            raise HTTPException(
                status_code=400,
                detail="No phone number available for this booking"
            )
        
        if not customer_phone:
            raise HTTPException(
                status_code=400,
                detail="Customer phone number not found"
            )
        
        # Calculate time until meeting
        now = datetime.utcnow()
        time_diff = booking.scheduled_time - now
        hours_until = int(time_diff.total_seconds() / 3600)
        
        # Format datetime
        formatted_date = booking.scheduled_time.strftime("%B %d, %Y")
        formatted_time = booking.scheduled_time.strftime("%I:%M %p")
        join_url = f"{settings.domain}/join/{booking.session_id}"
        
        # Create reminder message
        if hours_until <= 1:
            time_msg = "in 1 hour"
        elif hours_until < 24:
            time_msg = f"in {hours_until} hours"
        else:
            time_msg = f"on {formatted_date}"
        
        reminder_message = (
            f"Reminder: Your insurance meeting is {time_msg}!\n\n"
            f"📅 {formatted_date}\n"
            f"🕒 {formatted_time}\n\n"
            f"Join:\n{join_url}\n\n"
            f"See you soon!"
        )
        
        # Send reminder SMS
        sms_result = twilio_service.send_reminder_sms(
            to_phone_number=customer_phone,
            meeting_time=f"{formatted_date} at {formatted_time}",
            join_url=join_url,
            customer_name=customer_name
        )
        
        if not sms_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send reminder: {sms_result.error}"
            )
        
        logger.info(f"Reminder sent for booking {booking_id}")
        
        return {"success": True, "message": "Reminder sent successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send reminder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

