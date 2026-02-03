"""
Lesson History Model
Stores user's generated lessons for history/sidebar display
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base
import uuid


class LessonHistory(Base):
    """Lesson generation history table"""
    __tablename__ = "lesson_history"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Lesson Parameters
    topic = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False)  # School, Undergraduate, etc.
    duration = Column(Integer, nullable=False)  # in minutes
    
    # Lesson Content
    lesson_data = Column(Text, nullable=True)  # JSON string for SQLite compatibility
    title = Column(String(255), nullable=True)  # Auto-generated from topic
    
    # Organization
    is_favorite = Column(Boolean, default=False, nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated tags for SQLite
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LessonHistory {self.title or self.topic}>"
