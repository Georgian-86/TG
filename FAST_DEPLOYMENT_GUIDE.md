# TeachGenie - Fast AWS Deployment Guide
## 3-Tier Architecture (No Terraform Required)

**Time to Deploy: ~30-45 minutes**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                    ┌───────────────────┐
│   AWS Amplify     │                    │   App Runner      │
│   (Frontend)      │◄───────────────────│   (Backend API)   │
│   React App       │     API Calls      │   FastAPI         │
└───────────────────┘                    └───────────────────┘
                                                   │
                                                   ▼
                                         ┌───────────────────┐
                                         │   RDS PostgreSQL  │
                                         │   (Database)      │
                                         └───────────────────┘
```

| Tier | AWS Service | Why This? |
|------|-------------|-----------|
| **Web** | AWS Amplify | Auto CI/CD from GitHub, free SSL, CDN |
| **Application** | AWS App Runner | Zero config containers, auto-scaling |
| **Database** | RDS PostgreSQL | Managed, backups, Multi-AZ option |

---

## Prerequisites

1. AWS Account with billing enabled
2. GitHub repository with your code
3. AWS CLI installed (optional but helpful)

---

## Step 1: Database (RDS PostgreSQL) - 10 mins

### 1.1 Create RDS Instance

1. Go to **AWS Console → RDS → Create database**

2. Configure:
   ```
   Engine: PostgreSQL
   Version: 15.x
   Template: Free tier (or Production for real deployment)
   
   DB instance identifier: teachgenie-db
   Master username: teachgenie_admin
   Master password: [Generate a strong password - SAVE THIS!]
   
   Instance class: db.t3.micro (free tier) or db.t3.small (production)
   Storage: 20 GB gp3
   
   Connectivity:
   - VPC: Default VPC
   - Public access: Yes (for initial setup, change to No later)
   - Security group: Create new → "teachgenie-db-sg"
   
   Database name: teachgenie
   ```

3. Click **Create database** (takes ~5 minutes)

### 1.2 Configure Security Group

1. Go to **EC2 → Security Groups → teachgenie-db-sg**
2. Edit **Inbound rules**:
   ```
   Type: PostgreSQL
   Port: 5432
   Source: 0.0.0.0/0 (temporary - restrict after App Runner setup)
   ```

### 1.3 Get Connection String

Once RDS is available, note the **Endpoint**:
```
teachgenie-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com
```

Your DATABASE_URL:
```
postgresql+asyncpg://teachgenie_admin:YOUR_PASSWORD@teachgenie-db.xxxxxxxxxxxx.us-east-1.rds.amazonaws.com:5432/teachgenie
```

---

## Step 2: Backend (AWS App Runner) - 10 mins

### 2.1 Push Dockerfile to GitHub

Ensure your `backend/Dockerfile` exists (already created earlier).

### 2.2 Create App Runner Service

1. Go to **AWS Console → App Runner → Create service**

2. **Source**:
   ```
   Repository type: Source code repository
   Connect to GitHub (authorize AWS)
   Repository: your-github-username/Teach-Genie
   Branch: main
   Source directory: /backend
   ```

3. **Build settings**:
   ```
   Configuration file: Configure all settings here
   Runtime: Python 3
   Build command: pip install -r requirements.txt
   Start command: uvicorn app.main:app --host 0.0.0.0 --port 8000
   Port: 8000
   ```

   **OR use Dockerfile** (recommended):
   ```
   Configuration file: Configure all settings here
   Runtime: Docker
   (App Runner will auto-detect the Dockerfile)
   ```

4. **Service settings**:
   ```
   Service name: teachgenie-api
   CPU: 1 vCPU
   Memory: 2 GB
   
   Environment variables:
   - ENVIRONMENT = production
   - DEBUG = false
   - DATABASE_URL = [your RDS connection string]
   - SECRET_KEY = [generate: openssl rand -hex 32]
   - OPENAI_API_KEY = sk-your-key
   - EMAIL_API_KEY = re_your-resend-key
   - EMAIL_FROM = info@teachgenie.ai
   - FRONTEND_URL = https://main.xxxx.amplifyapp.com (update after Amplify setup)
   - GOOGLE_CLIENT_ID = your-google-client-id
   - GOOGLE_CLIENT_SECRET = your-google-client-secret
   - GOOGLE_REDIRECT_URI = https://xxxx.us-east-1.awsapprunner.com/api/v1/auth/google/callback
   ```

5. **Auto scaling**:
   ```
   Min instances: 1
   Max instances: 5
   Max concurrency: 100
   ```

6. Click **Create & deploy**

### 2.3 Get API URL

Once deployed, note your App Runner URL:
```
https://xxxxxxxx.us-east-1.awsapprunner.com
```

Test it:
```bash
curl https://xxxxxxxx.us-east-1.awsapprunner.com/health
```

---

## Step 3: Frontend (AWS Amplify) - 10 mins

### 3.1 Create Amplify App

1. Go to **AWS Console → Amplify → Create new app**

2. **Host web app**:
   ```
   Connect to GitHub
   Repository: your-github-username/Teach-Genie
   Branch: main
   ```

3. **Build settings**:
   ```yaml
   # Auto-detected or paste this:
   version: 1
   applications:
     - frontend:
         phases:
           preBuild:
             commands:
               - npm ci
           build:
             commands:
               - npm run build
         artifacts:
           baseDirectory: build
           files:
             - '**/*'
         cache:
           paths:
             - node_modules/**/*
       appRoot: frontend
   ```

4. **Environment variables**:
   ```
   REACT_APP_API_URL = https://xxxxxxxx.us-east-1.awsapprunner.com
   ```

5. Click **Save and deploy**

### 3.2 Get Frontend URL

Your Amplify URL:
```
https://main.xxxxxxxxxx.amplifyapp.com
```

---

## Step 4: Connect Everything - 5 mins

### 4.1 Update App Runner Environment Variables

Go back to **App Runner → teachgenie-api → Configuration → Environment variables**:

Update:
```
FRONTEND_URL = https://main.xxxxxxxxxx.amplifyapp.com
GOOGLE_REDIRECT_URI = https://xxxxxxxx.us-east-1.awsapprunner.com/api/v1/auth/google/callback
```

Click **Apply changes** (triggers new deployment).

### 4.2 Update Google OAuth Console

1. Go to **Google Cloud Console → APIs & Services → Credentials**
2. Edit your OAuth 2.0 Client
3. Add **Authorized redirect URIs**:
   ```
   https://xxxxxxxx.us-east-1.awsapprunner.com/api/v1/auth/google/callback
   ```
4. Add **Authorized JavaScript origins**:
   ```
   https://main.xxxxxxxxxx.amplifyapp.com
   ```

### 4.3 Restrict RDS Security Group

1. Go to **EC2 → Security Groups → teachgenie-db-sg**
2. Edit **Inbound rules**:
   - Remove `0.0.0.0/0`
   - Add App Runner VPC connector IP range (or keep open if using public access)

---

## Step 5: Custom Domain (Optional) - 10 mins

### 5.1 Frontend Domain (Amplify)

1. **Amplify → Your app → Domain management → Add domain**
2. Enter: `teachgenie.ai`
3. Amplify will provide DNS records
4. Add these to your DNS provider (Route 53, Cloudflare, etc.)

### 5.2 Backend Domain (App Runner)

1. **App Runner → teachgenie-api → Custom domains → Link domain**
2. Enter: `api.teachgenie.ai`
3. Add the provided CNAME records to your DNS

---

## Verification Checklist

```bash
# Test backend health
curl https://api.teachgenie.ai/health

