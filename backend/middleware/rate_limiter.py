"""
Rate limiting middleware using slowapi.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging

logger = logging.getLogger(__name__)

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Default rate limit
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
    strategy="fixed-window"
)


def setup_rate_limiting(app):
    """
    Configure rate limiting for FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    logger.info("Rate limiting configured")


# Rate limit decorators for different endpoints
# Usage: @limiter.limit("5/minute")
# Apply different limits based on endpoint sensitivity
RATE_LIMITS = {
    "auth_login": "5/minute",  # Prevent brute force
    "auth_register": "3/hour",  # Prevent spam accounts
    "sms_send": "10/hour",  # Limit SMS costs
    "ai_query": "20/minute",  # Prevent AI abuse
    "general_api": "100/minute"  # General endpoints
}
