"""
Add OAuth fields to users table
Migration for Google OAuth support
"""
import sqlite3
from pathlib import Path

def run_migration():
    """Add OAuth-related columns to users table"""
    db_path = Path("teachgenie.db")
    
    if not db_path.exists():
        print(f"Error: Database file {db_path} not found!")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        migrations = []
        
        # Add oauth_provider column
        if 'oauth_provider' not in existing_columns:
            migrations.append(("oauth_provider", "ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)"))
        
        # Add oauth_id column
        if 'oauth_id' not in existing_columns:
            migrations.append(("oauth_id", "ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)"))
        
        # Add profile_picture_url column
        if 'profile_picture_url' not in existing_columns:
            migrations.append(("profile_picture_url", "ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(500)"))
        
        # Add profile_completed column
        if 'profile_completed' not in existing_columns:
            migrations.append(("profile_completed", "ALTER TABLE users ADD COLUMN profile_completed BOOLEAN DEFAULT TRUE"))
        
        # Run migrations
        for col_name, sql in migrations:
            print(f"Adding column: {col_name}")
            cursor.execute(sql)
        
        # Update existing users to have profile_completed = TRUE
        if migrations:
            print("Setting profile_completed = TRUE for existing users...")
            cursor.execute("UPDATE users SET profile_completed = TRUE WHERE profile_completed IS NULL")
        
        conn.commit()
        
        # Verify migrations
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n✅ Migration completed successfully!")
        print("\nCurrent users table schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
