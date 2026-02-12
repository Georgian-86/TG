"""
View recent admin logs from production
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from datetime import datetime

async def view_recent_logs():
    database_url = "postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
    engine = create_async_engine(database_url)
    
    try:
        async with engine.connect() as conn:
            # Get summary by category
            print("\n" + "=" * 60)
            print("ADMIN LOGS SUMMARY")
            print("=" * 60)
            
            result = await conn.execute(text("""
                SELECT 
                    category,
                    level,
                    COUNT(*) as count
                FROM admin_logs
                GROUP BY category, level
                ORDER BY category, level
            """))
            
            print("\nLogs by Category & Level:")
            for row in result:
                print(f"  {row[0]:<20} {row[1]:<10} {row[2]:>5} logs")
            
            # Get recent logs
            print("\n" + "=" * 60)
            print("RECENT ADMIN LOGS (Last 10)")
            print("=" * 60)
            
            result = await conn.execute(text("""
                SELECT 
                    created_at,
                    level,
                    category,
                    event_name,
                    message,
                    user_email,
                    ip_address
                FROM admin_logs
                ORDER BY created_at DESC
                LIMIT 10
            """))
            
            logs = result.fetchall()
            for log in logs:
                created = log[0].strftime('%Y-%m-%d %H:%M:%S') if log[0] else 'N/A'
                print(f"\n[{created}] {log[1].upper()} - {log[2]}")
                print(f"  Event: {log[3]}")
                print(f"  Message: {log[4][:100]}{'...' if len(log[4]) > 100 else ''}")
                if log[5]:
                    print(f"  User: {log[5]}")
                if log[6]:
                    print(f"  IP: {log[6]}")
            
            # Get error logs
            print("\n" + "=" * 60)
            print("ERROR/CRITICAL LOGS (Last 5)")
            print("=" * 60)
            
            result = await conn.execute(text("""
                SELECT 
                    created_at,
                    level,
                    category,
                    event_name,
                    message,
                    exception_type
                FROM admin_logs
                WHERE level IN ('error', 'critical')
                ORDER BY created_at DESC
                LIMIT 5
            """))
            
            errors = result.fetchall()
            if errors:
                for err in errors:
                    created = err[0].strftime('%Y-%m-%d %H:%M:%S') if err[0] else 'N/A'
                    print(f"\n[{created}] ⚠️  {err[1].upper()} - {err[2]}")
                    print(f"  Event: {err[3]}")
                    print(f"  Message: {err[4][:100]}{'...' if len(err[4]) > 100 else ''}")
                    if err[5]:
                        print(f"  Exception: {err[5]}")
            else:
                print("\n✅ No error/critical logs found")
            
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(view_recent_logs())
