"""
Key Takeaways Agent
Extracts and generates concise key takeaways from lesson content
Async class-based implementation with BaseAgent inheritance
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
        sections: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate key takeaways from lesson content
        
        Args:
            topic: Lesson topic
            level: Educational level
            learning_objectives: List of learning objectives
            sections: Lesson sections with content
            
        Returns:
            List of 5 concise key takeaways
        """
        logger.info(f"Generating key takeaways for: {topic}")
        
        # Build content summary for context
        content_summary = "\n".join([
            f"- {section.get('title', '')}: {section.get('content', '')[:100]}..."
            for section in sections[:3]  # Use first 3 sections for context
        ])
        
        system_prompt = (
            "You are an expert educator skilled at distilling complex lessons into "
            "memorable, actionable key takeaways. Return JSON only."
        )
        
        user_prompt = f"""
Topic: {topic}
Learner Level: {level}

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in learning_objectives[:4])}

Lesson Content Overview:
{content_summary}

Generate EXACTLY 5 concise, memorable key takeaways that:
1. Capture the most important concepts from this lesson
2. Are practical and actionable
3. Use clear, simple language appropriate for {level} learners
4. Each takeaway should be 1-2 sentences maximum
5. Focus on what students should remember and be able to do

Output Format (JSON):
{{
    "key_takeaways": [
        "First key takeaway...",
        "Second key takeaway...",
        "Third key takeaway...",
        "Fourth key takeaway...",
        "Fifth key takeaway..."
    ]
}}
"""
        
        try:
            result = await self.call_llm(system_prompt, user_prompt)
            takeaways = result.get("key_takeaways", [])
            
            # Ensure we have exactly 5 takeaways
            if len(takeaways) < 5:
                # Add fallback takeaways if needed
                fallbacks = [
                    f"Understand the fundamental concepts of {topic}",
                    f"Apply {topic} principles to real-world scenarios",
                    f"Recognize common patterns and applications in {topic}",
                    f"Analyze problems using {topic} methodologies",
                    f"Evaluate outcomes and interpret results correctly"
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
                f"Understand the core concepts of {topic}",
                f"Apply {topic} to practical situations",
                f"Recognize key patterns in {topic}",
                f"Analyze and solve problems using {topic}",
                f"Evaluate and interpret results correctly"
            ]
