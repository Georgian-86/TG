"""
Lesson API Endpoints
Lesson generation, retrieval, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import time
import asyncio
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.lesson import Lesson, LessonStatus
from app.schemas.lesson import LessonCreate, LessonResponse, LessonStatusResponse
from app.core.security import get_current_active_user, RateLimiter
from app.agents.orchestrator import AgentOrchestrator
from app.core.logging_utils import log_admin_event
from app.models.admin_log import LogLevel, LogCategory

router = APIRouter()
orchestrator = AgentOrchestrator()

# Concurrency limiter: max 25 simultaneous lesson generations
# Prevents OpenAI API and DB connection exhaustion under load
_generation_semaphore = asyncio.Semaphore(25)

async def generate_lesson_task(lesson_id: str, topic: str, level: str, duration: int, include_quiz: bool, db_session_factory):
    """Background task to run the AI orchestrator"""
    start_time = time.time()
    
    try:
        # We need a fresh session for background tasks
        async with db_session_factory() as db:
            try:
                # Get the lesson record
                result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
                lesson = result.scalar_one_or_none()
                if not lesson:
                    print(f"Lesson {lesson_id} not found in background task")
                    return

                # Update status to generating
                lesson.status = LessonStatus.GENERATING
                lesson.error_message = None  # Clear any previous error
                await db.commit()
                
                print(f"Starting generation for lesson {lesson_id}: {topic}")

                # Run orchestrator
                lesson_data = await orchestrator.generate_full_lesson(topic, level, duration, include_quiz)
                
                print(f"Generation complete for {lesson_id}")

                # Update lesson with results
                lesson.lesson_plan = lesson_data["sections"]
                lesson.resources = lesson_data["resources"]
                lesson.quiz = lesson_data["quiz"]
                lesson.learning_objectives = lesson_data.get("learning_objectives", [])
                lesson.status = LessonStatus.COMPLETED
                lesson.completed_at = datetime.utcnow()
                lesson.processing_time_seconds = int(time.time() - start_time)
                
                # Use generated key takeaways from orchestrator
                lesson.key_takeaways = lesson_data.get("key_takeaways", [])

                await db.commit()
                
                print(f"Lesson {lesson_id} saved to database successfully")
                
                await log_admin_event(
                    level=LogLevel.INFO,
                    category=LogCategory.USER_ACTION,
                    event_name="lesson_generated",
                    message=f"Lesson generated successfully: {topic}",
                    user_id=lesson.user_id
                )

            except Exception as e:
                # Handle failure - refetch lesson in case session was closed
                print(f"Error generating lesson {lesson_id}: {str(e)}")
                import traceback
                traceback.print_exc()
                
                try:
                    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
                    lesson = result.scalar_one_or_none()
                    if lesson:
                        lesson.status = LessonStatus.FAILED
                        lesson.error_message = str(e)[:500]  # Limit error message length
                        await db.commit()
                        print(f"Lesson {lesson_id} marked as FAILED")
                except Exception as commit_error:
                    print(f"Failed to update lesson status: {commit_error}")
                
                await log_admin_event(
                    level=LogLevel.ERROR,
                    category=LogCategory.SYSTEM,
                    event_name="lesson_generation_failed",
                    message=f"Failed to generate lesson: {str(e)}",
                    event_metadata={"lesson_id": lesson_id, "topic": topic}
                )
    
    except Exception as outer_error:
        print(f"Critical error in background task: {outer_error}")
        import traceback
        traceback.print_exc()


@router.post("/generate", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_in: LessonCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI lesson (Synchronous with caching - returns completed lesson)
    Generation takes ~20-30 seconds, cached results return instantly
    """
    print(f"DEBUG: Starting lesson generation for topic: {lesson_in.topic}")
    import asyncio
    from app.core.cache import get_cache
    
    # Check concurrency limit before proceeding
    if _generation_semaphore._value == 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is busy generating lessons. Please try again in a moment."
        )
    
    # Check usage quota
    if current_user.lessons_this_month >= current_user.lessons_quota:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Monthly lesson quota exceeded. Please upgrade your plan."
        )

    # Check cache first (before creating DB record)
    cache = get_cache()
    cached_data = await cache.get(
        topic=lesson_in.topic,
        level=lesson_in.level,
        duration=lesson_in.duration,
        include_quiz=lesson_in.include_quiz
    )
    
    if cached_data:
        # Create DB record from cached data
        new_lesson = Lesson(
            user_id=current_user.id,
            topic=lesson_in.topic,
            level=lesson_in.level,
            duration=lesson_in.duration,
            include_quiz=lesson_in.include_quiz,
            include_rbt=lesson_in.include_rbt,
            lo_po_mapping=lesson_in.lo_po_mapping,
            iks_integration=lesson_in.iks_integration,
            status=LessonStatus.COMPLETED,
            lesson_plan=cached_data["sections"],
            resources=cached_data.get("resources"),
            quiz=cached_data.get("quiz"),
            learning_objectives=cached_data.get("learning_objectives", []),
            key_takeaways=cached_data.get("key_takeaways", []),
            processing_time_seconds=0,  # Instant from cache
            completed_at=datetime.utcnow()
        )
        
        # Convert file paths to URLs for downloads
        if cached_data.get("ppt_path"):
            new_lesson.ppt_url = "/" + cached_data["ppt_path"].replace("\\", "/")
        if cached_data.get("pdf_path"):
            new_lesson.pdf_url = "/" + cached_data["pdf_path"].replace("\\", "/")
        
        db.add(new_lesson)
        current_user.lessons_this_month += 1
        await db.commit()
        await db.refresh(new_lesson)
        
        await log_admin_event(
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            event_name="lesson_cached_retrieved",
            message=f"Cached lesson retrieved: {new_lesson.topic}",
            user_id=current_user.id
        )
        
        response = LessonResponse.from_orm(new_lesson)
        response.generation_time = 0.0  # Instant from cache
        return response

    # Create initial database record
    new_lesson = Lesson(
        user_id=current_user.id,
        topic=lesson_in.topic,
        level=lesson_in.level,
        duration=lesson_in.duration,
        include_quiz=lesson_in.include_quiz,
        include_rbt=lesson_in.include_rbt,
        lo_po_mapping=lesson_in.lo_po_mapping,
        iks_integration=lesson_in.iks_integration,
        status=LessonStatus.GENERATING
    )
    
    db.add(new_lesson)
    current_user.lessons_this_month += 1
    await db.commit()
    await db.refresh(new_lesson)

    await log_admin_event(
        level=LogLevel.INFO,
        category=LogCategory.USER_ACTION,
        event_name="lesson_generation_started",
        message=f"User {current_user.email} started lesson generation: {new_lesson.topic}",
        user_id=current_user.id
    )

    # Run generation with timeout (90 seconds max)
    start_time = time.time()
    
    try:
        # Apply timeout and concurrency limit
        async with _generation_semaphore:
          async with asyncio.timeout(120):
            # Calculate quiz parameters based on lesson duration
            # Quiz duration is approximately 1/6 of lesson duration (10-15% of class time)
            quiz_duration = max(5, min(new_lesson.duration // 6, 30))  # Min 5 min, Max 30 min
            
            # Quiz marks scale more aggressively: 5 marks per minute of quiz
            # This gives more questions for longer lessons to match blueprint expectations
            quiz_marks = max(20, min(quiz_duration * 5, 100))  # Min 20 (2 qs), Max 100 marks
            
            # Generate lesson content with user's country for localization
            lesson_data = await orchestrator.generate_full_lesson(
                new_lesson.topic,
                new_lesson.level,
                new_lesson.duration,
                new_lesson.include_quiz,
                quiz_duration=quiz_duration,
                quiz_marks=quiz_marks,
                country=current_user.country or "Global",  # Use user's country for localized content
                include_rbt=new_lesson.include_rbt
            )

        # Update lesson with results
        new_lesson.lesson_plan = lesson_data["sections"]
        new_lesson.resources = lesson_data["resources"]
        new_lesson.quiz = lesson_data["quiz"]
        new_lesson.learning_objectives = lesson_data.get("learning_objectives", [])
        new_lesson.status = LessonStatus.COMPLETED
        new_lesson.completed_at = datetime.utcnow()
        new_lesson.processing_time_seconds = int(time.time() - start_time)
        new_lesson.key_takeaways = lesson_data.get("key_takeaways", [])
        
        # Convert file paths to URLs for downloads
        if lesson_data.get("ppt_path"):
            # Convert "outputs/file.pptx" to "/outputs/file.pptx"
            new_lesson.ppt_url = "/" + lesson_data["ppt_path"].replace("\\", "/")
        if lesson_data.get("pdf_path"):
            new_lesson.pdf_url = "/" + lesson_data["pdf_path"].replace("\\", "/")

        await db.commit()
        await db.refresh(new_lesson)
        
        # Cache the generated lesson for future requests
        await cache.set(
            topic=new_lesson.topic,
            level=new_lesson.level,
            duration=new_lesson.duration,
            include_quiz=new_lesson.include_quiz,
            data=lesson_data
        )
        
        # Convert enums to strings for proper serialization
        response_data = LessonResponse.from_orm(new_lesson)
        response_data.generation_time = float(new_lesson.processing_time_seconds) if new_lesson.processing_time_seconds else 0.0
        
        await log_admin_event(
            level=LogLevel.INFO,
            category=LogCategory.USER_ACTION,
            event_name="lesson_generated",
            message=f"Lesson generated successfully: {new_lesson.topic}",
            user_id=current_user.id
        )
        
        return response_data

    except asyncio.TimeoutError:
        # Handle timeout
        # Refund the quota since generation failed
        current_user.lessons_this_month = max(0, current_user.lessons_this_month - 1)
        
        new_lesson.status = LessonStatus.FAILED
        new_lesson.error_message = "Generation timed out after 90 seconds. Please try again or reduce lesson duration."
        
        db.add(current_user)
        await db.commit()
        await db.refresh(new_lesson)
        
        await log_admin_event(
            level=LogLevel.ERROR,
            category=LogCategory.SYSTEM,
            event_name="lesson_generation_timeout",
            message=f"Lesson generation timed out: {new_lesson.topic}",
            event_metadata={"lesson_id": new_lesson.id, "topic": new_lesson.topic}
        )
        
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Lesson generation timed out after 90 seconds. Please try again with a shorter duration."
        )
        
    except Exception as e:
        # Handle failure with detailed logging
        import traceback
        error_trace = traceback.format_exc()
        
        print(f"❌ Lesson generation error: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        
        # Refund the quota since generation failed
        current_user.lessons_this_month = max(0, current_user.lessons_this_month - 1)
        
        new_lesson.status = LessonStatus.FAILED
        new_lesson.error_message = str(e)[:500]
        
        db.add(current_user)
        await db.commit()
        await db.refresh(new_lesson)
        
        await log_admin_event(
            level=LogLevel.ERROR,
            category=LogCategory.SYSTEM,
            event_name="lesson_generation_failed",
            message=f"Failed to generate lesson: {str(e)}",
            event_metadata={"lesson_id": new_lesson.id, "topic": new_lesson.topic, "error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lesson generation failed: {str(e)}"
        )

    return new_lesson


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get lesson details and status"""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    if lesson.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized to view this lesson")
    
    return lesson
