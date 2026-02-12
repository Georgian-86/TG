# Database Backup & Data Export Guide

## ✅ Your Current Backup Status

### **Automated Backups (Already Enabled)**
- ✅ **Backup Retention:** 30 days (extended from 7 days)
- ✅ **Backup Window:** 03:48-04:18 UTC (daily)
- ✅ **Latest Backup:** 2026-02-12 18:54:31 UTC
- ✅ **Point-in-Time Recovery:** Available (last 30 days)
- ✅ **Transaction Logs:** Backed up every 5 minutes

### **What's Protected:**
✅ All database changes (including your new columns)
✅ All user data, lessons, admin logs
✅ Schema changes and migrations
✅ Can restore to ANY second in last 30 days

---

## 🛡️ Backup Strategy (3 Layers of Protection)

### **Layer 1: Automated AWS RDS Backups (Active)**
**What:** AWS automatically backs up your entire database daily
**Retention:** 30 days
**Recovery:** Point-in-time recovery to any second

```powershell
# Restore to 2 hours ago
$restoreTime = (Get-Date).AddHours(-2).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")
aws rds restore-db-instance-to-point-in-time `
  --source-db-instance-identifier teachgenie-db `
  --target-db-instance-identifier teachgenie-db-restored `
  --restore-time $restoreTime `
  --region us-east-1
```

### **Layer 2: Manual Snapshots (On-Demand)**
**What:** Create permanent backups before major changes
**Retention:** Forever (until you delete)
**Cost:** ~$0.095/GB/month (~$2/month for 20GB)

```powershell
# Create manual snapshot
aws rds create-db-snapshot `
  --db-instance-identifier teachgenie-db `
  --db-snapshot-identifier teachgenie-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss') `
  --region us-east-1

# List all snapshots
aws rds describe-db-snapshots `
  --db-instance-identifier teachgenie-db `
  --region us-east-1 `
  --query "DBSnapshots[*].{Name:DBSnapshotIdentifier,Created:SnapshotCreateTime,Size:AllocatedStorage,Status:Status}" `
  --output table
```

### **Layer 3: Data Exports (For Analysis)**
**What:** Export tables to CSV/JSON for local analysis
**Use:** Analytics, reporting, external backup

```powershell
# Export all data to CSV files
python backend/export_database_backup.py
```

---

## 📊 Data Export & Analysis

### **Quick Export (All Tables):**

I've created a script that exports all your data:

```powershell
# Run the export
python backend/export_database_backup.py

# Output location: data_exports/[timestamp]/
# ├── users.csv
# ├── lessons.csv
# ├── admin_logs.csv
# ├── feedbacks.csv
# ├── lessons_full_content.json
# └── export_summary.txt
```

### **What Gets Exported:**

| Table | Data | Use Case |
|-------|------|----------|
| `users.csv` | User info, quotas, subscriptions | User analytics, growth tracking |
| `lessons.csv` | Lesson metadata, topics, status | Usage patterns, popular topics |
| `lessons_full_content.json` | Full lesson plans, quizzes, resources | Training AI models, content analysis |
| `admin_logs.csv` | System events, errors, user actions | Security audits, debugging |
| `feedbacks.csv` | User ratings & comments | Product improvements, satisfaction |

### **Analysis Examples:**

```python
import pandas as pd

# Load user data
users = pd.read_csv('data_exports/[timestamp]/users.csv')

# Top organizations
print(users['organization'].value_counts())

# Lessons per user
lessons = pd.read_csv('data_exports/[timestamp]/lessons.csv')
print(lessons.groupby('user_id').size().describe())

# Most popular topics
print(lessons['topic'].value_counts().head(20))
```

---

## 🚨 Critical Backup Schedule

### **Before Every Major Change:**

```powershell
# 1. Create snapshot before deployment
$SNAPSHOT_ID = "teachgenie-pre-deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
aws rds create-db-snapshot `
  --db-instance-identifier teachgenie-db `
  --db-snapshot-identifier $SNAPSHOT_ID `
  --region us-east-1

echo "Snapshot created: $SNAPSHOT_ID"

# 2. Deploy changes...

# 3. Verify after deployment
python backend/check_admin_logs_table.py
```

### **Weekly Data Export (Recommended):**

Create a scheduled task to export data weekly:

**Windows Task Scheduler:**
```powershell
# Create weekly export task
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "c:\Users\golu kumar\Desktop\New folder\Teach-Genie\backend\export_database_backup.py"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am

Register-ScheduledTask -TaskName "TeachGenie-WeeklyBackup" `
  -Action $action -Trigger $trigger -Description "Weekly data export"
```

---

## 🔄 Restore Procedures

### **Scenario 1: Oops! Deleted Data (Last Hour)**

```powershell
# Point-in-time restore to 1 hour ago
$restoreTime = (Get-Date).AddHours(-1).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")

