"""
Test the history endpoint directly
"""
import asyncio
import httpx

async def test_history():
    # Production API URL
    api_url = "https://pwwgcganfv.us-east-1.awsapprunner.com"
    
    # You need to provide a valid token from your login
    print("Testing history endpoint...")
    print(f"API URL: {api_url}/api/v1/lessons/history")
    
    # Test without auth first to see the error
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{api_url}/api/v1/lessons/history?page=1&page_size=50",
                timeout=30.0
            )
            print(f"\nStatus Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_history())
