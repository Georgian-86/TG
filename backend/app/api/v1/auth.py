"""
Authentication API Endpoints
User registration, login, token management
"""
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, TokenRefresh,
    PasswordChange, UserUpdate, ProfileCompletion,
    EmailVerificationRequest, EmailVerificationCode
)

from app.database import get_db
from app.models.user import User
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token, get_current_active_user,
    RateLimiter
)
from app.core.logging_utils import log_admin_event
from app.models.admin_log import LogLevel, LogCategory
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(RateLimiter(times=50, seconds=3600))  # 50 registrations per hour per IP
):
    """
    Register a new user
    
    Security:
    - Rate limited to prevent abuse
    - Password complexity validation
    - Email uniqueness check
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        await log_admin_event(
            level=LogLevel.WARNING,
            category=LogCategory.AUTHENTICATION,
            event_name="registration_duplicate_email",
            message=f"Registration attempt with existing email: {user_data.email}",
            user_email=user_data.email,
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please login."
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        organization=user_data.organization,
        country=getattr(user_data, 'country', None),
        phone_number=getattr(user_data, 'phone_number', None),
        is_active=True,
        is_verified=False  # Email verification would go here
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log successful registration
    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.AUTHENTICATION,
        event_name="user_registered",
        message=f"New user registered: {new_user.email}",
        user_id=new_user.id,
        user_email=new_user.email,
        ip_address=request.client.host if request.client else None
    )
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(RateLimiter(times=50, seconds=300))  # 50 attempts per 5 minutes
):
    """
    Login and receive access + refresh tokens
    
    Security:
    - Rate limited to prevent brute force
    - Logs failed attempts
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    # Check if user exists
    if not user:
        await log_admin_event(
            level=LogLevel.WARNING,
            category=LogCategory.SECURITY,
            event_name="login_failed_email_not_found",
            message=f"Login attempt with unregistered email: {credentials.email}",
            user_email=credentials.email,
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered. Please register first to login."
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        await log_admin_event(
            level=LogLevel.WARNING,
            category=LogCategory.SECURITY,
            event_name="login_failed_wrong_password",
            message=f"Failed login attempt with incorrect password for email: {credentials.email}",
            user_email=credentials.email,
            ip_address=request.client.host if request.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Simple debug print for user visibility
    print(f"Login success: {user.email}")
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Log successful login
    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.AUTHENTICATION,
        event_name="user_login",
        message=f"User logged in: {user.email}",
        user_id=user.id,
        user_email=user.email,
        ip_address=request.client.host if request.client else None
    )
    
    # Return authentication tokens WITH user data for frontend state management
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "organization": user.organization,
            "subscription_tier": user.subscription_tier.value,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "profile_picture_url": user.profile_picture_url,
            "feedback_provided": user.feedback_provided
        }
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    user_id = payload.get("sub")
    
    # Verify user still exists and is active
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    if user_data.organization is not None:
        current_user.organization = user_data.organization
    
    await db.commit()
    await db.refresh(current_user)
    
    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.USER_ACTION,
        event_name="profile_updated",
        message=f"User updated profile: {current_user.email}",
        user_id=current_user.id,
        user_email=current_user.email
    )
    
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    await db.commit()
    
    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.SECURITY,
        event_name="password_changed",
        message=f"User changed password: {current_user.email}",
        user_id=current_user.id,
        user_email=current_user.email
    )
    
    return {"message": "Password changed successfully"}
# Force reload comment 2



# ===== Google OAuth Endpoints =====

