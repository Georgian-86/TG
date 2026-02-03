"""
Planner Agent
Responsible for creating the high-level lesson structure
"""
from typing import Dict, Any
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Generates the initial structure and objectives for a lesson"""
    
    async def run(self, topic: str, level: str, duration: int) -> Dict[str, Any]:
        """Generate lesson structure"""
        logger.info(f"Planning lesson: {topic} ({level})")
        
        system_prompt = (
            "You are an expert curriculum designer. Your goal is to create a logical "
            "structure for a lesson based on the user's topic, level, and duration. "
            "Return JSON only."
        )
        
        user_prompt = f"""
        Topic: {topic}
        Learner Level: {level}
        Total Duration: {duration} minutes
        
        Generate a structure that includes:
        1. A clear title.
        2. 4-6 specific learning objectives.
        3. A logical sequence of 5 sections. 
           - For each section, provide just the 'title' and a 'description' of what it should cover.
           - Duration for each section must sum to {duration} minutes.
        
        Example Output Format:
        {{
            "title": "Introduction to Linear Regression",
            "objectives": ["Obj 1", "Obj 2"],
            "sections": [
                {{"title": "Section Title", "description": "What to cover", "duration_minutes": 10}}
            ]
        }}
        """
        
        try:
            plan = await self.call_llm(system_prompt, user_prompt)
            return plan
        except Exception as e:
            logger.error(f"Planner Agent failed: {e}")
            # Fallback structure if LLM fails
            return {
                "title": topic,
                "objectives": ["Understand core concepts", "Apply to real-life scenarios"],
                "sections": [
                    {"title": "Introduction", "description": "Overview of the topic", "duration_minutes": duration // 5},
                    {"title": "Core Concepts", "description": "Key theories and ideas", "duration_minutes": duration // 5},
                    {"title": "Examples", "description": "Step-by-step examples", "duration_minutes": duration // 5},
                    {"title": "Applications", "description": "Real-world uses", "duration_minutes": duration // 5},
                    {"title": "Summary", "description": "Conclusion and wrap-up", "duration_minutes": duration // 5}
                ]
            }
