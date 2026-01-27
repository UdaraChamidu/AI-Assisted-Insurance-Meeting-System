from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.ingestion_service import ingestion_service
import logging

router = APIRouter(prefix="/rag", tags=["RAG"])
logger = logging.getLogger(__name__)

async def run_pipeline_task():
    """Background task wrapper."""
    try:
        await ingestion_service.run_pipeline()
    except Exception as e:
        logger.error(f"Manual ingestion failed: {e}")

@router.post("/trigger")
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Manually trigger the SharePoint ingestion pipeline.
    Runs in background.
    """
    background_tasks.add_task(run_pipeline_task)
    return {"status": "started", "message": "Ingestion pipeline triggered in background"}
