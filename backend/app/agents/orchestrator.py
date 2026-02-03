"""
Agent Orchestrator
Coordinates the sequence of agents to generate a complete lesson
Enhanced with presentation and key takeaways agents
"""
from typing import Dict, Any, List
import logging
import asyncio
from app.agents.planner import PlannerAgent
from app.agents.content import ContentAgent
from app.agents.quiz import QuizAgent
from app.agents.key_takeaways import KeyTakeawaysAgent
from app.agents.presentation import PresentationAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Manages the end-to-end generation workflow"""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.content_gen = ContentAgent()
        self.quiz_gen = QuizAgent()
        self.key_takeaways_gen = KeyTakeawaysAgent()
        self.presentation_gen = PresentationAgent()

    async def generate_full_lesson(
        self, 
        topic: str, 
        level: str, 
        duration: int, 
        include_quiz: bool = True,
        quiz_duration: int = 10,
        quiz_marks: int = 20
    ) -> Dict[str, Any]:
        """
        Orchestrate the full generation flow
        1. Plan Structure
        2. Generate Content (Parallel: sections + resources)
        3. Generate Key Takeaways
        4. Generate Quiz (if requested)
        5. Generate Presentations (PPT + PDF)
        """
        logger.info(f"Starting orchestration for: {topic}")
        
        # 1. Planning phase
        plan = await self.planner.run(topic, level, duration)
        
        # 2. Content generation (Parallel)
        # We use gather to run all sections and resource search simultaneously
        sections_task = self.content_gen.run_parallel(topic, level, plan['sections'])
        resources_task = self.content_gen.find_resources(topic, level)
        
        sections, resources = await asyncio.gather(sections_task, resources_task)
        
        # 3. Key Takeaways generation
        key_takeaways = await self.key_takeaways_gen.run(
            topic, level, plan['objectives'], sections
        )
        
        # 4. Optional Quiz generation
        if include_quiz:
            quiz = await self.quiz_gen.run(topic, level, quiz_duration, quiz_marks)
        else:
            quiz = {"questions": []}
        
        # 5. Generate Presentations (PPT + PDF in parallel)
        presentation_files = await self.presentation_gen.run(
            topic, level, duration, sections, key_takeaways
        )
        
        # 6. Compile final state
        lesson_data = {
            "title": plan["title"],
            "level": level,
            "duration_minutes": duration,
            "learning_objectives": plan["objectives"],
            "sections": sections,
            "resources": resources,
            "key_takeaways": key_takeaways,
            "quiz": quiz,
            "ppt_path": presentation_files.get("ppt_path"),
            "pdf_path": presentation_files.get("pdf_path"),
            "status": "completed"
        }
        
        logger.info(f"Successfully orchestrated lesson: {topic}")
        return lesson_data
