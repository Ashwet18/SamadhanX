# SamadhanX Quick Start Guide

**Get up and running in 5 minutes!**

## Prerequisites Check

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] Git installed

## Quick Setup (5 minutes)

### Step 1: Clone and Configure (1 min)
```bash
# If not already cloned
git clone <your-repo-url>
cd samadhanx

# Copy environment file
cp .env.example .env

# Quick edit (or use default for development)
# nano .env  # Optional: customize settings
```

### Step 2: Start Everything (2 min)
```bash
# One command to rule them all!
make dev

# Wait for services to start (~2 minutes first time)
# Docker will download images and build containers
```

### Step 3: Verify (1 min)
Open these URLs in your browser:
- ✅ Frontend: http://localhost:3000
- ✅ Backend API: http://localhost:8000
- ✅ API Documentation: http://localhost:8000/docs
- ✅ Database Admin: http://localhost:5050 (admin@samadhanx.dev / admin123)

### Step 4: Test API (1 min)
```bash
# Test the health endpoint
curl http://localhost:8000/

# Should return:
# {"message":"SamadhanX API is running","version":"1.0.0","environment":"development","status":"healthy"}
```

## 🎉 You're Ready!

The complete development environment is now running with:
- PostgreSQL database with pgvector
- Redis for caching
- FastAPI backend with hot reload
- Next.js frontend with hot reload
- Database admin tools

## Common Development Tasks

### View Logs
```bash
# All services
make logs

# Just backend
make logs-backend

# Just frontend
make logs-frontend
```

### Stop Everything
```bash
make down
```

### Restart Services
```bash
make restart
```

### Run Tests
```bash
make test
```

### Database Operations
```bash
# Connect to database
make db-shell

# Run migrations
make db-migrate

# Reset database (WARNING: deletes all data)
make db-reset
```

### Code Quality
```bash
# Format code
make format

# Run linters
make lint
```

## Development Workflow

### Backend Development
```bash
cd backend

# Install dependencies (if not using Docker)
pip install -r requirements.txt

# Run backend standalone
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use make command
make dev-backend
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run frontend standalone
npm run dev

# Or use make command
make dev-frontend
```

## Next Steps for Your Team

### 1. Backend Team - Implement First API Endpoint
File: `backend/app/routers/auth.py`
```python
from fastapi import APIRouter, Depends
from app.schemas.base import MessageResponse

router = APIRouter()

@router.post("/register", response_model=MessageResponse)
async def register_user(user_data: UserCreate):
    # TODO: Implement user registration
    return {"message": "User registered successfully", "success": True}
```

### 2. Frontend Team - Create First Component
File: `frontend/components/forms/RegisterForm.tsx`
```typescript
export function RegisterForm() {
  // TODO: Implement registration form
  return (
    <form>
      <input type="email" placeholder="Email" />
      <input type="password" placeholder="Password" />
      <button type="submit">Register</button>
    </form>
  )
}
```

### 3. Database Team - Create First Migration
```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "create users table"

# Edit the migration file in migrations/versions/
# Then apply it
alembic upgrade head
```

## Troubleshooting

### Docker Issues
```bash
# Clean everything and start fresh
make clean-all
make dev
```

### Port Conflicts
If ports 3000, 8000, 5432, or 6379 are in use:
1. Stop conflicting services
2. Or edit docker-compose.yml to use different ports

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Permission Issues (Linux/Mac)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Useful Commands Reference

| Task | Command |
|------|---------|
| Start all services | `make dev` |
| Stop all services | `make down` |
| View all logs | `make logs` |
| Run tests | `make test` |
| Format code | `make format` |
| Database shell | `make db-shell` |
| Redis shell | `make redis-shell` |
| Backend shell | `make shell-backend` |
| See all commands | `make help` |

## Environment Variables Quick Reference

Key variables to customize in `.env`:

```bash
# Database
DATABASE_URL=postgresql://samadhanx:your_password@localhost:5432/samadhanx

# JWT Secret (generate with: make generate-secret)
JWT_SECRET_KEY=your-super-secret-key-here

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# AI Services (add when needed)
OPENAI_API_KEY=sk-your-key-here

# Email (add when needed)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Team Collaboration Tips

### Work Distribution
- **Backend Team**: Focus on `backend/app/` directory
- **Frontend Team**: Focus on `frontend/` directory
- **Database Team**: Focus on `backend/app/models/` and migrations
- **DevOps Team**: Focus on `docker-compose.yml` and deployment

### Git Workflow
```bash
# Always work on feature branches
git checkout -b feature/your-feature-name

# Commit often with clear messages
git commit -m "feat(auth): add user registration endpoint"

# Pull latest before pushing
git pull origin main --rebase
git push origin feature/your-feature-name
```

### Communication
- Use GitHub Issues for tasks
- Use Pull Requests for code review
- Document decisions in `docs/` directory

## Getting Help

- **Documentation**: Check `docs/` directory
- **API Reference**: http://localhost:8000/docs
- **Make Commands**: Run `make help`
- **Team Lead**: Ask your team lead or mentor

## Success Checklist

- [ ] All services running (`docker-compose ps` shows all healthy)
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API responding at http://localhost:8000
- [ ] API docs visible at http://localhost:8000/docs
- [ ] Database accessible via pgAdmin
- [ ] Tests passing (`make test`)
- [ ] Git repository initialized
- [ ] Team members have access

**Ready to build something amazing! 🚀**

---

*For detailed information, see README.md and docs/ directory*