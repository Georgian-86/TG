# ============================================
# TeachGenie Terraform Variables
# ============================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
}

variable "alert_email" {
  description = "Email address for CloudWatch alerts"
  type        = string
}

# Application Secrets (sensitive)
variable "secret_key" {
  description = "Application secret key for JWT"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "email_api_key" {
  description = "Resend email API key"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Google OAuth client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
}

# Optional overrides
variable "ecs_cpu" {
  description = "ECS task CPU units"
  type        = number
  default     = 1024
}

variable "ecs_memory" {
  description = "ECS task memory in MB"
  type        = number
  default     = 2048
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 2
}

# ============================================
# RDS Production Configuration
# ============================================

variable "rds_instance_class" {
  description = "RDS primary instance class"
  type        = string
  default     = "db.t3.medium" # 2 vCPU, 4GB RAM - good for production start
}

variable "rds_replica_instance_class" {
  description = "RDS read replica instance class"
  type        = string
  default     = "db.t3.small" # Can be smaller than primary
}

variable "rds_allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 50
}

variable "rds_max_allocated_storage" {
  description = "Maximum storage autoscaling limit in GB"
  type        = number
  default     = 200
}

variable "rds_master_username" {
  description = "RDS master username"
  type        = string
  default     = "teachgenie_admin"
  sensitive   = true
}

variable "rds_master_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "rds_backup_retention_days" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 30 # Production-grade: 30 days
}

variable "rds_multi_az" {
  description = "Enable Multi-AZ deployment for high availability"
  type        = bool
  default     = true # Always true for production
}

variable "rds_enable_read_replicas" {
  description = "Enable read replicas for scalability"
  type        = bool
  default     = true
}

variable "rds_enable_cross_region_replica" {
  description = "Enable cross-region read replica for disaster recovery"
  type        = bool
  default     = false # Enable when needed
}

variable "rds_performance_insights_enabled" {
  description = "Enable Performance Insights"
  type        = bool
  default     = true
}

variable "rds_deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

# ============================================
# ElastiCache Configuration
# ============================================

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}
