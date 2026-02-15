"""
Planner Agent
Responsible for creating the high-level lesson structure
Expert curriculum design with level-appropriate, country-specific or globally accessible content
"""
from typing import Dict, Any
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Generates the initial structure and objectives for a lesson"""
    
    async def run(self, topic: str, level: str, duration: int, include_quiz: bool = False, country: str = "Global") -> Dict[str, Any]:
        """Generate lesson structure"""
        logger.info(f"Planning lesson: {topic} ({level}) for {country}")
        
        from app.agents.utils import duration_profile, get_level_guidance, get_level_profile, get_localization_guidance, requires_localization
        profile = duration_profile(duration)
        level_guidance = get_level_guidance(level)
        level_profile = get_level_profile(level)
        localization_guidance = get_localization_guidance(topic, country)
        needs_local, category = requires_localization(topic)
        target_sections = len(profile["sections"])
        target_objectives = profile["objectives"]
        
        # CRITICAL: Only show country when the topic actually needs localization
        # For universal science topics (Newton's Law, etc.), hide country to prevent LLM bias
        country_line = f"USER COUNTRY: {country}" if (needs_local and country != "Global") else "USER COUNTRY: Global (Universal Topic)"
        
        # Build system prompt - remove country-specific language for universal topics
        if needs_local:
            system_prompt = """You are a world-class curriculum designer with expertise in:
- Instructional design and learning science
- Cross-cultural education and localized content
- Age-appropriate pedagogy for all education levels
- Evidence-based teaching methodologies
- Country-specific regulations and standards (when applicable)

Your curricula must be:
1. Appropriately localized for topics requiring country-specific knowledge (law, accounting, commerce)
2. Globally accessible for universal topics (science, mathematics, technology)
3. Pedagogically sound and research-backed
4. Appropriately challenging for the target level

Return ONLY valid JSON."""
        else:
            system_prompt = """You are a world-class curriculum designer with expertise in:
- Instructional design and learning science
- Universal scientific and academic content
- Age-appropriate pedagogy for all education levels
- Evidence-based teaching methodologies

Your curricula must be:
1. GLOBALLY ACCESSIBLE — do NOT reference any specific country, nation, or region
2. Universally applicable — use international examples and standards only
3. Pedagogically sound and research-backed
4. Appropriately challenging for the target level

IMPORTANT: This is a universal topic. Do NOT mention any country name (India, USA, etc.) anywhere in the output.

Return ONLY valid JSON."""
        
        user_prompt = f"""
TOPIC: {topic}
EDUCATION LEVEL: {level}
TOTAL DURATION: {duration} minutes
QUIZ INCLUDED: {include_quiz}
{country_line}

{level_guidance}

{localization_guidance}

DURATION-BASED STRUCTURE GUIDANCE:
- Depth: {profile['depth_guidance']}
- Suggested Pacing: {profile['pacing']}

CURRICULUM DESIGN REQUIREMENTS:

1. LEARNING OBJECTIVES (EXACTLY {target_objectives}):
   - Must be specific, measurable, and achievable within {duration} minutes
   - Use action verbs appropriate for {level} level
   - Progress from foundational to more complex skills
   - Avoid vague statements like "understand the basics"

2. SECTION STRUCTURE (EXACTLY {target_sections} SECTIONS):
   Required sections for {duration}-minute lesson: {', '.join(profile['sections'])}
   
   **IMPORTANT**: Section titles must be topic-specific and engaging.
   - ❌ BAD: "Worked Examples: Key Events", "Applications: Real World Uses"  
   - ✅ GOOD: "Key Events of the French Revolution", "Modern Climate Change Impacts"
   - DO NOT use generic prefixes like "Introduction:", "Examples:", "Applications:", etc.
   - Each title should directly describe the specific content for THIS topic
   
   Each section must have:
   - Clear, engaging, topic-specific title (no generic words)
   - Specific content focus (not generic descriptions)
   - Logical flow from previous section

3. GLOBAL ACCESSIBILITY:
   - Use examples that resonate across cultures
   - Avoid region-specific references unless universally known
   - Consider diverse learner backgrounds

4. LEVEL-APPROPRIATE CONTENT:
   - Vocabulary: {level_profile['vocabulary']}
   - Examples: {level_profile['examples']}
   - Complexity: {level_profile['complexity']}

OUTPUT FORMAT (JSON):
{{
    "title": "Clear, Engaging Lesson Title",
    "level": "{level}",
    "duration": "{duration} minutes",
    "objectives": [
        "Specific learning objective 1",
        "Specific learning objective 2"
    ],
    "sections": [
        {{"title": "Section Title", "content": "Specific focus and approach for this section"}},
    ],
    "quiz_enabled": {str(include_quiz).lower()}
}}
"""
        
        try:
            plan = await self.call_llm(system_prompt, user_prompt, temperature=0.2)
            # Ensure strictly formatted fields
            if "duration" not in plan:
                plan["duration"] = f"{duration} minutes"
            plan["quiz_enabled"] = include_quiz 
            return plan
        except Exception as e:
            logger.error(f"Planner Agent failed: {e}")
            # Fallback structure
            return {
                "title": topic,
                "level": level,
                "duration": f"{duration} minutes",
                "objectives": [
                    f"Understand the fundamental concepts of {topic}",
                    f"Apply {topic} principles to practical scenarios",
                    f"Analyze real-world applications of {topic}"
                ][:target_objectives],
                "sections": [
                    {"title": section, "content": f"Comprehensive coverage of {section.lower()} for {topic}."}
                    for section in profile["sections"]
                ],
                "quiz_enabled": include_quiz
            }

async def planner_agent(state):
    """
    Creates the teaching plan with sections, duration, and quiz flag.
    (Functional wrapper for LangGraph compatibility)
    """
    agent = PlannerAgent()
    topic = state.get("topic", "Untitled")
    level = state.get("level", "School")
    # Ensure duration is an integer
    duration = int(state.get("duration", 60))
    include_quiz = state.get("include_quiz", False)
    country = state.get("country", "Global")
    
    plan = await agent.run(topic, level, duration, include_quiz, country)
    
    state["lesson_plan"] = plan
    return state
