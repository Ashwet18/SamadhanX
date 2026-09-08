# SamadhanX Backend

FastAPI-based backend service for the SamadhanX platform.

## Architecture

The backend follows a modular monolith architecture with clear separation of concerns:

```
app/
├── main.py              # FastAPI application entry point
├── core/                # Core configurations and utilities
│   ├── config.py        # Settings and environment variables
│   └── security.py      # Authentication and security utilities
├── models/              # SQLAlchemy database models
│   ├── base.py          # Base model classes and mixins
│   └── __init__.py      # Model registry
├── schemas/             # Pydantic schemas for validation
│   ├── base.py          # Base schema classes
│   └── __init__.py      # Schema registry
├── routers/             # FastAPI route handlers
│   └── __init__.py      # Router registry
├── services/            # Business logic layer
│   ├── base.py          # Base service class
│   └── __init__.py      # Service registry
└── db/                  # Database configuration
    └── database.py      # SQLAlchemy setup
```

## Key Design Principles

1. **Separation of Concerns**: Clear boundaries between API, business logic, and data layers
2. **Dependency Injection**: FastAPI's dependency system for database sessions and services
3. **Type Safety**: Full type hints throughout the codebase
4. **Validation**: Pydantic schemas for all input/output validation
5. **Security**: JWT authentication with role-based access control
6. **Scalability**: Modular design allows future microservices extraction

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (for future task queue implementation)

### Installation

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Environment configuration:**
```bash
cp ../.env.example .env
# Edit .env with your configuration
```

4. **Database setup:**
```bash
# Ensure PostgreSQL is running
# Create database: samadhanx
# Run migrations (when implemented):
# alembic upgrade head
```

5. **Start development server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

Configuration is managed through environment variables (see `.env.example`):

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_*`: Individual database connection parameters

### Authentication
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ALGORITHM`: Algorithm for JWT encoding (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### AI Services
- `OPENAI_API_KEY`: OpenAI API key for LLM services
- `EMBEDDING_MODEL`: Model for text embeddings

### External Services
- `MAPS_API_KEY`: Google Maps or similar API key
- `SMTP_*`: Email configuration for notifications

## API Structure

The API follows RESTful conventions with consistent patterns:

### Planned Endpoints

```
/api/v1/
├── auth/                # Authentication endpoints
│   ├── POST /login      # User login
│   ├── POST /refresh    # Token refresh
│   └── POST /logout     # User logout
├── users/               # User management
│   ├── GET /me          # Current user profile
│   ├── PUT /me          # Update profile
│   └── GET /{id}        # Get user by ID
├── challenges/          # Challenge management
│   ├── GET /            # List challenges
│   ├── POST /           # Create challenge
│   ├── GET /{id}        # Get challenge
│   ├── PUT /{id}        # Update challenge
│   └── POST /{id}/submit # Submit for review
├── universities/        # University data
│   ├── GET /            # List universities
│   ├── GET /{id}        # Get university
│   └── GET /{id}/capabilities # University capabilities
├── projects/            # Project management
│   ├── GET /            # List projects
│   ├── POST /           # Create project
│   ├── GET /{id}        # Get project
│   └── PUT /{id}        # Update project
├── industry/            # Industry partnerships
│   ├── GET /partners    # List partners
│   └── POST /partnerships # Create partnership
├── analytics/           # Government analytics
│   ├── GET /dashboard   # Dashboard data
│   └── GET /reports     # Generate reports
└── notifications/       # System notifications
    ├── GET /            # List notifications
    └── POST /{id}/read  # Mark as read
```

## Database Models

### Planned Model Structure

The database will include the following main entity groups:

**User Management:**
- `User` - Base user entity with authentication
- `Role` - System roles (CITIZEN, GOVERNMENT_OFFICER, etc.)
- `UserRole` - Many-to-many user-role relationships

**Academic Entities:**
- `University` - Academic institutions
- `Department` - University departments
- `Faculty` - Faculty members with expertise
- `Student` - Student participants
- `Expertise` - Skill and knowledge areas

**Challenge Management:**
- `Challenge` - Citizen-submitted problems
- `ChallengeMedia` - Attached files and images
- `Category` - Problem categorization
- `ChallengeAIAnalysis` - AI-generated insights

**Project Execution:**
- `Project` - University-led solution projects
- `ProjectMember` - Team composition
- `ProjectMilestone` - Progress tracking
- `ProjectDeliverable` - Outputs and results

**Partnerships:**
- `IndustryPartner` - Corporate collaborators
- `Partnership` - Project partnerships
- `Funding` - Financial support tracking
- `Mentorship` - Guidance relationships

## Security Implementation

### Authentication Flow
1. User provides credentials (email/password)
2. Server validates and returns JWT access/refresh tokens
3. Client includes access token in Authorization header
4. Server validates token and extracts user context
5. RBAC checks ensure user has required permissions

### Password Security
- bcrypt hashing with automatic salt generation
- Configurable password strength requirements
- Secure token generation and validation

### API Security
- Input validation using Pydantic schemas
- SQL injection prevention through ORM
- CORS configuration for frontend integration
- Rate limiting for abuse prevention

## Development Guidelines

### Code Style
- **Formatting**: Black for code formatting
- **Import Sorting**: isort for import organization
- **Type Checking**: mypy for static type analysis
- **Linting**: flake8 for code quality checks

### Testing
- **Framework**: pytest for test execution
- **Coverage**: pytest-cov for coverage reporting
- **Async Testing**: pytest-asyncio for async code

### Database Migrations
- **Tool**: Alembic for schema migrations
- **Workflow**: Create migrations for all schema changes
- **Naming**: Descriptive migration names with timestamps

### Error Handling
- Consistent HTTP status codes
- Structured error responses
- Proper exception handling and logging
- User-friendly error messages

## Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Connection pooling for efficient resource usage
- Query optimization using SQLAlchemy best practices

### Caching Strategy
- Redis for session and frequently accessed data
- API response caching for expensive operations
- Database query result caching

### Scalability Planning
- Stateless API design for horizontal scaling
- Async operations for I/O intensive tasks
- Background task processing with Celery

## Monitoring and Logging

### Logging
- Structured logging with JSON format
- Configurable log levels per environment
- Request/response logging for debugging

### Error Tracking
- Sentry integration for error monitoring
- Performance tracking and alerting
- User behavior analytics

## Future Enhancements

1. **AI Integration**: Machine learning pipelines for challenge analysis
2. **Real-time Features**: WebSocket connections for live updates
3. **Mobile API**: Optimized endpoints for mobile applications
4. **Microservices**: Gradual extraction of domain services
5. **Advanced Analytics**: Complex reporting and data visualization
6. **Integration APIs**: Third-party system connections