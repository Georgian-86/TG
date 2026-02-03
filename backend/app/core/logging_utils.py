"""
Logging utilities for admin monitoring
Structured logging with database persistence
"""
import logging
from typing import Optional, Dict, Any
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def log_admin_event(
    level: str,
    category: str,
    event_name: str,
    message: str,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    endpoint: Optional[str] = None,
    http_method: Optional[str] = None,
    status_code: Optional[int] = None,
    event_metadata: Optional[Dict[str, Any]] = None,
    exception_type: Optional[str] = None,
    traceback: Optional[str] = None
):
    """Log an admin event to the database"""
    try:
        from app.models.admin_log import AdminLog
        
        async with AsyncSessionLocal() as db:
            log_entry = AdminLog(
                level=level,
                category=category,
                event_name=event_name,
                message=message,
                user_id=user_id,
                user_email=user_email,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                http_method=http_method,
                status_code=status_code,
                event_metadata=event_metadata,
                exception_type=exception_type,
                traceback=traceback
            )
            db.add(log_entry)
            await db.commit()
            
    except Exception as e:
        logger.error(f"Failed to log admin event: {e}")
