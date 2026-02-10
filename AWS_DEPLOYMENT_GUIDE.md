# Teach-Genie AWS Production Deployment Guide

## Complete Three-Tier Architecture with CI/CD

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Phase 1: VPC & Networking](#3-phase-1-vpc--networking)
4. [Phase 2: Database Tier (RDS)](#4-phase-2-database-tier-rds)
5. [Phase 3: Application Tier (ECS Fargate)](#5-phase-3-application-tier-ecs-fargate)
6. [Phase 4: Web Tier (CloudFront + S3)](#6-phase-4-web-tier-cloudfront--s3)
7. [Phase 5: CI/CD Pipeline](#7-phase-5-cicd-pipeline)
8. [Phase 6: Monitoring & Logging](#8-phase-6-monitoring--logging)
9. [Phase 7: Security Hardening](#9-phase-7-security-hardening)
10. [Cost Estimation](#10-cost-estimation)
11. [Deployment Checklist](#11-deployment-checklist)

---

## 1. Architecture Overview

### Three-Tier Architecture Diagram

```
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                        INTERNET                             │
                                    └─────────────────────────────────────────────────────────────┘
                                                              │
                                                              ▼
                                    ┌─────────────────────────────────────────────────────────────┐
                                    │                    AWS CloudFront                           │
                                    │              (CDN + SSL Termination)                        │
                                    │                   *.teachgenie.ai                           │
                                    └─────────────────────────────────────────────────────────────┘
                                                    │                    │
                                                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                              AWS VPC                                                     │
│                                         (10.0.0.0/16)                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                    PUBLIC SUBNETS                                                  │  │
│  │                                                                                                    │  │
│  │   ┌─────────────────────────┐              ┌─────────────────────────┐                            │  │
│  │   │   Public Subnet 1a      │              │   Public Subnet 1b      │                            │  │
│  │   │     10.0.1.0/24         │              │     10.0.2.0/24         │                            │  │
│  │   │                         │              │                         │                            │  │
│  │   │  ┌─────────────────┐   │              │  ┌─────────────────┐   │                            │  │
│  │   │  │   NAT Gateway   │   │              │  │   NAT Gateway   │   │                            │  │
│  │   │  └─────────────────┘   │              │  └─────────────────┘   │                            │  │
│  │   │                         │              │                         │                            │  │
│  │   │  ┌─────────────────┐   │              │  ┌─────────────────┐   │                            │  │
│  │   │  │ ALB (Frontend)  │◄──┼──────────────┼──┤ ALB (Frontend)  │   │                            │  │
│  │   │  └─────────────────┘   │              │  └─────────────────┘   │                            │  │
│  │   └─────────────────────────┘              └─────────────────────────┘                            │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                   PRIVATE SUBNETS (Application)                                    │  │
│  │                                                                                                    │  │
│  │   ┌─────────────────────────┐              ┌─────────────────────────┐                            │  │
│  │   │   Private Subnet 1a     │              │   Private Subnet 1b     │                            │  │
│  │   │     10.0.3.0/24         │              │     10.0.4.0/24         │                            │  │
│  │   │                         │              │                         │                            │  │
│  │   │  ┌─────────────────┐   │              │  ┌─────────────────┐   │                            │  │
│  │   │  │  ECS Fargate    │   │              │  │  ECS Fargate    │   │                            │  │
│  │   │  │  (FastAPI)      │   │              │  │  (FastAPI)      │   │                            │  │
│  │   │  │  Task 1         │   │              │  │  Task 2         │   │                            │  │
│  │   │  └─────────────────┘   │              │  └─────────────────┘   │                            │  │
│  │   │                         │              │                         │                            │  │
│  │   │  ┌─────────────────┐   │              │  ┌─────────────────┐   │                            │  │
│  │   │  │  ElastiCache    │   │              │  │  ElastiCache    │   │                            │  │
│  │   │  │  (Redis)        │◄──┼──────────────┼──┤  (Redis)        │   │                            │  │
│  │   │  └─────────────────┘   │              │  └─────────────────┘   │                            │  │
│  │   └─────────────────────────┘              └─────────────────────────┘                            │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                   PRIVATE SUBNETS (Database)                                       │  │
│  │                                                                                                    │  │
│  │   ┌─────────────────────────┐              ┌─────────────────────────┐                            │  │
│  │   │   DB Subnet 1a          │              │   DB Subnet 1b          │                            │  │
│  │   │     10.0.5.0/24         │              │     10.0.6.0/24         │                            │  │
│  │   │                         │              │                         │                            │  │
│  │   │  ┌─────────────────┐   │              │  ┌─────────────────┐   │                            │  │
│  │   │  │  RDS PostgreSQL │   │   Sync       │  │  RDS PostgreSQL │   │                            │  │
│  │   │  │    (Primary)    │───┼──────────────┼──►   (Standby)     │   │                            │  │
│  │   │  └─────────────────┘   │              │  └─────────────────┘   │                            │  │
│  │   └─────────────────────────┘              └─────────────────────────┘                            │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────────────────────────────┐
                    │                         S3 BUCKET                                    │
                    │          (React Frontend Static Files + PDF/PPT Storage)            │
                    └─────────────────────────────────────────────────────────────────────┘
```

### AWS Services Used

| Tier | Service | Purpose |
|------|---------|---------|
| **Web** | CloudFront | CDN, SSL termination, caching |
| **Web** | S3 | React frontend hosting |
| **Web** | Route 53 | DNS management |
| **Web** | ACM | SSL certificates |
| **App** | ECS Fargate | Containerized FastAPI backend |
| **App** | ALB | Load balancing for backend |
| **App** | ElastiCache | Redis for caching |
| **App** | ECR | Docker image registry |
| **Data** | RDS PostgreSQL | Primary database |
| **Security** | Secrets Manager | API keys, DB credentials |
| **Security** | WAF | Web Application Firewall |
| **CI/CD** | CodePipeline | Automated deployments |
| **CI/CD** | CodeBuild | Build and test |
| **Monitoring** | CloudWatch | Logs and metrics |
| **Monitoring** | X-Ray | Distributed tracing |

---

## 2. Prerequisites

### 2.1 AWS Account Setup

```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Verify
aws sts get-caller-identity
```

### 2.2 Required Tools

```bash
# Install Terraform (Infrastructure as Code)
# Windows (via Chocolatey)
choco install terraform

# Install Docker
# Download from https://www.docker.com/products/docker-desktop

# Verify installations
terraform --version
docker --version
aws --version
```

### 2.3 Domain Setup

1. Register domain (e.g., `teachgenie.ai`) in Route 53 or transfer existing
2. Create hosted zone in Route 53
3. Note the hosted zone ID for later

---

## 3. Phase 1: VPC & Networking

### 3.1 Create VPC Infrastructure

Create file: `infrastructure/terraform/vpc.tf`

```hcl
# Provider Configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "teachgenie-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "TeachGenie"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "teachgenie-vpc-${var.environment}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name = "teachgenie-igw-${var.environment}"
  }
}

# Availability Zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "teachgenie-public-${count.index + 1}-${var.environment}"
    Tier = "Public"
  }
}

# Private Subnets (Application)
resource "aws_subnet" "private_app" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 3)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "teachgenie-private-app-${count.index + 1}-${var.environment}"
    Tier = "Application"
  }
}

# Private Subnets (Database)
resource "aws_subnet" "private_db" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 5)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "teachgenie-private-db-${count.index + 1}-${var.environment}"
    Tier = "Database"
  }
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"
  
  tags = {
    Name = "teachgenie-nat-eip-${count.index + 1}-${var.environment}"
  }
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = {
    Name = "teachgenie-nat-${count.index + 1}-${var.environment}"
  }
  
  depends_on = [aws_internet_gateway.main]
}

# Route Table - Public
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name = "teachgenie-public-rt-${var.environment}"
  }
}

# Route Tables - Private
resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = {
    Name = "teachgenie-private-rt-${count.index + 1}-${var.environment}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_app" {
  count          = 2
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "private_db" {
  count          = 2
  subnet_id      = aws_subnet.private_db[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Outputs
output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  value = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  value = aws_subnet.private_db[*].id
}
```

### 3.2 Security Groups

Create file: `infrastructure/terraform/security_groups.tf`

```hcl
# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "teachgenie-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTP from anywhere (redirect to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "teachgenie-alb-sg-${var.environment}"
  }
}

# ECS Tasks Security Group
resource "aws_security_group" "ecs_tasks" {
  name        = "teachgenie-ecs-sg"
  description = "Security group for ECS Fargate tasks"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "teachgenie-ecs-sg-${var.environment}"
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "teachgenie-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  tags = {
    Name = "teachgenie-rds-sg-${var.environment}"
  }
}

# ElastiCache Security Group
resource "aws_security_group" "elasticache" {
  name        = "teachgenie-elasticache-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "Redis from ECS"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  tags = {
    Name = "teachgenie-elasticache-sg-${var.environment}"
  }
}
```

### 3.3 Deploy VPC

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan
```

---

## 4. Phase 2: Database Tier (RDS)

### 4.1 Create RDS PostgreSQL

Create file: `infrastructure/terraform/rds.tf`

```hcl
# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "teachgenie-db-subnet-group"
  subnet_ids = aws_subnet.private_db[*].id
  
  tags = {
    Name = "teachgenie-db-subnet-group-${var.environment}"
  }
}

# Random password for RDS
resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store password in Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "teachgenie/db-password-${var.environment}"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "teachgenie_admin"
    password = random_password.db_password.result
    host     = aws_db_instance.main.address
    port     = 5432
    dbname   = "teachgenie"
  })
}

# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "teachgenie-pg-params"
  
  parameter {
    name  = "log_connections"
    value = "1"
  }
  
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
  
  parameter {
    name  = "log_duration"
    value = "1"
  }
  
  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "teachgenie-db-${var.environment}"
  
  # Engine
  engine               = "postgres"
  engine_version       = "15.4"
  instance_class       = "db.t3.medium"  # Production: db.r6g.large
  
  # Storage
  allocated_storage     = 100
  max_allocated_storage = 500
  storage_type          = "gp3"
  storage_encrypted     = true
  
  # Database
  db_name  = "teachgenie"
  username = "teachgenie_admin"
  password = random_password.db_password.result
  port     = 5432
  
  # Network
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  multi_az               = true  # High availability
  
  # Backup
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"
  
  # Performance
  parameter_group_name        = aws_db_parameter_group.main.name
  performance_insights_enabled = true
  
  # Deletion protection
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "teachgenie-final-snapshot"
  
  tags = {
    Name = "teachgenie-db-${var.environment}"
  }
}

# Outputs
output "db_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive = true
}

output "db_secret_arn" {
  value = aws_secretsmanager_secret.db_password.arn
}
```

### 4.2 Create ElastiCache Redis

Create file: `infrastructure/terraform/elasticache.tf`

```hcl
# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "teachgenie-cache-subnet-group"
  subnet_ids = aws_subnet.private_app[*].id
}

# ElastiCache Redis Cluster
resource "aws_elasticache_replication_group" "main" {
  replication_group_id = "teachgenie-redis"
  description          = "Redis cluster for TeachGenie caching"
  
  node_type            = "cache.t3.micro"  # Production: cache.r6g.large
  num_cache_clusters   = 2
  
  engine               = "redis"
  engine_version       = "7.0"
  port                 = 6379
  
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.elasticache.id]
  
  automatic_failover_enabled = true
  multi_az_enabled           = true
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  snapshot_retention_limit = 7
  snapshot_window          = "02:00-03:00"
  
  tags = {
    Name = "teachgenie-redis-${var.environment}"
  }
}

output "redis_endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}
```

---

## 5. Phase 3: Application Tier (ECS Fargate)

### 5.1 Create ECR Repository

Create file: `infrastructure/terraform/ecr.tf`

```hcl
# ECR Repository
resource "aws_ecr_repository" "backend" {
  name                 = "teachgenie-backend"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = "AES256"
  }
  
  tags = {
    Name = "teachgenie-backend-${var.environment}"
  }
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

output "ecr_repository_url" {
  value = aws_ecr_repository.backend.repository_url
}
```

### 5.2 Create Dockerfile

Create file: `backend/Dockerfile`

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 5.3 Create ECS Cluster and Service

Create file: `infrastructure/terraform/ecs.tf`

```hcl
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "teachgenie-cluster-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "teachgenie-cluster-${var.environment}"
  }
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name
  
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  
  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution" {
  name = "teachgenie-ecs-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for Secrets Manager
