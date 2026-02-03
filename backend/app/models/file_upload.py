"""
File Upload Model
Stores metadata for uploaded files (avatars, documents, etc.)
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid


class FileUpload(Base):
    """File upload metadata table"""
    __tablename__ = "file_uploads"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Foreign Key to User
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # File Metadata
    file_type = Column(String(50), nullable=False)  # 'avatar', 'document', etc.
    file_url = Column(String(500), nullable=False)  # Full URL to file
    file_name = Column(String(255), nullable=True)  # Original filename
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)  # e.g., 'image/jpeg'
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<FileUpload {self.file_name} ({self.file_type})>"
