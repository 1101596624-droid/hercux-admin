# HERCU Backend - Quick Start Guide

## ✅ What's Been Created

FastAPI backend skeleton with complete project structure:

### 📁 Directory Structure
```
backend/
├── app/
│   ├── api/v1/endpoints/    # 7 API modules
│   ├── core/                # Configuration
│   ├── db/                  # Database connections
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── main.py              # FastAPI app
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

### 🗄️ Database Models Created
- **User** - User accounts
- **Course** - Course metadata
- **CourseNode** - Content nodes (CORE)
- **LearningProgress** - Progress tracking
- **TrainingPlan** - AI-generated plans
- **Achievement** - Badges and achievements

### 🔌 API Endpoints Created (30+ endpoints)
1. **User Module** - Profile, summary, statistics
2. **Course Module** - Browse, filter, enroll
3. **Node Module** - Get config, update progress (CORE)
4. **AI Module** - Guide chat, plan generation
5. **Training Module** - Plan management
6. **Achievement Module** - Badges, skill tree

## 🚀 Next Steps

### Step 1: Setup Environment

```bash
cd C:\Users\11015\Desktop\项目核心\hercux\backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure .env

```bash
# Copy example
copy .env.example .env

# Edit .env and set:
# - DATABASE_URL (PostgreSQL)
# - REDIS_URL
# - NEO4J credentials
# - SECRET_KEY
# - ANTHROPIC_API_KEY
```

### Step 3: Setup Databases

**PostgreSQL:**
```bash
# Install PostgreSQL if needed
# Create database
createdb hercu_db
```

**Redis:**
```bash
# Install Redis or use Docker
docker run -d -p 6379:6379 redis:latest
```

**Neo4j:**
```bash
# Use Docker
docker run -d -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### Step 4: Run Server

```bash
# Method 1: Using run.py
python run.py

# Method 2: Using uvicorn directly
uvicorn app.main:app --reload
```

### Step 5: Test API

Visit: http://localhost:8000/api/v1/docs

## 📋 TODO - Implementation Tasks

### Priority 1: Core Functionality
- [ ] Add Alembic migrations
- [ ] Create initial database tables
- [ ] Implement JWT authentication
- [ ] Add user registration/login endpoints
- [ ] Test core node endpoint with sample data

### Priority 2: AI Integration
- [ ] Integrate Claude API for guide chat
- [ ] Implement training plan generation
- [ ] Add conversation history management

### Priority 3: Content Ingestion
- [ ] Create content ingestion endpoint
- [ ] Define course package JSON format
- [ ] Implement bulk node import

### Priority 4: Business Logic
- [ ] Implement node unlock logic (prerequisites)
- [ ] Add achievement unlock triggers
- [ ] Implement recommendation algorithm
- [ ] Add Neo4j skill tree queries

### Priority 5: Production Ready
- [ ] Add comprehensive error handling
- [ ] Implement logging
- [ ] Add rate limiting
- [ ] Write unit tests
- [ ] Add API documentation
- [ ] Setup monitoring

## 🔑 Key Files to Understand

1. **app/main.py** - FastAPI application entry point
2. **app/models/models.py** - Database schema
3. **app/schemas/schemas.py** - API request/response models
4. **app/api/v1/endpoints/nodes.py** - CORE workstation endpoint
5. **app/core/config.py** - Configuration management

## 🎯 Core Endpoint: GET /api/v1/nodes/{nodeId}

This is the **most important endpoint** - it drives the Learning Workstation:

**Request:**
```
GET /api/v1/nodes/node_biomech_01
```

**Response:**
```json
{
  "node_id": "node_biomech_01",
  "type": "simulator",
  "component_id": "force-balance-sim",
  "title": "Force Balance Analysis",
  "config": {
    "initialLoad": 50,
    "gravity": 9.8,
    "guidePrompt": "Observe center of mass shift..."
  },
  "status": "unlocked",
  "completion_percentage": 0.0
}
```

The frontend uses this config to dynamically load the correct component.

## 📞 Need Help?

Check the main README.md for:
- Detailed API documentation
- Database schema details
- Development guidelines
- Security notes

## 🎉 You're Ready!

The backend skeleton is complete. Now you can:
1. Setup the databases
2. Run the server
3. Start implementing the TODO items
4. Connect with the frontend

Good luck! 🚀