resource "aws_iam_role_policy" "ecs_secrets" {
  name = "teachgenie-ecs-secrets-policy"
  role = aws_iam_role.ecs_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.db_password.arn,
          aws_secretsmanager_secret.app_secrets.arn
        ]
      }
    ]
  })
}

# IAM Role for ECS Task
resource "aws_iam_role" "ecs_task" {
  name = "teachgenie-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Application Secrets
resource "aws_secretsmanager_secret" "app_secrets" {
  name = "teachgenie/app-secrets-${var.environment}"
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY       = var.secret_key
    OPENAI_API_KEY   = var.openai_api_key
    EMAIL_API_KEY    = var.email_api_key
    GOOGLE_CLIENT_ID = var.google_client_id
    GOOGLE_CLIENT_SECRET = var.google_client_secret
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/teachgenie-${var.environment}"
  retention_in_days = 30
}

# ECS Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "teachgenie-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024  # 1 vCPU
  memory                   = 2048  # 2 GB
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${aws_ecr_repository.backend.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        { name = "ENVIRONMENT", value = "production" },
        { name = "DEBUG", value = "false" },
        { name = "REDIS_URL", value = "redis://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379/0" },
        { name = "FRONTEND_URL", value = "https://${var.domain_name}" },
        { name = "GOOGLE_REDIRECT_URI", value = "https://api.${var.domain_name}/api/v1/auth/google/callback" }
      ]
      
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.db_password.arn}:connection_string::"
        },
        {
          name      = "SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:SECRET_KEY::"
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:OPENAI_API_KEY::"
        },
        {
          name      = "EMAIL_API_KEY"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:EMAIL_API_KEY::"
        },
        {
          name      = "GOOGLE_CLIENT_ID"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:GOOGLE_CLIENT_ID::"
        },
        {
          name      = "GOOGLE_CLIENT_SECRET"
          valueFrom = "${aws_secretsmanager_secret.app_secrets.arn}:GOOGLE_CLIENT_SECRET::"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
  
  tags = {
    Name = "teachgenie-backend-task-${var.environment}"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "teachgenie-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  
  enable_deletion_protection = true
  
  tags = {
    Name = "teachgenie-alb-${var.environment}"
  }
}

# ALB Target Group
resource "aws_lb_target_group" "backend" {
  name        = "teachgenie-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }
  
  tags = {
    Name = "teachgenie-backend-tg-${var.environment}"
  }
}

# ALB Listener (HTTPS)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.api.arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# ALB Listener (HTTP - Redirect to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ECS Service
resource "aws_ecs_service" "backend" {
  name            = "teachgenie-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.private_app[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
  
  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  
  tags = {
    Name = "teachgenie-backend-service-${var.environment}"
  }
  
  depends_on = [aws_lb_listener.https]
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "teachgenie-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}
```

---

## 6. Phase 4: Web Tier (CloudFront + S3)

### 6.1 S3 Bucket for Frontend

Create file: `infrastructure/terraform/s3.tf`

```hcl
# S3 Bucket for Frontend
resource "aws_s3_bucket" "frontend" {
  bucket = "teachgenie-frontend-${var.environment}"
  
  tags = {
    Name = "teachgenie-frontend-${var.environment}"
  }
}

# Block all public access (CloudFront will access via OAC)
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket for PDFs/PPTs
resource "aws_s3_bucket" "assets" {
  bucket = "teachgenie-assets-${var.environment}"
  
  tags = {
    Name = "teachgenie-assets-${var.environment}"
  }
}

resource "aws_s3_bucket_cors_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://${var.domain_name}"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3600
  }
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.id
}

