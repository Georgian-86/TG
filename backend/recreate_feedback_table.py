import asyncio
from app.database import engine, Base
from app.models.feedback import Feedback

async def recreate_table():
    async with engine.begin() as conn:
        print("Dropping feedbacks table...")
        # Use run_sync to execute synchronous DDL commands
        await conn.run_sync(lambda sync_conn: Feedback.__table__.drop(sync_conn))
        print("Feedbacks table dropped.")
        
        print("Recreating feedbacks table...")
        await conn.run_sync(Base.metadata.create_all)
        print("Feedbacks table recreated successfully.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(recreate_table())
