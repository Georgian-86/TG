"""
Content Agent
Generates detailed content for each lesson section
Expert instructional design with FULLY DYNAMIC content structure based on topic and duration
"""
from typing import Dict, Any, List
import asyncio
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    """Generates instructional content and finds resources with FULLY DYNAMIC structure"""
    
    def _get_subsection_count(self, duration: int) -> tuple:
        """Determine number of subsections based on duration"""
        if duration <= 15:
            return (2, 3)  # min, max subsections
        elif duration <= 30:
            return (3, 4)
        elif duration <= 60:
            return (4, 5)
        elif duration <= 90:
            return (5, 6)
        else:
            return (5, 7)
    
    async def generate_section(self, topic: str, level: str, section_info: Dict[str, Any], duration: int = 60, country: str = "Global") -> Dict[str, Any]:
        """Generate content for a specific section with FULLY DYNAMIC subsections"""
        
        from app.agents.utils import get_level_profile, duration_profile, get_localization_guidance
        level_profile = get_level_profile(level)
        dur_profile = duration_profile(duration)
        localization_guidance = get_localization_guidance(topic, country)
        
        # Get dynamic subsection count based on duration
        min_subs, max_subs = self._get_subsection_count(duration)
        
        # Adjust depth instruction based on duration
        depth_instruction = dur_profile.get("depth_guidance", "Provide comprehensive content")
            
        system_prompt = f"""You are a world-renowned instructional designer and subject matter expert.

Your task is to generate DYNAMIC content subsections that are PERFECTLY TAILORED to the specific topic.
DO NOT use generic structures - CREATE subsections that make sense for THIS EXACT topic.

Your content must be:
1. Pedagogically sound and evidence-based
2. TOPIC-SPECIFIC - subsection names must reflect what makes sense for this particular topic
3. Engaging, memorable, and intellectually stimulating
4. Precisely calibrated to the learner's level
5. Rich with subject-specific examples and explanations

CRITICAL: 
- You decide the subsection titles based on what the topic requires
- Generate content as READABLE TEXT, not nested JSON
- Each subsection should be a flowing paragraph or structured text

Return ONLY valid JSON with string content values."""
        
        user_prompt = f"""
TOPIC: {topic}
EDUCATION LEVEL: {level}
SECTION: {section_info.get('title', 'Untitled')}
SECTION FOCUS: {section_info.get('description', section_info.get('content', 'General overview'))}
LESSON DURATION: {duration} minutes

LEVEL-SPECIFIC REQUIREMENTS:
- Vocabulary: {level_profile['vocabulary']}
- Complexity: {level_profile['complexity']}
- Cognitive Load: {level_profile['cognitive_load']}

{localization_guidance}

DYNAMIC CONTENT REQUIREMENTS:
1. Create {min_subs}-{max_subs} subsections that are PERFECT for "{topic}"
2. YOU DECIDE the subsection titles - make them specific to this topic
3. Examples of dynamic subsection naming:
   - For "Macbeth": "Character Analysis", "Key Themes", "Historical Context", "Famous Soliloquies"
   - For "Photosynthesis": "The Light Reactions", "Calvin Cycle", "Chloroplast Structure", "Real-World Importance"
   - For "World War II": "Causes of the War", "Major Battles", "Key Figures", "Impact on Society"
   - For "Python Programming": "Basic Syntax", "Data Types", "Control Flow", "Best Practices"

4. Use examples DIRECTLY RELEVANT to "{topic}" - NOT generic case studies
5. Make content engaging and intellectually rich

DEPTH: {depth_instruction}

OUTPUT FORMAT (JSON with YOUR chosen subsection names):
{{
    "title": "{section_info.get('title', 'Section')}",
    "content": {{
        "your_chosen_subsection_1": "Well-written paragraph(s) for this subtopic...",
        "your_chosen_subsection_2": "Detailed explanation with topic-specific content...",
        "your_chosen_subsection_3": "More content as appropriate...",
        ... (create {min_subs}-{max_subs} subsections that make sense for {topic})
    }}
}}

IMPORTANT: 
- Subsection keys should be descriptive and topic-specific (use snake_case)
- All content values must be properly formatted text strings, not nested objects
- The number of subsections should match the lesson duration ({duration} mins = {min_subs}-{max_subs} subsections)
"""
        return await self.call_llm(system_prompt, user_prompt, temperature=0.4)

    async def run_parallel(self, topic: str, level: str, sections: List[Dict[str, Any]], duration: int = 60, country: str = "Global") -> List[Dict[str, Any]]:
        """Generate all sections in parallel"""
        tasks = [self.generate_section(topic, level, s, duration, country) for s in sections]
        results = await asyncio.gather(*tasks)
        return list(results)

    async def find_resources(self, topic: str, level: str) -> List[Dict[str, Any]]:
        """Find relevant web resources"""
        from app.agents.utils import get_level_profile
        level_profile = get_level_profile(level)
        
        system_prompt = """You are an expert educational resource curator with access to global learning platforms.
Return ONLY valid JSON with realistic, high-quality resource URLs from reputable sources."""
        
        user_prompt = f"""
TOPIC: {topic}
EDUCATION LEVEL: {level}
TARGET AUDIENCE: {level_profile['age_range']}

Find EXACTLY 8 high-quality web learning resources that:

1. PLATFORM DIVERSITY (include at least one from each category):
   - Video platforms: YouTube (educational channels), Khan Academy, Coursera
   - Interactive: Codecademy, Brilliant, PhET Simulations
   - Reference: Wikipedia, Britannica, MDN, official documentation
   - Academic: MIT OCW, Stanford Online, edX

2. LEVEL APPROPRIATENESS:
   - Match {level} level complexity
   - Use {level_profile['vocabulary']}

3. GLOBAL ACCESSIBILITY:
   - Prefer resources available worldwide
   - Include free resources where possible

4. RESOURCE TYPES (include variety):
   - web_pages: Articles, tutorials
   - videos: Educational videos, lectures
   - research_articles: Academic papers (for higher levels)
   - blogs: Expert blogs, Medium articles

OUTPUT FORMAT (JSON):
{{
    "resources": [
        {{ "title": "Resource Title", "url": "https://...", "type": "web_pages|videos|research_articles|blogs" }}
    ]
}}
"""
        
        try:
            result = await self.call_llm(system_prompt, user_prompt, temperature=0.2)
            resources = result.get("resources", [])
            if not resources or not isinstance(resources, list):
                raise ValueError("No resources found or invalid format")
            return resources[:8]
        except Exception:
            return [
                {"title": f"Introduction to {topic}", "url": "https://www.khanacademy.org", "type": "videos"},
                {"title": f"{topic} Course", "url": "https://www.coursera.org", "type": "web_pages"},
                {"title": f"Understanding {topic}", "url": "https://ocw.mit.edu", "type": "web_pages"},
                {"title": f"{topic} - Wikipedia", "url": "https://en.wikipedia.org", "type": "web_pages"},
                {"title": f"Interactive {topic} Tutorial", "url": "https://www.brilliant.org", "type": "web_pages"},
                {"title": f"{topic} Explained", "url": "https://www.youtube.com", "type": "videos"},
                {"title": f"{topic} Documentation", "url": "https://developer.mozilla.org", "type": "web_pages"},
                {"title": f"Learn {topic}", "url": "https://www.edx.org", "type": "web_pages"}
            ]

