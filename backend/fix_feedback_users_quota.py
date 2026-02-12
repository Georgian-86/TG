"""
Fix quota for users who already submitted feedback but didn't get counter reset
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_feedback_users():
    # Use production PostgreSQL database
    database_url = "postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
    engine = create_async_engine(database_url)
    
    try:
        async with engine.connect() as conn:
            # Find users who provided feedback but still have high lesson counter
            result = await conn.execute(text("""
                SELECT id, email, lessons_this_month, feedback_provided
                FROM users
                WHERE feedback_provided = TRUE
            """))
            
            users = result.fetchall()
            print("=" * 80)
            print("USERS WHO PROVIDED FEEDBACK:")
            print("=" * 80)
            
            for user in users:
                print(f"\n{user[1]:30} | Used: {user[2]:3} lessons | Feedback: {user[3]}")
            
            if users:
                print("\n" + "=" * 80)
                print("RESETTING QUOTA FOR FEEDBACK USERS...")
                print("=" * 80)
                
                # Reset lessons_this_month to 0 for all feedback users
                result = await conn.execute(text("""
                    UPDATE users 
                    SET lessons_this_month = 0 
                    WHERE feedback_provided = TRUE
                    AND lessons_this_month > 0
                    RETURNING email, lessons_this_month
                """))
                
                updated = result.fetchall()
                await conn.commit()
                
                print(f"\n✅ Reset quota for {len(updated)} users:")
                for user in updated:
                    print(f"   - {user[0]:30} → Now at {user[1]}/10 lessons")
                
                print("\n" + "=" * 80)
                print("✅ QUOTA RESET COMPLETE!")
                print("All feedback users now have fresh 10 lesson quota")
                print("=" * 80)
            else:
                print("\n⚠️  No users with feedback found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_feedback_users())
