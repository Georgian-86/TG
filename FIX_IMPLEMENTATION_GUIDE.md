# Three-Part Fix Implementation Guide

## Issue 1: Hallucination with "Newton's Law of Cooling"

### Problem
The LLM is associating physics laws (e.g., "Newton's Law of Cooling") with regional/legal contexts because the `requires_localization()` function is too broad in detecting the word "Law". For physics "Laws," the country parameter should NOT trigger localization guidance.

### Solution
Update `get_localization_guidance()` in `utils.py` to distinguish between:
- **Physics/Science Laws (Universal)**: Law of Thermodynamics, Ohm's Law, Kepler's Laws
- **Legal/Commerce Laws (Region-Specific)**: Contract Law, Company Law, Tax Law

### Implementation
Add this helper function and update `requires_localization()`:

```python
UNIVERSAL_LAWS = {
    "newton", "ohm", "kepler", "boyle", "charles", "gay-lussac", "avogadro", "coulomb",
    "faraday", "ampere", "planck", "einstein", "heisenberg", "schrodinger", "pascal",
    "archimedes", "bernoulli", "hooke", "lenz", "kirchhoff", "stefan", "boltzmann",
    "conservation", "thermodynamic", "ideal", "gas", "motion", "gravity", "electromagnetic",
    "quantum", "relativity", "conservation of energy", "conservation of momentum"
}

def is_universal_law(topic: str) -> bool:
    """Check if topic is a universal scientific law"""
    topic_lower = topic.lower().strip()
    for law in UNIVERSAL_LAWS:
        if law in topic_lower:
            return True
    return False

def requires_localization(topic: str) -> tuple[bool, str]:
    """
    Check if a topic requires country-specific localization.
    Returns: (needs_localization: bool, category: str)
    """
    topic_lower = topic.lower().strip()
    
    # IMPORTANT: Physics/Science laws are NEVER region-specific
    if "law" in topic_lower and is_universal_law(topic):
        return False, "universal_science"
    
    # These ARE region-specific
    region_specific_keywords = {
        "law": ["contract", "criminal", "civil", "company", "tax", "labor", "property", "family", "constitutional"],
        "accounting": ["ifrs", "gaap", "accounting"],
        "commerce": ["trade", "business", "commerce", "commercial"],
        "economics": ["fiscal", "monetary", "economic"],
        "regulation": ["regulation", "regulatory", "compliance"]
    }
    
    for category, keywords in region_specific_keywords.items():
        for keyword in keywords:
            if keyword in topic_lower:
                return True, category
    
    return False, ""
```

---

## Issue 2: Dynamic Duration Profiles for Objectives, Takeaways, and Quiz

### Problem
Currently, the number of learning objectives, takeaways, and quiz questions are fixed. They should dynamically scale based on lesson duration (30 min → 60 min → longer).

### Solution
Update the `duration_profile()` function in `app/agents/utils.py` to return the complete structured profile with all dynamic values.

### Implementation Steps

**1. Update `duration_profile()` in `utils.py`:**

