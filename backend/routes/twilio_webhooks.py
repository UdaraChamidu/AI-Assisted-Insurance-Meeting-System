"""
Twilio webhook endpoints for SMS status callbacks.
"""

from fastapi import APIRouter, Form, Request
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/twilio", tags=["twilio-webhooks"])


@router.post("/sms-webhook")
async def sms_incoming_webhook(
    request: Request,
    MessageSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageStatus: Optional[str] = Form(None)
):
    """
    Handle incoming SMS messages from Twilio.
    
    This webhook is called when someone sends an SMS TO your Twilio number.
    You can use this to process customer replies.
    """
    try:
        logger.info(f"Incoming SMS from {From}: {Body}")
        
        # TODO: Process incoming SMS
        # For example:
        # - Match to existing lead
        # - Update booking status
        # - Trigger notifications
        
        return {
            "status": "ok",
            "message": "SMS received"
        }
    
    except Exception as e:
        logger.error(f"Error processing incoming SMS: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post("/sms-status")
async def sms_status_callback(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    To: str = Form(...),
    From: str = Form(None),
    ErrorCode: Optional[str] = Form(None),
    ErrorMessage: Optional[str] = Form(None)
):
    """
    Handle SMS delivery status updates from Twilio.
    
    Called when SMS status changes: queued → sending → sent → delivered
    Or: failed, undelivered
    """
    try:
        logger.info(f"SMS Status Update: {MessageSid} - {MessageStatus}")
        
        if ErrorCode:
            logger.error(f"SMS Error {ErrorCode}: {ErrorMessage}")
        
        # TODO: Update SMS status in database
        # For example:
        # - Update lead record with delivery status
        # - Retry if failed
        # - Send notification to admin if delivery failed
        
        return {
            "status": "ok",
            "message_sid": MessageSid,
            "message_status": MessageStatus
        }
    
    except Exception as e:
        logger.error(f"Error processing SMS status: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.post("/voice-webhook")
async def voice_incoming_webhook(
    request: Request,
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...)
):
    """
    Handle incoming voice calls to your Twilio number.
    
    Returns TwiML to control call behavior.
    """
    try:
        logger.info(f"Incoming call from {From}")
        
        # Return TwiML to play message and hang up
        from fastapi.responses import Response
        
        twiml_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">
        Thank you for calling our insurance consultation service. 
        Please use the meeting link sent to you via SMS to join your scheduled video consultation.
        If you have questions, please reply to the SMS or email us.
    </Say>
    <Hangup/>
</Response>"""
        
        return Response(content=twiml_response, media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Error processing incoming call: {str(e)}")
        return Response(content="<Response><Hangup/></Response>", media_type="application/xml")
