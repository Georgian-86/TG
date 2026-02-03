"""
Test lesson generation via API with monitoring
"""
import httpx
import time
import asyncio

API_BASE = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyZjQzN2E0Zi00YzQ3LTQwYWItOTIzYi05MjIxMmI3NTY4ZmMiLCJleHAiOjE3MzczOTU1NjEsImlhdCI6MTczNzM5Mzc2MSwidHlwZSI6ImFjY2VzcyJ9.XKGpRA"

async def test():
    async with httpx.AsyncClient(timeout=300.0) as client:
        headers = {"Authorization": f"Bearer {TOKEN}"}
        
        # Start generation
        print("Starting generation...")
        resp = await client.post(
            f"{API_BASE}/api/v1/lessons/generate",
            headers=headers,
            json={
                "topic": "Machine Learning Basics",
                "level": "Undergraduate",
                "duration": 45,
                "include_quiz": True
            }
        )
        
        lesson = resp.json()
        print(f"Response: {lesson}")
        lesson_id = lesson["id"]
        print(f"Lesson ID: {lesson_id}")
        print(f"Initial Status: {lesson['status']}")
        
        # Poll for status
        for i in range(20):
            await asyncio.sleep(5)
            status_resp = await client.get(
                f"{API_BASE}/api/v1/lessons/{lesson_id}",
                headers=headers
            )
            data = status_resp.json()
            print(f"[{i*5}s] Status: {data['status']} | Error: {data.get('error_message', 'None')}")
            
            if data["status"] in ["COMPLETED", "FAILED"]:
                print(f"\nFinal Status: {data['status']}")
                if data["status"] == "COMPLETED":
                    print(f"Processing Time: {data.get('processing_time_seconds')}s")
                    print(f"Sections: {len(data.get('lesson_plan', []))}")
                break

if __name__ == "__main__":
    asyncio.run(test())
