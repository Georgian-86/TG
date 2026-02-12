import asyncio
from app.database import engine
from sqlalchemy import text

async def reset_feedback_status():
    email = "optimus4586prime@gmail.com"
    print(f"Resetting feedback status for {email}...")
    
    async with engine.begin() as conn:
        # Check current status
        result = await conn.execute(text("SELECT id, feedback_provided FROM users WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        if not user:
            print("User not found.")
            return

        print(f"Current Status - ID: {user.id}, Feedback Provided: {user.feedback_provided}")

        # Reset status
        await conn.execute(text("UPDATE users SET feedback_provided = 0, updated_at = CURRENT_TIMESTAMP WHERE email = :email"), {"email": email})
        print("Update executed.")

        # Verify change
        result = await conn.execute(text("SELECT feedback_provided FROM users WHERE email = :email"), {"email": email})
        updated_user = result.fetchone()
        print(f"New Status - Feedback Provided: {updated_user.feedback_provided}")

if __name__ == "__main__":
    asyncio.run(reset_feedback_status())
