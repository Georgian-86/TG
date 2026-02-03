"""Test lesson generation API"""
import requests
import json

# 1. Login
print('Logging in...')
login_r = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'email': 'finaltest@example.com',
    'password': 'Test1234'
})
token = login_r.json()['access_token']
print('Got auth token\n')

# 2. Generate lesson
print('Generating lesson (may take 20-30 seconds)...')
lesson_r = requests.post(
    'http://localhost:8000/api/v1/lessons/generate',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'topic': 'Introduction to Python',
        'level': 'Undergraduate',
        'duration': 45,
        'include_quiz': False
    },
    timeout=120
)

print(f'Response Status: {lesson_r.status_code}\n')

if lesson_r.status_code == 201:
    data = lesson_r.json()
    print('Lesson generated successfully!\n')
    print(f'Response Keys: {list(data.keys())}\n')
    print(f'Topic: {data.get("topic")}')
    print(f'Level: {data.get("level")}')
    print(f'Duration: {data.get("duration")} minutes')
    print(f'Lesson Plan Sections: {len(data.get("lesson_plan", []))}')
    print(f'Key Takeaways: {len(data.get("key_takeaways", []))}')
    print(f'Resources: {len(data.get("resources", []))}')
    print(f'Quiz: {"Yes" if data.get("quiz") else "No"}')
    print(f'PPT URL: {data.get("ppt_url") or "Not generated"}')
    print(f'PDF URL: {data.get("pdf_url") or "Not generated"}')
    
    # Show first section as sample
    if data.get('lesson_plan'):
        print(f'\nFirst Section Sample:')
        first = data['lesson_plan'][0]
        print(f'  Title: {first.get("title", "N/A")}')
        content_preview = first.get('content', '')[:100]
        print(f'  Content: {content_preview}...')
        
    print('\nFull response saved to lesson_response.json')
    with open('lesson_response.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
else:
    print(f'Error: {lesson_r.text[:500]}')
