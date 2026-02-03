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
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: white;
            margin-bottom: 20px;
        }}
        .logo-accent {{
            color: #f97316;
        }}
        .content {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-top: 20px;
        }}
        .otp-code {{
            font-size: 42px;
            font-weight: bold;
            letter-spacing: 12px;
            color: #667eea;
            background: #f0f4ff;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
            font-family: 'Courier New', monospace;
        }}
        .warning {{
            background: #fff7ed;
            border-left: 4px solid #f97316;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            text-align: left;
        }}
        .footer {{
            color: white;
            margin-top: 20px;
            font-size: 14px;
        }}
        .footer a {{
            color: white;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            Teach<span class="logo-accent">Genie</span>
        </div>
        
        <div class="content">
            <h2 style="color: #333; margin-top: 0;">Verify Your Email Address</h2>
            <p style="color: #666;">{greeting}</p>
            <p style="color: #666;">Thank you for signing up with TeachGenie! To complete your registration, please use the verification code below:</p>
            
            <div class="otp-code">{otp}</div>
            
            <div class="warning">
                <strong>⏱️ This code expires in 10 minutes</strong><br>
                <small>For your security, do not share this code with anyone.</small>
            </div>
            
            <p style="color: #999; font-size: 14px; margin-top: 30px;">
                If you didn't request this code, please ignore this email or contact our support team if you have concerns.
            </p>
        </div>
        
        <div class="footer">
            <p>Need help? <a href="mailto:support@teachgenie.ai">Contact Support</a></p>
            <p style="font-size: 12px; color: rgba(255,255,255,0.8);">
                &copy; 2024 TeachGenie. AI-Powered Teaching Assistant.
            </p>
        </div>
    </div>
</body>
</html>
"""
        
        text_content = f"""
TeachGenie - Email Verification

{greeting}

Thank you for signing up with TeachGenie! To complete your registration, please use the verification code below:

Verification Code: {otp}

This code expires in 10 minutes.

For your security, do not share this code with anyone.

If you didn't request this code, please ignore this email or contact our support team at support@teachgenie.ai.

---
TeachGenie - AI-Powered Teaching Assistant
© 2024 TeachGenie
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
        
        payload = {
            "from": f"TeachGenie <{settings.EMAIL_FROM}>",
            "to": [email],
            "subject": "Verify Your Email - TeachGenie",
            "html": html_content,
            "text": text_content
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
