# Teach-Genie: Comprehensive Project Analysis

## 📋 Executive Summary

**Teach-Genie** is a full-stack AI-powered educational platform that generates comprehensive teaching materials including lesson plans, presentations, quizzes, and study resources. The application uses a multi-agent AI architecture to create pedagogically sound content tailored to different learning levels.

**Tech Stack:**
- **Backend:** FastAPI (Python) with async/await architecture
- **Frontend:** React 18 with React Router
- **Database:** PostgreSQL (Supabase) with SQLAlchemy ORM
- **AI:** OpenAI GPT-4o-mini
- **Authentication:** JWT + OAuth (Google) + Email OTP
- **Caching:** Redis (with memory fallback)
- **Storage:** Cloudflare R2 (S3-compatible)

---

## 🏗️ Architecture Overview

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Frontend - React SPA"
        UI[React Application]
        Pages[Pages: Home, Generator, Settings]
        Components[Reusable Components]
        Context[Context: Auth, Theme]
    end
    
    subgraph "Backend - FastAPI"
        API[FastAPI Application]
        Auth[Auth Routes]
        Lessons[Lesson Routes]
        Profile[Profile Routes]
    end
    
    subgraph "AI Agent System"
        Orchestrator[Agent Orchestrator]
        Planner[Planner Agent]
        Content[Content Agent]
        Quiz[Quiz Agent]
        KeyTakeaways[Key Takeaways Agent]
        Presentation[Presentation Agent]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL/Supabase)]
        Cache[(Redis Cache)]
        Storage[Cloudflare R2]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        Email[Email Service - Resend]
        OAuth[Google OAuth]
    end
    
    UI --> API
    API --> Auth
    API --> Lessons
    API --> Profile
    
    Lessons --> Orchestrator
    Orchestrator --> Planner
    Orchestrator --> Content
    Orchestrator --> Quiz
    Orchestrator --> KeyTakeaways
    Orchestrator --> Presentation
    
    Content --> OpenAI
    Quiz --> OpenAI
    KeyTakeaways --> OpenAI
    
    API --> DB
    API --> Cache
    Presentation --> Storage
    
    Auth --> Email
    Auth --> OAuth
```

---

## 🔐 Authentication & Security

### Authentication System

The application implements a **multi-layered authentication system**:

#### 1. **JWT Token-Based Authentication**
- **Access Tokens:** Short-lived (30 minutes) for API requests
- **Refresh Tokens:** Long-lived (7 days) for seamless re-authentication
- **Algorithm:** HS256 with secure secret key
- **Token Payload:** User ID, expiration, issued at, token type

#### 2. **OAuth Integration (Google)**
- Google Sign-In using `@react-oauth/google`
- Backend OAuth flow with Authlib
- Automatic user creation/login
- Profile completion workflow for OAuth users

#### 3. **Email Verification (OTP)**
- 6-digit OTP codes sent via Resend email service
- Bcrypt-hashed OTP storage
- 10-minute expiration
- Rate limiting: 3 emails per hour per address
- Max 5 verification attempts per OTP

#### 4. **Security Features**
- **Password Security:** Bcrypt hashing with salt
- **Rate Limiting:** SlowAPI middleware
  - Registration: 5 per hour per IP
  - Login: 10 per 5 minutes per IP
  - Email verification: 3 per hour per email
- **CORS:** Configurable origins (currently open for development)
- **Session Middleware:** Required for OAuth flows
- **Admin Logging:** All auth events logged to database

### User Model

```python
class User:
    # Identity
    id: UUID (String(36))
    email: String(255) - unique, indexed
    password_hash: String(255)
    
    # Status
    is_active: Boolean
    email_verified: Boolean
    profile_completed: Boolean
    
    # Profile
    full_name: String(255)
    organization: String(255)
    country: String(100)
    phone_number: String(20)
    profile_picture_url: String(500)
    bio: String(500)
    job_title: String(100)
    department: String(100)
    
    # Subscription
    subscription_tier: Enum (free, basic, pro, enterprise)
    stripe_customer_id: String(255)
    stripe_subscription_id: String(255)
    
    # OAuth
    oauth_provider: String(50)
    oauth_id: String(255)
    
    # Authorization
    role: Enum (user, admin, super_admin)
    
    # Usage Tracking
    lessons_this_month: Integer
    last_reset_date: DateTime
    
    # Timestamps
    created_at, updated_at, last_login_at: DateTime
