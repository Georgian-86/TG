"""
FINAL Test - Complete JSON Response
"""
import httpx
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"
EMAIL = "final_test@demo.com"
PASSWORD = "TestPass123"

def test_final():
    print("=" * 80)
    print("🎯 FINAL API TEST - Complete JSON Response")
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
        print("   Topic: Introduction to Data Science")
        print("   Level: Undergraduate") 
        print("   Duration: 30 minutes")
        print("   Quiz: Yes\n")
        print("⏳ Generating (~20-30 seconds)...\n")
        
        start_time = time.time()
        
        try:
            gen_resp = client.post(
                f"{API_BASE}/api/v1/lessons/generate",
                headers=headers,
                json={
                    "topic": "Introduction to Data Science",
                    "level": "Undergraduate",
                    "duration": 30,
                    "include_quiz": True
                }
            )
            
            elapsed = time.time() - start_time
            
            print("=" * 80)
            print(f"📊 HTTP Response - Status: {gen_resp.status_code} | Time: {elapsed:.2f}s")
            print("=" * 80)
            
            if gen_resp.status_code == 201:
                lesson = gen_resp.json()
                
                print("\n" + "="*80)
                print("✅ ✅ ✅  SUCCESS - COMPLETE JSON RESPONSE  ✅ ✅ ✅")
                print("="*80)
                print(json.dumps(lesson, indent=2, default=str))
                print("="*80)
                
                # Save to file
                with open("final_api_response.json", "w") as f:
                    json.dump(lesson, f, indent=2, default=str)
                print(f"\n💾 Saved to: final_api_response.json")
                
                # Summary
                print("\n📝 Summary:")
                print(f"   Lesson ID: {lesson.get('id')}")
                print(f"   Topic: {lesson.get('topic')}")
                print(f"   Status: {lesson.get('status')}")
                print(f"   Generation Time: {lesson.get('processing_time_seconds')}s")
                print(f"   Sections: {len(lesson.get('lesson_plan', []))}")
                print(f"   Resources: {len(lesson.get('resources', []))}")
                print(f"   Quiz Questions: {len(lesson.get('quiz', {}).get('questions', []))}")
                
                print("\n" + "="*80)
                print("🎉 API WORKS PERFECTLY!")
                print("="*80)
                
                return lesson
                
            else:
                print(f"\n❌ FAILED - Status {gen_resp.status_code}")
                try:
                    print(json.dumps(gen_resp.json(), indent=2))
                except:
                    print(gen_resp.text)
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print(f"\n🕐 Started: {datetime.now().strftime('%H:%M:%S')}\n")
    test_final()
    print(f"\n🕐 Finished: {datetime.now().strftime('%H:%M:%S')}\n")
