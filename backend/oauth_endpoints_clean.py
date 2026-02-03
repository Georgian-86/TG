

# ===== Google OAuth Endpoints =====

@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow
    Redirects user to Google consent screen
    """
    from app.core.oauth import oauth
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session (in production, use Redis)
    request.session['oauth_state'] = state
    
    # Build authorization URL
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)


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
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = await get_google_user_info(token)
        
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
            # Existing user - update OAuth fields if needed
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = google_id
                user.profile_picture_url = profile_picture
            user.last_login_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)
            
        else:
            # New user - create account
            user = User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(secrets.token_urlsafe(32)),  # Random password
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
        
        # Build response URL based on profile completion status
        if user.profile_completed:
            frontend_url = f"http://localhost:3000/generator?token={access_token}"
        else:
            frontend_url = f"http://localhost:3000/complete-profile?token={access_token}"
        
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        print(f"Google OAuth error: {e}")
        # In production, log the full error
        return RedirectResponse(url=f"http://localhost:3000/login?error=oauth_failed")


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
