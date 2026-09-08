# SamadhanX Database Setup Instructions

Quick reference for setting up and running the SamadhanX database layer.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ installed
- Git installed

## Step-by-Step Setup

### 1. Clone Repository (if not already done)

```bash
git clone <repository-url>
cd SamadhanX
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# The .env.example already has correct Docker credentials:
# POSTGRES_PASSWORD=samadhanx_dev_password
# DATABASE_URL=postgresql://samadhanx:samadhanx_dev_password@localhost:5432/samadhanx
```

### 3. Start PostgreSQL

```bash
# Start PostgreSQL with pgvector
docker-compose up -d postgres

# Wait for PostgreSQL to be healthy (takes ~10-15 seconds)
docker-compose ps postgres

# Check logs if needed
docker-compose logs -f postgres
```

### 4. Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
# Still in backend directory

# Generate initial migration from models
alembic revision --autogenerate -m "initial schema"

# Review the generated migration file in migrations/versions/

# Apply the migration
alembic upgrade head

# Verify migration applied
alembic current
```

### 6. Seed Development Data

```bash
# Run seed script (idempotent - safe to run multiple times)
python -m app.db.seed

# Expected output:
# 🌱 Starting database seed...
#   Creating roles...
#   Creating users...
#   Creating expertise areas...
#   Creating categories...
#   Creating universities...
#   Creating industry partners...
#   Creating challenges...
#   Creating projects...
# ✅ Database seeded successfully!
```

### 7. Verify Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U samadhanx -d samadhanx

# Run verification queries
SELECT COUNT(*) FROM users;           -- Should show 20+
SELECT COUNT(*) FROM universities;    -- Should show 5
SELECT COUNT(*) FROM challenges;      -- Should show 10
SELECT COUNT(*) FROM projects;        -- Should show 3-5
SELECT name FROM roles;               -- Should show all 10 roles
\dt                                   -- List all tables (should show 32)
\q                                    -- Exit psql
```

### 8. Start Backend Server

```bash
# Still in backend directory with venv activated

# Start FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python module
python -m uvicorn app.main:app --reload
```

### 9. Test Health Endpoint

```bash
# In a new terminal
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "ok",
#   "message": "SamadhanX API is running",
#   "version": "1.0.0",
#   "environment": "development",
#   "database": "connected",
#   "database_error": null
# }
```

### 10. Run Tests

```bash
# In backend directory with venv activated
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Expected: All 13 tests should pass
```

## Quick Command Reference

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Start only PostgreSQL
docker-compose up -d postgres

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres

# Check service status
docker-compose ps

# Connect to PostgreSQL
docker-compose exec postgres psql -U samadhanx -d samadhanx

# Restart PostgreSQL
docker-compose restart postgres
```

### Alembic Commands

```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history

# View SQL without executing
alembic upgrade head --sql
```

### Database Commands

```bash
# Run seed script
python -m app.db.seed

# Connect to database
docker-compose exec postgres psql -U samadhanx -d samadhanx

# Backup database
docker-compose exec postgres pg_dump -U samadhanx samadhanx > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U samadhanx -d samadhanx

# Reset database (CAUTION: deletes all data)
docker-compose exec postgres psql -U samadhanx -d samadhanx -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
alembic upgrade head
python -m app.db.seed
```

### Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_models.py::test_user_creation

# Run tests matching pattern
pytest -k "test_challenge"

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

### Backend Server Commands

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Specify host and port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server (no reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn (production)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## Seeded User Credentials

All seeded users have the same password: `Password@123`

### Test Users

| Email | Role | Description |
|-------|------|-------------|
| admin@samadhanx.gov.in | Platform Admin | System administrator |
| sunita.devi@jharkhand.gov.in | Government Officer | Joint Secretary, DST |
| ramesh.mahato@jharkhand.gov.in | Government Officer | Director, Rural Development |
| rajesh.kumar@example.com | Citizen | Test citizen user |
| priya.sharma@example.com | Citizen | Test citizen user |
| amit.singh@example.com | Citizen | Test citizen user |
| anjali.verma@bitmesra.ac.in | University Admin | BIT Mesra admin |
| suresh.oraon@nitmsr.ac.in | University Admin | NIT Jamshedpur admin |

### Faculty & Students
- Faculty: `rakesh.kumar@university.ac.in`, `meena.gupta@university.ac.in`, etc.
- Students: `rahul.kumar@student.ac.in`, `anita.sharma@student.ac.in`, etc.

## Troubleshooting

### Docker not starting

```bash
# Check Docker is running
docker --version
docker-compose --version

