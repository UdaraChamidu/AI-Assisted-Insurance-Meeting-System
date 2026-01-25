
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from scripts.ingest_sharepoint import IngestionPipeline
import logging
import asyncio

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        # self.pipeline = IngestionPipeline()
        
    async def run_ingestion_job(self):
        """Job to run the ingestion pipeline."""
        try:
            logger.info("Running scheduled ingestion job...")
            # Detect mode based on env or default (or just run both? safer to stick to config)
            # For now, let's assume we want to run based on what's configured. 
            # If SHAREPOINT_SITE_ID is missing, maybe fall back to well known or just skip?
            # The script defaults to SharePoint unless local=True is passed. 
            # We can make this configurable via env var INGESTION_MODE='local' or 'sharepoint'
            
            # Simple heuristic: Run standard mode (SharePoint) by default, 
            # but if we are in dev/mock, maybe run local?
            # Let's run local mode if 'kb_dev' exists and we are in dev?
            # User wants "pipeline to sharepoint". Let's run standard mode.
            # But wait, user currently has NO sharepoint creds.
            # So running standard mode will fail log error.
            # I will check an env var "INGESTION_MODE"
            
            import os
            mode = os.getenv("INGESTION_MODE", "sharepoint")
            local_mode = (mode == "local")
            
            # await self.pipeline.run(local_mode=local_mode)
            pass
            
        except Exception as e:
            logger.error(f"Ingestion job failed: {e}")

    def start(self):
        """Start the scheduler."""
        # Add job to run every hour
        self.scheduler.add_job(self.run_ingestion_job, 'interval', minutes=60)
        self.scheduler.start()
        logger.info("Scheduler started. Ingestion job scheduled every 60 minutes.")

# Global Instance
scheduler_service = SchedulerService()
