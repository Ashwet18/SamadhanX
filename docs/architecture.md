# SamadhanX System Architecture

## Overview

SamadhanX is designed as a **modular monolith** that connects citizens, government agencies, universities, and industry partners to systematically solve societal challenges through innovation and collaboration. The architecture supports the complete lifecycle from challenge submission to impact measurement.

## Architecture Principles

### 1. **Modular Monolith Design**
- Single deployable unit with clear internal boundaries
- Domain-driven module separation
- Ability to extract modules to microservices in the future
- Shared database with well-defined schemas

### 2. **Scalability & Performance**
- Horizontal scaling through load balancers
- Database read replicas for query optimization
- Caching layers for frequently accessed data
- Async processing for heavy operations (AI analysis)

### 3. **Security & Privacy**
- Role-based access control (RBAC) throughout the system
- JWT-based authentication with refresh tokens
- Input validation and sanitization at all layers
- Audit logging for compliance and monitoring

### 4. **Maintainability & Extensibility**
- Clean architecture with separation of concerns
- Dependency injection for loose coupling
- Comprehensive testing strategy
- Documentation-driven development

## System Context Diagram

```mermaid
graph TB
    subgraph "External Actors"
        C[Citizens]
        G[Government Officers]
        U[Universities]
        I[Industry Partners]
        M[Mentors]
    end
    
    subgraph "SamadhanX Platform"
        SX[SamadhanX System]
    end
    
    subgraph "External Systems"
        AI[AI/ML Services]
        MAP[Maps API]
        SMS[SMS Gateway]
        EMAIL[Email Service]
        STORAGE[Object Storage]
    end
    
    C --> SX
    G --> SX
    U --> SX
    I --> SX
    M --> SX
    
    SX --> AI
    SX --> MAP
    SX --> SMS
    SX --> EMAIL
    SX --> STORAGE
```

## High-Level Architecture

```mermaid
graph TD
    subgraph "Client Layer"
        WEB[Web Frontend<br/>Next.js]
        MOBILE[Mobile App<br/>Future]
    end
    
    subgraph "API Gateway Layer"
        LB[Load Balancer]
        CORS[CORS Handler]
        AUTH[Authentication]
        RATE[Rate Limiting]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend]
        subgraph "Core Modules"
            AUTH_MOD[Authentication]
            CHALLENGE[Challenge Management]
            PROJECT[Project Management]
            UNIVERSITY[University System]
            INDUSTRY[Industry Partnerships]
            ANALYTICS[Analytics Engine]
            AI_MOD[AI Processing]
        end
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL<br/>Primary Database)]
        VECTOR[(pgvector<br/>Embeddings)]
        CACHE[(Redis<br/>Cache)]
        FILES[Object Storage<br/>Media Files]
    end
    
    subgraph "External Services"
        LLM[LLM Services<br/>OpenAI]
        MAPS[Maps API]
        NOTIFY[Notification Services]
    end
    
    WEB --> LB
    MOBILE --> LB
    
    LB --> CORS
    CORS --> AUTH
    AUTH --> RATE
    RATE --> API
    
    API --> AUTH_MOD
    API --> CHALLENGE
    API --> PROJECT
    API --> UNIVERSITY
    API --> INDUSTRY
    API --> ANALYTICS
    API --> AI_MOD
    
    AUTH_MOD --> DB
    CHALLENGE --> DB
    PROJECT --> DB
    UNIVERSITY --> DB
    INDUSTRY --> DB
    ANALYTICS --> DB
    
    AI_MOD --> VECTOR
    API --> CACHE
    API --> FILES
    
    AI_MOD --> LLM
    API --> MAPS
    API --> NOTIFY
```

## Detailed Component Architecture

### Frontend Architecture (Next.js)

```mermaid
graph TD
    subgraph "Next.js Application"
        subgraph "App Router"
            PAGES[Pages/Routes]
            LAYOUT[Layout Components]
            MIDDLEWARE[Middleware]
        end
        
        subgraph "Component Layer"
            UI[UI Components]
            FORMS[Form Components]
            CHARTS[Chart Components]
            MAPS_COMP[Map Components]
        end
        
        subgraph "State Management"
            REACT_QUERY[React Query<br/>Server State]
            ZUSTAND[Zustand<br/>Client State]
            CONTEXT[React Context<br/>Theme/Auth]
        end
        
        subgraph "Utilities"
            API_CLIENT[API Client]
            UTILS[Utility Functions]
            HOOKS[Custom Hooks]
        end
    end
    
    PAGES --> LAYOUT
    PAGES --> UI
    PAGES --> FORMS
    
    FORMS --> REACT_QUERY
    UI --> ZUSTAND
    LAYOUT --> CONTEXT
    
    REACT_QUERY --> API_CLIENT
    API_CLIENT --> UTILS
    
    HOOKS --> REACT_QUERY
    HOOKS --> ZUSTAND
```

