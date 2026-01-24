"""
FastAPI main application.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from database import init_db, close_db
from websocket.manager import connection_manager
from websocket.handlers import (
    handle_transcription_event,
    handle_participant_join,
    handle_participant_leave
)
from middleware.error_handler import register_error_handlers
from middleware.rate_limiter import setup_rate_limiting, limiter
import logging

# Import routers
from routes import sessions, zoom, leads, ai, auth, twilio_webhooks, bookings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.app_debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application stopped")


# Create FastAPI app
app = FastAPI(
    title="AI-Assisted Insurance Meeting System",
    description="Backend API for AI-powered insurance consultations via Zoom",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if not settings.is_production else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handlers
register_error_handlers(app)

# Setup rate limiting
setup_rate_limiting(app)

# Include routers
app.include_router(auth.router)  # Authentication
app.include_router(twilio_webhooks.router)  # Twilio webhooks
app.include_router(bookings.router)  # Bookings
app.include_router(sessions.router)
app.include_router(zoom.router)
app.include_router(leads.router)
app.include_router(ai.router)

@app.get("/")
@limiter.limit("20/minute")
async def root(request: Request):
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI-Assisted Insurance Meeting System",
        "version": "1.0.0"
    }

@app.get("/health")
@limiter.limit("20/minute")
async def health_check(request: Request):
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "websocket_connections": connection_manager.get_connection_count()
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    role: str = "staff"  # Query parameter: ?role=staff or ?role=customer
):
    """
    WebSocket endpoint for real-time communication.
    
    Args:
        session_id: Session identifier
        role: User role (staff or customer)
    """
    await connection_manager.connect(websocket, session_id, role)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "event_type": "connection.established",
            "session_id": session_id,
            "role": role,
            "message": "Connected successfully"
        })
        
        logger.info(f"WebSocket connected: session={session_id}, role={role}")
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            event_type = data.get('event_type')
            
            # Route events to handlers
            if event_type == 'transcription.new':
                await handle_transcription_event(session_id, data.get('data', {}))
            
            elif event_type == 'participant.joined':
                await handle_participant_join(session_id, data.get('data', {}))
            
            elif event_type == 'participant.left':
                await handle_participant_leave(session_id, data.get('data', {}))
            
            else:
                logger.warning(f"Unknown event type: {event_type}")
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, session_id, role)
        logger.info(f"WebSocket disconnected: session={session_id}, role={role}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        connection_manager.disconnect(websocket, session_id, role)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.app_debug
    )

 
