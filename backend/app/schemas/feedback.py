from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class FeedbackCreate(BaseModel):
    """
    Schema matching all 10+1 sections of the frontend FeedbackModal.
    Every field the frontend sends is captured here.
    """
    model_config = ConfigDict(extra="allow")  # Accept any extra fields gracefully

    # Section 1: Basic Info & Context
    designation: Optional[str] = None
    department: Optional[str] = None
    teaching_experience: Optional[str] = None
    rating_context: Optional[int] = 0

    # Section 2: Usage & Adoption
    usage_frequency: Optional[str] = None
    primary_purpose: Optional[List[str]] = None
    rating_usage: Optional[int] = 0

    # Section 3: Time & Productivity
    time_saved: Optional[str] = None
    speed_vs_manual: Optional[str] = None
    value_single_click: Optional[str] = None
    rating_time: Optional[int] = 0

    # Section 4: Zero-Prompt Experience
    zero_prompt_ease: Optional[str] = None
    complexity_vs_others: Optional[str] = None
    rating_zero_prompt: Optional[int] = 0

    # Section 5: Content Quality & Academic Relevance
    content_accuracy: Optional[str] = None
    classroom_suitability: Optional[str] = None
    quiz_scenario_relevance: Optional[str] = None
    rating_content: Optional[int] = 0

    # Section 6: UX & Interface
    interface_intuitive: Optional[str] = None
    technical_issues: Optional[str] = None          # "Yes" / "No"
    technical_issues_details: Optional[str] = None  # Free-text details if Yes
    rating_interface: Optional[int] = 0

    # Section 7: Comparison & Objective
    comparison_vs_llm: Optional[str] = None
    comparison_objective: Optional[str] = None

    # Section 8: Adoption & Recommendation
    will_use_regularly: Optional[str] = None
    will_recommend: Optional[str] = None
    support_adoption: Optional[str] = None
    rating_adoption: Optional[int] = 0

    # Section 9: Open Feedback
    liked_most: Optional[str] = None
    liked_least: Optional[str] = None
    feature_requests: Optional[str] = None
    testimonial_consent: Optional[bool] = False

    # Section 10: Final Verdict
    one_sentence_verdict: Optional[str] = None
    avg_generation_time: Optional[str] = None
    workflow_satisfaction: Optional[str] = None
    rating_workflow: Optional[int] = 0

    # Section 11: Overall Rating
    overall_rating: Optional[int] = 0

class FeedbackResponse(BaseModel):
    id: int
    user_id: str
    message: str = "Feedback received successfully. Trials unlocked."
