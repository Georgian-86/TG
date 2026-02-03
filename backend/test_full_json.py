"""
Test Sync API with Full JSON Response Display
"""
import httpx
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
EMAIL = "prod_test@demo.com"
PASSWORD = "ProdPassword123"

def test_with_full_json():
    print("=" * 80)
    print("🧪 TeachGenie API - Full JSON Response Test")
    print("=" * 80)
    
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
        print("✅ Logged in successfully\n")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Generate Lesson
        print("[2/2] 🚀 Generating lesson...")
        print("   Topic: Machine Learning Basics")
        print("   Level: Undergraduate") 
        print("   Duration: 30 minutes")
        print("   Quiz: Yes\n")
        print("⏳ Please wait (~20-30 seconds)...\n")
        
        start_time = time.time()
        
        try:
            gen_resp = client.post(
                f"{API_BASE}/api/v1/lessons/generate",
                headers=headers,
                json={
                    "topic": "Machine Learning Basics",
                    "level": "Undergraduate",
                    "duration": 30,
                    "include_quiz": True
                }
            )
            
            elapsed = time.time() - start_time
            
            print("=" * 80)
            print(f"📊 HTTP Response")
            print("=" * 80)
            print(f"Status Code: {gen_resp.status_code}")
            print(f"Time Elapsed: {elapsed:.2f}s\n")
            
            if gen_resp.status_code == 201:
                lesson = gen_resp.json()
                
                print("=" * 80)
                print("✅ SUCCESS - Complete JSON Response")
                print("=" * 80)
                print(json.dumps(lesson, indent=2, default=str))
                print("=" * 80)
                
                # Also show a summary
                print("\n📝 Quick Summary:")
                print(f"   Lesson ID: {lesson.get('id')}")
                print(f"   Topic: {lesson.get('topic')}")
                print(f"   Status: {lesson.get('status')}")
                print(f"   Processing Time: {lesson.get('processing_time_seconds')}s")
                print(f"   Sections: {len(lesson.get('lesson_plan', []))}")
                print(f"   Resources: {len(lesson.get('resources', []))}")
                print(f"   Quiz Questions: {len(lesson.get('quiz', {}).get('questions', []))}")
                
                # Save to file for inspection
                with open("latest_lesson_response.json", "w") as f:
                    json.dump(lesson, f, indent=2, default=str)
                print(f"\n💾 Full response saved to: latest_lesson_response.json")
                
                return lesson
                
            else:
                print("=" * 80)
                print(f"❌ FAILED - Status {gen_resp.status_code}")
                print("=" * 80)
                print("Response Body:")
                try:
                    error_json = gen_resp.json()
                    print(json.dumps(error_json, indent=2))
                except:
                    print(gen_resp.text)
                print("=" * 80)
                
        except httpx.ReadTimeout:
            print(f"\n⚠️  Request timed out after {time.time() - start_time:.1f}s")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print(f"\n🕐 Test started: {datetime.now().strftime('%H:%M:%S')}\n")
    result = test_with_full_json()
    print(f"\n🕐 Test finished: {datetime.now().strftime('%H:%M:%S')}\n")
