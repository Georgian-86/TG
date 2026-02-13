"""
Email Service
Resend API integration for sending OTP verification emails
"""
import httpx
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email sending service using Resend API"""
    
    RESEND_API_URL = "https://api.resend.com/emails"
    
    @staticmethod
    def get_otp_email_template(otp: str, user_name: Optional[str] = None) -> tuple[str, str]:
        """
        Generate HTML and plain text email templates for OTP
        
        Args:
            otp: 6-digit OTP code
            user_name: Optional user name for personalization
        
        Returns:
            Tuple of (html_content, text_content)
        """
        greeting = f"Hi {user_name}," if user_name else "Hi there,"
        
        # Simplified HTML to avoid spam filters - removed gradients, shadows, complex styling
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; padding: 30px; border: 1px solid #e5e7eb; border-radius: 8px;">
        <h1 style="color: #4F46E5; margin: 0 0 10px 0;">TeachGenie</h1>
        <h2 style="color: #111827; font-size: 20px; margin: 0 0 20px 0;">Email Verification</h2>
        
        <p style="color: #6B7280; margin: 0 0 30px 0;">{greeting}</p>
        <p style="color: #374151; margin: 0 0 30px 0;">Your verification code is:</p>
        
        <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #4F46E5; background: #F3F4F6; padding: 20px; border-radius: 8px; margin: 0 0 30px 0; font-family: monospace;">
            {otp}
        </div>
        
        <p style="color: #6B7280; font-size: 14px; margin: 0 0 10px 0;">
            <strong>This code expires in 10 minutes.</strong>
        </p>
        <p style="color: #9CA3AF; font-size: 12px; margin: 0;">
            If you didn't request this code, please ignore this email.
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 20px;">
        <p style="color: #9CA3AF; font-size: 12px;">
            TeachGenie &copy; 2026 | <a href="mailto:support@teachgenie.ai" style="color: #4F46E5;">Contact Support</a>
        </p>
    </div>
</body>
</html>
"""
        
        # Plain text version with clear formatting
        text_content = f"""
TeachGenie - Email Verification

{greeting}

Your verification code is:

{otp}

This code expires in 10 minutes.

Enter this code to complete your registration at teachgenie.ai

---
If you didn't request this code, please ignore this email.
Need help? Contact support@teachgenie.ai

TeachGenie © 2026
"""
        
        return html_content, text_content
    
    @staticmethod
    async def send_verification_email(
        email: str,
        otp: str,
        user_name: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send OTP verification email via Resend API
        
        Args:
            email: Recipient email address
            otp: 6-digit OTP code
            user_name: Optional user name for personalization
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        html_content, text_content = EmailService.get_otp_email_template(otp, user_name)
        # Simplified payload with spam-proof subject and reply-to
        # FIX: Removed duplicate "text" key and changed FROM format for Resend compatibility
        payload = {
            "from": settings.EMAIL_FROM,  # Use plain email only (Resend requirement)
            "to": [email],
            "subject": f"Your TeachGenie verification code: {otp}",  # Put code in subject for visibility
            "reply_to": ["support@teachgenie.ai"],
            "html": html_content,
            "text": text_content,
            "tags": [
                {"name": "category", "value": "email_verification"}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {settings.EMAIL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Retry logic for network failures
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        EmailService.RESEND_API_URL,
                        json=payload,
                        headers=headers,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Verification email sent successfully to {email}")
                        return True, None
                    else:
                        error_msg = f"Resend API error: {response.status_code} - {response.text}"
                        logger.error(error_msg)
                        
                        # Don't retry on client errors (4xx)
                        if 400 <= response.status_code < 500:
                            return False, "Failed to send email. Please try again later."
                        
                        # Retry on server errors (5xx)
                        if attempt < max_retries - 1:
                            continue
                        
                        return False, "Failed to send email. Please try again later."
                        
            except Exception as e:
                logger.error(f"Error sending email to {email}: {str(e)}")
                
                if attempt < max_retries - 1:
                    continue
                
                return False, "Network error. Please check your connection and try again."
        
        return False, "Failed to send email after multiple attempts."
