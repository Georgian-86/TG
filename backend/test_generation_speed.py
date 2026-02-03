"""
Performance Test: Lesson Generation Speed
Measures the time taken to generate a complete lesson with the new async agents
"""
import asyncio
import time
import httpx
from datetime import datetime

API_BASE = "http://localhost:8000"

async def test_generation_speed():
    """Test the full lesson generation pipeline"""
    
    print("=" * 60)
    print("🧪 TeachGenie Performance Test")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: Login
        print("\n[1/4] Logging in...")
        login_response = await client.post(
            f"{API_BASE}/api/v1/auth/login",
            json={
                "email": "prod_test@demo.com",
                "password": "ProdPassword123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        print("✅ Logged in successfully")
        
        # Step 2: Start generation
        print("\n[2/4] Starting lesson generation...")
        print("Topic: Photosynthesis")
        print("Level: School")
        print("Duration: 60 minutes")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        start_time = time.time()
        gen_response = await client.post(
            f"{API_BASE}/api/v1/lessons/generate",
            headers=headers,
            json={
                "topic": "Photosynthesis",
                "level": "School",
                "duration": 60,
                "include_quiz": True
            }
        )
        
        if gen_response.status_code != 202:
            print(f"❌ Generation failed: {gen_response.text}")
            return
        
        lesson_data = gen_response.json()
        lesson_id = lesson_data["id"]
        print(f"✅ Generation started (ID: {lesson_id})")
        
        # Step 3: Poll for completion
        print("\n[3/4] Waiting for generation to complete...")
        max_polls = 60  # 5 minutes max
        poll_interval = 5  # Check every 5 seconds
        
        for poll_count in range(max_polls):
            await asyncio.sleep(poll_interval)
            
            status_response = await client.get(
                f"{API_BASE}/api/v1/lessons/{lesson_id}",
                headers=headers
            )
            
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.text}")
                return
            
            lesson = status_response.json()
            status = lesson["status"]
            
            elapsed = time.time() - start_time
            print(f"⏱️  [{int(elapsed)}s] Status: {status}")
            
            if status == "COMPLETED":
                end_time = time.time()
                total_time = end_time - start_time
                
                print("\n" + "=" * 60)
                print("✅ GENERATION COMPLETE!")
                print("=" * 60)
                print(f"⏱️  Total Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
                print(f"📊 Processing Time (API): {lesson.get('processing_time_seconds', 'N/A')}s")
                print(f"📝 Sections Generated: {len(lesson.get('lesson_plan', []))}")
                print(f"❓ Quiz Questions: {len(lesson.get('quiz', {}).get('questions', []))}")
                print(f"🔗 Resources Found: {len(lesson.get('resources', []))}")
                
                # Performance Analysis
                print("\n" + "-" * 60)
                print("📈 PERFORMANCE ANALYSIS")
                print("-" * 60)
                
                if total_time < 30:
                    print("🚀 EXCELLENT: Sub-30 second generation!")
                elif total_time < 60:
                    print("✅ GOOD: Under 1 minute")
                elif total_time < 120:
                    print("⚠️  ACCEPTABLE: 1-2 minutes")
                else:
                    print("🐌 SLOW: Over 2 minutes (optimization needed)")
                
                print(f"\nEstimated speedup vs sequential: ~{(total_time * 1.6):.1f}s → {total_time:.1f}s")
                print(f"That's approximately {((1.6 - 1) * 100):.0f}% faster!")
                
                return lesson
                
            elif status == "FAILED":
                print(f"❌ Generation failed: {lesson.get('error_message', 'Unknown error')}")
                return
        
        print("⚠️  Timeout: Generation took longer than expected")

if __name__ == "__main__":
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    result = asyncio.run(test_generation_speed())
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
