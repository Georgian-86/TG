"""
Quick cache test - Generate same lesson twice to verify caching
"""
import httpx
import time

API_BASE = "http://localhost:8000"
EMAIL = "final_test@demo.com"
PASSWORD = "TestPass123"

def test_cache():
    with httpx.Client(timeout=120.0) as client:
        # Login
        print("🔐 Logging in...")
        login = client.post(f"{API_BASE}/api/v1/auth/login", 
                           json={"email": EMAIL, "password": PASSWORD})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in\n")
        
        # Test payload
        payload = {
            "topic": "JavaScript Basics",
            "level": "School",
            "duration": 30,
            "include_quiz": True
        }
        
        # First request
        print("⏱️  Request 1 (should generate ~24s)...")
        start = time.time()
        resp1 = client.post(f"{API_BASE}/api/v1/lessons/generate", 
                           headers=headers, json=payload)
        time1 = time.time() - start
        
        if resp1.status_code == 201:
            data1 = resp1.json()
            print(f"✅ Generated in {time1:.1f}s")
            print(f"   Processing: {data1['processing_time_seconds']}s")
            print(f"   Sections: {len(data1['lesson_plan'])}\n")
        else:
            print(f"❌ Failed: {resp1.status_code}\n")
            return
        
        # Second request (should be cached)
        print("⚡ Request 2 (should be instant from cache)...")
        start = time.time()
        resp2 = client.post(f"{API_BASE}/api/v1/lessons/generate", 
                           headers=headers, json=payload)
        time2 = time.time() - start
        
        if resp2.status_code == 201:
            data2 = resp2.json()
            print(f"✅ Retrieved in {time2:.1f}s")
            print(f"   Processing: {data2['processing_time_seconds']}s")
            print(f"   Sections: {len(data2['lesson_plan'])}\n")
        else:
            print(f"❌ Failed: {resp2.status_code}\n")
            return
        
        # Results
        print("=" * 60)
        print(f"First:  {time1:>6.1f}s (generated)")
        print(f"Second: {time2:>6.1f}s (cached)")
        print(f"Speedup: {time1/time2:>5.1f}x faster" if time2 > 0 else "Speedup: ∞x")
        print("=" * 60)
        
        if data2['processing_time_seconds'] == 0:
            print("✅ CACHING WORKS! (processing_time=0 means cached)")
        else:
            print("⚠️  Cache miss (both requests generated new content)")

if __name__ == "__main__":
    test_cache()
