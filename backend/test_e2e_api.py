"""
Complete End-to-End API Test
Tests the full flow: Login → Generate → Poll → Results
"""
import httpx
import asyncio
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
EMAIL = "prod_test@demo.com"
PASSWORD = "ProdPassword123"

async def test_full_flow():
    print("=" * 70)
    print("🧪 TeachGenie API - End-to-End Generation Test")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: Login
        print("\n[1/4] 🔐 Logging in...")
        login_resp = await client.post(
            f"{API_BASE}/api/v1/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
        
        token_data = login_resp.json()
        token = token_data["access_token"]
        print(f"✅ Logged in successfully")
        print(f"   Token expires in: {token_data['expires_in']}s")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Start Generation
        print("\n[2/4] 🚀 Starting lesson generation...")
        print("   Topic: Linear Algebra Basics")
        print("   Level: Undergraduate")
        print("   Duration: 45 minutes")
        print("   Quiz: Yes")
        
        start_time = time.time()
        gen_resp = await client.post(
            f"{API_BASE}/api/v1/lessons/generate",
            headers=headers,
            json={
                "topic": "Linear Algebra Basics",
                "level": "Undergraduate",
                "duration": 45,
                "include_quiz": True
            }
        )
        
        if gen_resp.status_code != 202:
            print(f"❌ Generation failed: {gen_resp.text}")
            return
        
        lesson = gen_resp.json()
        lesson_id = lesson["id"]
        print(f"✅ Generation started")
        print(f"   Lesson ID: {lesson_id}")
        print(f"   Initial Status: {lesson['status']}")
        
        # Step 3: Poll for Completion
        print("\n[3/4] ⏳ Waiting for generation to complete...")
        print("-" * 70)
        
        max_polls = 30  # 2.5 minutes max
        poll_interval = 5  # Check every 5 seconds
        
        for poll_count in range(max_polls):
            await asyncio.sleep(poll_interval)
            
            status_resp = await client.get(
                f"{API_BASE}/api/v1/lessons/{lesson_id}",
                headers=headers
            )
            
            if status_resp.status_code != 200:
                print(f"❌ Status check failed: {status_resp.text}")
                return
            
            data = status_resp.json()
            status = data["status"]
            elapsed = time.time() - start_time
            
            # Show progress
            if status == "PENDING":
                print(f"⏱️  [{int(elapsed):3d}s] Status: PENDING (waiting to start...)")
            elif status == "GENERATING":
                print(f"⏱️  [{int(elapsed):3d}s] Status: GENERATING (AI working...)")
            elif status == "COMPLETED":
                print(f"⏱️  [{int(elapsed):3d}s] Status: COMPLETED ✅")
                
                # Step 4: Show Results
                print("\n" + "=" * 70)
                print("✅ LESSON GENERATION SUCCESSFUL!")
                print("=" * 70)
                
                print(f"\n⏱️  Performance Metrics:")
                print(f"   Total Time: {elapsed:.2f}s")
                print(f"   Processing Time: {data.get('processing_time_seconds', 'N/A')}s")
                
                print(f"\n📚 Generated Content:")
                print(f"   Topic: {data['topic']}")
                print(f"   Level: {data['level']}")
                print(f"   Duration: {data['duration']} minutes")
                
                lesson_plan = data.get('lesson_plan', [])
                resources = data.get('resources', [])
                quiz = data.get('quiz', {})
                
                print(f"\n📝 Content Breakdown:")
                print(f"   • Sections: {len(lesson_plan)}")
                if lesson_plan:
                    for i, section in enumerate(lesson_plan, 1):
                        title = section.get('title', 'N/A')
                        content_len = len(str(section.get('content', '')))
                        print(f"      {i}. {title} ({content_len} chars)")
                
                print(f"   • Resources: {len(resources)}")
                if resources:
                    for i, res in enumerate(resources[:3], 1):  # Show first 3
                        title = res.get('title', 'N/A')
                        print(f"      {i}. {title}")
                
                quiz_questions = quiz.get('questions', []) if quiz else []
                print(f"   • Quiz Questions: {len(quiz_questions)}")
                
                print("\n" + "=" * 70)
                
                # Performance rating
                if elapsed < 30:
                    rating = "🚀 EXCELLENT"
                elif elapsed < 45:
                    rating = "✅ GOOD"
                elif elapsed < 60:
                    rating = "👍 ACCEPTABLE"
                else:
                    rating = "⚠️  SLOW"
                
                print(f"Performance Rating: {rating}")
                print("=" * 70)
                
                return data
                
            elif status == "FAILED":
                error_msg = data.get('error_message', 'Unknown error')
                print(f"⏱️  [{int(elapsed):3d}s] Status: FAILED ❌")
                print("\n" + "=" * 70)
                print("❌ GENERATION FAILED")
                print("=" * 70)
                print(f"Error: {error_msg}")
                print("=" * 70)
                return None
        
        # Timeout
        print(f"\n⚠️  Timeout after {max_polls * poll_interval}s")
        print("Generation is taking longer than expected")

if __name__ == "__main__":
    print(f"\nTest started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    result = asyncio.run(test_full_flow())
    print(f"\nTest finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