```python
def duration_profile(minutes: int) -> dict:
    """
    Return dynamic content profile based on lesson duration.
    This profile is used throughout the lesson generation pipeline.
    """
    if minutes <= 30:
        return {
            "objectives": 3,
            "sections": ["Introduction", "Core Concepts"],
            "takeaways": 3,
            "quiz": 1,
            "subsections_per_section": {"Introduction": 2, "Core Concepts": 3},
            "depth_guidance": "Focused coverage of essential concepts only",
            "pacing": "Brisk - ~15 minutes per section",
            "content_length": "concise"  # For agent prompts
        }
    elif minutes <= 45:
        return {
            "objectives": 4,
            "sections": ["Introduction", "Core Concepts", "Worked Examples"],
            "takeaways": 4,
            "quiz": 1,
            "subsections_per_section": {"Introduction": 2, "Core Concepts": 4, "Worked Examples": 3},
            "depth_guidance": "Moderate depth with practical examples",
            "pacing": "Moderate - ~15 minutes per section",
            "content_length": "moderate"
        }
    elif minutes <= 60:
        return {
            "objectives": 5,
            "sections": ["Introduction", "Core Concepts", "Worked Examples", "Applications"],
            "takeaways": 5,
            "quiz": 2,
            "subsections_per_section": {"Introduction": 2, "Core Concepts": 4, "Worked Examples": 3, "Applications": 3},
            "depth_guidance": "In-depth coverage with real-world applications",
            "pacing": "Moderate - ~15 minutes per section",
            "content_length": "detailed"
        }
    else:  # > 60 minutes
        return {
            "objectives": 6,
            "sections": ["Introduction", "Core Concepts", "Worked Examples", "Applications", "Discussion / Case Studies"],
            "takeaways": 6,
            "quiz": 3,
            "subsections_per_section": {"Introduction": 2, "Core Concepts": 5, "Worked Examples": 4, "Applications": 4, "Discussion / Case Studies": 3},
            "depth_guidance": "Comprehensive coverage with critical analysis and discussions",
            "pacing": "Leisurely - ~15 minutes per section with discussion",
            "content_length": "comprehensive"
        }
```

**2. Update `planner.py` to use ALL profile values:**

Line 60-77 needs to pass `profile["quiz"]` to the planning prompt:

```python
# In planner_agent function, extract quiz count from profile
quiz_question_count = profile.get("quiz", 1)  # Default to 1 if not in profile

user_prompt = f"""
...
TOTAL DURATION: {duration} minutes
QUIZ INCLUDED: {include_quiz}
QUIZ QUESTIONS EXPECTED: {quiz_question_count}
...
"""
```

**3. Update `quiz_agent()` in `quiz.py` to use profile["quiz"]:**

Instead of calculating num_questions dynamically, use the profile value:

```python
async def quiz_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """FAIL-SAFE QUIZ AGENT"""
    agent = QuizAgent()
    
    topic = state.get("topic", "General Topic")
    level = state.get("level", "Undergraduate")
    marks = state.get("quiz_marks", 20)
    country = state.get("country", "Global")
    duration = int(state.get("duration", 60))
    
    # GET quiz count from profile (not calculated)
    from app.agents.utils import duration_profile
    profile = duration_profile(duration)
    num_questions = profile["quiz"]  # Use profile value directly
    
    quiz_duration = state.get("quiz_duration", 10)
    #... rest of function
```

**4. Update `key_takeaways.py` to use profile["takeaways"]:**

```python
async def run(self, ...):
    """Generate key takeaways from lesson content"""
    from app.agents.utils import duration_profile
    profile = duration_profile(duration)
    target_takeaways = profile["takeaways"]  # Use instead of fixed count
    
    user_prompt = f"""
    ...
    GENERATE EXACTLY {target_takeaways} KEY TAKEAWAYS
    ...
    """
```

---

## Issue 3: Capture ALL Feedback Form Fields in Backend

### Problem
The frontend form collects 10 pages of detailed feedback, but the backend is missing some fields. The database model has the fields but they're not all being populated in the API endpoint.

### Solution
Update `backend/app/api/v1/feedback.py` to map ALL form fields to database columns.

### Missing Fields to Add
The frontend is sending these fields that aren't currently saved:

1. `delay_experience` - Step 10 (Time expectations)
2. `failure_frequency` - Step 10 (Reliability)
3. `failure_details` - Step 10 (Error reporting)
4. `retry_frequency` - Step 10 (Recovery frequency)
5. `speed_vs_others` - Step 10 (Comparison to other tools)
6. `confidence_impact` - Step 10 (Impact on user confidence)
7. `workflow_satisfaction` - Step 10 (Workflow satisfaction rating)
8. `used_outputs` - Step 2 (Which outputs were used - list)

### Implementation
Update `feedback.py` API endpoint (around line 65-90):

