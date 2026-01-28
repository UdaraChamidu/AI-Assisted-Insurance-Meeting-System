
from config import settings
from services.openai_service import OpenAIService
from services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

class AIFactory:
    """
    Factory to return the configured AI Service (OpenAI or Gemini).
    """
    _instance = None
    
    @classmethod
    def get_service(cls):
        """
        Get the AI service instance based on configuration.
        """
        if cls._instance:
            return cls._instance
            
        provider = settings.ai_provider.lower()
        
        if provider == "openai":
            logger.info("AIFactory: Initializing OpenAI Service")
            cls._instance = OpenAIService()
        elif provider == "gemini":
            logger.info("AIFactory: Initializing Gemini Service")
            cls._instance = GeminiService()
        else:
            logger.warning(f"Unknown AI_PROVIDER '{provider}'. Defaulting to OpenAI.")
            cls._instance = OpenAIService()
            
        return cls._instance

# Global helper
def get_ai_service():
    return AIFactory.get_service()
