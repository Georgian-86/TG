"""
Pydantic Schemas for User Authentication
Request/Response validation models
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# ===== User Schemas =====

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_complexity(cls, v):
        """Validate password complexity"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response (no sensitive data)"""
    id: str  # String UUID for SQLite compatibility
    is_active: bool
    is_verified: bool  # Legacy field
    email_verified: bool = False  # Email OTP verification status
    subscription_tier: str
    role: str
    lessons_this_month: int
    lessons_quota: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    # OAuth fields
    oauth_provider: Optional[str] = None
    profile_picture_url: Optional[str] = None
    profile_completed: bool = True
    feedback_provided: bool = False
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_complexity(cls, v):
        """Validate password complexity"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


# ===== Token Schemas =====

class Token(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Optional[dict] = None  # User data included in login response


class TokenRefresh(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class TokenPayload(BaseModel):
    """Schema for decoded token payload"""
    sub: UUID  # User ID
    exp: int
    iat: int
    type: str  # access or refresh


# ===== OAuth Schemas =====

class ProfileCompletion(BaseModel):
    """Schema for completing OAuth user profile"""
    organization: str = Field(..., min_length=2, max_length=200)
    country: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=20)


# ===== OTP Verification Schemas =====

class EmailVerificationRequest(BaseModel):
    """Schema for sending verification email"""
    email: EmailStr


class EmailVerificationCode(BaseModel):
    """Schema for verifying email with OTP"""
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6, pattern=r'^\d{6}$')