```

### Subscription Tiers & Quotas

| Tier | Monthly Lessons | Features |
|------|----------------|----------|
| **Free** | 5 | Basic lesson generation |
| **Basic** | 50 | All features |
| **Pro** | Unlimited | Priority support |
| **Enterprise** | Unlimited | API access, custom branding |

---

## 🤖 AI Agent Architecture

### Agent Orchestrator

The `AgentOrchestrator` coordinates a sequential pipeline of specialized agents:

```python
async def generate_full_lesson(topic, level, duration, include_quiz):
    # 1. Planning Phase
    plan = await planner.run(topic, level, duration)
    
    # 2. Content Generation (Parallel)
    sections, resources = await asyncio.gather(
        content_gen.run_parallel(topic, level, plan['sections']),
        content_gen.find_resources(topic, level)
    )
    
    # 3. Key Takeaways
    key_takeaways = await key_takeaways_gen.run(topic, level, plan['objectives'], sections)
    
    # 4. Quiz (Optional)
    if include_quiz:
        quiz = await quiz_gen.run(topic, level, quiz_duration, quiz_marks)
    
    # 5. Presentations (PPT + PDF)
    presentation_files = await presentation_gen.run(topic, level, duration, sections, key_takeaways)
    
    return lesson_data
```

### Individual Agents

#### 1. **Planner Agent**
- **Purpose:** Academic structuring and curriculum alignment
- **Output:** Lesson title, learning objectives, section structure
- **Logic:** Rule-based planning (no LLM)

#### 2. **Content Agent**
- **Purpose:** Generate detailed lesson content
- **LLM Model:** GPT-4o-mini
- **Temperature:** 0.2 (focused, consistent)
- **Output:** 
  - 4-6 learning objectives
  - 5 detailed sections (120-150 words each)
  - 5 curated web resources
- **Sections:** Introduction, Core Concepts, Worked Examples, Applications, Summary

#### 3. **Key Takeaways Agent**
- **Purpose:** Distill essential learning points
- **LLM Model:** GPT-4o-mini
- **Temperature:** 0.4
- **Output:** 5 concise key takeaways

#### 4. **Quiz Agent**
- **Purpose:** Gamified, scenario-based assessment
- **LLM Model:** GPT-4o-mini
- **Temperature:** 0.5 (creative scenarios)
- **Adaptive Question Count:**
  - ≤5 min → 2 scenarios
  - ≤10 min → 3 scenarios
  - ≤15 min → 4 scenarios
  - >15 min → 5 scenarios
- **Question Format:** Scenario, question, 4 options, correct answer, explanation
- **Answer Diversity:** Ensures correct answers vary (A, B, C, D)

#### 5. **Presentation Agent**
- **Purpose:** Generate classroom-ready materials
- **Output:**
  - PowerPoint (.pptx) with `python-pptx`
  - PDF notes with `fpdf`
- **Features:**
  - Professional formatting
  - Mascot branding
  - Unicode-safe text (DejaVu fonts)
  - Max 6 bullets per slide

---

## 🗄️ Database Schema

### Core Tables

#### **users**
Primary user authentication and profile table (detailed above)

#### **lessons**
```sql
CREATE TABLE lessons (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    topic VARCHAR(255),
    level VARCHAR(50),
    duration_minutes INTEGER,
    include_quiz BOOLEAN,
    
    -- Generated Content (JSONB)
    lesson_data JSONB,
    
    -- File References
    ppt_url VARCHAR(500),
    pdf_url VARCHAR(500),
    
    -- Status
    status VARCHAR(50), -- pending, processing, completed, failed
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### **email_otps**
```sql
CREATE TABLE email_otps (
    id UUID PRIMARY KEY,
    email VARCHAR(255),
    otp_hash VARCHAR(255),
    attempts INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP,
    created_at TIMESTAMP
);
```

#### **admin_logs**
```sql
CREATE TABLE admin_logs (
    id UUID PRIMARY KEY,
    event_name VARCHAR(100),
    level VARCHAR(20), -- info, warning, error
    category VARCHAR(50), -- authentication, lesson_generation, etc.
    user_email VARCHAR(255),
    ip_address VARCHAR(45),
    status_code INTEGER,
    details JSONB,
    created_at TIMESTAMP
);
```

#### **lesson_history**
```sql
CREATE TABLE lesson_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    lesson_id UUID REFERENCES lessons(id),
    action VARCHAR(50), -- created, viewed, downloaded
    created_at TIMESTAMP
);
```

---

## 🌐 API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/register` | Create new user account | No |
| POST | `/login` | Login with email/password | No |
| POST | `/refresh` | Refresh access token | No |
| GET | `/me` | Get current user profile | Yes |
| PUT | `/me` | Update user profile | Yes |
| POST | `/change-password` | Change password | Yes |
| GET | `/google/login` | Initiate Google OAuth | No |
| GET | `/google/callback` | Google OAuth callback | No |
| POST | `/complete-profile` | Complete OAuth profile | Yes |
| POST | `/send-verification` | Send OTP email | No |
| POST | `/verify-email` | Verify OTP code | No |
| POST | `/resend-verification` | Resend OTP | No |

### Lessons (`/api/v1/lessons`)

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/generate` | Generate new lesson (sync) | Yes |
| GET | `/{lesson_id}` | Get lesson details | Yes |
| GET | `/history` | Get user's lesson history | Yes |

### Profile (`/api/v1/users`)

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/me` | Get current user | Yes |
| PUT | `/me` | Update profile | Yes |

### Debug (`/api/v1/debug`)

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/users` | List all users (admin) | Yes |
| GET | `/logs` | View admin logs | Yes |

---

## 💾 Caching Strategy

### Lesson Cache

**Purpose:** Avoid regenerating identical lessons

**Implementation:**
```python
# Memory-based cache (upgradeable to Redis)
cache_key = f"lesson:{topic}:{level}:{duration}:{include_quiz}"

# Check cache before generation
cached_lesson = cache.get(cache_key)
if cached_lesson:
    return cached_lesson

# Generate and cache
lesson = await orchestrator.generate_full_lesson(...)
cache.set(cache_key, lesson, ttl=3600)  # 1 hour
```

**Cache Invalidation:**
- TTL: 1 hour (3600 seconds)
- Manual clear via admin endpoint (future)

---

## 🎨 Frontend Architecture

### Technology Stack

**Core:**
- React 18.2.0
- React Router DOM 6.20.0
- Axios for API calls

**UI Libraries:**
- Framer Motion (animations)
- Lucide React (icons)
- Tabler Icons React
- React Select (dropdowns)
- Rough Notation (text highlighting)

**Styling:**
- Custom CSS with theme system
- Multiple themes: Light, Dark, Ocean, Elegant
- Responsive design

### Project Structure

```
frontend/src/
├── App.js                    # Main app with routing
├── index.js                  # Entry point
├── pages/                    # Route pages
│   ├── Home.js               # Landing page
│   ├── Login.js              # Login page
│   ├── Signup.js             # Registration page
│   ├── VerifyEmail.js        # OTP verification
│   ├── CompleteProfile.js    # OAuth profile completion
│   ├── GeneratorPage.js      # Lesson generator
│   ├── SettingsPage.js       # User settings
│   ├── LearnMore.js          # About/features
│   └── Team.js               # Team page
├── components/               # Reusable components
│   ├── Navbar.js
│   ├── Footer.js
│   ├── Hero.js
│   ├── Features.js
│   ├── Generator.js          # Main generator component
│   ├── LessonView.js         # Display generated lesson
│   ├── ProtectedRoute.js     # Auth guard
│   ├── GoogleSignInButton.js
│   ├── OTPInput.js
│   └── ...
├── context/                  # React Context
│   ├── AuthContext.js        # Authentication state
│   └── ThemeContext.js       # Theme management
├── services/                 # API services
│   └── api.js                # Axios instance
└── styles/                   # CSS files
    ├── index.css
    ├── theme-light.css
    ├── theme-dark.css
    └── ...
```

### Routing

```javascript
<Routes>
  {/* Public Routes */}
  <Route path="/" element={<Home />} />
  <Route path="/login" element={<Login />} />
  <Route path="/signup" element={<Signup />} />
  <Route path="/verify-email" element={<VerifyEmail />} />
  <Route path="/complete-profile" element={<CompleteProfile />} />
  <Route path="/auth-callback" element={<AuthCallback />} />
  
  {/* Protected Routes */}
  <Route path="/generator" element={
    <ProtectedRoute>
      <GeneratorPage />
    </ProtectedRoute>
  } />
  <Route path="/settings" element={
    <ProtectedRoute>
      <SettingsPage />
    </ProtectedRoute>
  } />
</Routes>
```

### State Management

**AuthContext:**
- User authentication state
- Login/logout functions
- Token management (localStorage)
- Protected route guards

**ThemeContext:**
- Theme selection (Light, Dark, Ocean, Elegant)
- Theme persistence (localStorage)
- Dynamic CSS class application

---

## 🔄 Key User Flows

### 1. User Registration Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Email
    participant DB
    
    User->>Frontend: Fill signup form
    Frontend->>Backend: POST /api/v1/auth/register
    Backend->>DB: Create user (email_verified=false)
    Backend->>Email: Send OTP
    Backend-->>Frontend: 201 Created
    Frontend->>User: Redirect to /verify-email
    
    User->>Frontend: Enter OTP
    Frontend->>Backend: POST /api/v1/auth/verify-email
    Backend->>DB: Verify OTP, update user
    Backend-->>Frontend: 200 OK + tokens
    Frontend->>User: Redirect to /generator
```

### 2. Google OAuth Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Google
    participant DB
    
    User->>Frontend: Click "Sign in with Google"
    Frontend->>Backend: GET /api/v1/auth/google/login
    Backend->>Google: Redirect to consent screen
    User->>Google: Authorize
    Google->>Backend: GET /callback?code=...
    Backend->>Google: Exchange code for tokens
    Google-->>Backend: User info
    Backend->>DB: Create/update user
    Backend->>Frontend: Redirect with session
    
    alt Profile incomplete
        Frontend->>User: Redirect to /complete-profile
        User->>Frontend: Fill required fields
        Frontend->>Backend: POST /api/v1/auth/complete-profile
    end
    
    Frontend->>User: Redirect to /generator
```

### 3. Lesson Generation Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Cache
    participant Orchestrator
    participant OpenAI
    participant DB
    
    User->>Frontend: Fill lesson form (topic, level, duration)
    Frontend->>Backend: POST /api/v1/lessons/generate
    
    Backend->>Cache: Check cache
    alt Cache hit
        Cache-->>Backend: Cached lesson
        Backend-->>Frontend: 200 OK (instant)
    else Cache miss
        Backend->>DB: Create lesson record (status=processing)
        Backend->>Orchestrator: Start generation
        
        Orchestrator->>OpenAI: Generate content
        Orchestrator->>OpenAI: Generate quiz
        Orchestrator->>OpenAI: Generate key takeaways
        Orchestrator-->>Backend: Complete lesson data
        
        Backend->>DB: Update lesson (status=completed)
        Backend->>Cache: Store in cache
        Backend-->>Frontend: 200 OK (~20-30s)
    end
    
    Frontend->>User: Display lesson + download buttons
```

---

## 📦 Dependencies

### Backend (`requirements.txt`)

**Core Framework:**
- `fastapi==0.109.2`
- `uvicorn[standard]==0.27.1`
- `python-multipart==0.0.9`

**Database:**
- `sqlalchemy==2.0.25`
- `asyncpg==0.29.0` (async PostgreSQL)
- `alembic==1.13.1` (migrations)

**Authentication:**
- `python-jose[cryptography]==3.3.0` (JWT)
- `passlib[bcrypt]==1.7.4` (password hashing)
- `Authlib==1.3.0` (OAuth)

**AI:**
- `openai==1.10.0`
- `tiktoken==0.5.2` (token counting)

**Caching:**
- `redis==5.0.1`

**Storage:**
- `boto3==1.34.34` (S3/R2)

**Monitoring:**
- `sentry-sdk[fastapi]==1.40.0`
- `structlog==24.1.0`

**Testing:**
- `pytest==8.0.0`
- `pytest-asyncio==0.23.4`
- `pytest-cov==4.1.0`

### Frontend (`package.json`)

**Core:**
- `react==18.2.0`
- `react-dom==18.2.0`
- `react-router-dom==6.20.0`

**HTTP:**
- `axios==1.6.0`

**UI/Animation:**
- `framer-motion==12.27.5`
- `lucide-react==0.300.0`
- `@tabler/icons-react==3.36.1`

**OAuth:**
- `@react-oauth/google==0.13.4`

**Utilities:**
- `clsx==2.1.1`
- `tailwind-merge==3.4.0`

---

## 🚀 Deployment Architecture

### Current Setup

**Backend:**
- Platform: Railway (recommended) or AWS EC2
- Database: Supabase PostgreSQL
- Redis: Railway built-in
- Storage: Cloudflare R2 (10GB free)

**Frontend:**
- Platform: Vercel (recommended)
- Build: `npm run build`
- Deploy: Automatic from Git

### Environment Variables

**Backend (`.env`):**
```env
# Application
APP_NAME=TeachGenie API
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# Security
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Storage
S3_ENDPOINT_URL=https://[account-id].r2.cloudflarestorage.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET_NAME=teachgenie-lessons

# Email
EMAIL_API_KEY=re_...
EMAIL_FROM=noreply@teachgenie.ai

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://api.teachgenie.ai/api/v1/auth/google/callback

# CORS
CORS_ORIGINS=["https://teachgenie.ai", "https://www.teachgenie.ai"]
```

**Frontend (`.env.local`):**
```env
REACT_APP_API_URL=https://api.teachgenie.ai
REACT_APP_GOOGLE_CLIENT_ID=...
```

---

## 🔍 Key Features

### ✅ Implemented

1. **Multi-Agent Lesson Generation**
   - Planner, Content, Quiz, Key Takeaways, Presentation agents
   - Async/parallel processing
   - OpenAI GPT-4o-mini integration

2. **Comprehensive Authentication**
   - Email/password with JWT
   - Google OAuth
   - Email OTP verification
   - Rate limiting

3. **User Management**
   - Profile management
   - Subscription tiers
   - Usage quota tracking
   - Lesson history

4. **Lesson Features**
   - Adaptive quiz generation
   - PPT and PDF export
   - Web resource curation
   - Caching for performance

5. **Admin Features**
   - Event logging
   - User management
   - Debug endpoints

6. **Frontend**
   - Responsive design
   - Multiple themes
   - Protected routes
   - Error boundaries

### 🔄 In Progress / Planned

1. **Payment Integration**
   - Stripe subscription management
   - Upgrade/downgrade flows
   - Invoice generation

2. **Enhanced Storage**
   - Cloudflare R2 integration
   - File upload for custom materials
   - Lesson sharing

3. **Advanced Features**
   - Collaborative lesson editing
   - Lesson templates
   - Export to LMS (Moodle, Canvas)
   - Mobile app

4. **Analytics**
   - Usage dashboards
   - Lesson performance metrics
   - User engagement tracking

---

## 🐛 Known Issues & Technical Debt

1. **CORS Configuration**
   - Currently set to `allow_origins=["*"]` for development
   - **Action:** Restrict to specific domains in production

2. **OAuth Security**
   - `OAUTHLIB_INSECURE_TRANSPORT=1` allows HTTP in development
   - **Action:** Remove in production (HTTPS only)

3. **Cache Implementation**
   - Currently using memory cache
   - **Action:** Migrate to Redis for production

4. **File Storage**
   - Local filesystem storage (`outputs/` directory)
   - **Action:** Migrate to Cloudflare R2

5. **Error Handling**
   - Some endpoints lack comprehensive error handling
   - **Action:** Add try-catch blocks and proper error responses

6. **Testing Coverage**
   - Limited test coverage
   - **Action:** Add integration tests for critical flows

---

## 📊 Performance Considerations

### Lesson Generation Time

**Typical Generation:** 20-30 seconds
- Planner: ~1s (rule-based)
- Content: ~10-15s (OpenAI API)
- Quiz: ~5-8s (OpenAI API)
- Key Takeaways: ~3-5s (OpenAI API)
- Presentation: ~2-3s (local generation)

**Optimization Strategies:**
1. **Caching:** Identical lessons return instantly
2. **Parallel Processing:** Content sections generated concurrently
3. **Token Optimization:** Using `gpt-4o-mini` (cost-effective)
4. **Background Tasks:** Future async generation option

### Database Optimization

- **Indexes:** Email, user_id, lesson_id
- **Connection Pooling:** SQLAlchemy async pool
- **Query Optimization:** Select only needed fields

---

## 🔒 Security Best Practices

1. **Password Security**
   - Bcrypt hashing with salt
   - Minimum 8 characters, complexity requirements
   - No password in logs

2. **Token Security**
   - Short-lived access tokens (30 min)
   - Refresh token rotation
   - Secure storage (httpOnly cookies recommended)

3. **Rate Limiting**
   - Per-IP and per-user limits
   - Prevents brute force and DDoS

4. **Input Validation**
   - Pydantic schemas
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS prevention

5. **Monitoring**
   - Admin logs for all auth events
   - Sentry for error tracking
   - Failed login attempt tracking

---

## 📚 Documentation

**Existing Documentation:**
- `architecture_analysis.md.resolved` - Original architecture analysis
- `api_documentation.md.resolved` - API endpoint documentation
- `async_architecture.md.resolved` - Async implementation details
- `security_audit.md.resolved` - Security analysis
- `production_deployment_plan.md.resolved` - Deployment guide
- `supabase_setup_guide.md.resolved` - Database setup

---

## 🎯 Recommendations

### Immediate Actions

1. **Security Hardening**
   - Update CORS origins to specific domains
   - Remove `OAUTHLIB_INSECURE_TRANSPORT` in production
   - Implement rate limiting on all endpoints

2. **Production Readiness**
   - Migrate to Redis cache
   - Implement Cloudflare R2 storage
   - Set up Sentry monitoring
   - Configure production environment variables

3. **Testing**
   - Add integration tests for auth flows
   - Add E2E tests for lesson generation
   - Set up CI/CD pipeline

### Future Enhancements

1. **Scalability**
   - Implement background task queue (Celery)
   - Add load balancing
   - Database read replicas

2. **Features**
   - Lesson versioning
   - Collaborative editing
   - Advanced analytics
   - Mobile app

3. **Monetization**
   - Stripe integration
   - Usage-based billing
   - Enterprise features

---

## 📞 Support & Maintenance

**Creator:** Lovi Raj Gupta  
**Project:** TeachGenie.ai  
**Tagline:** "Powered by AI • Designed for passionate educators by a learner"

**Tech Stack Summary:**
- Backend: FastAPI + PostgreSQL + Redis + OpenAI
- Frontend: React + React Router + Framer Motion
- Deployment: Railway + Vercel + Supabase + Cloudflare R2

---

*Document generated: February 3, 2026*  
*Analysis Version: 1.0*
