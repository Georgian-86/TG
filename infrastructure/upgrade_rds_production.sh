#!/bin/bash
# ============================================
# RDS Production Upgrade Script
# ============================================
# This script upgrades your RDS instance to production-grade configuration
# with Multi-AZ, read replicas, and enhanced monitoring

set -e

REGION="us-east-1"
DB_INSTANCE="teachgenie-db"
REPLICA_INSTANCE="${DB_INSTANCE}-replica-1"

echo "=========================================="
echo "RDS Production Upgrade Script"
echo "=========================================="
echo ""
echo "This script will:"
echo "✅ Enable Multi-AZ (High Availability)"
echo "✅ Extend backups to 30 days"
echo "✅ Enable Performance Insights"
echo "✅ Enable storage autoscaling"
echo "✅ Upgrade instance to db.t3.medium"
echo "✅ Create read replica"
echo ""
echo "⚠️  WARNING: Some operations cause brief downtime (1-2 minutes)"
echo ""

read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "=========================================="
echo "Step 1: Current Configuration"
echo "=========================================="
aws rds describe-db-instances \
  --db-instance-identifier $DB_INSTANCE \
  --region $REGION \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Class:DBInstanceClass,MultiAZ:MultiAZ,BackupRetention:BackupRetentionPeriod,Storage:AllocatedStorage,PerformanceInsights:PerformanceInsightsEnabled}' \
  --output table

echo ""
read -p "Press Enter to start upgrade..."

echo ""
echo "=========================================="
echo "Step 2: Enable Multi-AZ & Upgrades"
echo "=========================================="
echo "⏱️  This will take 10-20 minutes..."

aws rds modify-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --multi-az \
  --db-instance-class db.t3.medium \
  --backup-retention-period 30 \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --max-allocated-storage 100 \
  --apply-immediately \
  --region $REGION

echo "✅ Upgrade initiated"

echo ""
echo "Waiting for instance to become available..."
echo "(This takes 10-20 minutes. You can press Ctrl+C and come back later)"

# Wait for available status
while true; do
    STATUS=$(aws rds describe-db-instances \
      --db-instance-identifier $DB_INSTANCE \
      --region $REGION \
      --query 'DBInstances[0].DBInstanceStatus' \
      --output text)
    
    echo "Current status: $STATUS"
    
    if [ "$STATUS" = "available" ]; then
        break
    fi
    
    sleep 30
done

echo "✅ Primary database upgraded successfully!"

echo ""
echo "=========================================="
echo "Step 3: Create Read Replica"
echo "=========================================="

read -p "Create read replica now? (yes/no): " CREATE_REPLICA
if [ "$CREATE_REPLICA" = "yes" ]; then
    echo "Creating read replica..."
    
    aws rds create-db-instance-read-replica \
      --db-instance-identifier $REPLICA_INSTANCE \
      --source-db-instance-identifier $DB_INSTANCE \
      --db-instance-class db.t3.small \
      --availability-zone us-east-1b \
      --publicly-accessible false \
      --enable-performance-insights \
      --region $REGION
    
    echo "✅ Read replica creation initiated (takes 10-20 minutes)"
    echo ""
    echo "Check status with:"
    echo "  aws rds describe-db-instances --db-instance-identifier $REPLICA_INSTANCE --region $REGION"
fi

echo ""
echo "=========================================="
echo "✅ UPGRADE COMPLETE!"
echo "=========================================="
echo ""
echo "Updated Configuration:"
aws rds describe-db-instances \
  --db-instance-identifier $DB_INSTANCE \
  --region $REGION \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Class:DBInstanceClass,MultiAZ:MultiAZ,BackupRetention:BackupRetentionPeriod,Storage:AllocatedStorage,MaxStorage:MaxAllocatedStorage,PerformanceInsights:PerformanceInsightsEnabled}' \
  --output table

if [ "$CREATE_REPLICA" = "yes" ]; then
    echo ""
    echo "To get read replica endpoint when ready:"
    echo "  aws rds describe-db-instances --db-instance-identifier $REPLICA_INSTANCE --query 'DBInstances[0].Endpoint.Address' --output text --region $REGION"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. ✅ Multi-AZ enabled (High Availability)"
echo "2. ✅ Backups extended to 30 days"
echo "3. ✅ Performance Insights enabled"
echo "4. ✅ Instance upgraded to db.t3.medium"
echo "5. View Performance Insights: https://console.aws.amazon.com/rds/home?region=$REGION#database:id=$DB_INSTANCE"
echo "6. Update your application to use read replica for read operations"
echo ""
echo "📚 See infrastructure/RDS_PRODUCTION_GUIDE.md for application code changes"
