import httpx
import asyncio

async def test_login():
    async with httpx.AsyncClient() as client:
        try:
            print("Checking health on 8000...")
            health = await client.get("http://127.0.0.1:8000/health", timeout=5.0)
            print(f"Health: {health.status_code} {health.text}")
            
            print("Checking login on 8000...")
            resp = await client.get("http://127.0.0.1:8000/api/v1/auth/google/login", follow_redirects=False, timeout=10.0)
            print(f"Status Code: {resp.status_code}")
            print(f"Location: {resp.headers.get('location')}")
        except Exception as e:
            print(f"Error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_login())
