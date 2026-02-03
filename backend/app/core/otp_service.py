"""
OTP Service
Secure OTP generation, hashing, and validation
"""
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.email_otp import EmailOTP


class OTPService:
    """Secure OTP generation and validation service"""
    
    # Rate limiting storage (in-memory for now, use Redis in production)
    _rate_limit_store: Dict[str, list] = {}
    
    @staticmethod
    def generate_otp() -> str:
        """
        Generate a cryptographically secure 6-digit OTP
        Uses secrets module for secure random generation
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    @staticmethod
    def hash_otp(otp: str) -> str:
        """
        Hash OTP using bcrypt
        Cost factor 12 for security (2^12 iterations)
        """
        return bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    
    @staticmethod
    def verify_otp_hash(otp: str, otp_hash: str) -> bool:
        """
        Verify OTP against bcrypt hash
        Uses constant-time comparison to prevent timing attacks
        """
        try:
            return bcrypt.checkpw(otp.encode('utf-8'), otp_hash.encode('utf-8'))
        except Exception:
            return False
    
    @classmethod
    def check_rate_limit(cls, email: str, limit: int = 3, window_hours: int = 1) -> tuple[bool, int]:
        """
        Check if email has exceeded rate limit
        
        Args:
            email: Email address to check
            limit: Maximum requests allowed (default 3)
            window_hours: Time window in hours (default 1)
        
        Returns:
            Tuple of (allowed: bool, seconds_until_reset: int)
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=window_hours)
        
        # Get or create request history for this email
        if email not in cls._rate_limit_store:
            cls._rate_limit_store[email] = []
        
        # Remove old requests outside the window
        cls._rate_limit_store[email] = [
            req_time for req_time in cls._rate_limit_store[email]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(cls._rate_limit_store[email]) >= limit:
            # Calculate seconds until oldest request expires
            oldest = min(cls._rate_limit_store[email])
            seconds_until_reset = int((oldest + timedelta(hours=window_hours) - now).total_seconds())
            return False, max(seconds_until_reset, 0)
        
        # Add current request
        cls._rate_limit_store[email].append(now)
        return True, 0
    
    @staticmethod
    async def create_otp(
        db: AsyncSession,
        email: str,
        otp_code: str,
        ip_address: Optional[str] = None,
        expiry_minutes: int = 10
    ) -> EmailOTP:
        """
        Create and store a new OTP in database
        
        Args:
            db: Database session
            email: Email address
            otp_code: Plain OTP code (will be hashed)
            ip_address: Request IP address for audit
            expiry_minutes: OTP validity period (default 10)
        
        Returns:
            Created EmailOTP instance
        """
        # Hash the OTP
        otp_hash = OTPService.hash_otp(otp_code)
        
        # Create OTP record
        otp_record = EmailOTP.create_with_expiry(
            email=email,
            otp_hash=otp_hash,
            ip_address=ip_address,
            expiry_minutes=expiry_minutes
        )
        
        db.add(otp_record)
        await db.commit()
        await db.refresh(otp_record)
        
        return otp_record
    
    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        email: str,
        otp_code: str,
        ip_address: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Verify OTP code for an email
        
        Args:
            db: Database session
            email: Email address
            otp_code: Plain OTP code to verify
            ip_address: Request IP address
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Find the most recent unverified OTP for this email
        result = await db.execute(
            select(EmailOTP)
            .where(EmailOTP.email == email, EmailOTP.verified == False)
            .order_by(EmailOTP.created_at.desc())
        )
        otp_record = result.scalar_one_or_none()
        
        if not otp_record:
            return False, "No verification code found. Please request a new one."
        
        # Check if expired
        if otp_record.is_expired:
            return False, "Verification code expired. Please request a new one."
        
        # Check if too many attempts
        if not otp_record.can_attempt:
            return False, "Too many failed attempts. Please request a new code."
        
        # Verify the OTP
        if OTPService.verify_otp_hash(otp_code, otp_record.otp_hash):
            # Mark as verified
            otp_record.verified = True
            await db.commit()
            return True, None
        else:
            # Increment attempt counter
            otp_record.attempts += 1
            await db.commit()
            
            attempts_remaining = 5 - otp_record.attempts
            if attempts_remaining > 0:
                return False, f"Invalid verification code. {attempts_remaining} attempts remaining."
            else:
                return False, "Too many failed attempts. Please request a new code."
    
    @staticmethod
    async def invalidate_existing_otps(db: AsyncSession, email: str) -> int:
        """
        Mark all existing OTPs for an email as verified (invalidate them)
        Used when resending OTP to prevent confusion
        
        Returns:
            Number of OTPs invalidated
        """
        result = await db.execute(
            select(EmailOTP)
            .where(EmailOTP.email == email, EmailOTP.verified == False)
        )
        otps = result.scalars().all()
        
        for otp in otps:
            otp.verified = True
        
        await db.commit()
        return len(otps)
    
    @staticmethod
    async def cleanup_expired_otps(db: AsyncSession, older_than_hours: int = 24) -> int:
        """
        Delete OTPs older than specified hours
        Should be run as a background task
        
        Returns:
            Number of OTPs deleted
        """
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        result = await db.execute(
            delete(EmailOTP).where(EmailOTP.created_at < cutoff)
        )
        
        await db.commit()
        return result.rowcount
