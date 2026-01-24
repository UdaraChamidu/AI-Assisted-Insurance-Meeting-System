"""
Zoom API routes.
"""

from fastapi import APIRouter, HTTPException
from models import ZoomSignatureRequest, ZoomSignatureResponse
from services.zoom_service import zoom_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/zoom", tags=["zoom"])


@router.post("/signature", response_model=ZoomSignatureResponse)
async def generate_signature(request: ZoomSignatureRequest):
    """Generate Zoom Web SDK signature for joining a meeting."""
    try:
        signature = zoom_service.generate_sdk_signature(
            meeting_number=request.meeting_number,
            role=request.role
        )
        
        # Get meeting details to include password if available
        meeting_details = zoom_service.get_meeting_details(request.meeting_number)
        password = meeting_details.get('password') if meeting_details else None
        
        return ZoomSignatureResponse(
            signature=signature,
            sdk_key=zoom_service.sdk_key,
            meeting_number=request.meeting_number,
            password=password
        )
        
    except Exception as e:
        logger.error(f"Failed to generate signature: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meeting")
async def create_meeting(
    topic: str = "Insurance Consultation",
    duration: int = 30
):
    """Create a new Zoom meeting."""
    try:
        meeting_data = zoom_service.create_meeting(
            topic=topic,
            duration_minutes=duration
        )
        
        if not meeting_data:
            raise HTTPException(status_code=500, detail="Failed to create meeting")
        
        return meeting_data
        
    except Exception as e:
        logger.error(f"Failed to create meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meeting/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get Zoom meeting details."""
    try:
        meeting_details = zoom_service.get_meeting_details(meeting_id)
        
        if not meeting_details:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return meeting_details
        
    except Exception as e:
        logger.error(f"Failed to get meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
