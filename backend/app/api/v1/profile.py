"""
Profile Management API Endpoints
Handles user profile updates and avatar uploads
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.profile import ProfileUpdate, ProfileResponse
from app.core.security import get_current_user
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile
    """
    return current_user


@router.put("/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile information
    """
    try:
        # Update only provided fields
        update_data = profile_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"Profile updated for user: {current_user.email}")
        return current_user
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/profile/avatar", response_model=dict)
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload user avatar to local storage
    """
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Create uploads directory if not exists
    upload_dir = os.path.join("app", "uploads", "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate filename
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{current_user.id}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Generate URL
    # Assuming the app is mounted at root, and we mount /uploads at /uploads
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/uploads/avatars/{filename}"
    
    # Update user's profile picture URL
    current_user.profile_picture_url = file_url
    await db.commit()
    
    return {
        "message": "Avatar uploaded successfully",
        "url": file_url
    }


@router.delete("/profile/avatar")
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove user's avatar
    """
    current_user.profile_picture_url = None
    await db.commit()
    
    return {"message": "Avatar removed successfully"}
