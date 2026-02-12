# Production-Grade RDS Implementation Guide

## 🎯 Overview
This guide will help you upgrade your RDS database to production-grade with:
- ✅ Multi-AZ deployment (99.95% availability)
- ✅ Read replicas (horizontal scaling)
- ✅ 30-day automated backups
- ✅ Performance Insights
- ✅ Enhanced monitoring
- ✅ Point-in-time recovery

## 📊 Current vs Production State

| Feature | Current | Production Target |
|---------|---------|------------------|
| Instance Class | db.t3.micro | db.t3.medium+ |
| Multi-AZ | ❌ No | ✅ Yes |
| Read Replicas | ❌ None | ✅ 1-2 replicas |
| Backup Retention | 7 days | 30 days |
| Performance Insights | ❌ No | ✅ Yes |
| Storage | 20GB | 50GB+ autoscaling |

## 🚀 Quick Implementation (AWS CLI)

### Option 1: Immediate Upgrade (CLI Commands)

**⚠️ Warning:** These operations will cause brief downtime. Schedule during maintenance window.

#### Step 1: Enable Multi-AZ (High Availability)
```bash
# Enable Multi-AZ - Creates standby in different AZ
# Downtime: 1-2 minutes
aws rds modify-db-instance \
  --db-instance-identifier teachgenie-db \
  --multi-az \
  --apply-immediately \
  --region us-east-1

echo "✅ Multi-AZ deployment initiated"
echo "⏱️  This will take 5-15 minutes to complete"
```

#### Step 2: Extend Backup Retention
```bash
# Increase backup retention to 30 days
# No downtime
aws rds modify-db-instance \
  --db-instance-identifier teachgenie-db \
  --backup-retention-period 30 \
  --region us-east-1

echo "✅ Backup retention extended to 30 days"
```

#### Step 3: Enable Performance Insights
```bash
# Enable Performance Insights for query monitoring
# No downtime
aws rds modify-db-instance \
  --db-instance-identifier teachgenie-db \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --region us-east-1

echo "✅ Performance Insights enabled"
```

#### Step 4: Upgrade Instance Size (Recommended)
```bash
# Upgrade from db.t3.micro to db.t3.medium
# Downtime: 1-2 minutes
aws rds modify-db-instance \
  --db-instance-identifier teachgenie-db \
  --db-instance-class db.t3.medium \
  --apply-immediately \
  --region us-east-1

echo "✅ Instance upgrade to db.t3.medium initiated"
echo "⏱️  This will take 5-10 minutes to complete"
```

#### Step 5: Enable Storage Autoscaling
```bash
# Enable storage autoscaling up to 100GB
# No downtime
aws rds modify-db-instance \
  --db-instance-identifier teachgenie-db \
  --max-allocated-storage 100 \
  --region us-east-1

echo "✅ Storage autoscaling enabled (max 100GB)"
```

#### Step 6: Create Read Replica
```bash
# Wait for Multi-AZ to complete first
# Check status
aws rds describe-db-instances \
  --db-instance-identifier teachgenie-db \
  --query "DBInstances[0].DBInstanceStatus" \
  --output text \
  --region us-east-1

# Once status is "available", create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier teachgenie-db-replica-1 \
  --source-db-instance-identifier teachgenie-db \
  --db-instance-class db.t3.small \
  --availability-zone us-east-1b \
  --publicly-accessible false \
  --enable-performance-insights \
  --region us-east-1

echo "✅ Read replica creation initiated"
echo "⏱️  This will take 10-20 minutes to complete"
```

### Option 2: Conservative Upgrade (During Maintenance Window)

Use `--no-apply-immediately` flag to apply changes during your maintenance window:

```bash
# All changes will be applied during maintenance window (Mon 04:00-05:00 UTC)
aws rds modify-db-instance \
  --db-instance-identifier teachgenie-db \
  --multi-az \
  --db-instance-class db.t3.medium \
  --backup-retention-period 30 \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --max-allocated-storage 100 \
  --no-apply-immediately \
  --region us-east-1

echo "✅ Changes scheduled for next maintenance window"
echo "📅 Next window: Monday 04:00-05:00 UTC"
```

## 📈 Monitoring Your Upgrades

### Check Current Status
```bash
aws rds describe-db-instances \
  --db-instance-identifier teachgenie-db \
  --query 'DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ,Class:DBInstanceClass,BackupRetention:BackupRetentionPeriod,PerformanceInsights:PerformanceInsightsEnabled}' \
  --output table \
  --region us-east-1
```

### Monitor Ongoing Operations
```bash
# Watch for "available" status
watch -n 10 'aws rds describe-db-instances \
  --db-instance-identifier teachgenie-db \
  --query "DBInstances[0].DBInstanceStatus" \
  --output text \
  --region us-east-1'
```

### Check Read Replica Status
```bash
aws rds describe-db-instances \
  --db-instance-identifier teachgenie-db-replica-1 \
  --query 'DBInstances[0].{Status:DBInstanceStatus,ReplicationLag:SecondsBehindMaster,Endpoint:Endpoint.Address}' \
  --output table \
  --region us-east-1
```

## 🔧 Connect to Read Replica

Once the read replica is available, get its endpoint:

```bash
# Get read replica endpoint
REPLICA_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier teachgenie-db-replica-1 \
  --query "DBInstances[0].Endpoint.Address" \
  --output text \
  --region us-east-1)

echo "Read Replica Endpoint: $REPLICA_ENDPOINT"
```

### Update Your Application

Add a read-only connection string to App Runner:

