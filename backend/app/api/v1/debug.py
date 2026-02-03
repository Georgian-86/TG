"""
Debug endpoints for development
"""
from fastapi import APIRouter
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()
orchestrator = AgentOrchestrator()

@router.get("/test-orchestrator")
async def test_orchestrator():
    """Simple test to see if orchestrator works in HTTP context"""
    try:
        result = await orchestrator.generate_full_lesson(
            topic="Test Topic",
            level="School",
            duration=30,
            include_quiz=False
        )
        return {"status": "success", "data":result}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.post("/clear-rate-limits")
async def clear_rate_limits():
    """
    Clear in-memory rate limits (for testing purposes only)
    """
    try:
        from app.core.otp_service import OTPService
        
        # Clear the rate limit store
        OTPService._rate_limit_store.clear()
        
        return {
            "status": "success",
            "message": "Rate limits cleared",
            "cleared_entries": "all"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