@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow
    Redirects user to Google consent screen
    """
    from app.core.oauth import oauth
    
    # Build authorization URL
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    # DEBUG: Log session before redirect
    print(f"DEBUG: Initiating Google Login. Session Keys: {list(request.session.keys())}")
    
    # Authlib automatically generates and saves 'state' to session
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Google OAuth callback
    Creates or logs in user with Google account
    """
    from app.core.oauth import oauth, get_google_user_info
    
    try:
        # DEBUG: Log session content on callback
        print(f"DEBUG: Google Callback Received. Session Keys: {list(request.session.keys())}")
        print(f"DEBUG: Query Params: {request.query_params}")
        
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        print(f"✓ OAuth token received successfully")
        
        # Get user info from Google
        user_info = await get_google_user_info(token)
        print(f"✓ User info retrieved: {user_info.get('email')}")
        
        # Extract user data
        email = user_info.get('email')
        full_name = user_info.get('name', '')
        profile_picture = user_info.get('picture')
        google_id = user_info.get('id')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve email from Google"
            )
        
        # Check if user exists
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Existing user - update OAuth fields and profile info
            user.oauth_provider = 'google'
            user.oauth_id = google_id
            
            # Always update profile picture if available from Google
            if profile_picture:
                user.profile_picture_url = profile_picture
                
            user.last_login_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            
        else:
            # New user - create account
            user = User(
                email=email,
                full_name=full_name,
                password_hash=hash_password(secrets.token_urlsafe(32)),  # Random password
                is_verified=True,  # Google accounts are pre-verified
                oauth_provider='google',
                oauth_id=google_id,
                profile_picture_url=profile_picture,
                profile_completed=False,  # Need to collect missing fields
                last_login_at=datetime.utcnow()
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            await log_admin_event(
                level=LogLevel.INFO,
                category=LogCategory.USER_ACTION,
                event_name="google_oauth_registration",
                message=f"New user registered via Google OAuth: {email}",
                user_id=str(user.id)
            )
        
        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
    # Build response URL
        base_url = settings.FRONTEND_URL or "http://localhost:3000"
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
            
        if user.profile_completed:
            frontend_url = f"{base_url}/auth-callback?token={access_token}"
        else:
            frontend_url = f"{base_url}/complete-profile?token={access_token}"
        
        return RedirectResponse(url=frontend_url)
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        print(f"✗ OAuth HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"✗ Google OAuth error: {e}")
        print(f"Full traceback:\n{error_details}")
        
        # Log the error
        await log_admin_event(
            level=LogLevel.ERROR,
            category=LogCategory.SECURITY,
            event_name="oauth_failure",
            message=f"Google OAuth failed: {str(e)}"
        )
        
        error_base_url = settings.FRONTEND_URL or "http://localhost:3000"
        if not error_base_url.startswith("http"):
            error_base_url = f"https://{error_base_url}"
            
        return RedirectResponse(url=f"{error_base_url}/login?error=oauth_failed&detail={str(e)[:100]}")


@router.post("/complete-profile", response_model=UserResponse)
async def complete_profile(
    profile_data: ProfileCompletion,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete OAuth user profile with missing required fields
    Required for Google OAuth users
    """
    # Update user with missing fields
    current_user.organization = profile_data.organization
    current_user.country = profile_data.country
    current_user.phone_number = profile_data.phone_number
    current_user.profile_completed = True
    
    await db.commit()
    await db.refresh(current_user)
    
    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.USER_ACTION,
        event_name="profile_completed",
        message=f"User completed OAuth profile: {current_user.email}",
        user_id=str(current_user.id)
    )
    
    return UserResponse.from_orm(current_user)


@router.get("/universities")
async def get_universities(country: str):
    """
    Proxy endpoint to fetch universities from hipolabs to avoid CORS issues on frontend.
    """
    import httpx
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"http://universities.hipolabs.com/search?country={country}", timeout=10.0)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching universities: {e}")
            return []


# ===== Email Verification Endpoints =====

@router.post("/send-verification-email")
async def send_verification_email(
    verification_request: EmailVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(RateLimiter(times=50, seconds=3600))  # 50 emails per hour
):
    """
    Send OTP verification email
    
    Security:
    - Rate limited: 3 emails per hour per email address
    - OTP hashed with bcrypt before storage
    - 10-minute expiration
    """
    from app.core.otp_service import OTPService
    from app.core.email_service import EmailService
    from datetime import datetime
    
    # Extract email from request body
    email = verification_request.email
    
    
    # Check rate limit
    allowed, seconds_until_reset = OTPService.check_rate_limit(email, limit=50, window_hours=1)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Try again in {seconds_until_reset} seconds."
        )
    
    # Check if user exists (but don't require it for signup flow)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    # If user already registered AND verified, tell them to login
    if user and user.password_hash and user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered and verified. Please login instead."
        )
    
    # If user exists but NOT verified, allow them to resend OTP (continue below)
    # This handles stuck registrations where users didn't get the first OTP
    
    # Generate OTP
    otp_code = OTPService.generate_otp()
    
    # Store OTP in database (hashed)
    ip_address = request.client.host if request.client else None
    await OTPService.create_otp(db, email, otp_code, ip_address)
    
    # Send email (with user name if user exists)
    user_name = user.full_name if user else None
    
    # Dev mode: log OTP to console AND send email
    if settings.ENVIRONMENT == "development":
        logger.warning(f"[DEV MODE] OTP for {email}: {otp_code}")
        print(f"\n\n===== DIGIT OTP CODE: {otp_code} =====\n\n")
        
    # Always attempt to send email if API key is present
    success, error_msg = await EmailService.send_verification_email(
        email=email,
        otp=otp_code,
        user_name=user_name
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg or "Failed to send email"
        )
    
    # Update user record if user exists
    if user:
        user.email_verification_sent_at = datetime.utcnow()
        await db.commit()
    
        # Log event with appropriate message
        event_msg = "Verification email resent" if user.password_hash else "Verification email sent"
        await log_admin_event(
            level=LogLevel.INFO,
            category=LogCategory.AUTHENTICATION,
            event_name="verification_email_sent",
            message=f"{event_msg} to {email} (verified: {user.email_verified})",
            user_id=user.id,
            user_email=email,
            ip_address=ip_address
        )
    
    # Mask email for privacy
    email_parts = email.split('@')
    masked_email = f"{email_parts[0][:2]}**@{email_parts[1]}"
    
    # Determine if this is a resend (user exists with password but not verified)
    is_resend = user and user.password_hash and not user.email_verified
    message = "Verification code resent. Check your inbox and spam folder." if is_resend else "Verification email sent"
    
    response = {
        "message": message,
        "email": masked_email,
        "expires_in_seconds": 600,
        "can_resend_in_seconds": 60,
        "is_resend": is_resend  # Frontend can use this to show "check spam" message
    }
    
    # Dev mode: return OTP in response for debugging
    if settings.ENVIRONMENT == "development":
        response["dev_otp"] = otp_code
        
    return response


@router.post("/verify-email")
async def verify_email(
    verification_code: EmailVerificationCode,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email with OTP code
    
    Security:
    -Max 5 attempts per OTP
    - Constant-time comparison
    - Auto-invalidation after expiration
    """
    from app.core.otp_service import OTPService
    
    email = verification_code.email
    otp = verification_code.otp
    
    # OTP format already validated by Pydantic schema
    if not otp.isdigit() or len(otp) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP format"
        )
    
    # Verify OTP
    ip_address = request.client.host if request.client else None
    success, error_msg = await OTPService.verify_otp(db, email, otp, ip_address)
    
    if not success:
        await log_admin_event(
            level=LogLevel.WARNING,
            category=LogCategory.AUTHENTICATION,
            event_name="email_verification_failed",
            message=f"Failed verification attempt for {email}: {error_msg}",
            user_email=email,
            ip_address=ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Mark user as verified
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if user:
        user.email_verified = True
        await db.commit()
        await db.refresh(user)
        
        await log_admin_event(
            level=LogLevel.INFO,
            category=LogCategory.AUTHENTICATION,
            event_name="email_verified",
            message=f"Email verified successfully: {email}",
            user_id=user.id,
            user_email=email,
            ip_address=ip_address
        )
        
        return {
            "verified": True,
            "message": "Email verified successfully",
            "user": {
                "email": user.email,
                "email_verified": user.email_verified
            }
        }
    
    # For signup flow: return success even if user doesn't exist yet
    # User will be created after verification in the signup process
    return {
        "verified": True,
        "message": "Email verified successfully"
    }


@router.post("/resend-verification-email")
async def resend_verification_email(
    verification_request: EmailVerificationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(RateLimiter(times=50, seconds=3600))
):
    """
    Resend OTP verification email
    Invalidates previous OTPs for this email
    """
    from app.core.otp_service import OTPService
    from app.core.email_service import EmailService
    from datetime import datetime
    
    # Extract email from request body
    email = verification_request.email
    
    # Check rate limit
    allowed, seconds_until_reset = OTPService.check_rate_limit(email, limit=50, window_hours=1)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many requests. Try again in {seconds_until_reset} seconds."
        )
    
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    if user.email_verified:
        return {"message": "Email already verified"}
    
    # Invalidate existing OTPs
    invalidated_count = await OTPService.invalidate_existing_otps(db, email)
    
    # Generate new OTP
    otp_code = OTPService.generate_otp()
    
    # Store new OTP
    ip_address = request.client.host if request.client else None
    await OTPService.create_otp(db, email, otp_code, ip_address)
    
    # Send email
    # Dev mode: log OTP AND send email
    if settings.ENVIRONMENT == "development":
        logger.warning(f"[DEV MODE] Resend OTP for {email}: {otp_code}")
        print(f"\n\n===== DIGIT OTP CODE: {otp_code} =====\n\n")

    # Always attempt to send email
    success, error_msg = await EmailService.send_verification_email(
        email=email,
        otp=otp_code,
        user_name=user.full_name
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg or "Failed to send email"
        )
    
    # Update user record
    user.email_verification_sent_at = datetime.utcnow()
    await db.commit()
    
    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.AUTHENTICATION,
        event_name="verification_email_resent",
        message=f"Verification email resent to {email} (invalidated {invalidated_count} old OTPs)",
        user_id=user.id,
        user_email=email,
        ip_address=ip_address
    )
    
    email_parts = email.split('@')
    masked_email = f"{email_parts[0][:2]}**@{email_parts[1]}"
    
    response = {
        "message": "New verification email sent",
        "email": masked_email,
        "expires_in_seconds": 600
    }
    
    # Dev mode: return OTP in response for debugging
    if settings.ENVIRONMENT == "development":
        response["dev_otp"] = otp_code
        
    return response

