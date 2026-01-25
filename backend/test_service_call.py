
import os
import sys
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Add current dir to path to find config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.gemini_service import gemini_service
    print("Service initialized.")
    
    print("Testing generate_response with empty context (Simulating /chat)...")
    response = gemini_service.generate_response(
        query="What is an insurance premium?",
        context_chunks=[]
    )
    
    print("\n--- RESPONSE ---")
    print(response)
    
except Exception as e:
    print("\n--- CRITICAL FAILURE ---")
    print(e)
    import traceback
    traceback.print_exc()
