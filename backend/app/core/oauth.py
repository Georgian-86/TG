"""
Google OAuth Client Configuration
"""
from authlib.integrations.starlette_client import OAuth
from app.config import settings
import httpx

# Shared HTTP client with connection pooling (prevents "too many open files")
_http_client = None

def get_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTP client with connection pooling"""
    global _http_client
    if _http_client is None:
        # Create client with connection pooling and limits
        _http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0
            ),
            timeout=30.0,
            follow_redirects=True,
            verify=not settings.DEBUG  # Only disable SSL verification in development
        )
    return _http_client

async def close_http_client():
    """Close the shared HTTP client (call on app shutdown)"""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth client
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account',
        'timeout': 30.0
    }
)

async def get_google_user_info(token: dict) -> dict:
    """
    Fetch user info from Google using access token
    
    Args:
        token: OAuth token dict with 'access_token'
        
    Returns:
        dict with user info (email, name, picture, etc.)
    """
    client = get_http_client()
    response = await client.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {token["access_token"]}'}
    )
    response.raise_for_status()
    return response.json()
