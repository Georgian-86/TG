"""
Database migration: Add country and phone_number columns to users table
"""
import sqlite3

def migrate():
    """Add missing columns to users table"""
    conn = sqlite3.connect('teachgenie.db')
    cursor = conn.cursor()
    
    try:
        print("Checking if country column exists...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'country' not in columns:
            print("Adding 'country' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN country VARCHAR(100)")
            print("OK: country column added")
        else:
            print("SKIP: country column already exists")
        
        if 'phone_number' not in columns:
            print("Adding 'phone_number' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)")
            print("OK: phone_number column added")
        else:
            print("SKIP: phone_number column already exists")
        
        conn.commit()
        print("\nMigration completed successfully!")
        
        # Verify the columns were added
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nUpdated table schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
