from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
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
    Submit feedback (all 10+1 sections) and unlock remaining free trials.
    Stores every field from the frontend form + a raw JSON backup.
    """
    logger = logging.getLogger("app.api.feedback")
    logger.info(f"Feedback submission started for user {current_user.id}")

    try:
        # Dump the entire payload as raw JSON for safety/future-proofing
        raw_payload = feedback.model_dump()

        db_feedback = Feedback(
            user_id=current_user.id,

            # Section 1: Basic Info & Context
            designation=feedback.designation,
            department=feedback.department,
            teaching_experience=feedback.teaching_experience,
            rating_context=feedback.rating_context,

            # Section 2: Usage & Adoption
            usage_frequency=feedback.usage_frequency,
            primary_purpose=json.dumps(feedback.primary_purpose) if feedback.primary_purpose else None,
            rating_usage=feedback.rating_usage,

            # Section 3: Time & Productivity
            time_saved=feedback.time_saved,
            speed_vs_manual=feedback.speed_vs_manual,
            value_single_click=feedback.value_single_click,
            rating_time=feedback.rating_time,

            # Section 4: Zero-Prompt Experience
            zero_prompt_ease=feedback.zero_prompt_ease,
            complexity_vs_others=feedback.complexity_vs_others,
            rating_zero_prompt=feedback.rating_zero_prompt,

            # Section 5: Content Quality & Academic Relevance
            content_accuracy=feedback.content_accuracy,
            classroom_suitability=feedback.classroom_suitability,
            quiz_scenario_relevance=feedback.quiz_scenario_relevance,
            rating_content=feedback.rating_content,

            # Section 6: UX & Interface
            interface_intuitive=feedback.interface_intuitive,
            technical_issues=feedback.technical_issues,
            technical_issues_details=feedback.technical_issues_details,
            rating_interface=feedback.rating_interface,

            # Section 7: Comparison & Objective
            comparison_vs_llm=feedback.comparison_vs_llm,
            comparison_objective=feedback.comparison_objective,

            # Section 8: Adoption & Recommendation
            will_use_regularly=feedback.will_use_regularly,
            will_recommend=feedback.will_recommend,
            support_adoption=feedback.support_adoption,
            rating_adoption=feedback.rating_adoption,

            # Section 9: Open Feedback
            liked_most=feedback.liked_most,
            liked_least=feedback.liked_least,
            feature_requests=feedback.feature_requests,
            testimonial_consent=feedback.testimonial_consent,

            # Section 10: Final Verdict
            one_sentence_verdict=feedback.one_sentence_verdict,
            avg_generation_time=feedback.avg_generation_time,
            workflow_satisfaction=feedback.workflow_satisfaction,
            rating_workflow=feedback.rating_workflow,

            # Section 11: Overall Rating
            overall_rating=feedback.overall_rating,

            # Raw JSON backup of the entire payload
            raw_response=raw_payload,
        )

        db.add(db_feedback)
        logger.info(f"Feedback object added to session — all 10+1 sections captured")

        # Unlock Trials — Reset lesson counter to give fresh quota
        stmt = update(User).where(User.id == current_user.id).values(
            feedback_provided=True,
            lessons_this_month=0  # Reset counter to give fresh quota after feedback
        )
        await db.execute(stmt)
        await db.commit()
        await db.refresh(db_feedback)

        logger.info(f"✅ Feedback submitted successfully. User {current_user.email} quota reset to 0/{current_user.lessons_quota}")

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
