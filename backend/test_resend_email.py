"""
Test Resend Email Sending
Direct test of Resend API to verify email delivery
"""
import asyncio
import httpx
from app.config import settings

async def test_resend_email():
    """Test sending email through Resend"""
    
    print("\n" + "="*60)
    print("RESEND EMAIL TEST")
    print("="*60)
    
    print(f"\nAPI Key: {settings.EMAIL_API_KEY[:10]}...")
    print(f"From Email: {settings.EMAIL_FROM}")
    
    # Test email
    test_email = input("\nEnter your email address to test: ").strip()
    test_otp = "123456"
    
    print(f"\nSending test email to: {test_email}")
    print(f"Test OTP: {test_otp}")
    
    # Prepare email
    email_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #f97316;">TeachGenie Email Verification</h1>
        <p>Your verification code is:</p>
        <h2 style="font-size: 42px; letter-spacing: 8px; color: #000; font-family: monospace;">
            {test_otp}
        </h2>
        <p>This code expires in 10 minutes.</p>
    </div>
    """
    
    email_text = f"""
    TeachGenie Email Verification
    
    Your verification code is: {test_otp}
    
    This code expires in 10 minutes.
    """
    
    payload = {
        "from": settings.EMAIL_FROM,
        "to": [test_email],
        "subject": "[TEST] TeachGenie Email Verification",
        "html": email_html,
        "text": email_text
    }
    
    headers = {
        "Authorization": f"Bearer {settings.EMAIL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\nSending request to Resend API...")
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers=headers
            )
            
            print(f"\nResponse Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("\n✅ Email sent successfully!")
                print(f"Check {test_email} for the test email")
            else:
                print(f"\n❌ Failed to send email")
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_resend_email())
