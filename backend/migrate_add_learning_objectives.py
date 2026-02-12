"""
Migration: Add learning_objectives column to lessons table
"""
import sqlite3
import sys
from pathlib import Path

# Database paths to check
db_paths = [
    "teachgenie.db",
    "teach_genie.db",
    "test.db"
]

def add_learning_objectives_column(db_path):
    """Add learning_objectives column to lessons table if it doesn't exist"""
    if not Path(db_path).exists():
        print(f"⚠️  Database {db_path} does not exist, skipping...")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(lessons)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'learning_objectives' in columns:
            print(f"✓ Column 'learning_objectives' already exists in {db_path}")
            conn.close()
            return True
        
        # Add the column
        print(f"Adding 'learning_objectives' column to {db_path}...")
        cursor.execute("""
            ALTER TABLE lessons 
            ADD COLUMN learning_objectives TEXT
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✓ Successfully added 'learning_objectives' column to {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating {db_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("Database Migration: Add learning_objectives column")
    print("=" * 60)
    
    success_count = 0
    for db_path in db_paths:
        if add_learning_objectives_column(db_path):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"Migration complete! Successfully migrated {success_count} database(s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
