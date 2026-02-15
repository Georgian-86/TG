# Pricing Package Update - Complete Guide

## 🎯 Overview

The pricing packages have been updated with new tier names, features, and quotas to better reflect TeachGenie's value proposition.

---

## 📦 New Pricing Structure

### 🟢 Free Plan – Starter for Individual Teachers
**Best for trying TeachGenie**

**Price:** $0 forever

**Features:**
- 10 content generations/month
- PDF download only
- Key Learning Objectives
- Structured Content
- Key Takeaways
- RBT (Revised Bloom's Taxonomy) Mapping
- Standard quality generation

**Perfect for:** Teachers exploring AI-assisted teaching for the first time.

---

### 🥈 Silver Plan – For Active Teachers
**Best for regular classroom usage**

**Price:** $10/month or $100/year (17% savings)

**Features:**
- Everything in Free +
- 20 generations/month
- PPT + PDF downloads
- Scenario-based quizzes
- Key takeaways & structured notes
- RBT mapping
- Faster generation speed
- Better content depth

**Perfect for:** Teachers who create lessons & presentations weekly.

---

### 🥇 Gold Plan – Power Teachers & Content Creators
**Best for advanced teaching & premium content**

**Price:** $25/month or $250/year (17% savings)

**Features:**
- Everything in Silver +
- 50 generations/month
- Premium graphics & visual slides
- Enhanced PPT designs
- Advanced scenario-based quizzes
- Smart structured explanations
- Priority generation speed
- High-depth academic content

**Perfect for:** Educators, trainers, coaching institutes, content creators.

---

### 🏫 Institutional Plan – For Schools, Colleges & Universities
**Custom pricing | Fully customizable**

**Price:** Custom pricing based on institution needs

**Core Features:**
- Unlimited or bulk generations
- Multi-teacher access (dashboard for all faculty)
- Admin control panel
- Custom templates for institution

**Advanced Academic Mapping:**
- RBT Mapping
- IKS Mapping (Indian Knowledge System)
- LO-PO Mapping (Learning Outcome – Program Outcome)
- Level-based cognitive load control

**Customization Options:**
- Institution branding on PPT/PDF
- Custom lesson formats
- Department-wise access
- Training & onboarding support
- Dedicated support

**Perfect for:** Schools • Colleges • Universities • Coaching Institutes • EdTech organizations

---

## 🔄 Migration from Old Tiers

### Old → New Mapping

| Old Tier | New Tier | Monthly Quota |
|----------|----------|---------------|
| Free | Free | 10 |
| Basic | Silver | 20 |
| Pro | Gold | 50 |
| Enterprise | Institutional | Unlimited |

---

## 📝 Files Modified

### Frontend Changes

#### 1. **PricingPage.js** (`frontend/src/pages/PricingPage.js`)
- Updated tier names, emojis, and badges
- Added new features for each plan
- Added subtitle and "Perfect for" sections
- Enhanced institutional plan styling with purple gradient
- Updated pricing ($25/month for Gold)

### Backend Changes

#### 2. **User Model** (`backend/app/models/user.py`)
- Updated `SubscriptionTier` enum:
  ```python
  class SubscriptionTier(str, enum.Enum):
      FREE = "free"
      SILVER = "silver"           # was BASIC
      GOLD = "gold"               # was PRO
      INSTITUTIONAL = "institutional"  # was ENTERPRISE
  ```

- Updated `lessons_quota` property:
  ```python
  quotas = {
      SubscriptionTier.FREE: 10,
      SubscriptionTier.SILVER: 20,
      SubscriptionTier.GOLD: 50,
      SubscriptionTier.INSTITUTIONAL: 999999
  }
  ```

#### 3. **Config Settings** (`backend/app/config.py`)
- Updated quota constants:
  ```python
  FREE_TIER_LESSONS_PER_MONTH: int = 10
  SILVER_TIER_LESSONS_PER_MONTH: int = 20
  GOLD_TIER_LESSONS_PER_MONTH: int = 50
  INSTITUTIONAL_TIER_LESSONS_PER_MONTH: int = 999999
  ```

#### 4. **Migration Script** (`backend/migrate_subscription_tiers.py`)
- New script to migrate existing users from old tier names to new ones
- Automatically updates database records

---

## 🚀 Deployment Steps

### Step 1: Backup Database
```bash
# Create a backup before migration
python backend/export_database_backup.py
```

### Step 2: Run Migration Script
```bash
cd backend
python migrate_subscription_tiers.py
```

This will:
- Update all users with `basic` → `silver`
- Update all users with `pro` → `gold`
- Update all users with `enterprise` → `institutional`
- Show before/after tier distribution

### Step 3: Deploy Frontend Changes
```bash
cd frontend
npm run build
# Deploy to your hosting platform (Amplify, Vercel, etc.)
```

### Step 4: Restart Backend Service
```bash
# If using Railway or similar
git push origin main

# If using local server
cd backend
python -m app.main
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Pricing page displays all 4 tiers correctly
- [ ] Free plan shows 10 generations/month
- [ ] Silver plan shows 20 generations/month  
- [ ] Gold plan shows 50 generations/month
- [ ] Institutional plan shows "Custom pricing"
- [ ] Existing users can still access the system
- [ ] User quotas are enforced correctly
- [ ] Migration script completed without errors

---

## 🔍 Testing

### Test User Quotas
```python
# Test in Python console
from app.models import User, SubscriptionTier

# Check quota mapping
user = User(subscription_tier=SubscriptionTier.FREE)
print(user.lessons_quota)  # Should print: 10

user.subscription_tier = SubscriptionTier.SILVER
print(user.lessons_quota)  # Should print: 20

user.subscription_tier = SubscriptionTier.GOLD
print(user.lessons_quota)  # Should print: 50

user.subscription_tier = SubscriptionTier.INSTITUTIONAL
print(user.lessons_quota)  # Should print: 999999
```

### Test Frontend Display
1. Navigate to `/pricing` page
2. Verify all 4 plans are visible
3. Check monthly/yearly toggle works
4. Verify feature lists are complete
5. Test "Perfect for" sections display properly

---

## 📊 Database Schema

No schema changes required! The `subscription_tier` column remains a string enum, just with new accepted values.

**Existing schema:**
```sql
subscription_tier VARCHAR(50) DEFAULT 'free'
```

This is compatible with the new tier names.

---

## 🛠️ Rollback Plan

If you need to rollback:

1. **Restore database backup:**
   ```bash
   # Restore from backup
   psql $DATABASE_URL < backup.sql
   ```

2. **Revert code changes:**
   ```bash
   git revert HEAD
   git push origin main
   ```

---

## 💡 Notes

- **No breaking changes:** The API endpoints remain the same
- **Backward compatible:** Old tier names in database will be migrated
- **Frontend independent:** Backend changes don't affect frontend beyond tier names
- **Quota enforcement:** Automatically handled by `lessons_quota` property

---

## 📞 Support

If you encounter any issues:
1. Check migration script logs
2. Verify database connection
3. Check user tier distribution in database
4. Review API logs for quota enforcement

---

## 📅 Completed

✅ Frontend pricing page updated  
✅ Backend subscription tiers updated  
✅ User model quota mapping updated  
✅ Configuration constants updated  
✅ Migration script created  
✅ Documentation completed

---

**Last Updated:** February 15, 2026  
**Version:** 2.0.0
