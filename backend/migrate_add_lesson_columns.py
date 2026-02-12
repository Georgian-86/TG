"""
Add missing columns to lessons table in production
Adds: include_rbt, lo_po_mapping, iks_integration
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def migrate_add_lesson_columns():
    # Production database URL
    database_url = "postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
    
    engine = create_async_engine(database_url)
    
    try:
        async with engine.begin() as conn:
            print("=" * 70)
            print("MIGRATING LESSONS TABLE - ADDING MISSING COLUMNS")
            print("=" * 70)
            
            # Check if columns already exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'lessons' 
                AND column_name IN ('include_rbt', 'lo_po_mapping', 'iks_integration')
            """))
            existing_columns = [row[0] for row in result]
            
            print(f"\nExisting columns: {existing_columns if existing_columns else 'None'}")
            
            # Add include_rbt if not exists
            if 'include_rbt' not in existing_columns:
                print("\n[1/3] Adding column: include_rbt")
                await conn.execute(text("""
                    ALTER TABLE lessons 
                    ADD COLUMN include_rbt BOOLEAN NOT NULL DEFAULT TRUE
                """))
                print("✅ Added include_rbt column")
            else:
                print("\n[1/3] Column include_rbt already exists, skipping")
            
            # Add lo_po_mapping if not exists
            if 'lo_po_mapping' not in existing_columns:
                print("\n[2/3] Adding column: lo_po_mapping")
                await conn.execute(text("""
                    ALTER TABLE lessons 
                    ADD COLUMN lo_po_mapping BOOLEAN NOT NULL DEFAULT FALSE
                """))
                print("✅ Added lo_po_mapping column")
            else:
                print("\n[2/3] Column lo_po_mapping already exists, skipping")
            
            # Add iks_integration if not exists
            if 'iks_integration' not in existing_columns:
                print("\n[3/3] Adding column: iks_integration")
                await conn.execute(text("""
                    ALTER TABLE lessons 
                    ADD COLUMN iks_integration BOOLEAN NOT NULL DEFAULT FALSE
                """))
                print("✅ Added iks_integration column")
            else:
                print("\n[3/3] Column iks_integration already exists, skipping")
            
            # Verify columns were added
            result = await conn.execute(text("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'lessons' 
                AND column_name IN ('include_rbt', 'lo_po_mapping', 'iks_integration')
                ORDER BY column_name
            """))
            
            print("\n" + "=" * 70)
            print("VERIFICATION - New Columns:")
            print("=" * 70)
            for row in result:
                print(f"  {row[0]:<20} {row[1]:<15} default={row[2]:<10} nullable={row[3]}")
            
            print("\n✅ Migration completed successfully!")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_add_lesson_columns())
