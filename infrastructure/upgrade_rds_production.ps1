# ============================================
# RDS Production Upgrade Script (Windows)
# ============================================
# This script upgrades your RDS instance to production-grade configuration
# with Multi-AZ, read replicas, and enhanced monitoring

$ErrorActionPreference = "Stop"

$REGION = "us-east-1"
$DB_INSTANCE = "teachgenie-db"
$REPLICA_INSTANCE = "$DB_INSTANCE-replica-1"

Write-Host "=========================================="
Write-Host "RDS Production Upgrade Script"
Write-Host "=========================================="
Write-Host ""
Write-Host "This script will:"
Write-Host "✅ Enable Multi-AZ (High Availability)"
Write-Host "✅ Extend backups to 30 days"
Write-Host "✅ Enable Performance Insights"
Write-Host "✅ Enable storage autoscaling"
Write-Host "✅ Upgrade instance to db.t3.medium"
Write-Host "✅ Create read replica"
Write-Host ""
Write-Host "⚠️  WARNING: Some operations cause brief downtime (1-2 minutes)"
Write-Host ""

$CONFIRM = Read-Host "Continue? (yes/no)"
if ($CONFIRM -ne "yes") {
    Write-Host "Aborted."
    exit 0
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Step 1: Current Configuration"
Write-Host "=========================================="
aws rds describe-db-instances `
  --db-instance-identifier $DB_INSTANCE `
  --region $REGION `
  --query 'DBInstances[0].{Status:DBInstanceStatus,Class:DBInstanceClass,MultiAZ:MultiAZ,BackupRetention:BackupRetentionPeriod,Storage:AllocatedStorage,PerformanceInsights:PerformanceInsightsEnabled}' `
  --output table

Write-Host ""
Read-Host "Press Enter to start upgrade..."

Write-Host ""
Write-Host "=========================================="
Write-Host "Step 2: Enable Multi-AZ & Upgrades"
Write-Host "=========================================="
Write-Host "⏱️  This will take 10-20 minutes..."

aws rds modify-db-instance `
  --db-instance-identifier $DB_INSTANCE `
  --multi-az `
  --db-instance-class db.t3.medium `
  --backup-retention-period 30 `
  --enable-performance-insights `
  --performance-insights-retention-period 7 `
  --max-allocated-storage 100 `
  --apply-immediately `
  --region $REGION

Write-Host "✅ Upgrade initiated"

Write-Host ""
Write-Host "Waiting for instance to become available..."
Write-Host "(This takes 10-20 minutes. You can close and check status later)"

# Wait for available status
do {
    $STATUS = aws rds describe-db-instances `
      --db-instance-identifier $DB_INSTANCE `
      --region $REGION `
      --query 'DBInstances[0].DBInstanceStatus' `
      --output text
    
    Write-Host "Current status: $STATUS"
    
    if ($STATUS -eq "available") {
        break
    }
    
    Start-Sleep -Seconds 30
} while ($true)

Write-Host "✅ Primary database upgraded successfully!"

Write-Host ""
Write-Host "=========================================="
Write-Host "Step 3: Create Read Replica"
Write-Host "=========================================="

$CREATE_REPLICA = Read-Host "Create read replica now? (yes/no)"
if ($CREATE_REPLICA -eq "yes") {
    Write-Host "Creating read replica..."
    
    aws rds create-db-instance-read-replica `
      --db-instance-identifier $REPLICA_INSTANCE `
      --source-db-instance-identifier $DB_INSTANCE `
      --db-instance-class db.t3.small `
      --availability-zone us-east-1b `
      --no-publicly-accessible `
      --enable-performance-insights `
      --region $REGION
    
    Write-Host "✅ Read replica creation initiated (takes 10-20 minutes)"
    Write-Host ""
    Write-Host "Check status with:"
    Write-Host "  aws rds describe-db-instances --db-instance-identifier $REPLICA_INSTANCE --region $REGION"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "✅ UPGRADE COMPLETE!"
Write-Host "=========================================="
Write-Host ""
Write-Host "Updated Configuration:"
aws rds describe-db-instances `
  --db-instance-identifier $DB_INSTANCE `
  --region $REGION `
  --query 'DBInstances[0].{Status:DBInstanceStatus,Class:DBInstanceClass,MultiAZ:MultiAZ,BackupRetention:BackupRetentionPeriod,Storage:AllocatedStorage,MaxStorage:MaxAllocatedStorage,PerformanceInsights:PerformanceInsightsEnabled}' `
  --output table

if ($CREATE_REPLICA -eq "yes") {
    Write-Host ""
    Write-Host "To get read replica endpoint when ready:"
    Write-Host "  aws rds describe-db-instances --db-instance-identifier $REPLICA_INSTANCE --query 'DBInstances[0].Endpoint.Address' --output text --region $REGION"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Next Steps:"
Write-Host "=========================================="
Write-Host "1. ✅ Multi-AZ enabled (High Availability)"
Write-Host "2. ✅ Backups extended to 30 days"
Write-Host "3. ✅ Performance Insights enabled"
Write-Host "4. ✅ Instance upgraded to db.t3.medium"
Write-Host "5. View Performance Insights: https://console.aws.amazon.com/rds/home?region=$REGION#database:id=$DB_INSTANCE"
Write-Host "6. Update your application to use read replica for read operations"
Write-Host ""
Write-Host "📚 See infrastructure/RDS_PRODUCTION_GUIDE.md for application code changes"
