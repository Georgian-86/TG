from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Section 1: Context
    designation = Column(String(255))
    department = Column(String(255))
    teaching_experience = Column(String(50))
    rating_context = Column(Integer, default=0)

    # Section 2: Usage
    usage_frequency = Column(String(50))
    primary_purpose = Column(Text)  # Stored as JSON string
    used_outputs = Column(Text)     # Stored as JSON string
    rating_usage = Column(Integer, default=0)

    # Section 3: Time & Productivity
    time_saved = Column(String(50))
    speed_vs_manual = Column(String(50))
    value_single_click = Column(String(50))
    rating_time = Column(Integer, default=0)

    # Section 4: Zero-Prompt Experience
    zero_prompt_ease = Column(String(50))
    # manual_guidance_needed removed
    complexity_vs_others = Column(String(50))
    rating_zero_prompt = Column(Integer, default=0)

    # Section 5: Content Quality & Academic Relevance
    content_accuracy = Column(String(50))
    classroom_suitability = Column(String(50))
    quiz_scenario_relevance = Column(String(50)) # Renamed from quiz_relevance
    rating_content = Column(Integer, default=0)

    # Section 6: User Experience & Interface
    interface_intuitive = Column(String(50))
    technical_issues = Column(Text)
    rating_interface = Column(Integer, default=0)

    # Section 7: Comparison & Positioning
    comparison_vs_llm = Column(Text) # Replaced vs_traditional/vs_other_ai
    comparison_objective = Column(String(50)) # New objective question

    # Section 8: Adoption & Recommendation
    will_use_regularly = Column(String(50))
    will_recommend = Column(String(50))
    support_adoption = Column(String(50))
    rating_adoption = Column(Integer, default=0)

    # Section 9: Open Feedback
    liked_most = Column(Text, nullable=True)
    liked_least = Column(Text, nullable=True)
    feature_requests = Column(Text, nullable=True)
    testimonial_consent = Column(Boolean, default=False)

    # Section 10: Final Verdict & Performance
    one_sentence_verdict = Column(Text, nullable=True)
    avg_generation_time = Column(String(50))
    delay_experience = Column(String(50))
    failure_frequency = Column(String(50))
    failure_details = Column(Text, nullable=True)
    # reliability_rating removed/not requested directly but keeping if valid, user said 'overall rating at very end'
    # Keeping other metrics
    retry_frequency = Column(String(50))
    speed_vs_others = Column(String(50))
    workflow_satisfaction = Column(String(50))
    confidence_impact = Column(String(50))
    rating_workflow = Column(Integer, default=0)
    
    # Overall Rating (Moved to end conceptually)
    overall_rating = Column(Integer, default=0)
    # Removed duplicate columns that were already defined above

    created_at = Column(DateTime(timezone=True), server_default=func.now())
