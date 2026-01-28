
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_provider_switch():
    print("--- TESTING AI PROVIDER SWITCHING ---")
    
    # 1. Test OpenAI (Default/Configured)
    print("\n[1] Testing OpenAI Config...")
    os.environ['AI_PROVIDER'] = 'openai'
    from config import Settings
    settings = Settings(_env_file='.env') # Force reload
    print(f"    AI API Configured: {settings.ai_provider}")
    
    from services.ai_factory import AIFactory
    # Reset singleton/instance for test
    AIFactory._instance = None
    
    service = AIFactory.get_service()
    print(f"    Service Class: {service.__class__.__name__}")
    
    if service.__class__.__name__ == 'OpenAIService':
        print("    ✅ Correctly loaded OpenAIService")
    else:
        print("    ❌ Failed to load OpenAIService")
        
    from rag.embeddings import EmbeddingService
    # We need to re-init embedding service as it reads settings on init
    embed_service = EmbeddingService()
    print(f"    Embedding Provider: {embed_service.provider}")
    print(f"    Embedding Dimension: {embed_service.dimension}")
    
    if embed_service.dimension == 1024:
        print("    ✅ Correctly set 1024 dimensions")
    else:
        print("    ❌ Incorrect dimensions for OpenAI")

    # 2. Test Gemini (Simulated)
    print("\n[2] Testing Gemini Config (Simulated)...")
    # Store old val
    old_provider = os.environ.get('AI_PROVIDER')
    
    # Set to Gemini
    os.environ['AI_PROVIDER'] = 'gemini'
    # We must reload settings manually because the global 'settings' object is already instantiated
    # In a real app restart, it would load fresh. Here we hack it for testing.
    from config import settings as global_settings
    global_settings.ai_provider = 'gemini'
    
    # Reset Factory
    AIFactory._instance = None
    service_gemini = AIFactory.get_service()
    print(f"    Service Class: {service_gemini.__class__.__name__}")
    
    if service_gemini.__class__.__name__ == 'GeminiService':
        print("    ✅ Correctly loaded GeminiService")
    else:
        print("    ❌ Failed to load GeminiService")
        
    # Re-init embedding service
    # Note: EmbeddingService checks settings.ai_provider.lower()
    embed_service_gemini = EmbeddingService()
    print(f"    Embedding Provider: {embed_service_gemini.provider}")
    print(f"    Embedding Dimension: {embed_service_gemini.dimension}")
    
    if embed_service_gemini.dimension == 768:
        print("    ✅ Correctly set 768 dimensions")
    else:
        print("    ❌ Incorrect dimensions for Gemini")
        
    # Restore
    if old_provider:
        os.environ['AI_PROVIDER'] = old_provider
    global_settings.ai_provider = 'openai' # Restore global
    
    print("\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    test_provider_switch()
