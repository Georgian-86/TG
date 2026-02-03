"""
Test the Synchronous Lesson Generation API
"""
import httpx
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
EMAIL = "prod_test@demo.com"
PASSWORD = "ProdPassword123"

def test_sync_generation():
    print("=" * 70)
    print("🧪 TeachGenie - Synchronous Generation Test")
    print("=" * 70)
    
    with httpx.Client(timeout=120.0) as client:
        # Login
        print("\n[1/2] 🔐 Logging in...")
        login_resp = client.post(
            f"{API_BASE}/api/v1/auth/login",
            json={"email": EMAIL, "password": PASSWORD}
        )
        
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return
        
        token = login_resp.json()["access_token"]
        print("✅ Logged in successfully")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate Lesson
        print("\n[2/2] 🚀 Generating lesson...")
        print("   Topic: Python Programming Basics")
        print("   Level: School")
        print("   Duration: 30 minutes")
        print("   Quiz: Yes")
        print("\n⏳ Please wait (~20-30 seconds)...")
        
        start_time = time.time()
        
        try:
            gen_resp = client.post(
                f"{API_BASE}/api/v1/lessons/generate",
                headers=headers,
                json={
                    "topic": "Python Programming Basics",
                    "level": "School",
                    "duration": 30,
                    "include_quiz": True
                }
            )
            
            elapsed = time.time() - start_time
            
            if gen_resp.status_code == 201:
                lesson = gen_resp.json()
                
                print("\n" + "=" * 70)
                print("✅ LESSON GENERATED SUCCESSFULLY!")
                print("=" * 70)
                
                print(f"\n⏱️  Generation Time: {elapsed:.2f}s")
                print(f"   Processing Time: {lesson.get('processing_time_seconds')}s")
                
                print(f"\n📚 Lesson Details:")
                print(f"   ID: {lesson['id']}")
                print(f"   Topic: {lesson['topic']}")
                print(f"   Level: {lesson['level']}")
                print(f"   Status: {lesson['status']}")
                
                lesson_plan = lesson.get('lesson_plan', [])
                resources = lesson.get('resources', [])
                quiz = lesson.get('quiz', {})
                
                print(f"\n📝 Generated Content:")
                print(f"   • Sections: {len(lesson_plan)}")
                for i, section in enumerate(lesson_plan, 1):
                    title = section.get('title', 'N/A')
                    print(f"      {i}. {title}")
                
                print(f"   • Resources: {len(resources)}")
                print(f"   • Quiz Questions: {len(quiz.get('questions', []))}")
                
                print("\n" + "=" * 70)
                
                if elapsed < 25:
                    print("Performance Rating: 🚀 EXCELLENT")
                elif elapsed < 35:
                    print("Performance Rating: ✅ GOOD")
                else:
                    print("Performance Rating: 👍 ACCEPTABLE")
                
                print("=" * 70)
                return lesson
                
            else:
                print(f"\n❌ Generation failed (Status: {gen_resp.status_code})")
                print(f"Error: {gen_resp.text}")
                
        except httpx.ReadTimeout:
            print(f"\n⚠️  Request timed out after {time.time() - start_time:.1f}s")
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    print(f"\nTest started: {datetime.now().strftime('%H:%M:%S')}\n")
    result = test_sync_generation()
    print(f"\nTest finished: {datetime.now().strftime('%H:%M:%S')}\n")