### Backend Architecture (FastAPI)

```mermaid
graph TD
    subgraph "FastAPI Application"
        subgraph "API Layer"
            ROUTERS[Route Handlers]
            MIDDLEWARE[Middleware Stack]
            DEPS[Dependencies]
        end
        
        subgraph "Service Layer"
            AUTH_SVC[Auth Service]
            CHALLENGE_SVC[Challenge Service]
            PROJECT_SVC[Project Service]
            UNIVERSITY_SVC[University Service]
            AI_SVC[AI Service]
            NOTIFICATION_SVC[Notification Service]
        end
        
        subgraph "Data Layer"
            MODELS[SQLAlchemy Models]
            SCHEMAS[Pydantic Schemas]
            REPOSITORIES[Repository Pattern]
        end
        
        subgraph "Core"
            CONFIG[Configuration]
            SECURITY[Security Utils]
            DATABASE[Database Connection]
        end
    end
    
    ROUTERS --> DEPS
    ROUTERS --> AUTH_SVC
    ROUTERS --> CHALLENGE_SVC
    ROUTERS --> PROJECT_SVC
    
    AUTH_SVC --> MODELS
    CHALLENGE_SVC --> MODELS
    PROJECT_SVC --> MODELS
    
    MODELS --> DATABASE
    SCHEMAS --> MODELS
    
    DEPS --> SECURITY
    MIDDLEWARE --> CONFIG
    DATABASE --> CONFIG
```

## Data Architecture

### Database Design Strategy

1. **PostgreSQL as Primary Database**
   - ACID compliance for transactional integrity
   - Rich data types and JSON support
   - Full-text search capabilities
   - Mature ecosystem and tooling

2. **pgvector Extension**
   - Vector similarity search for AI embeddings
   - Semantic matching of challenges and capabilities
   - Duplicate challenge detection

3. **Redis for Caching**
   - Session storage
   - Frequently accessed reference data
   - Rate limiting counters
   - Background job queues

### Data Flow Architecture

```mermaid
graph LR
    subgraph "Data Sources"
        CITIZEN[Citizen Input]
        GOVT[Government Data]
        UNI[University Data]
        IND[Industry Data]
    end
    
    subgraph "Processing Pipeline"
        VALIDATE[Validation Layer]
        TRANSFORM[Data Transformation]
        AI_ANALYSIS[AI Analysis]
    end
    
    subgraph "Storage Layer"
        TRANSACTIONAL[(Transactional Data<br/>PostgreSQL)]
        VECTOR_DB[(Vector Data<br/>pgvector)]
        CACHE[(Cache<br/>Redis)]
        FILES[Media Files<br/>Object Storage]
    end
    
    subgraph "Output Layer"
        API_OUT[API Responses]
        REPORTS[Analytics Reports]
        NOTIFICATIONS[Notifications]
    end
    
    CITIZEN --> VALIDATE
    GOVT --> VALIDATE
    UNI --> VALIDATE
    IND --> VALIDATE
    
    VALIDATE --> TRANSFORM
    TRANSFORM --> AI_ANALYSIS
    TRANSFORM --> TRANSACTIONAL
    
    AI_ANALYSIS --> VECTOR_DB
    AI_ANALYSIS --> TRANSACTIONAL
    
    TRANSACTIONAL --> CACHE
    TRANSACTIONAL --> API_OUT
    TRANSACTIONAL --> REPORTS
    TRANSACTIONAL --> NOTIFICATIONS
```

## AI Architecture

### AI Processing Pipeline