aws rds restore-db-instance-to-point-in-time `
  --source-db-instance-identifier teachgenie-db `
  --target-db-instance-identifier teachgenie-db-recovered `
  --restore-time $restoreTime `
  --db-instance-class db.t3.micro `
  --region us-east-1

# Wait for restore (10-20 minutes)
# Then export specific data from recovered instance
```

### **Scenario 2: Bad Migration (Last Week)**

```powershell
# Restore from manual snapshot
aws rds restore-db-instance-from-db-snapshot `
  --db-instance-identifier teachgenie-db-restored `
  --db-snapshot-identifier teachgenie-pre-deploy-20260212 `
  --region us-east-1
```

### **Scenario 3: Complete Disaster**

```powershell
# 1. Restore from automated backup (30 days available)
aws rds restore-db-instance-to-point-in-time `
  --source-db-instance-identifier teachgenie-db `
  --target-db-instance-identifier teachgenie-db-disaster-recovery `
  --use-latest-restorable-time `
  --region us-east-1

# 2. Update App Runner to point to new database
# DATABASE_URL=postgresql+asyncpg://...@teachgenie-db-disaster-recovery.xxx.rds.amazonaws.com/teachgenie
```

---

## 📦 Offsite Backup (Recommended)

### **Option 1: Export to S3 (Cheapest)**

```powershell
# Export and upload to S3
python backend/export_database_backup.py

# Upload to S3
aws s3 sync data_exports/ s3://teachgenie-backups/database-exports/ --region us-east-1

# Cost: ~$0.023/GB/month (~$0.50/month for all exports)
```

### **Option 2: Copy Snapshots to Another Region (DR)**

```powershell
# Copy snapshot to us-west-2 for disaster recovery
aws rds copy-db-snapshot `
  --source-db-snapshot-identifier teachgenie-backup-20260212 `
  --target-db-snapshot-identifier teachgenie-backup-20260212-us-west-2 `
  --source-region us-east-1 `
  --region us-west-2

# Cost: ~$0.095/GB/month in second region
```

---

## 📈 Data Analysis Queries

Create `backend/analyze_data.py`:

```python
"""Quick data analysis queries"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def analyze():
    database_url = "postgresql+asyncpg://teachgenie_admin:...@teachgenie-db.../teachgenie"
    engine = create_async_engine(database_url)
    
    async with engine.connect() as conn:
        # Total users
        result = await conn.execute(text("SELECT COUNT(*) FROM users"))
        print(f"Total Users: {result.scalar()}")
        
        # Lessons generated
        result = await conn.execute(text("SELECT COUNT(*) FROM lessons WHERE status = 'COMPLETED'"))
        print(f"Completed Lessons: {result.scalar()}")
        
        # Top topics
        result = await conn.execute(text("""
            SELECT topic, COUNT(*) as count 
            FROM lessons 
            GROUP BY topic 
            ORDER BY count DESC 
            LIMIT 10
        """))
        print("\nTop 10 Topics:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")
    
    await engine.dispose()

asyncio.run(analyze())
```

---

## ✅ Backup Checklist

- [x] Automated daily backups (30 days)
- [x] Point-in-time recovery enabled
- [ ] Create manual snapshot before deployments
- [ ] Weekly data exports to CSV
- [ ] Monthly offsite backup to S3
- [ ] Test restore procedure (quarterly)
- [ ] Document recovery procedures
- [ ] Set up monitoring alerts

---

## 🚀 Quick Commands

```powershell
# Export all data NOW
python backend/export_database_backup.py

# Create snapshot NOW
aws rds create-db-snapshot --db-instance-identifier teachgenie-db --db-snapshot-identifier emergency-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss') --region us-east-1

# Check backup status
aws rds describe-db-instances --db-instance-identifier teachgenie-db --query "DBInstances[0].{Backup:BackupRetentionPeriod,Latest:LatestRestorableTime}" --region us-east-1

# List all snapshots
aws rds describe-db-snapshots --db-instance-identifier teachgenie-db --region us-east-1 --query "DBSnapshots[*].DBSnapshotIdentifier" --output table
```

---

## 💰 Backup Costs

| Backup Type | Storage | Cost/Month | Recommendation |
|-------------|---------|------------|----------------|
| Automated (30 days) | ~20GB | **FREE** (included) | ✅ Already active |
| Manual Snapshots | ~20GB each | $1.90/snapshot | Create before deployments |
| Data Exports (local) | ~50MB | **FREE** | Weekly exports |
| S3 Offsite Backup | ~500MB | $0.01 | Monthly uploads |
| **Total** | | **~$2-5/month** | Excellent protection |

**Your data is safe! All changes are automatically backed up.**
