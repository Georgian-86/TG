import sqlite3

def migrate():
    conn = sqlite3.connect('teachgenie.db')
    cursor = conn.cursor()
    
    # Check if is_favorite exists in lessons table
    cursor.execute("PRAGMA table_info(lessons)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "is_favorite" not in columns:
        print("Adding is_favorite column to lessons table...")
        cursor.execute("ALTER TABLE lessons ADD COLUMN is_favorite BOOLEAN DEFAULT 0")
        conn.commit()
        print("Done.")
    else:
        print("Column is_favorite already exists.")

    conn.close()

if __name__ == "__main__":
    migrate()
