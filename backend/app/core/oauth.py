"""
Google OAuth Client Configuration
"""
from authlib.integrations.starlette_client import OAuth
from app.config import settings

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
        'prompt': 'select_account',  # Always show account picker
        'verify': False  # Authlib passes this to httpx.AsyncClient
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
    import httpx
    
    # Disable SSL verification for development to fix [SSL: CERTIFICATE_VERIFY_FAILED]
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {token["access_token"]}'}
        )
        response.raise_for_status()
        return response.json()