```bash
# Get current credentials (use same username/password)
PRIMARY_URL="postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@teachgenie-db.cklww4emo61g.us-east-1.rds.amazonaws.com:5432/teachgenie"
READ_REPLICA_URL="postgresql+asyncpg://teachgenie_admin:4Q9QWxCUnbKAJC3@${REPLICA_ENDPOINT}:5432/teachgenie"

echo "Primary (Write): $PRIMARY_URL"
echo "Replica (Read): $READ_REPLICA_URL"
```

Add to App Runner environment variables:
```bash
DATABASE_URL               # Primary (write operations)
DATABASE_READ_REPLICA_URL  # Replica (read-only operations)
```

## 💰 Cost Estimation

### Current Cost (~$15/month)
- db.t3.micro: $0.018/hour × 730 hours = **$13.14/month**
- 20GB storage: $0.115/GB × 20 = **$2.30/month**
- **Total: ~$15.44/month**

### Production Configuration Cost (~$100-150/month)
- db.t3.medium primary (Multi-AZ): $0.136/hour × 730 = **$99.28/month**
- db.t3.small replica: $0.034/hour × 730 = **$24.82/month**
- 50GB storage (GP3): $0.115/GB × 50 = **$5.75/month**
- Backups (30 days): ~**$10/month**
- **Total: ~$140/month**

### Cost Optimization Tips
1. **Use Reserved Instances**: Save 30-60% with 1-year commitment
2. **Start with db.t3.small**: $0.034/hour (Multi-AZ = $49.64/month)
3. **Single Read Replica**: Only add more if needed
4. **Monitor Usage**: Scale down if underutilized

## 🛡️ Backup & Recovery Features

### Enhanced Backups (Enabled)
- ✅ Automated daily backups at 03:00 UTC
- ✅ 30-day retention period
- ✅ Point-in-time recovery (to any second in last 30 days)
- ✅ Transaction logs backed up every 5 minutes

### Manual Snapshots
```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier teachgenie-db \
  --db-snapshot-identifier teachgenie-db-$(date +%Y%m%d-%H%M%S) \
  --region us-east-1

# List all snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier teachgenie-db \
  --query 'DBSnapshots[*].{ID:DBSnapshotIdentifier,Created:SnapshotCreateTime,Status:Status}' \
  --output table \
  --region us-east-1
```

### Point-in-Time Restore
```bash
# Restore to specific time (example: 1 hour ago)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier teachgenie-db \
  --target-db-instance-identifier teachgenie-db-restored \
  --restore-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --region us-east-1
```

## 📊 Performance Insights Dashboard

Access Performance Insights:
```bash
# Get console URL
echo "https://console.aws.amazon.com/rds/home?region=us-east-1#database:id=teachgenie-db;is-cluster=false;tab=monitoring"
```

View:
- Top SQL queries
- Wait events
- Database load
- Connection usage

## 🎯 Application Code Changes

### Use Read Replicas for Scalability

Update `backend/app/database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings

# Primary database (for writes)
engine_primary = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
)

# Read replica (for read-only queries)
engine_replica = create_async_engine(
    settings.DATABASE_READ_REPLICA_URL or settings.DATABASE_URL,  # Fallback to primary
    pool_size=15,  # More connections for reads
    max_overflow=25,
)

# Use primary for writes
async def get_db_write():
    async with AsyncSessionLocal(bind=engine_primary) as session:
        yield session

# Use replica for reads
async def get_db_read():
    async with AsyncSessionLocal(bind=engine_replica) as session:
        yield session
```

Usage in routes:
```python
# Write operations (use primary)
@router.post("/lessons")
async def create_lesson(db: AsyncSession = Depends(get_db_write)):
    # INSERT/UPDATE/DELETE operations
    pass

# Read operations (use replica)
@router.get("/lessons")
async def list_lessons(db: AsyncSession = Depends(get_db_read)):
    # SELECT operations only
    pass
```

## ✅ Verification Checklist

After implementation, verify:

- [ ] Multi-AZ shows "Yes" in RDS console
- [ ] Instance class upgraded to db.t3.medium or higher
- [ ] Backup retention set to 30 days
- [ ] Performance Insights enabled
- [ ] Read replica status is "available"
- [ ] Read replica lag < 1 second
- [ ] CloudWatch alarms created
- [ ] Application can connect to both primary and replica
- [ ] Manual snapshot test successful
- [ ] Point-in-time recovery test successful

## 🚨 Troubleshooting

### Multi-AZ Not Enabling
```bash
# Check for pending modifications
aws rds describe-db-instances \
  --db-instance-identifier teachgenie-db \
  --query 'DBInstances[0].PendingModifiedValues'
```

### High Replication Lag
```bash
# Check replica lag
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name ReplicaLag \
  --dimensions Name=DBInstanceIdentifier,Value=teachgenie-db-replica-1 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

## 📚 Additional Resources

- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Multi-AZ Deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Read Replicas Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html)
- [Performance Insights](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html)

## 🎓 Next Steps

1. **Immediate (Today)**
   - Enable Multi-AZ
   - Extend backup retention to 30 days
   - Enable Performance Insights

2. **This Week**
   - Upgrade instance to db.t3.medium
   - Create read replica
   - Update application to use replica for reads

3. **Monitoring Setup**
   - Configure CloudWatch alarms
   - Set up SNS notifications
   - Create dashboard for database metrics

4. **Future Enhancements**
   - Cross-region replica for disaster recovery
   - Reserved instances for cost savings
   - Advanced parameter tuning
   - Connection pooling with PgBouncer
