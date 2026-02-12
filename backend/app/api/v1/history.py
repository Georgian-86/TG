"""
Lesson History API Endpoints
Handles lesson generation history and favorites
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, desc, func
from app.database import get_db
from app.models.user import User
from app.models.lesson import Lesson, LessonStatus
# from app.models.lesson_history import LessonHistory (Deprecated)
from app.schemas.profile import (
    LessonHistoryCreate,
    LessonHistoryResponse,
    LessonHistoryDetail,
    LessonHistoryList
)
from app.core.security import get_current_user
from typing import Optional, List
import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/history", response_model=LessonHistoryList)
async def get_lesson_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    favorites_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's lesson generation history from the main Lesson table
    """
    try:
        # Build query on Lesson table
        query = select(Lesson).where(
            Lesson.user_id == current_user.id,
            Lesson.status == LessonStatus.COMPLETED  # Only show completed lessons
        )
        
        # Filter by search term
        if search:
            query = query.where(Lesson.topic.ilike(f"%{search}%"))
        
        # Filter by favorites
        if favorites_only:
            query = query.where(Lesson.is_favorite == True)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(desc(Lesson.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await db.execute(query)
        lessons = result.scalars().all()
        
        # Map Lesson objects to LessonHistoryResponse schema
        items = []
        for lesson in lessons:
            items.append(LessonHistoryResponse(
                id=lesson.id,
                user_id=lesson.user_id,
                topic=lesson.topic,
                level=lesson.level.value if hasattr(lesson.level, 'value') else str(lesson.level),  # Convert enum to string
                duration=lesson.duration,
                title=lesson.topic,  # Use topic as title since Lesson doesn't have title field
                is_favorite=lesson.is_favorite,
                tags=None,  # Lesson model doesn't have tags
                created_at=lesson.created_at
            ))
        
        total_pages = math.ceil(total / page_size)
        
        return LessonHistoryList(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch lesson history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch lesson history"
        )


@router.get("/history/{lesson_id}", response_model=LessonHistoryDetail)
async def get_lesson_detail(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed lesson including full content
    """
    result = await db.execute(
        select(Lesson).where(
            Lesson.id== lesson_id,
            Lesson.user_id == current_user.id
        )
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Map Lesson to LessonHistoryDetail
    import json
    return LessonHistoryDetail(
        id=lesson.id,
        user_id=lesson.user_id,
        topic=lesson.topic,
        level=lesson.level.value if hasattr(lesson.level, 'value') else str(lesson.level),
        duration=lesson.duration,
        title=lesson.topic,
        is_favorite=lesson.is_favorite,
        tags=None,
        created_at=lesson.created_at,
        lesson_data=json.dumps(lesson.lesson_plan) if lesson.lesson_plan else None,
        updated_at=lesson.updated_at
    )


# Note: POST /save is deprecated as lessons are saved automatically upon generation. 
# Keeping it for backward compatibility if needed, but pointing to Lesson table.
@router.post("/save", response_model=LessonHistoryResponse, status_code=status.HTTP_201_CREATED)
async def save_lesson(
    lesson_data: LessonHistoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually save a lesson (Legacy)
    """
    try:
        new_lesson = Lesson(
            user_id=current_user.id,
            topic=lesson_data.topic,
            level=lesson_data.level,
            duration=lesson_data.duration,
            lesson_plan=lesson_data.lesson_data, # Map data
            status=LessonStatus.COMPLETED
        )
        
        db.add(new_lesson)
        await db.commit()
        await db.refresh(new_lesson)
        
        return new_lesson
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save lesson: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lesson"
        )


@router.post("/history/{lesson_id}/favorite")
async def toggle_favorite(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle favorite status for a lesson
    """
    result = await db.execute(
        select(Lesson).where(
            Lesson.id == lesson_id,
            Lesson.user_id == current_user.id
        )
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    lesson.is_favorite = not lesson.is_favorite
    await db.commit()
    
    return {
        "message": "Favorite status updated",
        "is_favorite": lesson.is_favorite
    }


@router.delete("/history/{lesson_id}")
async def delete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a lesson
    """
    result = await db.execute(
        delete(Lesson).where(
            Lesson.id == lesson_id,
            Lesson.user_id == current_user.id
        )
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    await db.commit()
    return {"message": "Lesson deleted successfully"}
