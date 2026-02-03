"""
Email OTP Model
Secure storage for email verification OTP codes
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid
from datetime import datetime, timedelta


class EmailOTP(Base):
    """Email OTP verification table with security features"""
    __tablename__ = "email_otps"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Email and OTP
    email = Column(String(255), nullable=False, index=True)  # Indexed for fast lookup
    otp_hash = Column(String(255), nullable=False)  # Bcrypt hashed OTP (never plaintext)
    
    # Security tracking
    attempts = Column(Integer, default=0, nullable=False)  # Failed verification attempts
    verified = Column(Boolean, default=False, nullable=False)  # Marks used OTPs
    ip_address = Column(String(45), nullable=True)  # IPv6 support (max 45 chars)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)  # Indexed for cleanup
    
    def __repr__(self):
        return f"<EmailOTP {self.email} - {'verified' if self.verified else 'pending'}>"
    
    @property
    def is_expired(self) -> bool:
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)
    
    @property
    def can_attempt(self) -> bool:
        """Check if more verification attempts are allowed"""
        return self.attempts < 5 and not self.verified and not self.is_expired
    
    @classmethod
    def create_with_expiry(cls, email: str, otp_hash: str, ip_address: str = None, expiry_minutes: int = 10):
        """Factory method to create OTP with automatic expiration"""
        return cls(
            email=email,
            otp_hash=otp_hash,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