output "assets_bucket_name" {
  value = aws_s3_bucket.assets.id
}
```

### 6.2 CloudFront Distribution

Create file: `infrastructure/terraform/cloudfront.tf`

```hcl
# CloudFront Origin Access Control
resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "teachgenie-frontend-oac"
  description                       = "OAC for TeachGenie frontend"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ACM Certificate for CloudFront (must be in us-east-1)
resource "aws_acm_certificate" "frontend" {
  provider          = aws.us_east_1
  domain_name       = var.domain_name
  subject_alternative_names = ["www.${var.domain_name}"]
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
}

# ACM Certificate for API (ALB)
resource "aws_acm_certificate" "api" {
  domain_name       = "api.${var.domain_name}"
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"
  aliases             = [var.domain_name, "www.${var.domain_name}"]
  price_class         = "PriceClass_100"  # US, Canada, Europe
  
  # Frontend Origin (S3)
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3-Frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id
  }
  
  # API Origin (ALB)
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-Backend"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  # Default behavior (Frontend)
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-Frontend"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }
  
  # API behavior
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-Backend"
    
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]
      cookies {
        forward = "all"
      }
    }
    
    viewer_protocol_policy = "https-only"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }
  
  # SPA fallback - serve index.html for all routes
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.frontend.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  # WAF
  web_acl_id = aws_wafv2_web_acl.main.arn
  
  tags = {
    Name = "teachgenie-cdn-${var.environment}"
  }
}

