"""
Simple OTP Test
Quick verification of OTP functionality
"""
import asyncio
from app.core.otp_service import OTPService

print("\n" + "="*70)
print("🧪 TESTING OTP VERIFICATION SYSTEM - QUICK TEST")
print("="*70)

# Test 1: OTP Generation
print("\n✓ TEST 1: OTP Generation")
otps = [OTPService.generate_otp() for _ in range(5)]
for i, otp in enumerate(otps, 1):
    print(f"  OTP {i}: {otp}")
    assert len(otp) == 6 and otp.isdigit(), "Invalid OTP format"
print("  ✓ All OTPs are 6-digit numbers")

# Test 2: OTP Hashing
print("\n✓ TEST 2: OTP Hashing & Verification")
test_otp = "123456"
hashed = OTPService.hash_otp(test_otp)
print(f"  Original: {test_otp}")
print(f"  Hashed: {hashed[:50]}...")
assert OTPService.verify_otp_hash(test_otp, hashed), "Hash verification failed"
assert not OTPService.verify_otp_hash("654321", hashed), "Should reject wrong OTP"
print("  ✓ Hashing and verification working correctly")

# Test 3: Rate Limiting
print("\n✓ TEST 3: Rate Limiting")
test_email = "ratetest@example.com"
for i in range(3):
    allowed, wait = OTPService.check_rate_limit(test_email)
    print(f"  Request {i+1}: Allowed={allowed}")
    assert allowed, f"Request {i+1} should be allowed"

allowed, wait = OTPService.check_rate_limit(test_email)
print(f"  Request 4: Allowed={allowed}, Wait Time={wait}s")
assert not allowed, "4th request should be blocked"
print("  ✓ Rate limiting working (3 requests/hour)")

# Summary
print("\n" + "="*70)
print("🎉 ALL QUICK TESTS PASSED!")
print("="*70)
print("\n📝 OTP System Status:")
print("  ✓ OTP generation working")
print("  ✓ OTP hashing/verification working  ")
print("  ✓ Rate limiting enforced")
print("\n💡 To test with real email, register a user and use the API endpoints:")
print("  POST /api/v1/auth/send-verification-email")
print("  POST /api/v1/auth/verify-email")
print("="*70)
