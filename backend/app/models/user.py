"""
User Model
Database schema for users and authentication
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """User table for authentication and profiles"""
    __tablename__ = "users"
    
    # Primary Key - Universal GUID type (works with SQLite and PostgreSQL)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # Legacy field
    
    # Email Verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)
    job_title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Subscription
    subscription_tier = Column(
        SQLEnum(SubscriptionTier, native_enum=False),
        default=SubscriptionTier.FREE,
        nullable=False
    )
    stripe_customer_id = Column(String(255), nullable=True, unique=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'email', etc.
    oauth_id = Column(String(255), nullable=True)  # Provider's user ID
    profile_completed = Column(Boolean, default=True, nullable=False)
    
    # Feedback Enforcement
    feedback_provided = Column(Boolean, default=False, nullable=True)
    
    # Authorization
    role = Column(SQLEnum(UserRole, native_enum=False), default=UserRole.USER, nullable=False)
    
    # API Key (for enterprise tier)
    api_key_hash = Column(String(64), nullable=True, unique=True, index=True)
    
    # Usage tracking
    lessons_this_month = Column(Integer, default=0, nullable=False)
    last_reset_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def lessons_quota(self) -> int:
        """Get monthly lesson quota based on subscription tier"""
        quotas = {
            SubscriptionTier.FREE: 100,
            SubscriptionTier.BASIC: 50,
            SubscriptionTier.PRO: 999999,  # Unlimited
            SubscriptionTier.ENTERPRISE: 999999
        }
        return quotas.get(self.subscription_tier, 5)
    
    @property
    def has_quota_remaining(self) -> bool:
        """Check if user has remaining lesson quota"""
        return self.lessons_this_month < self.lessons_quota