# S3 Bucket Policy for CloudFront
resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontOAC"
        Effect    = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = aws_cloudfront_distribution.main.arn
          }
        }
      }
    ]
  })
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.main.id
}

output "cloudfront_domain_name" {
  value = aws_cloudfront_distribution.main.domain_name
}
```

### 6.3 Route 53 DNS

Create file: `infrastructure/terraform/route53.tf`

```hcl
# Route 53 Hosted Zone (if not already exists)
data "aws_route53_zone" "main" {
  name = var.domain_name
}

# A Record for apex domain
resource "aws_route53_record" "apex" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# A Record for www
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "www.${var.domain_name}"
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.main.domain_name
    zone_id                = aws_cloudfront_distribution.main.hosted_zone_id
    evaluate_target_health = false
  }
}

# A Record for API subdomain
resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "api.${var.domain_name}"
  type    = "A"
  
  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

# ACM Validation Records
resource "aws_route53_record" "cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.frontend.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.main.zone_id
}
```

---

## 7. Phase 5: CI/CD Pipeline

### 7.1 GitHub Actions Workflow

Create file: `.github/workflows/deploy.yml`

```yaml
name: Deploy TeachGenie

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: teachgenie-backend
  ECS_CLUSTER: teachgenie-cluster-production
  ECS_SERVICE: teachgenie-backend-service
  S3_BUCKET: teachgenie-frontend-production
  CLOUDFRONT_DISTRIBUTION_ID: ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }}

