"""
Quick test script to check lesson generation endpoint
"""
import requests
import json

API_BASE = "http://localhost:8000"

# Test data
payload = {
    "topic": "French Revolution",
    "level": "high_school",
    "duration": 45,
    "include_quiz": True
}

# You'll need a valid token - get it from localStorage in browser
# or create a test user first
token = "test"  # Replace with actual token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Testing lesson generation endpoint...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{API_BASE}/api/v1/lessons/generate",
        json=payload,
        headers=headers,
        timeout=95
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
except requests.exceptions.Timeout:
    print("Request timed out after 95 seconds")
except Exception as e:
    print(f"Error: {str(e)}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")
