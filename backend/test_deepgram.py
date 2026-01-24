import asyncio
import os
import logging
# Load env vars
from dotenv import load_dotenv
load_dotenv(dotenv_path="d:/Insurance Agent/backend/.env")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions

API_KEY = os.getenv("DEEPGRAM_API_KEY")

async def test_deepgram():
    print(f"Testing Deepgram with Key: {API_KEY[:5]}...")
    
    try:
        client = DeepgramClient(API_KEY)
        dg_connection = client.listen.live.v("1")

        def on_open(self, open, **kwargs):
            print("Connection Open")

        def on_message(self, result, **kwargs):
            print(f"Message Received: {result.channel.alternatives[0].transcript}")

        def on_error(self, error, **kwargs):
            print(f"Error Received: {error}")

        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2", 
            language="en-US", 
            smart_format=True
        )

        print("Attempting to start connection...")
        if dg_connection.start(options) is False:
            print("❌ Failed to start connection")
            return
        
        print("✅ Connection started successfully! Waiting 5 seconds...")
        await asyncio.sleep(5)
        
        print("Finishing...")
        dg_connection.finish()
        print("✅ Finished")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: DEEPGRAM_API_KEY not found in .env")
    else:
        asyncio.run(test_deepgram())