```mermaid
graph TD
    subgraph "Input Processing"
        TEXT_INPUT[Challenge Text]
        MEDIA_INPUT[Media Files]
        LOCATION[Geographic Data]
    end
    
    subgraph "AI Analysis Pipeline"
        PREPROCESSING[Text Preprocessing<br/>- Language Detection<br/>- Normalization<br/>- Cleaning]
        
        CLASSIFICATION[Problem Classification<br/>- Category Assignment<br/>- Urgency Scoring<br/>- Complexity Analysis]
        
        SKILL_EXTRACTION[Skill Extraction<br/>- Required Expertise<br/>- Technical Skills<br/>- Domain Knowledge]
        
        EMBEDDING[Embedding Generation<br/>- Semantic Vectors<br/>- Similarity Encoding]
        
        MATCHING[University Matching<br/>- Capability Matching<br/>- Faculty Expertise<br/>- Resource Availability]
        
        DUPLICATE_DETECTION[Duplicate Detection<br/>- Semantic Similarity<br/>- Geographic Proximity<br/>- Temporal Analysis]
    end
    
    subgraph "Output Generation"
        STRUCTURED_DATA[Structured Challenge Data]
        RECOMMENDATIONS[University Recommendations]
        INSIGHTS[AI-Generated Insights]
    end
    
    TEXT_INPUT --> PREPROCESSING
    MEDIA_INPUT --> PREPROCESSING
    LOCATION --> PREPROCESSING
    
    PREPROCESSING --> CLASSIFICATION
    CLASSIFICATION --> SKILL_EXTRACTION
    SKILL_EXTRACTION --> EMBEDDING
    
    EMBEDDING --> MATCHING
    EMBEDDING --> DUPLICATE_DETECTION
    
    MATCHING --> RECOMMENDATIONS
    CLASSIFICATION --> STRUCTURED_DATA
    SKILL_EXTRACTION --> INSIGHTS
```

### AI Service Integration

```mermaid
graph TD
    subgraph "AI Services"
        LLM[Large Language Models<br/>OpenAI GPT-4]
        EMBEDDING_MODEL[Embedding Models<br/>text-embedding-ada-002]
        CLASSIFIER[Classification Models<br/>Custom Fine-tuned]
    end
    
    subgraph "AI Processing Layer"
        TEXT_PROCESSOR[Text Processing Service]
        EMBEDDING_SVC[Embedding Service]
        CLASSIFICATION_SVC[Classification Service]
        MATCHING_ENGINE[Matching Engine]
    end
    
    subgraph "Data Layer"
        VECTOR_STORE[(Vector Store<br/>pgvector)]
        KNOWLEDGE_BASE[(Knowledge Base<br/>PostgreSQL)]
        MODEL_CACHE[(Model Cache<br/>Redis)]
    end
    
    TEXT_PROCESSOR --> LLM
    EMBEDDING_SVC --> EMBEDDING_MODEL
    CLASSIFICATION_SVC --> CLASSIFIER
    
    EMBEDDING_SVC --> VECTOR_STORE
    MATCHING_ENGINE --> VECTOR_STORE
    CLASSIFICATION_SVC --> KNOWLEDGE_BASE
    
    TEXT_PROCESSOR --> MODEL_CACHE
    EMBEDDING_SVC --> MODEL_CACHE
```

## Security Architecture

### Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API Gateway
    participant Auth as Auth Service
    participant DB as Database
    
    U->>F: Login Request
    F->>A: POST /auth/login
    A->>Auth: Validate Credentials
    Auth->>DB: Check User & Password
    DB-->>Auth: User Data
    Auth-->>A: JWT Tokens
    A-->>F: Access & Refresh Tokens
    F-->>U: Login Success
    
    Note over F: Store tokens securely
    
    U->>F: Protected Resource Request
    F->>A: Request + Access Token
    A->>Auth: Validate Token
    Auth-->>A: User Context + Permissions
    A->>A: Check Authorization
    A-->>F: Resource Data
    F-->>U: Display Data
