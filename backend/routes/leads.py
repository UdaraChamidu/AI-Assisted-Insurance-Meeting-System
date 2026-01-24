"""
Lead management and SMS API routes.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from models import LeadCreate, Lead
from services.twilio_service import twilio_service
from config import settings
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leads", tags=["leads"])

# In-memory storage (use database in production)
_leads = {}


@router.post("", response_model=Lead)
async def create_lead_and_send_sms(request: LeadCreate):
    """
    Create a new lead and send SMS with booking link.
    """
    try:
        lead_id = str(uuid.uuid4())
        
        # Create lead
        lead = Lead(
            id=lead_id,
            phone_number=request.phone_number,
            customer_name=request.customer_name,
            notes=request.notes,
            sms_sent=False,
            sms_sent_at=None,
            created_at=datetime.utcnow()
        )
        
        # TODO: Replace with actual Microsoft Bookings URL
        booking_url = f"{settings.domain}/booking?lead_id={lead_id}"
        
        # Send SMS with description
        sms_response = twilio_service.send_booking_sms(
            to_phone_number=request.phone_number,
            booking_url=booking_url,
            customer_name=request.customer_name,
            description=request.notes  # Include notes/description in SMS
        )
        
        if sms_response.success:
            lead.sms_sent = True
            lead.sms_sent_at = datetime.utcnow()
        
        # Store lead
        _leads[lead_id] = lead
        
        logger.info(f"Created lead and sent SMS: {lead_id}")
        return lead
        
    except Exception as e:
        logger.error(f"Failed to create lead: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Lead])
async def list_leads():
    """List all leads."""
    return list(_leads.values())


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    """Get lead by ID."""
    lead = _leads.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/resend-sms")
async def resend_sms(lead_id: str):
    """Resend SMS to a lead."""
    lead = _leads.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    booking_url = f"{settings.domain}/booking?lead_id={lead_id}"
    
    sms_response = twilio_service.send_booking_sms(
        to_phone_number=lead.phone_number,
        booking_url=booking_url,
        customer_name=lead.customer_name,
        description=lead.notes  # Include notes when resending
    )
    
    if sms_response.success:
        lead.sms_sent_at = datetime.utcnow()
        return {"success": True, "message": "SMS sent successfully"}
    else:
        raise HTTPException(status_code=500, detail=sms_response.error)
