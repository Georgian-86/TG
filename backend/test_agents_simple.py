"""
Simple debug test for agent system
"""
import asyncio
from app.agents.orchestrator import AgentOrchestrator

async def test_agents():
    print("Testing Agent System...")
    
    try:
        orchestrator = AgentOrchestrator()
        print("✅ Orchestrator initialized")
        
        print("\n🚀 Starting generation...")
        result = await orchestrator.generate_full_lesson(
            topic="Photosynthesis",
            level="School",
            duration=30,
            include_quiz=True
        )
        
        print("\n✅ Generation complete!")
        print(f"Title: {result.get('title')}")
        print(f"Sections: {len(result.get('sections', []))}")
        print(f"Quiz Questions: {len(result.get('quiz', {}).get('questions', []))}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agents())
