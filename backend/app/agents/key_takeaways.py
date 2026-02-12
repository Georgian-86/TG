"""
Key Takeaways Agent
Extracts and generates concise key takeaways from lesson content
Level-appropriate, localized or globally accessible key insights
"""
from typing import Dict, Any, List
import logging
from app.agents.base import BaseAgent

logger = logging.getLogger(__name__)


class KeyTakeawaysAgent(BaseAgent):
    """Generates concise key takeaways from lesson content"""
    
    async def run(
        self,
        topic: str,
        level: str,
        learning_objectives: List[str],
        sections: List[Dict[str, Any]],
        country: str = "Global"
    ) -> List[Dict[str, str]]:
        """
        Generate key takeaways from lesson content
        
        Args:
            topic: Lesson topic
            level: Educational level
            learning_objectives: List of learning objectives
            sections: Lesson sections with content
            country: User's country for localization
            
        Returns:
            List of dictionaries with 'title' and 'description'
        """
        logger.info(f"Generating key takeaways for: {topic} ({country})")
        
        # Get level profile and localization guidance
        from app.agents.utils import get_level_profile, get_localization_guidance, requires_localization
        level_profile = get_level_profile(level)
        localization_guidance = get_localization_guidance(topic, country)
        needs_local, category = requires_localization(topic)
        
        # Validate inputs to prevent slice errors
        if not isinstance(sections, list):
            sections = []
        if not isinstance(learning_objectives, list):
            learning_objectives = []
        
        # Build content summary for context
        content_summary = "\n".join([
            f"- {section.get('title', '')}: {str(section.get('content', ''))[:150]}..."
            for section in sections[:4]  # Use first 4 sections for context
        ])
        
        # Adjust context based on whether topic needs localization
        if needs_local and country != "Global":
            context_instruction = f"Takeaways should reflect {country}-specific context where relevant to the topic."
        else:
            context_instruction = "Use universally understood concepts accessible worldwide."
        
        system_prompt = """You are an expert educator creating memorable key takeaways.

Your takeaways must be:
1. Memorable and immediately useful
2. Appropriately contextualized (localized for country-specific topics, global for universal topics)
3. Focused on core insights, not procedural steps
4. Different from learning objectives (insights, not goals)

Return ONLY valid JSON."""
        
        user_prompt = f"""
TOPIC: {topic}
EDUCATION LEVEL: {level}
TARGET AUDIENCE: {level_profile['age_range']}
USER COUNTRY: {country}

LEARNING OBJECTIVES (for context, DO NOT repeat these):
{chr(10).join(f"- {obj}" for obj in learning_objectives[:5])}

LESSON CONTENT OVERVIEW:
{content_summary}

{localization_guidance}

LEVEL-SPECIFIC REQUIREMENTS:
- Vocabulary: {level_profile['vocabulary']}
- Complexity: {level_profile['complexity']}

KEY TAKEAWAY DESIGN GUIDELINES:

1. STRUCTURE (EXACTLY 5 takeaways):
   Each takeaway MUST have:
   - "title": Short header (2-5 words) - the key concept
   - "description": One complete sentence explaining the insight

2. CONTENT QUALITY:
   - Focus on "aha moments" and core insights
   - Make them memorable and quotable
   - Ensure practical applicability
   - DO NOT repeat learning objectives verbatim

3. CONTEXT:
   - {context_instruction}

4. LEVEL APPROPRIATENESS:
   - For {level}: {level_profile['depth']} insights
   - Language: {level_profile['vocabulary']}

GOOD EXAMPLES:
{{
    "title": "Supply Meets Demand",
    "description": "Market prices naturally adjust to balance what sellers offer with what buyers want, creating equilibrium."
}}
{{
    "title": "Code Reusability",
    "description": "Functions allow you to write logic once and use it multiple times, reducing errors and saving development time."
}}

BAD EXAMPLES (DO NOT DO):
- Repeating objectives: "Understand the concept of supply and demand"
- Vague statements: "This topic is important for many reasons"
- Missing title: {{"title": "", "description": "..."}}

OUTPUT FORMAT (JSON):
{{
    "key_takeaways": [
        {{
            "title": "Short Memorable Header",
            "description": "Complete explanatory sentence with the key insight."
        }}
    ]
}}
"""
        
        try:
            result = await self.call_llm(system_prompt, user_prompt)
            takeaways = result.get("key_takeaways", [])
            
            # Ensure proper format
            if not isinstance(takeaways, list):
                 takeaways = []

            # Ensure we have exactly 5 takeaways
            if len(takeaways) < 5:
                # Add fallback takeaways if needed
                fallbacks = [
                    {"title": f"Core Concept", "description": f"{topic} represents a foundational idea with applications across multiple domains."},
                    {"title": "Practical Application", "description": f"The principles of {topic} can be directly applied to solve real-world problems."},
                    {"title": "Key Relationship", "description": f"Understanding how {topic} connects to related concepts enhances overall comprehension."},
                    {"title": "Common Patterns", "description": f"Recognizing recurring patterns in {topic} helps predict outcomes and make better decisions."},
                    {"title": "Global Relevance", "description": f"{topic} plays a significant role in international contexts and cross-cultural applications."}
                ]
                takeaways.extend(fallbacks[len(takeaways):5])
            
            # Truncate to exactly 5
            takeaways = takeaways[:5]
            
            logger.info(f"Generated {len(takeaways)} key takeaways")
            return takeaways
            
        except Exception as e:
            logger.error(f"Key takeaways generation failed: {e}")
            # Return fallback takeaways on error
            return [
                {"title": f"Core Concept", "description": f"{topic} represents a foundational idea with applications across multiple domains."},
                {"title": "Practical Application", "description": f"The principles of {topic} can be directly applied to solve real-world problems."},
                {"title": "Key Relationship", "description": f"Understanding how {topic} connects to related concepts enhances overall comprehension."},
                {"title": "Common Patterns", "description": f"Recognizing recurring patterns in {topic} helps predict outcomes and make better decisions."},
                {"title": "Global Relevance", "description": f"{topic} plays a significant role in international contexts and cross-cultural applications."}
            ]

async def key_takeaways_agent(state):
    """
    Extracts key takeaways from lesson content.
    (Functional wrapper for LangGraph compatibility)
    """
    agent = KeyTakeawaysAgent()
    topic = state.get("topic", "Untitled")
    level = state.get("level", "Beginner")
    country = state.get("country", "Global")
    
    # Get sections from plan
    plan = state.get("lesson_plan", {})
    sections = plan.get("sections", [])
    
    # Get objectives (handle strings or objects)
    raw_objectives = state.get("learning_objectives", [])
    learning_objectives = []
    
    for obj in raw_objectives:
        if isinstance(obj, dict):
            # Safe extraction avoiding None
            text = obj.get("text")
            if text:
                learning_objectives.append(text)
        elif isinstance(obj, str):
            learning_objectives.append(obj)
            
    # Use the class method for robust generation
    takeaways = await agent.run(topic, level, learning_objectives, sections, country)
    
    # Validation: Ensure we are NOT returning objectives by clear collision check
    # (Though this shouldn't happen with the new logic)
    
    state["key_takeaways"] = takeaways
    return state
