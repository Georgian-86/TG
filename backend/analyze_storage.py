"""
Analyze lesson storage in production database
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def analyze_storage():
    database_url = "postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
    engine = create_async_engine(database_url)
    
    try:
        async with engine.connect() as conn:
            print("\n" + "=" * 70)
            print("LESSON STORAGE ANALYSIS")
            print("=" * 70)
            
            # Total lessons
            result = await conn.execute(text("""
                SELECT 
                    COUNT(*) as total_lessons,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN ppt_url IS NOT NULL THEN 1 END) as with_ppt,
                    COUNT(CASE WHEN pdf_url IS NOT NULL THEN 1 END) as with_pdf
                FROM lessons
            """))
            stats = result.fetchone()
            
            print(f"\nLesson Statistics:")
            print(f"  Total Lessons: {stats[0]}")
            print(f"  Unique Users: {stats[1]}")
            print(f"  Completed: {stats[2]}")
            print(f"  With PPT URLs: {stats[3]}")
            print(f"  With PDF URLs: {stats[4]}")
            
            # Storage location analysis
            result = await conn.execute(text("""
                SELECT 
                    ppt_url,
                    pdf_url
                FROM lessons
                WHERE ppt_url IS NOT NULL OR pdf_url IS NOT NULL
                LIMIT 5
            """))
            
            print(f"\nSample File URLs:")
            urls = result.fetchall()
            for i, (ppt, pdf) in enumerate(urls, 1):
                print(f"\n  Lesson {i}:")
                if ppt:
                    print(f"    PPT: {ppt}")
                if pdf:
                    print(f"    PDF: {pdf}")
            
            # Check if URLs are local paths or cloud URLs
            result = await conn.execute(text("""
                SELECT 
                    CASE 
                        WHEN ppt_url LIKE '/outputs/%' THEN 'Local Path'
                        WHEN ppt_url LIKE 'http%' THEN 'Cloud URL'
                        ELSE 'Other'
                    END as storage_type,
                    COUNT(*) as count
                FROM lessons
                WHERE ppt_url IS NOT NULL
                GROUP BY storage_type
            """))
            
            print(f"\nStorage Type Distribution:")
            storage_types = result.fetchall()
            for stype, count in storage_types:
                print(f"  {stype}: {count} lessons")
            
            # Recent lessons
            result = await conn.execute(text("""
                SELECT 
                    topic,
                    status,
                    created_at,
                    CASE 
                        WHEN ppt_url IS NOT NULL THEN 'Yes'
                        ELSE 'No'
                    END as has_files
                FROM lessons
                ORDER BY created_at DESC
                LIMIT 5
            """))
            
            print(f"\nRecent Lessons:")
            recent = result.fetchall()
            for lesson in recent:
                created = lesson[2].strftime('%Y-%m-%d %H:%M') if lesson[2] else 'N/A'
                print(f"  [{created}] {lesson[0][:50]} - {lesson[1]} (Files: {lesson[3]})")
            
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(analyze_storage())
