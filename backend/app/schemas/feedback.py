from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Union, Dict, Any

class FeedbackCreate(BaseModel):
    # Section 1: Context
    designation: Optional[str] = None
    department: Optional[str] = None
    teaching_experience: Optional[str] = None
    rating_context: Optional[int] = 0

    # Section 2: Usage
    usage_frequency: Optional[str] = None
    primary_purpose: Optional[List[str]] = None
    used_outputs: Optional[List[str]] = None
    rating_usage: Optional[int] = 0

    # Section 3: Time
    time_saved: Optional[str] = None
    speed_vs_manual: Optional[str] = None
    value_single_click: Optional[str] = None
    rating_time: Optional[int] = 0

    # Section 4: Zero-Prompt
    zero_prompt_ease: Optional[str] = None
    complexity_vs_others: Optional[str] = None
    rating_zero_prompt: Optional[int] = 0

    # Section 5: Content
    content_accuracy: Optional[str] = None
    classroom_suitability: Optional[str] = None
    quiz_scenario_relevance: Optional[str] = None
    rating_content: Optional[int] = 0

    # Section 6: UX
    interface_intuitive: Optional[str] = None
    technical_issues: Optional[str] = None
    rating_interface: Optional[int] = 0

    # Section 7: Comparison
    comparison_vs_llm: Optional[str] = None
    comparison_objective: Optional[str] = None

    # Section 8: Adoption
    will_use_regularly: Optional[str] = None
    will_recommend: Optional[str] = None
    support_adoption: Optional[str] = None
    rating_adoption: Optional[int] = 0

    # Section 9: Open Feedback
    liked_most: Optional[str] = None
    liked_least: Optional[str] = None
    feature_requests: Optional[str] = None
    testimonial_consent: Optional[bool] = False

    # Section 10: Verdict & Performance
    one_sentence_verdict: Optional[str] = None
    avg_generation_time: Optional[str] = None
    delay_experience: Optional[str] = None
    failure_frequency: Optional[str] = None
    # Removed fields to match DB model (failure_details, reliability_rating, etc.)
    rating_workflow: Optional[int] = 0
    
    # Overall Rating
    overall_rating: Optional[int] = 0

    technical_issues_details: Optional[str] = None
    
    model_config = ConfigDict(extra='allow')

class FeedbackResponse(BaseModel):
    id: int
    user_id: str
    message: str = "Feedback received successfully. Trials unlocked."
