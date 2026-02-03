"""
Clear In-Memory Rate Limits
This clears the rate limit store without restarting the server
"""
import httpx
import asyncio


async def clear_rate_limits():
    """Clear all rate limits via debug endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post('http://localhost:8000/api/v1/debug/clear-rate-limits')
            if response.status_code == 200:
                print("\n✅ Rate limits cleared successfully!")
                print("You can now send OTP requests again.\n")
            else:
                print(f"\n❌ Failed to clear rate limits: {response.text}\n")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nAlternative: Restart the backend server to clear rate limits.\n")


if __name__ == "__main__":
    print("\n🧹 Clearing in-memory rate limits...")
    asyncio.run(clear_rate_limits())