# Test frontend
open https://teachgenie.ai
```

- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Frontend loads without errors
- [ ] User registration works
- [ ] Email verification works
- [ ] Google login works
- [ ] Lesson generation works

---

## Cost Breakdown (Monthly)

| Service | Configuration | Cost |
|---------|---------------|------|
| **RDS** | db.t3.micro (free tier) | $0 first year, then ~$15 |
| **App Runner** | 1 vCPU, 2GB, min 1 instance | ~$30-50 |
| **Amplify** | Build + Hosting | ~$5-10 |
| **Data Transfer** | ~50 GB | ~$5 |
| **Total** | | **~$40-70/month** |

---

## Quick Deploy Commands (Alternative CLI Method)

```bash
# 1. Create RDS
aws rds create-db-instance \
  --db-instance-identifier teachgenie-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username teachgenie_admin \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --db-name teachgenie \
  --publicly-accessible

# 2. Create App Runner (after pushing to GitHub)
aws apprunner create-service \
  --service-name teachgenie-api \
  --source-configuration '{
    "CodeRepository": {
      "RepositoryUrl": "https://github.com/YOUR_USERNAME/Teach-Genie",
      "SourceCodeVersion": {"Type": "BRANCH", "Value": "main"},
      "SourceDirectory": "/backend",
      "CodeConfiguration": {
        "ConfigurationSource": "API",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "uvicorn app.main:app --host 0.0.0.0 --port 8000",
          "Port": "8000"
        }
      }
    }
  }'

# 3. Amplify (use console - easier for first setup)
```

---

## Troubleshooting

### App Runner deployment fails
- Check build logs in App Runner console
- Verify Dockerfile syntax
- Ensure all environment variables are set

### Database connection refused
- Check RDS security group allows inbound 5432
- Verify DATABASE_URL format
- Check RDS is in "Available" state

### Frontend not loading API
- Check REACT_APP_API_URL is correct
- Check browser console for CORS errors
- Verify App Runner FRONTEND_URL matches Amplify URL

### Google OAuth not working
- Verify redirect URI exactly matches (including https://)
- Check GOOGLE_REDIRECT_URI in App Runner matches Google Console

---

## Next Steps

1. **Add Redis** (ElastiCache) for caching - improves performance
2. **Enable Multi-AZ** for RDS - improves reliability
3. **Set up CloudWatch alarms** - get notified of issues
4. **Add WAF** via CloudFront - security protection

---

**Total Deployment Time: ~30-45 minutes**  
**Monthly Cost: ~$40-70**