jobs:
  # =========================
  # Backend Tests
  # =========================
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        working-directory: backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        working-directory: backend
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test
          SECRET_KEY: test-secret-key-minimum-32-characters-long
          ENVIRONMENT: test
        run: |
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: backend/coverage.xml

  # =========================
  # Frontend Tests
  # =========================
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Run tests
        working-directory: frontend
        run: npm test -- --coverage --watchAll=false
      
      - name: Build
        working-directory: frontend
        env:
          REACT_APP_API_URL: https://api.teachgenie.ai
        run: npm run build

  # =========================
  # Deploy Backend
  # =========================
  deploy-backend:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2
      
      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        working-directory: backend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:latest .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
      
      - name: Download task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition teachgenie-backend \
            --query taskDefinition > task-definition.json
      
      - name: Update ECS task definition
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: task-definition.json
          container-name: backend
          image: ${{ steps.build-image.outputs.image }}
      
      - name: Deploy to Amazon ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v1
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true

  # =========================
  # Deploy Frontend
  # =========================
  deploy-frontend:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Build
        working-directory: frontend
        env:
          REACT_APP_API_URL: https://api.teachgenie.ai
          GENERATE_SOURCEMAP: false
        run: npm run build
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy to S3
        working-directory: frontend
        run: |
          aws s3 sync build/ s3://$S3_BUCKET/ \
            --delete \
            --cache-control "max-age=31536000" \
            --exclude "index.html" \
            --exclude "service-worker.js"
          
          # Upload index.html with no-cache
          aws s3 cp build/index.html s3://$S3_BUCKET/index.html \
            --cache-control "no-cache, no-store, must-revalidate"
      
      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
            --paths "/*"
