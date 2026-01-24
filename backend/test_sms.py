"""
Quick SMS test script to verify Twilio is working
"""

from services.twilio_service import twilio_service
import sys

def test_sms(phone_number: str):
    """Test sending SMS to a phone number."""
    
    print(f"\n📱 Testing SMS to: {phone_number}\n")
    print("=" * 60)
    
    # Send test SMS
    result = twilio_service.send_booking_sms(
        to_phone_number=phone_number,
        booking_url="https://example.com/test-booking",
        customer_name="Test User"
    )
    
    print(f"\n📊 Result:")
    print(f"   Success: {result.success}")
    
    if result.success:
        print(f"   Message SID: {result.message_sid}")
        print(f"\n✅ SMS request accepted by Twilio!")
        print(f"\n🔍 Next steps:")
        print(f"   1. Check your phone for the SMS")
        print(f"   2. Check Twilio logs: https://console.twilio.com/us1/monitor/logs/sms")
        print(f"   3. Look for Message SID: {result.message_sid}")
        print(f"\n⚠️  If you didn't receive it:")
        print(f"   - Verify your phone number in Twilio console (trial accounts only)")
        print(f"   - Check Twilio logs for delivery status")
    else:
        print(f"   Error: {result.error}")
        print(f"\n❌ SMS request failed!")
        print(f"\n💡 Common fixes:")
        print(f"   - Verify phone number format (E.164): +15551234567")
        print(f"   - For trial accounts: verify number in Twilio console")
        print(f"   - Check TWILIO credentials in .env file")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ Error: Phone number required!")
        print("\nUsage:")
        print("   python test_sms.py +15551234567")
        print("\nNote: Use E.164 format with country code")
        sys.exit(1)
    
    phone = sys.argv[1]
    test_sms(phone)
