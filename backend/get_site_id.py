
import asyncio
import os
import sys
from dotenv import load_dotenv
import requests

# Load env
load_dotenv(override=True)

# Add project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.sharepoint_service import sharepoint_service

def list_sites():
    print("--- SHAREPOINT SITE DISCOVERY ---")
    token = sharepoint_service.get_access_token()
    if not token:
        print("ERROR: Could not get Access Token. Check MS_CLIENT_ID/SECRET in .env")
        return

    print("Success: Authenticated with Microsoft Graph.")
    
    # Search for all sites (root search) or specific search
    # Note: "search=*" might not work on root, so we try a common search or just list recent
    
    print("\nAttempting to find sites...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Method 1: Search for "Compliance" (as suggested)
    search_term = "Compliance"
    print(f"\nSearching for '{search_term}'...")
    url = f"https://graph.microsoft.com/v1.0/sites?search={search_term}"
    resp = requests.get(url, headers=headers)
    
    found = False
    if resp.status_code == 200:
        sites = resp.json().get('value', [])
        for site in sites:
            found = True
            print(f"  [FOUND] Name: {site.get('name')} | DisplayName: {site.get('displayName')}")
            print(f"          ID: {site.get('id')}")
            print(f"          WebUrl: {site.get('webUrl')}")
            print("-" * 40)
    
    # Method 2: Search for * (everything)
    print("\nListing ALL accessible sites (top 20)...")
    url = f"https://graph.microsoft.com/v1.0/sites?search=*"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        sites = resp.json().get('value', [])
        for site in sites:
            print(f"  [FOUND] Name: {site.get('name')} | DisplayName: {site.get('displayName')}")
            print(f"          ID: {site.get('id')}")
            print("-" * 40)
    else:
        print(f"Error listing sites: {resp.status_code} - {resp.text}")

    print("\nINSTRUCTIONS:")
    print("1. Copy the 'ID' of the site you want to use.")
    print("2. Add it to your .env file: SHAREPOINT_SITE_ID=your_copied_id_here")

if __name__ == "__main__":
    list_sites()
