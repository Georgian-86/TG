"""
Pydantic Schemas for Lessons
Request/Response validation models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ===== Lesson Request/Response Schemas =====

class LessonCreate(BaseModel):
    """Schema for creating a new lesson"""
    topic: str = Field(..., min_length=3, max_length=500)
    level: str = Field(..., pattern="^(School|Undergraduate|Postgraduate|Professional)$")
    duration: int = Field(..., ge=20, le=120)  # 20-120 minutes
    include_quiz: bool = False
    quiz_duration: Optional[int] = Field(None, ge=5, le=20)
    quiz_marks: Optional[int] = Field(None, ge=10, le=50)
    
    @validator('topic')
    def sanitize_topic(cls, v):
        """Sanitize topic input"""
        # Remove excessive whitespace
        v = ' '.join(v.split())
        return v


class LessonResponse(BaseModel):
    """Schema for lesson response"""
    id: str  # String-based UUID for consistency
    topic: str
    level: str
    duration: int
    include_quiz: bool
    status: str
    error_message: Optional[str] = None
    lesson_plan: Optional[List[Dict[str, Any]]] = None  # List of sections
    resources: Optional[List[Dict[str, Any]]] = None
    key_takeaways: Optional[List[str]] = None
    quiz: Optional[Dict[str, Any]] = None
    ppt_url: Optional[str] = None
    pdf_url: Optional[str] = None
    processing_time_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LessonListResponse(BaseModel):
    """Schema for lesson list with pagination"""
    lessons: List[LessonResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LessonStatusResponse(BaseModel):
    """Schema for lesson status (lightweight)"""
    id: str
    status: str
    progress: Optional[int] = None  # 0-100%
    current_stage: Optional[str] = None  # planner, content, quiz, etc.
    
    class Config:
        from_attributes = True