```

### Security Layers

1. **Network Security**
   - HTTPS everywhere with TLS 1.3
   - CORS configuration for frontend origins
   - Rate limiting per IP and user
   - DDoS protection through reverse proxy

2. **Application Security**
   - Input validation with Pydantic
   - SQL injection prevention via ORM
   - XSS protection through CSP headers
   - CSRF protection for state-changing operations

3. **Authentication Security**
   - JWT tokens with short expiration
   - Refresh token rotation
   - Password hashing with bcrypt
   - Multi-factor authentication (future)

4. **Authorization Security**
   - Role-based access control (RBAC)
   - Resource-level permissions
   - Audit logging for sensitive operations
   - Principle of least privilege

## Scalability & Performance

### Horizontal Scaling Strategy

```mermaid
graph TD
    subgraph "Load Balancer Layer"
        ALB[Application Load Balancer]
    end
    
    subgraph "Application Instances"
        API1[API Instance 1]
        API2[API Instance 2]
        API3[API Instance N]
    end
    
    subgraph "Database Layer"
        DB_PRIMARY[(Primary DB<br/>Read/Write)]
        DB_REPLICA1[(Read Replica 1)]
        DB_REPLICA2[(Read Replica 2)]
    end
    
    subgraph "Caching Layer"
        REDIS_PRIMARY[(Redis Primary)]
        REDIS_REPLICA[(Redis Replica)]
    end
    
    subgraph "Background Processing"
        CELERY1[Celery Worker 1]
        CELERY2[Celery Worker 2]
        QUEUE[(Task Queue<br/>Redis)]
    end
    
    ALB --> API1
    ALB --> API2
    ALB --> API3
    
    API1 --> DB_PRIMARY
    API1 --> DB_REPLICA1
    API2 --> DB_PRIMARY
    API2 --> DB_REPLICA2
    API3 --> DB_PRIMARY
    API3 --> DB_REPLICA1
    
    API1 --> REDIS_PRIMARY
    API2 --> REDIS_PRIMARY
    API3 --> REDIS_PRIMARY
    
    API1 --> QUEUE
    API2 --> QUEUE
    API3 --> QUEUE
    
    CELERY1 --> QUEUE
    CELERY2 --> QUEUE
    
    CELERY1 --> DB_PRIMARY
    CELERY2 --> DB_PRIMARY
```

### Performance Optimization Strategies

1. **Database Optimization**
   - Query optimization with proper indexing
   - Connection pooling for efficient resource usage
   - Read replicas for query distribution
   - Materialized views for complex analytics

2. **Caching Strategy**
   - API response caching for expensive operations
   - Database query result caching
   - Static asset caching with CDN
   - Application-level caching for reference data

3. **Async Processing**
   - Background jobs for AI analysis
   - Async email and notification sending
   - Batch processing for bulk operations
   - Event-driven architecture for loose coupling

## Deployment Architecture

### Container Architecture

```mermaid
graph TD
    subgraph "Container Orchestration"
        subgraph "Frontend Containers"
            NEXT1[Next.js App 1]
            NEXT2[Next.js App 2]
        end
        
        subgraph "Backend Containers"
            API1[FastAPI App 1]
            API2[FastAPI App 2]
            WORKER1[Celery Worker 1]
            WORKER2[Celery Worker 2]
        end
        
        subgraph "Database Containers"
            POSTGRES[(PostgreSQL)]
            REDIS[(Redis)]
        end
        
        subgraph "Infrastructure"
            NGINX[Nginx Reverse Proxy]
            MONITOR[Monitoring Stack]
        end
    end
    
    NGINX --> NEXT1
    NGINX --> NEXT2
    NGINX --> API1
    NGINX --> API2
    
    API1 --> POSTGRES
    API2 --> POSTGRES
    API1 --> REDIS
    API2 --> REDIS
    
    WORKER1 --> POSTGRES
    WORKER1 --> REDIS
    WORKER2 --> POSTGRES
    WORKER2 --> REDIS
    
    MONITOR --> API1
    MONITOR --> API2
    MONITOR --> POSTGRES
    MONITOR --> REDIS
```

### Environment Strategy

1. **Development Environment**
   - Docker Compose for local development
   - Hot reloading for rapid iteration
   - Local database and Redis instances
   - Mock external services

2. **Staging Environment**
   - Production-like environment for testing
   - CI/CD pipeline integration
   - Performance and load testing
   - Security scanning

3. **Production Environment**
   - Kubernetes orchestration
   - Auto-scaling based on metrics
   - Multi-zone deployment for high availability
   - Comprehensive monitoring and alerting

## Integration Architecture

### External Service Integration

```mermaid
graph TD
    subgraph "SamadhanX Core"
        API[FastAPI Backend]
    end
    
    subgraph "AI/ML Services"
        OPENAI[OpenAI API]
        CUSTOM_ML[Custom ML Models]
    end
    
    subgraph "Communication Services"
        EMAIL_SVC[Email Service<br/>SMTP/SendGrid]
        SMS_SVC[SMS Gateway]
        PUSH[Push Notifications]
    end
    
    subgraph "Geographic Services"
        MAPS[Maps API<br/>Google/OpenStreetMap]
        GEOCODING[Geocoding Service]
    end
    
    subgraph "Storage Services"
        S3[Object Storage<br/>AWS S3/MinIO]
        CDN[Content Delivery Network]
    end
    
    subgraph "Monitoring Services"
        LOGGING[Centralized Logging]
        METRICS[Metrics Collection]
        ALERTS[Alerting System]
    end
    
    API --> OPENAI
    API --> CUSTOM_ML
    API --> EMAIL_SVC
    API --> SMS_SVC
    API --> MAPS
    API --> S3
    
    API --> LOGGING
    API --> METRICS
    
    METRICS --> ALERTS
    S3 --> CDN