# Check if port 5432 is available
netstat -an | grep 5432

# On Windows:
netstat -ano | findstr :5432

# If port is in use, stop conflicting service or change port in docker-compose.yml
```

### Database connection refused

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# If still failing, check DATABASE_URL in .env matches docker-compose.yml
```

### Alembic migration errors

```bash
# Check current migration state
alembic current

# View migration history
alembic history

# If stuck, manually fix and stamp
alembic stamp head

# If models changed but migration didn't detect
alembic revision --autogenerate -m "fix" --force
```

### Seed script errors

```bash
# Check database is accessible
python -c "from app.db.database import engine; engine.connect(); print('OK')"

# Check if tables exist
docker-compose exec postgres psql -U samadhanx -d samadhanx -c "\dt"

# If tables missing, run migration first
alembic upgrade head

# Run seed in verbose mode (add debug prints to seed.py if needed)
python -m app.db.seed
```

### Tests failing

```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Check pytest is installed
pytest --version

# Run single test to isolate issue
pytest tests/test_models.py::test_user_creation -v

# Check if imports work
python -c "from app.models import User; print('OK')"
```

### pgvector not available

```bash
# Check if extension exists
docker-compose exec postgres psql -U samadhanx -d samadhanx -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# If not installed, check init script ran
docker-compose logs postgres | grep "CREATE EXTENSION"

# Manually create extension
docker-compose exec postgres psql -U samadhanx -d samadhanx -c "CREATE EXTENSION IF NOT EXISTS vector;"

# If pgvector image not available, use standard PostgreSQL and disable embedding table
```

## API Documentation

Once the backend server is running:

- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Database Access Tools

### pgAdmin (Web Interface)

```bash
# Start pgAdmin
docker-compose up -d pgadmin

# Access at http://localhost:5050
# Login: admin@samadhanx.dev
# Password: admin123

# Add server:
# - Host: postgres
# - Port: 5432
# - Username: samadhanx
# - Password: samadhanx_dev_password
# - Database: samadhanx
```

### DBeaver / DataGrip

Connection settings:
- Host: localhost
- Port: 5432
- Database: samadhanx
- Username: samadhanx
- Password: samadhanx_dev_password

## Performance Tips

1. **Connection Pooling**: Already configured (pool_size=20, max_overflow=30)
2. **Indexes**: All foreign keys and search fields indexed
3. **Eager Loading**: Use `selectinload()` for relationships
4. **Pagination**: Always paginate large queries
5. **Caching**: Use Redis for frequently accessed data (to be implemented)

## Next Steps

After database setup is verified:

1. ✅ Implement authentication APIs (/register, /login, /logout)
2. ✅ Implement challenge CRUD APIs
3. ✅ Implement university APIs with filtering
4. ✅ Integrate AI for challenge analysis
5. ✅ Implement file upload for media
6. ✅ Build frontend UI
7. ✅ Add real-time notifications
8. ✅ Implement analytics endpoints

## Getting Help

- Check `DATABASE_IMPLEMENTATION.md` for detailed documentation
- Check `docs/database.md` for schema details
- Check `docs/api.md` for API specifications
- Check FastAPI docs at http://localhost:8000/docs
- Review test files in `backend/tests/` for usage examples

## Success Checklist

- [ ] Docker running
- [ ] PostgreSQL container started
- [ ] Python dependencies installed
- [ ] Alembic migration applied
- [ ] Seed script executed successfully
- [ ] Backend server running
- [ ] Health endpoint returns "connected"
- [ ] All tests passing
- [ ] Can login to pgAdmin
- [ ] Can see 32 tables in database
- [ ] Can see 20+ users, 5 universities, 10 challenges

Once all checkboxes are complete, the database layer is fully operational! 🎉