async def content_agent(state):
    """
    Generates content based on the existing lesson plan.
    """
    agent = ContentAgent()
    topic = state.get("topic", "Untitled")
    level = state.get("level", "Beginner")
    duration = state.get("duration", 60)
    country = state.get("country", "Global")
    
    # Check if a plan exists (from PlannerAgent)
    lesson_plan = state.get("lesson_plan", {})
    sections = lesson_plan.get("sections", [])
    
    if sections:
        logger.info(f"Executing existing plan with {len(sections)} sections for {country}...")
        
        # 1. Generate Content for Sections (Parallel)
        full_sections = await agent.run_parallel(topic, level, sections, duration, country)
        
        # Update plan with full content
        lesson_plan["sections"] = full_sections
        
        # 2. Find Resources (since Planner doesn't do it)
        resources = await agent.find_resources(topic, level)
        lesson_plan["resources"] = resources
        
    else:
        # Fallback: One-Shot Generation (Old Logic) if no plan exists
        logger.warning("No lesson plan found. Using fallback one-shot generation.")
        duration = state.get("duration", 60)
        from app.agents.utils import duration_profile
        profile = duration_profile(duration)
        num_objectives = profile["objectives"]
        
        prompt = f"""
        Generate a detailed lesson plan on {topic} for {level} level.
        Include {num_objectives} objectives, 4-6 sections of content, and 5 resources.
        Return JSON with keys: title, level, duration, objectives, sections, resources.
        """
        try:
            lesson_plan = await agent.call_llm("Return JSON only.", prompt)
        except Exception:
            lesson_plan = {}
            
    # Safety Defaults
    lesson_plan.setdefault("title", topic)
    lesson_plan.setdefault("level", level)
    lesson_plan.setdefault("objectives", [f"Understand {topic}"])
    lesson_plan.setdefault("sections", [{"title": "Intro", "content": f"Introduction to {topic}"}])
    lesson_plan.setdefault("resources", [])
    
    state["lesson_plan"] = lesson_plan
    state["resources"] = lesson_plan["resources"]
    
    return state