```python
@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit feedback and unlock remaining free trials."""
    logger = logging.getLogger("app.api.feedback")
    logger.info(f"Feedback submission started for user {current_user.id}")

    try:
        # Create Feedback Entry - MAP ALL FIELDS
        db_feedback = Feedback(
            # Section 1: Context
            user_id=current_user.id,
            designation=feedback.designation,
            department=feedback.department,
            teaching_experience=feedback.teaching_experience,
            rating_context=feedback.rating_context,
            
            # Section 2: Usage  
            usage_frequency=feedback.usage_frequency,
            primary_purpose=json.dumps(feedback.primary_purpose) if feedback.primary_purpose else None,
            used_outputs=json.dumps(feedback.used_outputs) if feedback.used_outputs else None,
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
            
            # Section 5: Content Quality
            content_accuracy=feedback.content_accuracy,
            classroom_suitability=feedback.classroom_suitability,
            quiz_scenario_relevance=feedback.quiz_scenario_relevance,
            rating_content=feedback.rating_content,
            
            # Section 6: UX & Interface
            interface_intuitive=feedback.interface_intuitive,
            technical_issues=feedback.technical_issues,
            rating_interface=feedback.rating_interface,
            
            # Section 7: Comparison
            comparison_vs_llm=feedback.comparison_vs_llm,
            comparison_objective=feedback.comparison_objective,
            
            # Section 8: Adoption
            will_use_regularly=feedback.will_use_regularly,
            will_recommend=feedback.will_recommend,
            support_adoption=feedback.support_adoption,
            rating_adoption=feedback.rating_adoption,
            
            # Section 9: Open Feedback
            liked_most=feedback.liked_most,
            liked_least=feedback.liked_least,
            feature_requests=feedback.feature_requests,
            testimonial_consent=feedback.testimonial_consent,
            
            # Section 10: Verdict & Performance - ADD MISSING FIELDS
            one_sentence_verdict=feedback.one_sentence_verdict,
            avg_generation_time=feedback.avg_generation_time,
            delay_experience=feedback.delay_experience,
            failure_frequency=feedback.failure_frequency,
            failure_details=feedback.failure_details,
            retry_frequency=feedback.retry_frequency,
            speed_vs_others=feedback.speed_vs_others,
            workflow_satisfaction=feedback.workflow_satisfaction,
            confidence_impact=feedback.confidence_impact,
            rating_workflow=feedback.rating_workflow,
            
            # Overall Rating
            overall_rating=feedback.overall_rating
        )
        
        db.add(db_feedback)
        logger.info("Feedback object added to session - ALL FIELDS CAPTURED")
        
        # Unlock Trials
        from sqlalchemy import update
        stmt = update(User).where(User.id == current_user.id).values(
            feedback_provided=True,
            lessons_this_month=0  # Reset counter
        )
        await db.execute(stmt)
        await db.commit()
        
        logger.info(f"Feedback saved successfully with all {len(feedback.__dict__)} fields")
        
        return FeedbackResponse(
            id=db_feedback.id,
            user_id=str(current_user.id),
            message="Feedback received successfully. Trials unlocked."
        )
        
    except Exception as e:
        logger.error(f"Error saving feedback: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Error processing feedback")
```

### Also ensure schema has all fields:

Update `backend/app/schemas/feedback.py` - verify all these fields are present:

```python
class FeedbackCreate(BaseModel):
    # ... existing fields ...
    
    # Section 10 - ADD THESE if missing
    delay_experience: Optional[str] = None
    failure_frequency: Optional[str] = None
    failure_details: Optional[str] = None
    retry_frequency: Optional[str] = None
    speed_vs_others: Optional[str] = None
    workflow_satisfaction: Optional[str] = None
    confidence_impact: Optional[str] = None
```

---

## Implementation Priority

1. **Issue #1 (Hallucination Fix)** - HIGHEST PRIORITY
   - Quick fix, prevents model confusion
   - Update `utils.py` only
   
2. **Issue #3 (Feedback Capture)** - MEDIUM PRIORITY  
   - Add ~8 missing fields to API endpoint
   - Ensure frontend form data is not lost
   
3. **Issue #2 (Dynamic Duration)** - MEDIUM-LOW PRIORITY
   - More widespread changes across multiple agents
   - Requires testing to ensure consistency

---