```

### API Integration Patterns

1. **Synchronous Integration**
   - REST API calls for real-time operations
   - Circuit breaker pattern for resilience
   - Timeout and retry mechanisms
   - Response caching where appropriate

2. **Asynchronous Integration**
   - Background job processing for heavy operations
   - Event-driven communication
   - Message queues for reliable delivery
   - Webhook support for external systems

## Monitoring & Observability

### Monitoring Stack

```mermaid
graph TD
    subgraph "Application Layer"
        API[FastAPI Application]
        FRONTEND[Next.js Frontend]
    end
    
    subgraph "Metrics Collection"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
    end
    
    subgraph "Logging"
        FLUENTD[Fluentd/Fluent Bit]
        ELASTICSEARCH[Elasticsearch]
        KIBANA[Kibana]
    end
    
    subgraph "Tracing"
        JAEGER[Jaeger]
        OPENTELEMETRY[OpenTelemetry]
    end
    
    subgraph "Alerting"
        ALERTMANAGER[Alert Manager]
        SLACK[Slack Notifications]
        EMAIL[Email Alerts]
    end
    
    API --> PROMETHEUS
    API --> FLUENTD
    API --> OPENTELEMETRY
    FRONTEND --> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTMANAGER
    
    FLUENTD --> ELASTICSEARCH
    ELASTICSEARCH --> KIBANA
    
    OPENTELEMETRY --> JAEGER
    
    ALERTMANAGER --> SLACK
    ALERTMANAGER --> EMAIL
```

### Key Metrics & Alerts

1. **Application Metrics**
   - Request latency and throughput
   - Error rates and status codes
   - Database query performance
   - Cache hit rates

2. **Business Metrics**
   - Challenge submission rates
   - University matching success rates
   - Project completion rates
   - User engagement metrics

3. **Infrastructure Metrics**
   - CPU and memory usage
   - Disk and network I/O
   - Database connection pools
   - Queue depths

## Future Architecture Considerations

### Microservices Migration Path

```mermaid
graph TD
    subgraph "Phase 1: Modular Monolith"
        MONOLITH[Single Application<br/>Multiple Modules]
    end
    
    subgraph "Phase 2: Service Extraction"
        AUTH_SVC[Auth Service]
        CHALLENGE_SVC[Challenge Service]
        MONOLITH_REDUCED[Reduced Monolith]
    end
    
    subgraph "Phase 3: Full Microservices"
        AUTH_MS[Auth Microservice]
        CHALLENGE_MS[Challenge Microservice]
        PROJECT_MS[Project Microservice]
        UNIVERSITY_MS[University Microservice]
        AI_MS[AI Microservice]
    end
    
    MONOLITH --> AUTH_SVC
    MONOLITH --> CHALLENGE_SVC
    MONOLITH --> MONOLITH_REDUCED
    
    AUTH_SVC --> AUTH_MS
    CHALLENGE_SVC --> CHALLENGE_MS
    MONOLITH_REDUCED --> PROJECT_MS
    MONOLITH_REDUCED --> UNIVERSITY_MS
    MONOLITH_REDUCED --> AI_MS
```

### Technology Evolution

1. **Short Term (6-12 months)**
   - Enhanced AI capabilities
   - Real-time features with WebSockets
   - Mobile application development
   - Advanced analytics and reporting

2. **Medium Term (1-2 years)**
   - Microservices extraction
   - Event-driven architecture
   - Multi-tenant capabilities
   - Advanced caching strategies

3. **Long Term (2+ years)**
   - Multi-cloud deployment
   - AI/ML model serving platform
   - Blockchain integration for transparency
   - IoT device integration

## Conclusion

The SamadhanX architecture is designed to be:

- **Scalable**: Horizontal scaling with load balancing and database replicas
- **Maintainable**: Clean separation of concerns with modular design
- **Secure**: Multi-layer security with comprehensive authentication and authorization
- **Observable**: Comprehensive monitoring and logging for operational excellence
- **Extensible**: Clear migration path to microservices as the system grows

The modular monolith approach provides the right balance between simplicity and scalability for the initial MVP while maintaining clear boundaries for future architectural evolution.