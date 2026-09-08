# SamadhanX — Jharkhand Societal Innovation Exchange

**Converting real societal problems into university-led innovation projects supported by industry and monitored by government.**

## Problem Statement

SIH26043: Creating a comprehensive platform to bridge the gap between citizen-reported societal challenges and academic innovation capabilities, enabling systematic problem-solving through university-industry collaboration with government oversight.

## Vision

SamadhanX transforms how society addresses complex challenges by creating a structured pipeline: Citizen → Societal Challenge → AI Analysis → Government Validation → University Matching → Student/Faculty Team → Industry Collaboration → Prototype → Pilot → Deployment → Impact Measurement.

## Problem

- Citizens face real societal problems but lack channels for systematic solution development
- Universities have research capabilities but limited real-world problem exposure
- Government agencies need data-driven insights for policy decisions
- Industry seeks meaningful CSR and innovation partnerships
- No integrated platform connects these stakeholders effectively

## Solution

SamadhanX is a modular monolith platform that:

1. **Captures** citizen challenges with rich contextual data
2. **Analyzes** problems using AI for classification and matching
3. **Validates** challenges through government review processes
4. **Matches** problems with university capabilities and expertise
5. **Facilitates** student/faculty team formation and project execution
6. **Connects** teams with industry partners for mentorship and funding
7. **Tracks** project lifecycle from prototype to deployment
8. **Measures** real-world impact and societal outcomes

## Key Features

- 🏛️ **Multi-Role Support**: Citizens, Government Officers, Universities, Industry Partners
- 🤖 **AI-Powered Matching**: Intelligent university-challenge matching with explainable recommendations
- 📊 **Challenge Lifecycle Management**: From submission to impact measurement
- 🎓 **Academic Integration**: Seamless university project workflow
- 🏢 **Industry Collaboration**: Partnership and mentorship facilitation
- 📈 **Impact Analytics**: Government dashboard for policy insights
- 🔍 **Duplicate Detection**: AI-powered challenge deduplication
- 🔒 **Role-Based Access Control**: Secure multi-stakeholder environment

## User Roles

The system supports 10 distinct user roles with flexible multi-role assignment:

1. **CITIZEN** - Submit challenges, track progress
2. **GOVERNMENT_OFFICER** - Validate challenges, monitor projects
3. **UNIVERSITY_ADMIN** - Manage institutional capabilities
4. **FACULTY** - Lead research projects, mentor students
5. **STUDENT** - Participate in project teams
6. **INDUSTRY** - Provide partnerships and funding
7. **MENTOR** - Guide project development
8. **CSR** - Corporate social responsibility engagement
9. **RESEARCHER** - Contribute expertise and analysis
10. **PLATFORM_ADMIN** - System administration and oversight

## System Architecture

```mermaid
graph TD
    A[Citizen] --> B[Challenge Submission]
    B --> C[AI Analysis & Classification]
    C --> D[Government Validation]
    D --> E[University Matching]
    E --> F[Student + Faculty Team]
    F --> G[Project Creation]
    G --> H[Industry Collaboration]
    H --> I[Prototype Development]
    I --> J[Pilot Testing]
    J --> K[Deployment]
    K --> L[Impact Measurement]
    L --> M[Government Analytics]
    
    N[AI Layer] --> C
    N --> E
    N --> O[Duplicate Detection]
    
    P[Database Layer] --> Q[PostgreSQL + pgvector]
    R[Authentication] --> S[JWT + RBAC]
```

## Technology Stack

### Frontend
- **Next.js** - React framework with SSR/SSG
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Responsive Design** - Mobile-first approach

### Backend
- **Python 3.11+** - Primary backend language
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Pydantic V2** - Data validation and settings
- **PostgreSQL 15+** - Primary database with pgvector
- **Alembic** - Database migration management
- **python-jose** - JWT token management
- **passlib[bcrypt]** - Password hashing
- **pytest** - Testing framework

