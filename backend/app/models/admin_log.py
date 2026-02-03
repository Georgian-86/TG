"""
Admin Log Model
Comprehensive logging for master admin monitoring
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Integer, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class LogLevel(str, enum.Enum):
    """Log severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, enum.Enum):
    """Log categories for filtering"""
    AUTHENTICATION = "authentication"
    LESSON_GENERATION = "lesson_generation"
    API_REQUEST = "api_request"
    PAYMENT = "payment"
    SECURITY = "security"
    SYSTEM = "system"
    USER_ACTION = "user_action"


class AdminLog(Base):
    """Admin logging table for comprehensive system monitoring"""
    __tablename__ = "admin_logs"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Log Classification
    level = Column(SQLEnum(LogLevel, native_enum=False), nullable=False, index=True)
    category = Column(SQLEnum(LogCategory, native_enum=False), nullable=False, index=True)
    
    # Event Details
    event_name = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # User Context (nullable for system events)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)  # Denormalized for quick access
    
    # Request Context
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 max length
    user_agent = Column(String(512), nullable=True)
    endpoint = Column(String(255), nullable=True, index=True)
    http_method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Additional Data (flexible JSON for any extra context)
    event_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' (reserved name)
    
    # Error Tracking
    exception_type = Column(String(255), nullable=True)
    traceback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AdminLog {self.level} - {self.event_name}>"
