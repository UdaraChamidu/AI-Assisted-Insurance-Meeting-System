import requests
import json
import requests
import sys
import os
from pathlib import Path

# Add backend to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from msal import ConfidentialClientApplication
from config import settings

def fetch_booking_business_id():
    print(f"🔍 Connecting to Microsoft Graph with Client ID: {settings.ms_client_id}")
    
    # 1. Login
    msal_app = ConfidentialClientApplication(
        client_id=settings.ms_client_id,
        client_credential=settings.ms_client_secret,
        authority=f"https://login.microsoftonline.com/{settings.ms_tenant_id}"
    )
    
    # We need Booking permissions (usually Bookings.Read.All)
    scopes = ["https://graph.microsoft.com/.default"]
    
    result = msal_app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" not in result:
        print("❌ Authentication Failed!")
        print(f"Error: {result.get('error_description')}")
        print("\nPlease ensure your App Registration has permissions like 'Bookings.Read.All'.")
        return

    token = result['access_token']
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 2. List Booking Businesses (Try Beta as requested)
    print("✅ Authenticated. Fetching Booking Businesses (Beta)...")
    
    url = "https://graph.microsoft.com/beta/solutions/bookingBusinesses"
    response = requests.get(url, headers=headers)
    
    # Analyze Response
    if response.status_code == 200:
        pass # Success
    elif response.status_code == 401:
        print("❌ API Error: 401 Unauthorized")
        print("Possible reasons:")
        print("1. Token invalid (check Client Secret).")
        print("2. App has no access to this tenant.")
        print(f"Response: {response.text}")
        return
    elif response.status_code == 403:
        print("❌ API Error: 403 Forbidden")
        print("Reason: Missing 'Bookings.Read.All' Application Permission or Admin Consent.")
        print(f"Response: {response.text}")
        return
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return

    data = response.json()
    businesses = data.get('value', [])
    
    print(f"Found {len(businesses)} Booking Businesses.")
    
    target_url = "https://outlook.office365.com/owa/calendar/EliteDealBroker3@helmygenesis.com/bookings/"
    target_name = "Elite Deal Broker"
    
    found_id = None
    
    for biz in businesses:
        bid = biz.get('id')
        name = biz.get('displayName')
        page_url = biz.get('publicUrl', '')
        
        print(f" - [{name}] ID: {bid}")
        # print(f"   URL: {page_url}")
        
        # Check match
        if target_url.lower() in page_url.lower() or name == target_name:
            print(f"\n🎯 MATCH FOUND!")
            found_id = bid
            break
            
    if found_id:
        print(f"\n✅ YOUR MS_BOOKING_BUSINESS_ID: {found_id}")
        print("Copy this ID into your .env file.")
    else:
        print("\n⚠️ No exact match found for 'Elite Deal Broker'.")
        print("Please check the list above and pick the correct ID manually.")

if __name__ == "__main__":
    fetch_booking_business_id()
