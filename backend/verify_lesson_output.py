import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def run_verification():
    print("1. Creating Test User...")
    email = f"tester_{int(time.time())}@example.com"
    password = "Password123!"
    
    try:
        # 1. Register
        reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        if reg_resp.status_code != 201:
             print(f"Registration status: {reg_resp.status_code}")
             print(f"Registration response: {reg_resp.text}")
        
        # 2. Login
        print(f"2. Logging in as {email}...")
        # Endpoint uses UserLogin Pydantic model -> expects JSON
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if login_resp.status_code != 200:
            print(f"Login failed: {login_resp.status_code}")
            print(f"Login response: {login_resp.text}")
            return

        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Generate Lesson
        print("3. Requesting Lesson Generation (Topic: 'Photosynthesis', Quiz: Yes)...")
        start_t = time.time()
        gen_resp = requests.post(
            f"{BASE_URL}/lessons/generate",
            headers=headers,
            json={
                "topic": "Photosynthesis",
                "level": "School",
                "duration": 20,
                "include_quiz": True, # Explicitly requesting quiz
                "quiz_duration": 10,
                "quiz_marks": 20
            },
            timeout=120
        )
        
        if gen_resp.status_code == 200 or gen_resp.status_code == 201:
            data = gen_resp.json()
            print("\n=== GENERATION SUCCESS ===")
            print(f"Time Taken: {time.time() - start_t:.2f}s")
            
            # CHECK RESOURCES
            resources = data.get("resources", [])
            print(f"\n[RESOURCES] Count: {len(resources)}")
            if resources:
                print(json.dumps(resources[:2], indent=2)) # Print first 2
            else:
                print("❌ NO RESOURCES FOUND")
                
            # CHECK QUIZ
            quiz = data.get("quiz", {})
            questions = quiz.get("questions", [])
            print(f"\n[QUIZ] Questions Count: {len(questions)}")
            if questions:
                print(json.dumps(questions[:1], indent=2)) # Print first question
            else:
                print("❌ NO QUIZ QUESTIONS FOUND")
                
        else:
            print(f"\n❌ GENERATION FAILED: {gen_resp.status_code}")
            print(gen_resp.text)

    except Exception as e:
        print(f"\n❌ SCRIPT ERROR: {e}")

if __name__ == "__main__":
    run_verification()