### AI & Analytics
- **Python** - AI/ML implementation
- **LLM Integration** - For challenge analysis
- **Embedding-based Search** - Semantic similarity
- **Vector Database** - pgvector for embeddings

### Infrastructure
- **Docker** - Containerization
- **docker-compose** - Local development
- **Object Storage** - Media file handling
- **Leaflet/Mapbox** - Geographic visualization

### Authentication & Security
- **JWT** - Token-based authentication
- **RBAC** - Role-based access control
- **Password Hashing** - Secure credential storage
- **Input Validation** - Data security

## AI Architecture

The AI pipeline processes challenges through multiple stages:

```mermaid
graph LR
    A[Citizen Input] --> B[Language Detection]
    B --> C[Normalization]
    C --> D[Problem Classification]
    D --> E[Skill Extraction]
    E --> F[Severity Analysis]
    F --> G[Structured Challenge]
    G --> H[Embedding Generation]
    H --> I[Duplicate Search]
    I --> J[University Matching]
    J --> K[Explainable Recommendations]
```

**Key AI Features:**
- Multi-language support with automatic detection
- Semantic problem classification and tagging
- Skill requirement extraction from challenge descriptions
- Urgency and severity scoring
- Vector-based duplicate detection
- Explainable university matching with confidence scores

## Challenge Lifecycle

Challenges flow through a structured state machine:

**Primary Flow:**
```
DRAFT → SUBMITTED → AI_ANALYSIS → PENDING_REVIEW → VALIDATED → 
MATCHING → UNIVERSITY_INVITED → ACCEPTED → PROJECT_CREATED → 
TEAM_FORMED → PROPOSAL_SUBMITTED → APPROVED → PROTOTYPE → 
TESTING → PILOT → DEPLOYED → IMPACT_MEASURED → COMPLETED
```

**Alternative States:**
- REJECTED, DUPLICATE, ON_HOLD, CANCELLED

**Note:** Challenge Status and Project Status are maintained separately, as one challenge may spawn multiple projects.

## Database Architecture

### Core Entities

**User Management:**
- `users`, `roles`, `user_roles`
- `citizens`, `government_officers`

**Academic Institutions:**
- `universities`, `departments`, `faculty`, `students`
- `expertise`, `faculty_expertise`, `university_expertise`
- `facilities`

**Industry & Partnerships:**
- `industry_partners`, `industry_expertise`
- `partnerships`, `funding`, `mentorships`

**Challenge Management:**
- `challenges`, `challenge_media`, `categories`
- `challenge_categories`, `challenge_ai_analysis`
- `challenge_embeddings`, `challenge_duplicates`
- `challenge_assignments`

**Project Execution:**
- `projects`, `project_members`, `project_mentors`
- `project_proposals`, `project_milestones`
- `project_deliverables`

**Analytics & Audit:**
- `impact_metrics`, `notifications`, `audit_logs`

### Design Principles
- PostgreSQL with normalized relational design
- UUIDs for primary keys where appropriate
- Foreign key constraints and referential integrity
- pgvector for semantic search capabilities
- Object storage URLs for media files (no BLOB storage)
- Comprehensive audit logging

## Repository Structure

```
samadhanx/
├── frontend/                 # Next.js application
│   ├── app/                 # Next.js 13+ app directory
│   ├── components/          # Reusable UI components
│   ├── lib/                 # Utility functions and configs
│   ├── types/               # TypeScript type definitions
│   └── public/              # Static assets
├── backend/                 # FastAPI application
│   └── app/
│       ├── main.py          # Application entry point
│       ├── core/            # Core configurations
│       ├── models/          # SQLAlchemy models
│       ├── schemas/         # Pydantic schemas
│       ├── routers/         # API route handlers
│       ├── services/        # Business logic layer
│       └── db/              # Database utilities
├── ai/                      # AI/ML components
│   ├── models/              # AI model implementations
│   ├── services/            # AI processing services
│   └── utils/               # AI utility functions
├── docs/                    # Documentation
│   ├── architecture.md      # System architecture
│   ├── database.md          # Database design
│   ├── api.md               # API documentation
│   └── workflows.md         # Process workflows
├── .github/
│   └── workflows/           # CI/CD pipelines
├── docker-compose.yml       # Local development setup
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── LICENSE                  # Project license
```

