from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Section 1: Basic Info & Context
    designation = Column(String(255))
    department = Column(String(255))
    teaching_experience = Column(String(50))
    rating_context = Column(Integer, default=0)

    # Section 2: Usage & Adoption
    usage_frequency = Column(String(50))
    primary_purpose = Column(Text)  # Stored as JSON string (array)
    rating_usage = Column(Integer, default=0)

    # Section 3: Time & Productivity
    time_saved = Column(String(50))
    speed_vs_manual = Column(String(50))
    value_single_click = Column(String(50))
    rating_time = Column(Integer, default=0)

    # Section 4: Zero-Prompt Experience
    zero_prompt_ease = Column(String(50))
    complexity_vs_others = Column(String(50))
    rating_zero_prompt = Column(Integer, default=0)

    # Section 5: Content Quality & Academic Relevance
    content_accuracy = Column(String(50))
    classroom_suitability = Column(String(50))
    quiz_scenario_relevance = Column(String(50))
    rating_content = Column(Integer, default=0)

    # Section 6: UX & Interface
    interface_intuitive = Column(String(50))
    technical_issues = Column(String(50))  # "Yes" / "No"
    technical_issues_details = Column(Text, nullable=True)  # Free text if Yes
    rating_interface = Column(Integer, default=0)

    # Section 7: Comparison & Objective
    comparison_vs_llm = Column(Text)
    comparison_objective = Column(String(255))

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

    # Section 10: Final Verdict
    one_sentence_verdict = Column(Text, nullable=True)
    avg_generation_time = Column(String(50))
    workflow_satisfaction = Column(String(50))
    rating_workflow = Column(Integer, default=0)

    # Section 11: Overall Rating
    overall_rating = Column(Integer, default=0)

    # Safety net: store entire raw payload as JSON for future-proofing
    raw_response = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
