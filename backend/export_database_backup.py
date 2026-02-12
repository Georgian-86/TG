"""
Export all data from production database for backup and analysis
Creates CSV files for all tables with timestamps
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import csv
import os
from datetime import datetime

async def export_all_data():
    database_url = "postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
    engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
    
    # Create exports directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = f"data_exports/{timestamp}"
    os.makedirs(export_dir, exist_ok=True)
    
    try:
        async with engine.connect() as conn:
            print("=" * 80)
            print(f"EXPORTING ALL DATA TO: {export_dir}")
            print("=" * 80)
            
            # Tables to export (corrected column names)
            tables = {
                'users': 'SELECT id, email, full_name, organization, country, subscription_tier, lessons_this_month, last_reset_date, created_at, last_login_at, email_verified, is_active FROM users',
                'lessons': 'SELECT id, user_id, topic, level, duration, include_quiz, include_rbt, lo_po_mapping, iks_integration, status, created_at, completed_at, is_favorite, processing_time_seconds FROM lessons',
                'admin_logs': 'SELECT id, level, category, event_name, message, user_email, ip_address, created_at FROM admin_logs ORDER BY created_at DESC LIMIT 5000',
                'feedbacks': 'SELECT id, user_id, overall_rating, rating_content, rating_time, rating_adoption, will_use_regularly, will_recommend, liked_most, liked_least, feature_requests, created_at FROM feedbacks',
                'email_otps': 'SELECT id, email, otp_hash, attempts, verified, ip_address, created_at, expires_at FROM email_otps',
                'lesson_history': 'SELECT id, user_id, topic, level, duration, created_at FROM lesson_history',
                'file_uploads': 'SELECT id, user_id, file_type, file_url, file_name, uploaded_at FROM file_uploads'
            }
            
            total_rows = 0
            
            for table_name, query in tables.items():
                try:
                    print(f"\n[{table_name}] Exporting...")
                    
                    result = await conn.execute(text(query))
                    rows = result.fetchall()
                    columns = result.keys()
                    
                    if rows:
                        # Write to CSV
                        csv_file = os.path.join(export_dir, f"{table_name}.csv")
                        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(columns)  # Header
                            writer.writerows(rows)    # Data
                        
                        print(f"  ✅ Exported {len(rows)} rows to {table_name}.csv")
                        total_rows += len(rows)
                    else:
                        print(f"  ⚠️  No data in {table_name}")
                        
                except Exception as e:
                    print(f"  ❌ Error exporting {table_name}: {e}")
            
            # Export lesson content (separate file for large JSON data)
            print(f"\n[lessons_content] Exporting full lesson data...")
            try:
                result = await conn.execute(text("""
                    SELECT id, topic, lesson_plan, resources, quiz, learning_objectives, 
                           key_takeaways, ppt_url, pdf_url
                    FROM lessons 
                    WHERE status = 'COMPLETED'
                    ORDER BY created_at DESC
                """))
                
                lesson_content = []
                for row in result:
                    lesson_content.append({
                        'id': row[0],
                        'topic': row[1],
                        'lesson_plan': row[2],
                        'resources': row[3],
                        'quiz': row[4],
                        'learning_objectives': row[5],
                        'key_takeaways': row[6],
                        'ppt_url': row[7],
                        'pdf_url': row[8]
                    })
                
                if lesson_content:
                    import json
                    json_file = os.path.join(export_dir, "lessons_full_content.json")
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(lesson_content, f, indent=2, default=str)
                    print(f"  ✅ Exported {len(lesson_content)} full lessons to JSON")
                else:
                    print(f"  ⚠️  No completed lessons to export")
            except Exception as e:
                print(f"  ❌ Error exporting lesson content: {e}")
            
            # Create summary report
            summary_file = os.path.join(export_dir, "export_summary.txt")
            with open(summary_file, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("DATABASE EXPORT SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Rows Exported: {total_rows}\n")
                f.write(f"Lesson Content: {len(lesson_content)} lessons\n")
                f.write(f"\nFiles Created:\n")
                for filename in os.listdir(export_dir):
                    filepath = os.path.join(export_dir, filename)
                    size = os.path.getsize(filepath)
                    f.write(f"  - {filename}: {size:,} bytes\n")
            
            print("\n" + "=" * 80)
            print(f"✅ EXPORT COMPLETED SUCCESSFULLY!")
            print(f"📁 Location: {os.path.abspath(export_dir)}")
            print(f"📊 Total Rows: {total_rows:,}")
            print(f"📄 Summary: {summary_file}")
            print("=" * 80)
            
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_all_data())
