"""
Pydantic Schemas for Profile and Lesson History
Request/Response validation models
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Any
from datetime import datetime


# ===== Profile Schemas =====

class ProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    job_title: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)


class ProfileResponse(BaseModel):
    """Schema for user profile response"""
    id: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    organization: Optional[str]
    country: Optional[str]
    phone_number: Optional[str]
    profile_picture_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== Lesson History Schemas =====

class LessonHistoryCreate(BaseModel):
    """Schema for creating lesson history"""
    topic: str = Field(..., min_length=1, max_length=255)
    level: str
    duration: int = Field(..., gt=0, le=300)
    lesson_data: Optional[str] = None  # JSON string
    title: Optional[str] = Field(None, max_length=255)
    tags: Optional[str] = None  # Comma-separated


class LessonHistoryResponse(BaseModel):
    """Schema for lesson history response"""
    id: str
    user_id: str
    topic: str
    level: str
    duration: int
    title: Optional[str]
    is_favorite: bool
    tags: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LessonHistoryDetail(LessonHistoryResponse):
    """Schema for detailed lesson history with full content"""
    lesson_data: Optional[str]  # JSON string
    updated_at: Optional[datetime]


class LessonHistoryList(BaseModel):
    """Schema for paginated lesson history list"""
    items: List[LessonHistoryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ===== File Upload Schemas =====

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    id: str
    file_url: str
    file_name: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
