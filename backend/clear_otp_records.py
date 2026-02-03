"""
Clear OTP Records
Remove all OTP records to reset rate limits for testing
"""
import asyncio
from sqlalchemy import delete
from app.database import AsyncSessionLocal
from app.models.email_otp import EmailOTP


async def clear_otps():
    """Clear all OTP records"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(delete(EmailOTP))
        count = result.rowcount
        await db.commit()
        
        print(f"\n✅ Cleared {count} OTP record(s)")
        print("Rate limits have been reset. You can now send OTPs again!\n")
        return count


if __name__ == "__main__":
    print("\n🧹 Clearing OTP records and resetting rate limits...")
    asyncio.run(clear_otps())