```

### 7.2 GitHub Secrets Required

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret Name | Description |
|------------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID |

---

## 8. Phase 6: Monitoring & Logging

### 8.1 CloudWatch Alarms

Create file: `infrastructure/terraform/monitoring.tf`

```hcl
# SNS Topic for Alerts
resource "aws_sns_topic" "alerts" {
  name = "teachgenie-alerts-${var.environment}"
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ECS CPU Alarm
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "teachgenie-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS CPU utilization is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.backend.name
  }
}

# ECS Memory Alarm
resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "teachgenie-ecs-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "ECS memory utilization is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.backend.name
  }
}

# RDS CPU Alarm
resource "aws_cloudwatch_metric_alarm" "rds_cpu_high" {
  alarm_name          = "teachgenie-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization is too high"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

# ALB 5XX Errors
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "teachgenie-alb-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "High number of 5XX errors"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "TeachGenie-${var.environment}"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "ECS CPU & Memory"
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.main.name, "ServiceName", aws_ecs_service.backend.name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title   = "ALB Request Count"
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.main.arn_suffix]
          ]
          period = 60
          stat   = "Sum"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "RDS Connections"
          metrics = [
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", aws_db_instance.main.id]
          ]
          period = 60
          stat   = "Average"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "ElastiCache Hits/Misses"
          metrics = [
            ["AWS/ElastiCache", "CacheHits", "CacheClusterId", "${aws_elasticache_replication_group.main.id}-001"],
            [".", "CacheMisses", ".", "."]
          ]
          period = 60
          stat   = "Sum"
          region = var.aws_region
        }
      }
    ]
  })
}
```

---

## 9. Phase 7: Security Hardening

### 9.1 WAF Configuration

Create file: `infrastructure/terraform/waf.tf`

```hcl
# WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
  name        = "teachgenie-waf-${var.environment}"
  description = "WAF for TeachGenie"
  scope       = "CLOUDFRONT"
  provider    = aws.us_east_1  # WAF for CloudFront must be in us-east-1
  
  default_action {
    allow {}
  }
  
  # AWS Managed Rules - Common Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }
  
  # AWS Managed Rules - Known Bad Inputs
  rule {
    name     = "AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesKnownBadInputsRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }
  
  # Rate Limiting
  rule {
    name     = "RateLimitRule"
    priority = 3
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRuleMetric"
      sampled_requests_enabled   = true
    }
  }
  
  # SQL Injection Protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 4
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }
  
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "teachgenie-waf"
    sampled_requests_enabled   = true
  }
  
  tags = {
    Name = "teachgenie-waf-${var.environment}"
  }
}
```

### 9.2 IAM Best Practices

Create file: `infrastructure/terraform/iam.tf`

```hcl
# CI/CD IAM User
resource "aws_iam_user" "cicd" {
  name = "teachgenie-cicd"
  
  tags = {
    Purpose = "GitHub Actions CI/CD"
  }
}

