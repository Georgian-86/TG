"""
Agent Orchestrator
Coordinates the sequence of agents to generate a complete lesson
Enhanced with presentation and key takeaways agents
"""
from typing import Dict, Any, List
import logging
import asyncio
from app.agents.planner import planner_agent
from app.agents.content import content_agent
from app.agents.quiz import quiz_agent
from app.agents.key_takeaways import key_takeaways_agent
from app.agents.resources import resources_agent
from app.agents.presentation import PresentationAgent
from app.agents.utils import dominant_rbt, extract_rbt_levels

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Manages the end-to-end generation workflow using functional agents"""
    
    def __init__(self):
        # Presentation agent is still class-based for now
        self.presentation_gen = PresentationAgent()

    async def generate_full_lesson(
        self, 
        topic: str, 
        level: str, 
        duration: int, 
        include_quiz: bool = True,
        quiz_duration: int = 10,
        quiz_marks: int = 20,
        country: str = "Global",
        include_rbt: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate the full generation flow using the state-based pipeline:
        1. Content Agent (One-Shot: Plan + Content)
        2. Key Takeaways Agent (Specialized extraction)
        3. Resources Agent (Specialized curation)
        4. Quiz Agent (Fail-safe generation)
        5. Presentation Agent (File generation)
        """
        logger.info(f"Starting orchestration for: {topic} (Country: {country}, RBT: {include_rbt})")
        
        # Initialize Shared State
        state = {
            "topic": topic,
            "level": level,
            "duration": duration,
            "include_quiz": include_quiz,
            "quiz_duration": quiz_duration,
            "quiz_marks": quiz_marks,
            "country": country,  # Pass country for localization
            "include_rbt": include_rbt
        }
        
        # 1. Planning Phase (Dynamic Structure)
        # Generates the optimal flow for the topic/level/duration
        logger.info("Running Planner Agent...")
        state = await planner_agent(state)
        
        # 2. Content Phase (Execution)
        # Generates deep content for each section in the plan
        logger.info("Running Content Agent...")
        state = await content_agent(state)
        
        # --- RBT ANALYSIS ---
        # Enrich objectives with Bloom's Taxonomy levels if requested
        raw_objectives = state.get("lesson_plan", {}).get("objectives", [])
        enriched_objectives = []
        
        if include_rbt:
            for obj in raw_objectives:
                if isinstance(obj, str):
                    rbt_level = dominant_rbt(obj)
                    levels = extract_rbt_levels(obj)
                    
                    # Create formatted text with [RBT Level] prefix
                    # Extract the first verb from the objective and replace with bracketed version
                    obj_clean = obj.strip()
                    formatted_text = f"[{rbt_level}] {obj_clean}"
                    
                    enriched_objectives.append({
                        "text": formatted_text,  # Now includes [RBT Level] prefix
                        "rbt": rbt_level,
                        "composite": len(levels) > 1
                    })
                else:
                    enriched_objectives.append(obj)
        else:
            # Pass through without RBT enrichment
             for obj in raw_objectives:
                if isinstance(obj, str):
                    enriched_objectives.append({
                        "text": obj,
                        "rbt": None,
                        "composite": False
                    })
                else:
                    enriched_objectives.append(obj)
        
        # Update state with enriched objectives
        state["lesson_plan"]["objectives"] = enriched_objectives
        state["learning_objectives"] = enriched_objectives
        
        # 2. Key Takeaways Generation
        # Extracts strictly formatted takeaways from the generated content
        logger.info("Running Key Takeaways Agent...")
        state = await key_takeaways_agent(state)
        
        # 3. Resources Generation
        # Curates specialized, categorized resources with safe links
        logger.info("Running Resources Agent...")
        state = await resources_agent(state)
        
        # 4. Optional Quiz Generation
        if include_quiz:
            logger.info("Running Quiz Agent...")
            state = await quiz_agent(state)
        else:
            state["quiz"] = {"questions": []}
        
        # 5. Presentation Generation (PPT + PDF)
        # Uses the data accumulated in state
        lesson_plan = state.get("lesson_plan", {})
        sections = lesson_plan.get("sections", [])
        takeaways = state.get("key_takeaways", [])
        
        logger.info("Running Presentation Agent...")
        presentation_files = await self.presentation_gen.run(
            topic, level, duration, sections, takeaways, state.get("quiz")
        )
        
        # 6. Compile final response
        # Merge specialized resources with plan resources if needed, 
        # or prefer specialized resources for the final output.
        
        # Flatten categorized resources into a single list for frontend compatibility
        final_resources = []
        raw_resources = state.get("resources", {})
        
        if isinstance(raw_resources, dict):
            for category, items in raw_resources.items():
                if isinstance(items, list):
                    for item in items:
                        # Add category field to preserve structure info
                        if isinstance(item, dict):
                            item["category"] = category
                            final_resources.append(item)
        elif isinstance(raw_resources, list):
            final_resources = raw_resources
            
        # If specialized resources failed (empty), fallback to Content Agent resources
        if not final_resources:
            content_resources = lesson_plan.get("resources", [])
            if isinstance(content_resources, list):
                 final_resources = content_resources
        
        # Ensure quiz is definitely populated if requested
        final_quiz = state.get("quiz", {})
        if include_quiz and not final_quiz.get("questions"):
             # Fallback quiz if agent failed but quiz was requested
             final_quiz = {
                "questions": [
                    {
                        "scenario": f"Reviewing the concepts of {topic}.",
                        "question": "Which of the following best describes the core concept?",
                        "options": {"A": "Concept A", "B": "Concept B", "C": "Concept C", "D": "Concept D"},
                        "correct_option": "A",
                        "explanation": "Fundamental understanding check.",
                        "rbt_level": "Remember"
                    }
                ]
             }

        lesson_data = {
            "title": lesson_plan.get("title", topic),
            "level": level,
            "duration_minutes": duration,
            "learning_objectives": state.get("learning_objectives", []),
            "sections": sections,
            "resources": final_resources, # specialized resources (flattened) or fallback
            "key_takeaways": takeaways,
            "quiz": final_quiz,
            "ppt_path": presentation_files.get("ppt_path"),
            "pdf_path": presentation_files.get("pdf_path"),
            "status": "completed"
        }
        
        logger.info(f"Successfully orchestrated lesson: {topic}. Resources: {len(final_resources)}, Quiz: {len(final_quiz.get('questions', []))}")
        return lesson_data