## Local Development Setup

### Prerequisites
- Node.js (v18+)
- Python (3.11+)
- PostgreSQL (14+)
- Docker and Docker Compose

### Environment Setup

1. **Clone and Setup:**
```bash
git clone <repository-url>
cd samadhanx
cp .env.example .env
# Edit .env with your configuration
```

2. **Database Setup:**
```bash
docker-compose up -d postgres
# Database will be available at localhost:5432
```

3. **Backend Development:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Frontend Development:**
```bash
cd frontend
npm install
npm run dev
# Application available at http://localhost:3000
```

5. **Full Stack with Docker:**
```bash
docker-compose up --build
```

## Environment Variables

Key environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/samadhanx
POSTGRES_USER=samadhanx
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=samadhanx

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=your-openai-key
EMBEDDING_MODEL=text-embedding-ada-002

# Object Storage
STORAGE_BACKEND=local  # or s3, gcs
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET=samadhanx-media

# External Services
MAPS_API_KEY=your-maps-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-app-password
```

## API Structure

The API is organized into logical groups:

- `/api/v1/auth` - Authentication and authorization
- `/api/v1/users` - User management
- `/api/v1/challenges` - Challenge CRUD and lifecycle
- `/api/v1/universities` - University and academic data
- `/api/v1/projects` - Project management
- `/api/v1/industry` - Industry partnerships
- `/api/v1/analytics` - Government analytics dashboard
- `/api/v1/notifications` - System notifications

## Development Roadmap

### Phase 1: MVP Foundation (Current)
- [x] Repository setup and architecture
- [ ] Authentication system
- [ ] Basic CRUD operations
- [ ] Challenge submission workflow
- [ ] Simple government validation

### Phase 2: Core Features
- [ ] AI analysis integration
- [ ] University matching system
- [ ] Project lifecycle management
- [ ] Basic industry partnerships

### Phase 3: Advanced Features
- [ ] Advanced AI capabilities
- [ ] Real-time notifications
- [ ] Analytics dashboard
- [ ] Impact measurement

### Phase 4: Scale & Polish
- [ ] Performance optimization
- [ ] Advanced security features
- [ ] Mobile applications
- [ ] Enterprise integrations

## Future Scalability

The modular monolith architecture supports future growth:

- **Microservices Migration**: Modules can be extracted to separate services
- **Horizontal Scaling**: Database read replicas and API load balancing
- **AI Service Scaling**: Separate AI inference services
- **Multi-tenant Architecture**: Support for multiple states/regions
- **Mobile Applications**: API-first design enables native mobile apps
- **Third-party Integrations**: Extensible plugin architecture

## Contributing

### Development Guidelines
- Use TypeScript strict mode for frontend development
- Apply Python type hints throughout backend code
- Implement Pydantic validation for all API inputs
- Follow clean architecture principles with service layers
- Store secrets in environment variables only
- Use meaningful commit messages following conventional commits
- Implement proper authorization checks for all endpoints
- Write business logic in service layers, not route handlers

### Code Style
- Frontend: ESLint + Prettier with TypeScript strict mode
- Backend: Black + isort + mypy for Python formatting and type checking
- Database: Use Alembic migrations for schema changes
- API: Follow OpenAPI 3.0 specification for documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## SIH Problem Statement Reference

**SIH26043**: Development of a comprehensive platform to facilitate systematic problem-solving by connecting citizen-reported societal challenges with academic research capabilities, enabling university-industry collaboration under government oversight for sustainable societal impact.

---

**Built with ❤️ for SIH 2026 - Jharkhand Societal Innovation Exchange**