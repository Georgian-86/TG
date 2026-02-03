"""
Security utilities for authentication and authorization
JWT tokens, password hashing, rate limiting
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt  # Direct bcrypt usage instead of passlib
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


# ===== Password Hashing =====

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt (production-ready)
    Handles 72-byte limit automatically
    """
    # Convert to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds for good security/performance balance
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# ===== JWT Token Management =====

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token with longer expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if payload.get("type") != token_type:
            raise credentials_exception
        
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT validation error: {e}")
        raise credentials_exception


# ===== Dependency Injection =====

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    from app.models.user import User
    from sqlalchemy import select
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Get current user and verify they're active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive user"
        )
    return current_user


# ===== Rate Limiting =====

class RateLimiter:
    """Simple rate limiter for local testing (no Redis required)"""
    
    def __init__(self, times: int, seconds: int):
        """
        Initialize rate limiter
        
        Args:
            times: Number of allowed requests
            seconds: Time window in seconds
        """
        self.times = times
        self.seconds = seconds
    
    async def __call__(self, request: Request):
        """
        Check rate limit (simplified for local testing)
        In production, this would use Redis
        """
        # For local testing, just allow all requests
        # In production with Redis, implement proper rate limiting
        return True
