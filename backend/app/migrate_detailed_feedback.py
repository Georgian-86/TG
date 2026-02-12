import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, inspect
from app.config import settings
import logging

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate():
    """Run database migration for detailed feedback (Async)"""
    # Create Async Engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # 1. Add feedback_provided column to users table if not exists
        try:
            def check_column(connection):
                inspector = inspect(connection)
                columns = [c['name'] for c in inspector.get_columns('users')]
                return 'feedback_provided' in columns

            exists = await conn.run_sync(check_column)
            
            if not exists:
                logger.info("Adding feedback_provided column to users table...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN feedback_provided BOOLEAN DEFAULT FALSE"))
                logger.info("Column added successfully.")
            else:
                logger.info("feedback_provided column already exists.")
                
        except Exception as e:
            logger.error(f"Error updating users table: {e}")

        # 2. Create feedbacks table
        try:
            logger.info("Creating feedbacks table...")
            # Using specific PostgreSQL syntax for TIMESTAMP
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS feedbacks (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(36) NOT NULL,
                    
                    -- Section 1: Context
                    designation TEXT,
                    department TEXT,
                    teaching_experience TEXT,
                    
                    -- Section 2: Usage
                    usage_frequency TEXT,
                    primary_purpose TEXT, -- JSON
                    used_outputs TEXT, -- JSON
                    
                    -- Section 3: Time
                    time_saved TEXT,
                    speed_vs_manual TEXT,
                    value_single_click TEXT,
                    
                    -- Section 4: Zero-Prompt
                    zero_prompt_ease TEXT,
                    manual_guidance_needed TEXT,
                    complexity_vs_others TEXT,
                    
                    -- Section 5: Content
                    content_accuracy TEXT,
                    classroom_suitability TEXT,
                    quiz_relevance TEXT,
                    
                    -- Section 6: UX
                    interface_intuitive TEXT,
                    technical_issues TEXT,
                    overall_rating INTEGER,
                    
                    -- Section 7: Comparison
                    vs_traditional TEXT,
                    vs_other_ai TEXT,
                    
                    -- Section 8: Adoption
                    will_use_regularly TEXT,
                    will_recommend TEXT,
                    support_adoption TEXT,
                    
                    -- Section 9: Open Feedback
                    liked_most TEXT,
                    liked_least TEXT,
                    feature_requests TEXT,
                    testimonial_consent BOOLEAN DEFAULT FALSE,
                    
                    -- Section 10: Verdict & Performance
                    one_sentence_verdict TEXT,
                    avg_generation_time TEXT,
                    delay_experience TEXT,
                    failure_frequency TEXT,
                    failure_details TEXT,
                    reliability_rating TEXT,
                    retry_frequency TEXT,
                    speed_vs_others TEXT,
                    workflow_satisfaction TEXT,
                    confidence_impact TEXT,
                    
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """))
            logger.info("Feedbacks table created successfully.")
            
        except Exception as e:
            logger.error(f"Error creating feedbacks table: {e}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
