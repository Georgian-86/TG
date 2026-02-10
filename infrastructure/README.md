# TeachGenie Infrastructure

This directory contains Terraform configurations for deploying TeachGenie to AWS.

## Prerequisites

1. **AWS CLI v2** configured with appropriate credentials
2. **Terraform** >= 1.5.0
3. **Domain** registered in Route 53 or with DNS pointing to Route 53

## Directory Structure

```
infrastructure/
└── terraform/
    ├── variables.tf           # Variable definitions
    ├── production.tfvars.example  # Example production variables
    ├── vpc.tf                 # VPC, subnets, NAT gateways (copy from guide)
    ├── security_groups.tf     # Security group definitions (copy from guide)
    ├── rds.tf                 # RDS PostgreSQL (copy from guide)
    ├── elasticache.tf         # Redis cache (copy from guide)
    ├── ecr.tf                 # Container registry (copy from guide)
    ├── ecs.tf                 # ECS Fargate cluster and service (copy from guide)
    ├── s3.tf                  # S3 buckets (copy from guide)
    ├── cloudfront.tf          # CDN configuration (copy from guide)
    ├── route53.tf             # DNS records (copy from guide)
    ├── waf.tf                 # Web Application Firewall (copy from guide)
    ├── monitoring.tf          # CloudWatch alarms and dashboard (copy from guide)
    └── iam.tf                 # IAM roles and policies (copy from guide)
```

## Quick Start

### 1. Create State Backend

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://teachgenie-terraform-state --region us-east-1

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### 2. Configure Variables

```bash
cp production.tfvars.example production.tfvars
# Edit production.tfvars with your values
```

### 3. Set Sensitive Variables

```bash
# Option 1: Environment variables
export TF_VAR_secret_key="your-secret-key-min-32-chars"
export TF_VAR_openai_api_key="sk-..."
export TF_VAR_email_api_key="re_..."
export TF_VAR_google_client_id="..."
export TF_VAR_google_client_secret="..."

# Option 2: Prompt during apply
terraform apply -var-file=production.tfvars
```

### 4. Deploy

```bash
terraform init
terraform plan -var-file=production.tfvars -out=tfplan
terraform apply tfplan
```

## Terraform Configurations

Copy the Terraform configurations from `AWS_DEPLOYMENT_GUIDE.md` in the project root:

- **Phase 3**: VPC (`vpc.tf`), Security Groups (`security_groups.tf`)
- **Phase 4**: RDS (`rds.tf`), ElastiCache (`elasticache.tf`)
- **Phase 5**: ECR (`ecr.tf`), ECS (`ecs.tf`)
- **Phase 6**: S3 (`s3.tf`), CloudFront (`cloudfront.tf`), Route53 (`route53.tf`)
- **Phase 8**: Monitoring (`monitoring.tf`)
- **Phase 9**: WAF (`waf.tf`), IAM (`iam.tf`)

## Outputs

After successful deployment, Terraform outputs:

- `vpc_id` - VPC identifier
- `ecr_repository_url` - Docker image registry URL
- `alb_dns_name` - Application Load Balancer DNS
- `cloudfront_domain_name` - CDN domain
- `db_endpoint` - RDS endpoint (sensitive)
- `redis_endpoint` - ElastiCache endpoint

## Cost Estimation

See `AWS_DEPLOYMENT_GUIDE.md` for detailed cost breakdown (~$340-400/month).

## Destroy

```bash
# WARNING: This will destroy all resources!
terraform destroy -var-file=production.tfvars
```

## Support

See the main `AWS_DEPLOYMENT_GUIDE.md` for troubleshooting and detailed instructions.
