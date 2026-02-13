"""
Lesson Model
Database schema for lessons and generated content
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class LessonStatus(str, enum.Enum):
    """Lesson generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LessonLevel(str, enum.Enum):
    """Educational level"""
    SCHOOL = "School"
    UNDERGRADUATE = "Undergraduate"
    POSTGRADUATE = "Postgraduate"
    PROFESSIONAL = "Research"


class Lesson(Base):
    """Lesson table for storing generated lesson plans"""
    __tablename__ = "lessons"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Lesson Details
    topic = Column(String(500), nullable=False)
    level = Column(SQLEnum(LessonLevel, native_enum=False), nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    include_quiz = Column(Boolean, default=False, nullable=False)
    
    # Advanced Options
    include_rbt = Column(Boolean, default=True, nullable=False)
    lo_po_mapping = Column(Boolean, default=False, nullable=False)
    iks_integration = Column(Boolean, default=False, nullable=False)
    
    # Processing Status
    status = Column(SQLEnum(LessonStatus, native_enum=False), default=LessonStatus.PENDING, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    
    # Generated Content (stored as JSON for SQLite/PostgreSQL compatibility)
    lesson_plan = Column(JSON, nullable=True)
    resources = Column(JSON, nullable=True)
    learning_objectives = Column(JSON, nullable=True)
    key_takeaways = Column(JSON, nullable=True)
    quiz = Column(JSON, nullable=True)
    
    # File URLs (PPT and PDF in cloud storage)
    ppt_url = Column(String(1024), nullable=True)
    pdf_url = Column(String(1024), nullable=True)
    
    # Metadata
    processing_time_seconds = Column(Integer, nullable=True)  # Track generation time
    openai_tokens_used = Column(Integer, nullable=True)  # Track API usage
    openai_cost = Column(Integer, nullable=True)  # Cost in cents
    
    # Organization
    is_favorite = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Lesson {self.topic} - {self.status}>"
