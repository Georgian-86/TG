"""
Content Agent
Generates detailed content for each lesson section
"""
from typing import Dict, Any, List
import asyncio
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    """Generates instructional content and finds resources"""
    
    async def generate_section(self, topic: str, level: str, section_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content for a specific section"""
        system_prompt = (
            "You are a senior instructional designer with expertise in creating "
            "engaging, clear, and pedagogically sound educational content. "
            "Return ONLY valid JSON."
        )
        
        user_prompt = f"""
Topic: {topic}
Level: {level}
Section Title: {section_info['title']}
Section Focus: {section_info['description']}

MANDATORY REQUIREMENTS:
- Target Word Count: 120-150 words
- Use clear, accessible language appropriate for {level} learners
- Include real-world and industry examples where relevant
- Structure content logically (intro → explanation → example → application)
- Be specific and practical, avoid generic statements

Generate the instructional content for this section.

OUTPUT FORMAT (JSON):
{{
    "title": "{section_info['title']}",
    "content": "Detailed instructional content with real-world examples..."
}}
"""
        return await self.call_llm(system_prompt, user_prompt)

    async def run_parallel(self, topic: str, level: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate all sections in parallel for speed"""
        tasks = [self.generate_section(topic, level, s) for s in sections]
        return await asyncio.gather(*tasks)

    async def find_resources(self, topic: str, level: str) -> List[Dict[str, Any]]:
        """Find relevant web resources"""
        system_prompt = (
            "You are an expert educational resource curator. "
            "Return ONLY valid JSON with realistic, high-quality resource URLs."
        )
        
        user_prompt = f"""
Topic: {topic}
Learner Level: {level}

Find EXACTLY 5 high-quality web learning resources that:
1. Are from reputable educational sources (Khan Academy, Coursera, MIT OpenCourseWare, etc.)
2. Match the {level} learning level
3. Cover different aspects of {topic}
4. Have realistic URLs (follow actual URL patterns of the platforms)
5. Include a mix of formats (articles, videos, interactive tutorials)

OUTPUT FORMAT (JSON):
{{
    "resources": [
        {{
            "title": "Clear, descriptive title",
            "url": "https://realistic-domain.com/path"
        }}
    ]
}}
"""
        
        try:
            result = await self.call_llm(system_prompt, user_prompt)
            resources = result.get("resources", [])
            
            # Fallback resources if empty or too few
            if len(resources) < 3:
                fallback_resources = [
                    {
                        "title": f"Introduction to {topic}",
                        "url": "https://www.khanacademy.org"
                    },
                    {
                        "title": f"{topic} Tutorial",
                        "url": "https://www.coursera.org"
                    },
                    {
                        "title": f"Understanding {topic}",
                        "url": "https://ocw.mit.edu"
                    }
                ]
                resources.extend(fallback_resources[len(resources):5])
            
            return resources[:5]  # Ensure exactly 5
            
        except Exception as e:
            logger.error(f"Resource finding failed: {e}")
            # Return fallback resources on error
            return [
                {"title": f"Introduction to {topic}", "url": "https://www.khanacademy.org"},
                {"title": f"{topic} Course", "url": "https://www.coursera.org"},
                {"title": f"{topic} Learning Path", "url": "https://ocw.mit.edu"},
                {"title": f"Interactive {topic} Tutorial", "url": "https://www.codecademy.com"},
                {"title": f"{topic} Documentation", "url": "https://developer.mozilla.org"}
            ]
