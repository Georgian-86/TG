"""
Quiz Agent
Generates scenario-based assessment questions
Enhanced with adaptive question count and answer diversity
"""
from typing import Dict, Any, List
import random
from app.agents.base import BaseAgent
import logging

logger = logging.getLogger(__name__)

class QuizAgent(BaseAgent):
    """Generates gamified quiz questions based on lesson content"""
    
    async def run(
        self,
        topic: str,
        level: str,
        quiz_duration: int = 10,
        quiz_marks: int = 20
    ) -> Dict[str, Any]:
        """Generate quiz questions based on topic, level, and duration"""
        logger.info(f"Generating quiz for: {topic} ({quiz_duration} minutes)")
        
        # Adaptive question count based on quiz duration
        if quiz_duration <= 5:
            num_scenarios = 2
        elif quiz_duration <= 10:
            num_scenarios = 3
        elif quiz_duration <= 15:
            num_scenarios = 4
        else:
            num_scenarios = 5
        
        system_prompt = (
            "You are an expert educator designing a GAMIFIED, REAL-LIFE quiz. "
            "Return ONLY valid JSON."
        )
        
        user_prompt = f"""
You are an expert educator designing a GAMIFIED, REAL-LIFE quiz.

Topic: {topic}
Learner level: {level}

STRICT RULES:
- Generate EXACTLY {num_scenarios} real-life scenarios
- Each scenario MUST be practical and decision-based
- DO NOT repeat correct answers across questions
- Correct option MUST vary between A, B, C, D
- Do NOT always choose option A

Each question MUST include:
- scenario (real-world context)
- question (clear decision to make)
- 4 options (A, B, C, D)
- correct_option (one of A/B/C/D)
- explanation (clear justification)

OUTPUT ONLY VALID JSON:

{{
  "quiz_title": "{topic} – Gamified Assessment",
  "total_marks": {quiz_marks},
  "questions": [
    {{
      "scenario": "Real-world situation...",
      "question": "What should you do?",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_option": "B",
      "explanation": "Detailed explanation..."
    }}
  ]
}}
"""
        
        try:
            quiz = await self.call_llm(system_prompt, user_prompt)
            
            # Safety check: ensure answer diversity
            questions = quiz.get("questions", [])
            used = set()
            
            for q in questions:
                # Validate correct_option is valid
                if q.get("correct_option") not in {"A", "B", "C", "D"}:
                    q["correct_option"] = random.choice(["A", "B", "C", "D"])
                
                # Ensure diversity in correct answers
                if q["correct_option"] in used and len(used) < 4:
                    available = [x for x in ["A", "B", "C", "D"] if x not in used]
                    if available:
                        q["correct_option"] = random.choice(available)
                
                used.add(q["correct_option"])
            
            logger.info(f"Generated {len(questions)} quiz questions")
            return quiz
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            return {"questions": []}
