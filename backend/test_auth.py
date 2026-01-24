import requests
import json

# Test registration
print("Testing registration...")
response = requests.post(
    "http://localhost:8000/api/auth/register",
    json={
        "email": "admin@insurance.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    print("\n✅ Registration successful!")
    user_data = response.json()
    print(f"User ID: {user_data['id']}")
    print(f"Email: {user_data['email']}")
    
    # Test login
    print("\n\nTesting login...")
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json={
            "email": "admin@insurance.com",
            "password": "admin123"
        }
    )
    
    print(f"Status Code: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    
    if login_response.status_code == 200:
        print("\n✅ Login successful!")
        tokens = login_response.json()
        print(f"Access Token: {tokens['access_token'][:50]}...")
else:
    print("\n❌ Registration failed!")
