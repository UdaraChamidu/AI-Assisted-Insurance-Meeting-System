"""
Simple Deepgram test to verify API key and connection.
Run this to test if Deepgram is working at all.
"""

import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import os
from dotenv import load_dotenv

load_dotenv()

async def test_deepgram():
    print("=" * 60)
    print("DEEPGRAM DIAGNOSTIC TEST")
    print("=" * 60)
    
    api_key = os.getenv("DEEPGRAM_API_KEY")
    print(f"\n1. API Key loaded: {api_key[:20]}..." if api_key else "ERROR: No API key!")
    
    if not api_key:
        print("FAILED: No Deepgram API key in .env")
        return
    
    try:
        # Initialize client
        print("\n2. Creating Deepgram client...")
        client = DeepgramClient(api_key)
        print("✓ Client created successfully")
        
        # Create connection
        print("\n3. Creating live connection...")
        dg_connection = client.listen.live.v("1")
        print("✓ Connection object created")
        
        # Track if callback was called
        callback_called = False
        
        # Register callback
        print("\n4. Registering callback...")
        def on_message(self, result, **kwargs):
            nonlocal callback_called
            callback_called = True
            print(f"\n✓✓✓ CALLBACK TRIGGERED! ✓✓✓")
            print(f"Result type: {type(result)}")
            print(f"Has channel: {hasattr(result, 'channel')}")
            if hasattr(result, 'channel') and result.channel:
                print(f"Alternatives: {len(result.channel.alternatives) if result.channel.alternatives else 0}")
                if result.channel.alternatives:
                    transcript = result.channel.alternatives[0].transcript
                    print(f"Transcript: '{transcript}'")
        
        def on_error(self, error, **kwargs):
            print(f"\n✗ ERROR CALLBACK: {error}")
        
        def on_close(self, close, **kwargs):
            print(f"\n✗ CLOSE CALLBACK: {close}")
        
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        print("✓ Callbacks registered")
        
        # Start connection
        print("\n5. Starting connection...")
        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format

=True,
            interim_results=True,
            punctuate=True
        )
        
        if dg_connection.start(options) is False:
            print("✗ FAILED: dg_connection.start() returned False")
            return
        print("✓ Connection started")
        
        # Send test audio (silence)
        print("\n6. Sending test audio...")
        test_audio = b'\x00' * 4800  # 1 second of silence at 48kHz
        dg_connection.send(test_audio)
        print("✓ Audio sent")
        
        # Wait for callback
        print("\n7. Waiting 5 seconds for callback...")
        await asyncio.sleep(5)
        
        # Check result
        print("\n" + "=" * 60)
        if callback_called:
            print("SUCCESS: Callback was triggered!")
            print("This means Deepgram is working correctly.")
        else:
            print("FAILURE: Callback was NEVER triggered!")
            print("This means there's an issue with:")
            print("  - API key validity")
            print("  - Callback registration")
            print("  - Deepgram SDK version")
        print("=" * 60)
        
        # Cleanup
        dg_connection.finish()
        
    except Exception as e:
        print(f"\n✗ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepgram())
