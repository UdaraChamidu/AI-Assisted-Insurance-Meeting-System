import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("DEEPGRAM_API_KEY")

print(f"Testing API Key: {api_key[:20]}...")

# Test API key validity
response = requests.get(
    "https://api.deepgram.com/v1/projects",
    headers={"Authorization": f"Token {api_key}"}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    print("\n✓ API KEY IS VALID!")
elif response.status_code == 401:
    print("\n✗ API KEY IS INVALID (401 Unauthorized)")
    print("Please create a new API key from https://console.deepgram.com/")
else:
    print(f"\n? Unexpected response code: {response.status_code}")
