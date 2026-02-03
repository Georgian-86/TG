"""
Test OTP Verification System
Manual test script to verify email OTP functionality
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add parent directory to path
sys.path.insert(0, '.')

from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.otp_service import OTPService
from app.core.email_service import EmailService


async def test_otp_generation():
    """Test OTP generation"""
    print("\n" + "="*60)
    print("TEST 1: OTP Generation")
    print("="*60)
    
    # Generate multiple OTPs to check randomness
    otps = [OTPService.generate_otp() for _ in range(5)]
    
    for i, otp in enumerate(otps, 1):
        print(f"OTP {i}: {otp}")
        assert len(otp) == 6, "OTP should be 6 digits"
        assert otp.isdigit(), "OTP should be numeric"
    
    print("✓ OTP generation working correctly")
    return True


async def test_otp_hashing():
    """Test OTP hashing and verification"""
    print("\n" + "="*60)
    print("TEST 2: OTP Hashing & Verification")
    print("="*60)
    
    otp = "123456"
    print(f"Original OTP: {otp}")
    
    # Hash the OTP
    otp_hash = OTPService.hash_otp(otp)
    print(f"Hashed OTP: {otp_hash[:50]}...")
    
    # Verify correct OTP
    is_valid = OTPService.verify_otp_hash(otp, otp_hash)
    print(f"Verify correct OTP: {is_valid}")
    assert is_valid, "Should verify correct OTP"
    
    # Verify incorrect OTP
    is_invalid = OTPService.verify_otp_hash("654321", otp_hash)
    print(f"Verify incorrect OTP: {is_invalid}")
    assert not is_invalid, "Should reject incorrect OTP"
    
    print("✓ OTP hashing and verification working correctly")
    return True


async def test_rate_limiting():
    """Test rate limiting"""
    print("\n" + "="*60)
    print("TEST 3: Rate Limiting")
    print("="*60)
    
    test_email = "ratelimit@test.com"
    
    # First 3 requests should be allowed
    for i in range(3):
        allowed, seconds = OTPService.check_rate_limit(test_email, limit=3, window_hours=1)
        print(f"Request {i+1}: Allowed={allowed}, Wait={seconds}s")
        assert allowed, f"Request {i+1} should be allowed"
    
    # 4th request should be blocked
    allowed, seconds = OTPService.check_rate_limit(test_email, limit=3, window_hours=1)
    print(f"Request 4: Allowed={allowed}, Wait={seconds}s")
    assert not allowed, "4th request should be blocked"
    assert seconds > 0, "Should return wait time"
    
    print("✓ Rate limiting working correctly")
    return True


async def test_database_operations():
    """Test database OTP operations"""
    print("\n" + "="*60)
    print("TEST 4: Database Operations")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        test_email = "dbtest@example.com"
        test_otp = "999888"
        
        # Create OTP
        print(f"Creating OTP for {test_email}...")
        otp_record = await OTPService.create_otp(
            db, 
            email=test_email,
            otp_code=test_otp,
            ip_address="127.0.0.1"
        )
        print(f"✓ OTP created: ID={otp_record.id}")
        
        # Verify OTP
        print(f"Verifying OTP {test_otp}...")
        success, error = await OTPService.verify_otp(db, test_email, test_otp)
        print(f"Verification result: Success={success}, Error={error}")
        assert success, "OTP verification should succeed"
        
        # Try to verify again (should fail - already verified)
        print("Attempting to verify again...")
        success2, error2 = await OTPService.verify_otp(db, test_email, test_otp)
        print(f"Second verification: Success={success2}, Error={error2}")
        assert not success2, "Should not verify already-used OTP"
        
        # Test wrong OTP
        await OTPService.create_otp(db, test_email, "111222", "127.0.0.1")
        print("Testing wrong OTP (should fail)...")
        success3, error3 = await OTPService.verify_otp(db, test_email, "000000")
        print(f"Wrong OTP result: Success={success3}, Error={error3}")
        assert not success3, "Wrong OTP should fail"
        
    print("✓ Database operations working correctly")
    return True


async def test_email_sending(recipient_email=None):
    """Test email sending (requires valid email)"""
    print("\n" + "="*60)
    print("TEST 5: Email Sending")
    print("="*60)
    
    if not recipient_email:
        print("⚠ Skipping email test - no recipient email provided")
        print("To test email sending, run: python test_otp_verification.py YOUR_EMAIL@example.com")
        return True
    
    otp = OTPService.generate_otp()
    print(f"Sending OTP {otp} to {recipient_email}...")
    
    success, error = await EmailService.send_verification_email(
        email=recipient_email,
        otp=otp,
        user_name="Test User"
    )
    
    if success:
        print(f"✓ Email sent successfully!")
        print(f"📧 Check {recipient_email} for the OTP: {otp}")
        return True
    else:
        print(f"✗ Email sending failed: {error}")
        return False


async def test_full_flow(test_email=None):
    """Test complete OTP flow with real user"""
    print("\n" + "="*60)
    print("TEST 6: Complete User Flow")
    print("="*60)
    
    if not test_email:
        print("⚠ Skipping full flow test - no test email provided")
        return True
    
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(select(User).where(User.email == test_email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"⚠ User {test_email} not found in database")
            print("Please register first at http://localhost:3000/signup")
            return True
        
        print(f"✓ Found user: {user.email}")
        print(f"  Current verification status: {user.email_verified}")
        
        # Generate and send OTP
        otp = OTPService.generate_otp()
        print(f"\n📧 Sending OTP {otp} to {test_email}...")
        
        # Store OTP
        await OTPService.create_otp(db, test_email, otp, "127.0.0.1")
        
        # Send email
        success, error = await EmailService.send_verification_email(
            email=test_email,
            otp=otp,
            user_name=user.full_name
        )
        
        if success:
            print(f"✓ Email sent successfully!")
            print(f"\n🔑 Your OTP is: {otp}")
            print(f"\nTo verify, run this curl command:")
            print(f"""
curl -X POST http://localhost:8000/api/v1/auth/verify-email \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "{test_email}", "otp": "{otp}"}}'
            """)
        else:
            print(f"✗ Email sending failed: {error}")
            return False
    
    return True


async def run_all_tests(test_email=None):
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 TESTING OTP VERIFICATION SYSTEM")
    print("="*70)
    
    results = []
    
    # Unit tests (always run)
    results.append(("OTP Generation", await test_otp_generation()))
    results.append(("OTP Hashing", await test_otp_hashing()))
    results.append(("Rate Limiting", await test_rate_limiting()))
    results.append(("Database Operations", await test_database_operations()))
    
    # Email test (optional)
    results.append(("Email Sending", await test_email_sending(test_email)))
    
    # Full flow test (optional)
    if test_email:
        results.append(("Full Flow", await test_full_flow(test_email)))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:12} {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print("="*70)
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! OTP system is working correctly.")
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed.")
    
    print("="*70)


if __name__ == "__main__":
    # Get test email from command line if provided
    test_email = sys.argv[1] if len(sys.argv) > 1 else None
    
    if test_email:
        print(f"\n📧 Testing with email: {test_email}")
    else:
        print("\n💡 TIP: Pass your email to test email sending:")
        print("   python test_otp_verification.py YOUR_EMAIL@example.com")
    
    asyncio.run(run_all_tests(test_email))
