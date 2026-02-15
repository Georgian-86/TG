"""
Fail-Safe Quiz Agent
Generates scenario-based multiple choice questions with strict schema enforcement.
Level-appropriate, localized or globally accessible quiz questions.
"""
import logging
from typing import Dict, Any, List
from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)

class QuizAgent(BaseAgent):
    """Quiz Agent Class for LLM interaction"""
    pass

# --------------------------------------------------
# CANONICAL QUIZ SCHEMA (DO NOT CHANGE)
#
# state["quiz"] = {
#     "questions": [
#         {
#             "scenario": str,
#             "question": str,
#             "options": { "A": str, "B": str, "C": str, "D": str },
#             "correct_option": "A",
#             "explanation": str,
#             "rbt_level": "Apply | Analyze | Evaluate"
#         }
#     ]
# }
# --------------------------------------------------


async def quiz_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    FAIL-SAFE QUIZ AGENT

    Guarantees:
    - ALWAYS returns a dict
    - state["quiz"] is ALWAYS a dict
    - state["quiz"]["questions"] is ALWAYS a list
    - options are ALWAYS a dict (A/B/C/D)
    """
    agent = QuizAgent()
    
    # -------------------------------
    # Absolute safety guard
    # -------------------------------
    if not isinstance(state, dict):
        state = {}

    topic = state.get("topic", "General Topic")
    level = state.get("level", "Undergraduate")
    marks = state.get("quiz_marks", 20)
    country = state.get("country", "Global")
    duration = int(state.get("duration", 60))

    quiz_duration = state.get("quiz_duration", 10)

    # Calculate number of questions based on lesson duration (from duration_profile)
    from app.agents.utils import duration_profile
    profile = duration_profile(duration)
    num_questions = profile["scenarios"]  # Use scenarios count from duration profile

    # Get level profile and localization guidance for appropriate question design
    from app.agents.utils import get_level_profile, get_localization_guidance, requires_localization
    level_profile = get_level_profile(level)
    localization_guidance = get_localization_guidance(topic, country)
    needs_local, category = requires_localization(topic)

    # Adjust system prompt based on whether topic needs localization
    if needs_local and country != "Global":
        context_instruction = f"""
LOCALIZATION REQUIREMENT:
This topic ({category}) requires {country}-specific scenarios and examples.
- Use {country} regulatory frameworks, laws, and standards
- Reference {country}-specific organizations and authorities
- Use local currency and measurement units
- Include scenarios relevant to {country} context"""
    else:
        context_instruction = """
GLOBAL ACCESSIBILITY:
- Use universal scenarios that work across cultures
- Avoid idioms, slang, or region-specific examples
- Use metric units and international standards"""

    system_prompt = f"""You are an expert assessment designer creating quiz questions.

Your questions must be:
1. Level-appropriate for {level_profile['age_range']} learners
2. Testing higher-order thinking (Application, Analysis, Evaluation)
3. Accurate and relevant to the topic context

{context_instruction}

STRICT OUTPUT FORMAT:
- Output ONLY a JSON ARRAY (no surrounding object)
- Each element represents ONE question

Each question MUST include:
- scenario (realistic situation relevant to the context)
- question (clear, unambiguous)
- options (array of exactly 4 strings, all plausible)
- correct_option (A, B, C, or D)
- explanation (why the answer is correct)
- rbt_level (Apply / Analyze / Evaluate)

Do NOT include markdown or commentary."""

    user_prompt = f"""
TOPIC: {topic}
EDUCATION LEVEL: {level}
USER COUNTRY: {country}
NUMBER OF QUESTIONS: {num_questions}

{localization_guidance}

LEVEL-SPECIFIC REQUIREMENTS:
- Vocabulary: {level_profile['vocabulary']}
- Example Types: {level_profile['examples']}
- Assessment Focus: {level_profile['assessment']}
- Complexity: {level_profile['complexity']}

QUESTION GUIDELINES:

1. SCENARIO DESIGN:
   - Use real-world situations relevant to {topic}
   - Make scenarios internationally applicable
   - Include specific details that require analysis

2. COGNITIVE LEVEL:
   For {level} level, focus on:
   - Application: Using knowledge in new situations
   - Analysis: Breaking down complex problems
   - Evaluation: Making judgments based on criteria

3. OPTION QUALITY:
   - All 4 options must be plausible
   - Avoid "all of the above" or "none of the above"
   - Make wrong options represent common misconceptions

4. GLOBAL ACCESSIBILITY:
   - Use metric units and international standards
   - Avoid cultural assumptions
   - Reference globally recognized examples
"""

    raw_questions = []

    try:
        parsed = await agent.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            json_output=True 
        )
        
        if isinstance(parsed, list):
            raw_questions = parsed
        elif isinstance(parsed, dict):
            for key, value in parsed.items():
                if isinstance(value, list):
                    raw_questions = value
                    break

    except Exception as e:
        logger.error(f"Quiz Agent LLM call failed: {e}")
        raw_questions = []

    # -------------------------------
    # HARD FALLBACK (never empty)
    # -------------------------------
    if not raw_questions:
        raw_questions = [
            {
                "scenario": "A team must apply a concept under time and resource constraints.",
                "question": "What is the most appropriate action?",
                "options": [
                    "Choose the fastest approach",
                    "Choose the most accurate approach",
                    "Balance accuracy with feasibility",
                    "Defer the decision"
                ],
                "correct_option": "C",
                "explanation": "Application-level decisions require contextual trade-offs.",
                "rbt_level": "Apply"
            }
        ]

    # -------------------------------
    # SCHEMA ENFORCEMENT (CRITICAL)
    # -------------------------------
    canonical_questions = []

    for q in raw_questions:

        opts = q.get("options", [])
        if not isinstance(opts, list) or len(opts) != 4:
            opts = ["Option A", "Option B", "Option C", "Option D"]

        options_dict = {
            "A": opts[0],
            "B": opts[1],
            "C": opts[2],
            "D": opts[3],
        }

        canonical_questions.append({
            "scenario": q.get("scenario", ""),
            "question": q.get("question", ""),
            "options": options_dict,
            "correct_option": q.get("correct_option", "A"),
            "explanation": q.get("explanation", ""),

            "rbt_level": q.get("rbt_level", "Apply") if state.get("include_rbt", True) else None
        })


    # -------------------------------
    # ENFORCE EXACT QUESTION COUNT
    # Truncate to match duration_profile to prevent LLM over-generation
    # (e.g., 60 min → 2 questions, not 5)
    # -------------------------------


    # -------------------------------
    # FINAL, SAFE ASSIGNMENT
    # -------------------------------
    # Limit questions to exact count requested
    canonical_questions = canonical_questions[:num_questions]
    
    state["quiz"] = {
        "questions": canonical_questions
    }

    return state
