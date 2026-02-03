"""
Database Migration: Add Dashboard Features
- Add profile fields to users table
- Create lesson_history table
- Create file_uploads table
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from app.config import settings
from app.database import Base
from app.models import User, LessonHistory, FileUpload


def run_migration():
    """Run database migration"""
    print("🔄 Starting database migration...\n")
    
    # Convert async database URL to sync URL for migrations
    sync_db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    sync_db_url = sync_db_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Database URL: {sync_db_url}\n")
    
    # Create engine
    engine = create_engine(sync_db_url, echo=False)
    
    try:
        # Create all new tables
        print("✅ Creating new tables...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("  - lesson_history")
        print("  - file_uploads")
        
        # Check existing columns
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        print(f"\n✅ Existing user columns: {len(existing_columns)}")
        
        # Add new columns to existing users table
        print("\n✅ Adding new columns to users table...")
        with engine.begin() as conn:
            # Add bio column
            if 'bio' not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN bio TEXT"))
                print("  ✓ Added 'bio' column")
            else:
                print("  - 'bio' column already exists")
            
            # Add job_title column
            if 'job_title' not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN job_title VARCHAR(100)"))
                print("  ✓ Added 'job_title' column")
            else:
                print("  - 'job_title' column already exists")
            
            # Add department column
            if 'department' not in existing_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN department VARCHAR(100)"))
                print("  ✓ Added 'department' column")
            else:
                print("  - 'department' column already exists")
        
        print("\n" + "="*50)
        print("✅ Migration completed successfully!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_migration()
