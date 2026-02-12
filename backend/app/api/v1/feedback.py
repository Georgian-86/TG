from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
import json
import logging

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback and unlock remaining free trials.
    """
    logger = logging.getLogger("app.api.feedback")
    logger.info(f"Feedback submission started for user {current_user.id}")

    try:
        # Create Feedback Entry
        db_feedback = Feedback(
            # Explicit mapping to prevent Pydantic/SQLAlchemy mismatches
            user_id=current_user.id,
            designation=feedback.designation,
            department=feedback.department,
            teaching_experience=feedback.teaching_experience,
            
            usage_frequency=feedback.usage_frequency,
            primary_purpose=json.dumps(feedback.primary_purpose) if feedback.primary_purpose else None,
            used_outputs=json.dumps(feedback.used_outputs) if feedback.used_outputs else None,
            
            time_saved=feedback.time_saved,
            speed_vs_manual=feedback.speed_vs_manual,
            value_single_click=feedback.value_single_click,
            
            zero_prompt_ease=feedback.zero_prompt_ease,
            complexity_vs_others=feedback.complexity_vs_others,
            rating_zero_prompt=feedback.rating_zero_prompt,
            
            content_accuracy=feedback.content_accuracy,
            classroom_suitability=feedback.classroom_suitability,
            quiz_scenario_relevance=feedback.quiz_scenario_relevance,
            rating_content=feedback.rating_content,
            
            interface_intuitive=feedback.interface_intuitive,
            technical_issues=feedback.technical_issues,
            rating_interface=feedback.rating_interface,
            
            comparison_vs_llm=feedback.comparison_vs_llm,
            comparison_objective=feedback.comparison_objective,
            
            will_use_regularly=feedback.will_use_regularly,
            will_recommend=feedback.will_recommend,
            support_adoption=feedback.support_adoption,
            rating_adoption=feedback.rating_adoption,
            
            liked_most=feedback.liked_most,
            liked_least=feedback.liked_least,
            feature_requests=feedback.feature_requests,
            testimonial_consent=feedback.testimonial_consent,
            
            one_sentence_verdict=feedback.one_sentence_verdict,
            avg_generation_time=feedback.avg_generation_time,
            rating_workflow=feedback.rating_workflow,
            overall_rating=feedback.overall_rating
        )
        
        db.add(db_feedback)
        logger.info("Feedback object added to session")
        
        # Unlock Trials - Reset lesson counter to give fresh quota
        from sqlalchemy import update
        stmt = update(User).where(User.id == current_user.id).values(
            feedback_provided=True,
            lessons_this_month=0  # Reset counter to give fresh quota after feedback
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(db_feedback)
        
        logger.info(f"Feedback submitted successfully. User {current_user.email} quota reset to 0/{current_user.lessons_quota}")
        
        return FeedbackResponse(
            id=db_feedback.id,
            user_id=current_user.id
        )

    except Exception as e:
        import traceback
        logger.error(f"FEEDBACK SUBMISSION FATAL ERROR: {str(e)}\n{traceback.format_exc()}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Submission failed: {str(e)}"
        )
