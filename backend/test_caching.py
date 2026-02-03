"""
Test the caching performance optimization
"""
import httpx
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
EMAIL = "final_test@demo.com"
PASSWORD = "TestPass123"

async def test_caching():
    print("=" * 80)
    print("🧪 Testing Lesson Caching Performance")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Login
        print("\n[1/3] 🔐 Logging in...")
        login_resp = await client.post(
            f"{API_BASE}/api/v1/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in\n")
        
        # First request (cache MISS - should take ~24s)
        print("[2/3] 🚀 First request (cache MISS - will generate)...")
        print("   Topic: Python for Beginners")
        print("   Expected: ~24 seconds\n")
        
        start_time = time.time()
        
        first_resp = await client.post(
            f"{API_BASE}/api/v1/lessons/generate",
            headers=headers,
            json={
                "topic": "Python for Beginners",
                "level": "School",
                "duration": 30,
                "include_quiz": True
            }
        )
        
        first_time = time.time() - start_time
        
        if first_resp.status_code == 201:
            lesson = first_resp.json()
            print(f"✅ Generated successfully in {first_time:.1f}s")
            print(f"   Processing time: {lesson.get('processing_time_seconds')}s\n")
        else:
            print(f"❌ Failed: {first_resp.status_code}")
            print(f"   {first_resp.text}\n")
            return
        
        # Second request (cache HIT - should be instant)
        print("[3/3] ⚡ Second request (cache HIT - instant)...")
        print("   Same topic: Python for Beginners")
        print("   Expected: <1 second\n")
        
        start_time = time.time()
        
        second_resp = await client.post(
            f"{API_BASE}/api/v1/lessons/generate",
            headers=headers,
            json={
                "topic": "Python for Beginners",
                "level": "School",
                "duration": 30,
                "include_quiz": True
            }
        )
        
        second_time = time.time() - start_time
        
        if second_resp.status_code == 201:
            lesson = second_resp.json()
            print(f"✅ Retrieved from cache in {second_time:.1f}s")
            print(f"   Processing time: {lesson.get('processing_time_seconds')}s (0 = from cache)\n")
        else:
            print(f"❌ Failed: {second_resp.status_code}\n")
            return
        
        # Results
        print("=" * 80)
        print("📊 CACHING PERFORMANCE RESULTS")
        print("=" * 80)
        print(f"First request (generated):  {first_time:>6.1f}s")
        print(f"Second request (cached):    {second_time:>6.1f}s")
        print(f"Speedup:                    {first_time / second_time:>6.1f}x faster")
        print(f"Time saved:                 {first_time - second_time:>6.1f}s")
        print("=" * 80)
        
        if second_time < 2:
            print("✅ Caching works perfectly!")
        else:
            print("⚠️  Cache may not be working (should be <2s)")
        
        print("=" * 80)

if __name__ == "__main__":
    import asyncio
    print(f"\n🕐 Test started: {datetime.now().strftime('%H:%M:%S')}\n")
    asyncio.run(test_caching())
    print(f"\n🕐 Test finished: {datetime.now().strftime('%H:%M:%S')}\n")
