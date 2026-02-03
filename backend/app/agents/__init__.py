"""
Agents Package
Multi-agent system for lesson generation

Exports all agents for easy import
"""
from app.agents.base import BaseAgent
from app.agents.planner import PlannerAgent
from app.agents.content import ContentAgent
from app.agents.quiz import QuizAgent
from app.agents.key_takeaways import KeyTakeawaysAgent
from app.agents.presentation import PresentationAgent
from app.agents.orchestrator import AgentOrchestrator

__all__ = [
    "BaseAgent",
    "PlannerAgent",
    "ContentAgent",
    "QuizAgent",
    "KeyTakeawaysAgent",
    "PresentationAgent",
    "AgentOrchestrator"
]
