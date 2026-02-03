import os
import sys
import asyncio

# Add current dir to path
sys.path.append(os.getcwd())

# Mock settings
os.environ["SECRET_KEY"] = "test"
os.environ["GOOGLE_CLIENT_ID"] = "test"
os.environ["GOOGLE_CLIENT_SECRET"] = "test" 
os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/callback"

try:
    print("Importing modules...")
    from starlette.middleware.sessions import SessionMiddleware
    from authlib.integrations.starlette_client import OAuth
    import httpx
    import itsdangerous
    print("Imports successful.")
    
    print("Initializing OAuth...")
    oauth = OAuth()
    oauth.register(
        name='google',
        client_id="test_id",
        client_secret="test_secret",
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    print("OAuth initialized successfully.")
    
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
