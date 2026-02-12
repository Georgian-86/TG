# ============================================
# Production-Grade RDS PostgreSQL Configuration
# ============================================

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.environment}-teachgenie-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name        = "TeachGenie DB Subnet Group"
    Environment = var.environment
  }
}

# DB Parameter Group (Performance Optimizations)
resource "aws_db_parameter_group" "postgres" {
  name   = "${var.environment}-teachgenie-postgres15"
  family = "postgres15"

  # Connection & Memory Settings
  parameter {
    name  = "max_connections"
    value = "200"
  }

  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/4096}" # 25% of RAM
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory/2048}" # 50% of RAM
  }

  parameter {
    name  = "work_mem"
    value = "16384" # 16MB
  }

  # Query Performance
  parameter {
    name  = "random_page_cost"
    value = "1.1" # Optimized for SSD
  }

  # Logging (for debugging)
  parameter {
    name  = "log_min_duration_statement"
    value = "1000" # Log slow queries > 1s
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  tags = {
    Name        = "TeachGenie PostgreSQL 15 Parameters"
    Environment = var.environment
  }
}

# Primary RDS Instance
resource "aws_db_instance" "primary" {
  identifier = "${var.environment}-teachgenie-db"

  # Engine Configuration
  engine               = "postgres"
  engine_version       = "15.5"
  instance_class       = var.rds_instance_class
  allocated_storage    = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage # Enable storage autoscaling
  storage_type         = "gp3"
  storage_encrypted    = true
  kms_key_id          = aws_kms_key.rds.arn

  # Database Configuration
  db_name  = "teachgenie"
  username = var.rds_master_username
  password = var.rds_master_password
  port     = 5432

  # Network & Security
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  # High Availability
  multi_az = var.rds_multi_az

  # Backup Configuration (Production-Grade)
  backup_retention_period   = var.rds_backup_retention_days
  backup_window            = "03:00-04:00" # UTC
  copy_tags_to_snapshot    = true
  delete_automated_backups = false
  skip_final_snapshot      = false
  final_snapshot_identifier = "${var.environment}-teachgenie-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Maintenance
  maintenance_window       = "Mon:04:00-Mon:05:00" # UTC, after backups
  auto_minor_version_upgrade = true
  apply_immediately        = false # Apply changes during maintenance window

  # Monitoring & Performance
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  performance_insights_enabled    = var.rds_performance_insights_enabled
  performance_insights_retention_period = var.rds_performance_insights_enabled ? 7 : null
  monitoring_interval             = 60 # Enhanced monitoring every 60s
  monitoring_role_arn            = aws_iam_role.rds_monitoring.arn

  # Protection
  deletion_protection = var.rds_deletion_protection

  # Parameter Group
  parameter_group_name = aws_db_parameter_group.postgres.name

  tags = {
    Name        = "TeachGenie Primary DB"
    Environment = var.environment
    Backup      = "daily"
  }

  lifecycle {
    prevent_destroy = true # Extra protection
  }
}

# Read Replica 1 (Same Region, Different AZ)
resource "aws_db_instance" "read_replica_1" {
  count = var.rds_enable_read_replicas ? 1 : 0

  identifier = "${var.environment}-teachgenie-db-replica-1"

  # Source
  replicate_source_db = aws_db_instance.primary.identifier

  # Instance Configuration
  instance_class    = var.rds_replica_instance_class
  storage_encrypted = true

  # Network
  publicly_accessible = false
  
  # Multi-AZ for replica (optional but recommended)
  multi_az = false

  # Monitoring
  performance_insights_enabled          = var.rds_performance_insights_enabled
  performance_insights_retention_period = var.rds_performance_insights_enabled ? 7 : null
  monitoring_interval                   = 60
  monitoring_role_arn                  = aws_iam_role.rds_monitoring.arn

  # Maintenance
  auto_minor_version_upgrade = true
  apply_immediately         = false

  tags = {
    Name        = "TeachGenie Read Replica 1"
    Environment = var.environment
    Role        = "read-replica"
  }
}

# Read Replica 2 (Cross-Region for DR - Optional)
resource "aws_db_instance" "read_replica_2_cross_region" {
  count    = var.rds_enable_cross_region_replica ? 1 : 0
  provider = aws.us_west_2 # Different region for disaster recovery

  identifier = "${var.environment}-teachgenie-db-replica-us-west-2"

  # Source
  replicate_source_db = aws_db_instance.primary.arn

  # Instance Configuration
  instance_class    = var.rds_replica_instance_class
  storage_encrypted = true

  # Monitoring
  performance_insights_enabled          = false # Optional for DR replica
  monitoring_interval                   = 60

  # Maintenance
  auto_minor_version_upgrade = true

  tags = {
    Name        = "TeachGenie Cross-Region Replica"
    Environment = var.environment
    Role        = "disaster-recovery"
  }
}

# KMS Key for RDS Encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name        = "TeachGenie RDS Key"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${var.environment}-teachgenie-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# IAM Role for Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.environment}-teachgenie-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "RDS Enhanced Monitoring Role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Alarms for Database Health
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.environment}-rds-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "Database CPU utilization is too high"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.id
  }
}

resource "aws_cloudwatch_metric_alarm" "database_memory" {
  alarm_name          = "${var.environment}-rds-low-memory"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "FreeableMemory"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "256000000" # 256MB
  alarm_description  = "Database freeable memory is too low"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.id
  }
}

resource "aws_cloudwatch_metric_alarm" "database_storage" {
  alarm_name          = "${var.environment}-rds-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name        = "FreeStorageSpace"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "5000000000" # 5GB
  alarm_description  = "Database free storage is too low"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.id
  }
}

resource "aws_cloudwatch_metric_alarm" "database_connections" {
  alarm_name          = "${var.environment}-rds-high-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "DatabaseConnections"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "180" # 90% of max_connections (200)
  alarm_description  = "Database connection count is too high"
  alarm_actions      = [aws_sns_topic.alerts.arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.primary.id
  }
}

# Outputs
output "rds_endpoint" {
  description = "RDS primary instance endpoint"
  value       = aws_db_instance.primary.endpoint
}

output "rds_replica_endpoint" {
  description = "RDS read replica endpoint"
  value       = var.rds_enable_read_replicas ? aws_db_instance.read_replica_1[0].endpoint : null
}

output "database_url" {
  description = "PostgreSQL connection string"
  value       = "postgresql+asyncpg://${var.rds_master_username}:${var.rds_master_password}@${aws_db_instance.primary.endpoint}/${aws_db_instance.primary.db_name}"
  sensitive   = true
}

output "database_url_read_replica" {
  description = "PostgreSQL read-only connection string"
  value       = var.rds_enable_read_replicas ? "postgresql+asyncpg://${var.rds_master_username}:${var.rds_master_password}@${aws_db_instance.read_replica_1[0].endpoint}/${aws_db_instance.primary.db_name}" : null
  sensitive   = true
}