resource "aws_iam_user_policy" "cicd" {
  name = "teachgenie-cicd-policy"
  user = aws_iam_user.cicd.name
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.frontend.arn,
          "${aws_s3_bucket.frontend.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudfront:CreateInvalidation"
        ]
        Resource = aws_cloudfront_distribution.main.arn
      },
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          aws_iam_role.ecs_execution.arn,
          aws_iam_role.ecs_task.arn
        ]
      }
    ]
  })
}
```

---

## 10. Cost Estimation

### Monthly Cost Breakdown (Estimated)

| Service | Configuration | Est. Monthly Cost |
|---------|--------------|-------------------|
| **ECS Fargate** | 2 tasks × 1 vCPU, 2GB RAM | ~$60 |
| **RDS PostgreSQL** | db.t3.medium, Multi-AZ, 100GB | ~$130 |
| **ElastiCache Redis** | cache.t3.micro × 2 | ~$25 |
| **Application Load Balancer** | 1 ALB | ~$20 |
| **NAT Gateway** | 2 × NAT Gateway + data transfer | ~$70 |
| **CloudFront** | 100GB transfer/month | ~$10 |
| **S3** | 10GB storage | ~$1 |
| **Route 53** | 1 hosted zone | ~$0.50 |
| **Secrets Manager** | 2 secrets | ~$1 |
| **CloudWatch** | Logs & metrics | ~$10 |
| **WAF** | Web ACL + rules | ~$10 |
| **Data Transfer** | ~50GB/month | ~$5 |
| | | |
| **Total Estimated** | | **~$340-400/month** |

### Cost Optimization Tips

1. **Use Reserved Instances** for RDS (save 30-40%)
2. **Use Savings Plans** for Fargate (save 20%)
3. **Single NAT Gateway** for non-prod (save $35/month)
4. **Smaller RDS instance** initially (db.t3.small = ~$65/month)
5. **Spot instances** for non-critical workloads

---

## 11. Deployment Checklist

### Pre-Deployment

- [ ] AWS Account created and configured
- [ ] Domain registered and DNS configured
- [ ] SSL certificates validated
- [ ] All secrets stored in Secrets Manager
- [ ] GitHub repository with Actions enabled
- [ ] GitHub Secrets configured

### Infrastructure Deployment

```bash
# 1. Create S3 bucket for Terraform state
aws s3 mb s3://teachgenie-terraform-state --region us-east-1

# 2. Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# 3. Initialize and apply Terraform
cd infrastructure/terraform
terraform init
terraform plan -var-file=production.tfvars -out=tfplan
terraform apply tfplan
```

### Application Deployment

```bash
# 1. Build and push Docker image
cd backend
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t teachgenie-backend .
docker tag teachgenie-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/teachgenie-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/teachgenie-backend:latest

# 2. Build and deploy frontend
cd frontend
REACT_APP_API_URL=https://api.teachgenie.ai npm run build
aws s3 sync build/ s3://teachgenie-frontend-production/ --delete
aws cloudfront create-invalidation --distribution-id <dist-id> --paths "/*"
```

### Post-Deployment Verification

- [ ] Health check: `curl https://api.teachgenie.ai/health`
- [ ] Frontend loads: `https://teachgenie.ai`
- [ ] User registration works
- [ ] Email verification works
- [ ] Google OAuth works
- [ ] Lesson generation works
- [ ] CloudWatch logs flowing
- [ ] Alarms configured and tested

### Rollback Plan

```bash
# Rollback ECS to previous task definition
aws ecs update-service \
  --cluster teachgenie-cluster-production \
  --service teachgenie-backend-service \
  --task-definition teachgenie-backend:<previous-revision>

# Rollback frontend
aws s3 sync s3://teachgenie-frontend-backup/ s3://teachgenie-frontend-production/
aws cloudfront create-invalidation --distribution-id <dist-id> --paths "/*"
```

---

## Quick Start Commands

```bash
# Clone infrastructure
git clone https://github.com/your-org/teachgenie-infrastructure.git
cd teachgenie-infrastructure

# Set up variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Deploy everything
terraform init
terraform apply -auto-approve

# First deployment
cd ../backend && docker build -t teachgenie-backend . && docker push ...
cd ../frontend && npm run build && aws s3 sync build/ s3://...
```

---

## Support & Troubleshooting

### Common Issues

1. **ECS tasks failing to start**: Check CloudWatch logs for container errors
2. **Database connection issues**: Verify security group rules and secrets
3. **SSL certificate pending**: Ensure DNS validation records are created
4. **502 errors**: Check ALB target group health checks

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster teachgenie-cluster-production --services teachgenie-backend-service

# View ECS logs
aws logs tail /ecs/teachgenie-production --follow

# Check RDS status
aws rds describe-db-instances --db-instance-identifier teachgenie-db-production

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
```

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Author**: TeachGenie DevOps Team
