# SamadhanX API Documentation

## Overview

The SamadhanX API is a RESTful web service built with FastAPI that provides endpoints for managing the complete challenge-to-solution lifecycle. The API follows OpenAPI 3.0 specification and includes comprehensive input validation, authentication, and error handling.

## Base Configuration

- **Base URL**: `https://api.samadhanx.gov.in` (Production)
- **Base URL**: `http://localhost:8000` (Development)
- **API Version**: v1
- **Documentation**: `/docs` (Swagger UI) and `/redoc` (ReDoc)

## Authentication

### JWT Token-Based Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com", 
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Token Usage

Include the access token in all authenticated requests:

```http
Authorization: Bearer {access_token}
```

### Token Refresh

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## API Structure

### 1. Authentication & User Management (`/api/v1/auth`, `/api/v1/users`)
### 2. Challenge Management (`/api/v1/challenges`)
### 3. University System (`/api/v1/universities`)
### 4. Project Management (`/api/v1/projects`)
### 5. Industry Partnerships (`/api/v1/industry`)
### 6. Analytics & Reporting (`/api/v1/analytics`)
### 7. Notifications (`/api/v1/notifications`)
### 8. File Management (`/api/v1/uploads`)

## Common Response Patterns

### Success Response
```json
{
  "data": {...},
  "message": "Operation completed successfully",
  "success": true
}
```

### Error Response
```json
{
  "message": "Validation failed",
  "success": false,
  "errors": {
    "email": ["Invalid email format"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false
}
```
## 1. Authentication & User Management

### Authentication Endpoints

#### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:** JWT tokens with user profile

#### Register
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "phone": "string",
  "role": "CITIZEN|GOVERNMENT_OFFICER|FACULTY|STUDENT|INDUSTRY",
  "organization": "string"
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
```

#### Logout
```http
POST /api/v1/auth/logout
```

#### Password Reset
```http
POST /api/v1/auth/reset-password
```

**Request Body:**
```json
{
  "email": "string"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
```

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

### User Management Endpoints

#### Get Current User Profile
```http
GET /api/v1/users/me
```

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "phone": "string",
    "avatar_url": "string",
    "roles": ["CITIZEN"],
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Update User Profile
```http
PUT /api/v1/users/me
```

#### Upload Avatar
```http
POST /api/v1/users/me/avatar
Content-Type: multipart/form-data
```

#### Get User by ID
```http
GET /api/v1/users/{user_id}
```

#### List Users (Admin only)
```http
GET /api/v1/users?page=1&page_size=20&role=CITIZEN&search=john
```
## 2. Challenge Management

### Challenge Endpoints

#### List Challenges
```http
GET /api/v1/challenges?page=1&page_size=20&status=SUBMITTED&city=Ranchi&category=water-management
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `status` (string): Filter by status
- `priority` (string): Filter by priority
- `city` (string): Filter by city
- `state` (string): Filter by state
- `category` (string): Filter by category
- `submitted_by` (uuid): Filter by submitter
- `assigned_to` (uuid): Filter by assignee
- `date_from` (date): Filter from date
- `date_to` (date): Filter to date
- `search` (string): Search in title and description

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Water shortage in Gumla district",
      "description": "Severe water crisis affecting 50+ villages...",
      "status": "SUBMITTED",
      "priority": "HIGH",
      "location_description": "Gumla District, Jharkhand",
      "city": "Gumla",
      "state": "Jharkhand",
      "latitude": 23.0442,
      "longitude": 84.5406,
      "categories": ["Water Management", "Rural Development"],
      "submitted_by": {
        "id": "uuid",
        "name": "John Doe",
        "role": "CITIZEN"
      },
      "media_urls": ["https://storage.../image1.jpg"],
      "ai_analysis": {
        "urgency_score": 8.5,
        "complexity_score": 6.2,
        "estimated_timeline": "6-12 months"
      },
      "submission_date": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

#### Create Challenge
```http
POST /api/v1/challenges
Content-Type: multipart/form-data
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "location_description": "string",
  "city": "string",
  "state": "string",
  "pincode": "string",
  "latitude": 0.0,
  "longitude": 0.0,
  "category_ids": ["uuid"],
  "estimated_impact": "LOCAL|REGIONAL|STATE|NATIONAL",
  "affected_population": 1000,
  "media_files": ["file1.jpg", "file2.pdf"]
}
```

#### Get Challenge Details
```http
GET /api/v1/challenges/{challenge_id}
```

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "title": "string",
    "description": "string",
    "status": "SUBMITTED",
    "priority": "HIGH",
    "location_details": {...},
    "categories": [...],
    "media": [...],
    "ai_analysis": {...},
    "projects": [...],
    "university_matches": [...],
    "timeline": [...],
    "submitted_by": {...}
  }
}
```

#### Update Challenge
```http
PUT /api/v1/challenges/{challenge_id}
```

#### Submit Challenge for Review
```http
POST /api/v1/challenges/{challenge_id}/submit
```

#### Validate Challenge (Government Officer)
```http
POST /api/v1/challenges/{challenge_id}/validate
```

**Request Body:**
```json
{
  "status": "VALIDATED|REJECTED",
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "review_notes": "string",
  "category_updates": ["uuid"]
}
```

#### Assign Challenge to University
```http
POST /api/v1/challenges/{challenge_id}/assign
```

**Request Body:**
```json
{
  "university_id": "uuid",
  "assignment_notes": "string",
  "response_deadline": "2024-02-15T23:59:59Z"
}
```
### Challenge Categories

#### List Categories
```http
GET /api/v1/challenges/categories?parent_id=uuid&level=1&active_only=true
```

#### Create Category (Admin only)
```http
POST /api/v1/challenges/categories
```

#### Duplicate Detection
```http
POST /api/v1/challenges/duplicate-check
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "location": "string"
}
```

**Response:**
```json
{
  "data": {
    "has_duplicates": true,
    "similar_challenges": [
      {
        "challenge_id": "uuid",
        "title": "string",
        "similarity_score": 0.85,
        "similarity_reasons": ["Similar location", "Similar keywords"]
      }
    ]
  }
}
```

### Challenge Media

#### Upload Challenge Media
```http
POST /api/v1/challenges/{challenge_id}/media
Content-Type: multipart/form-data
```

#### Get Challenge Media
```http
GET /api/v1/challenges/{challenge_id}/media
```

#### Delete Challenge Media
```http
DELETE /api/v1/challenges/{challenge_id}/media/{media_id}
```

## 3. University System

### University Endpoints

#### List Universities
```http
GET /api/v1/universities?city=Ranchi&type=PUBLIC&has_expertise=water-management
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Indian Institute of Technology (ISM) Dhanbad",
      "short_name": "IIT(ISM)",
      "city": "Dhanbad",
      "state": "Jharkhand",
      "university_type": "PUBLIC",
      "established_year": 1926,
      "logo_url": "https://...",
      "website": "https://iitism.ac.in",
      "total_students": 8000,
      "total_faculty": 400,
      "expertise_areas": ["Engineering", "Technology", "Research"],
      "active_projects": 15,
      "completed_projects": 45
    }
  ]
}
```

#### Get University Details
```http
GET /api/v1/universities/{university_id}
```

#### Get University Capabilities
```http
GET /api/v1/universities/{university_id}/capabilities
```

**Response:**
```json
{
  "data": {
    "expertise_areas": [
      {
        "expertise_id": "uuid",
        "name": "Water Resource Management",
        "category": "Environmental Engineering", 
        "proficiency_level": "EXPERT",
        "faculty_count": 12,
        "recent_projects": 8,
        "facilities": ["Water Testing Lab", "Hydrology Research Center"]
      }
    ],
    "departments": [...],
    "facilities": [...],
    "research_centers": [...]
  }
}
```

### Department Management

#### List Departments
```http
GET /api/v1/universities/{university_id}/departments
```

#### Get Department Details
```http
GET /api/v1/universities/{university_id}/departments/{department_id}
```

### Faculty Management

#### List Faculty
```http
GET /api/v1/universities/{university_id}/faculty?department_id=uuid&expertise=ai&available=true
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "name": "Dr. Priya Sharma",
        "email": "priya.sharma@iitism.ac.in"
      },
      "designation": "Associate Professor",
      "department": "Computer Science",
      "expertise_areas": ["Machine Learning", "Data Science"],
      "research_interests": ["AI in Healthcare", "NLP"],
      "experience_years": 12,
      "current_projects": 2,
      "max_projects": 3,
      "is_available": true,
      "publications": 45
    }
  ]
}
```

#### Get Faculty Details
```http
GET /api/v1/universities/{university_id}/faculty/{faculty_id}
```

### Student Management

#### List Students
```http
GET /api/v1/universities/{university_id}/students?department_id=uuid&program=B.Tech&year=3&available=true
```

#### Get Student Details
```http
GET /api/v1/universities/{university_id}/students/{student_id}
```
## 4. Project Management

### Project Endpoints

#### List Projects
```http
GET /api/v1/projects?status=ACTIVE&university_id=uuid&challenge_id=uuid&team_member=uuid
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Smart Water Distribution System",
      "description": "IoT-based water management solution...",
      "status": "PROTOTYPE",
      "challenge": {
        "id": "uuid",
        "title": "Water shortage in Gumla district"
      },
      "university": {
        "id": "uuid", 
        "name": "IIT(ISM) Dhanbad"
      },
      "team_lead": {
        "id": "uuid",
        "name": "Rahul Kumar",
        "role": "STUDENT"
      },
      "faculty_advisor": {
        "id": "uuid",
        "name": "Dr. Priya Sharma"
      },
      "team_size": 8,
      "start_date": "2024-02-01",
      "expected_end_date": "2024-08-31",
      "completion_percentage": 65.0,
      "total_budget": 500000.00,
      "funding_received": 300000.00
    }
  ]
}
```

#### Create Project
```http
POST /api/v1/projects
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string", 
  "challenge_id": "uuid",
  "university_id": "uuid",
  "department_id": "uuid",
  "project_type": "RESEARCH|DEVELOPMENT|INNOVATION",
  "estimated_budget": 500000.00,
  "start_date": "2024-02-01",
  "expected_end_date": "2024-08-31",
  "methodology": "string",
  "expected_outcomes": "string",
  "success_metrics": ["string"]
}
```

#### Get Project Details
```http
GET /api/v1/projects/{project_id}
```

#### Update Project
```http
PUT /api/v1/projects/{project_id}
```

#### Update Project Status
```http
POST /api/v1/projects/{project_id}/status
```

**Request Body:**
```json
{
  "status": "PROTOTYPE|TESTING|PILOT|DEPLOYED|COMPLETED",
  "notes": "string",
  "completion_percentage": 75.0
}
```

### Project Team Management

#### List Project Members
```http
GET /api/v1/projects/{project_id}/members
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "name": "Rahul Kumar",
        "email": "rahul@student.iitism.ac.in"
      },
      "role": "LEAD",
      "responsibilities": "Overall project coordination and development",
      "expertise_contribution": ["Full-stack Development", "IoT"],
      "joined_at": "2024-02-01T00:00:00Z",
      "is_active": true,
      "hours_per_week": 20,
      "total_hours_contributed": 240
    }
  ]
}
```

#### Add Project Member
```http
POST /api/v1/projects/{project_id}/members
```

**Request Body:**
```json
{
  "user_id": "uuid",
  "role": "LEAD|CO_LEAD|MEMBER|ADVISOR",
  "responsibilities": "string",
  "expertise_contribution": ["string"],
  "hours_per_week": 15
}
```

#### Update Project Member
```http
PUT /api/v1/projects/{project_id}/members/{member_id}
```

#### Remove Project Member
```http
DELETE /api/v1/projects/{project_id}/members/{member_id}
```

### Project Milestones

#### List Project Milestones
```http
GET /api/v1/projects/{project_id}/milestones?status=IN_PROGRESS
```

#### Create Milestone
```http
POST /api/v1/projects/{project_id}/milestones
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "planned_start_date": "2024-03-01",
  "planned_end_date": "2024-03-31",
  "priority": "HIGH",
  "order_sequence": 1,
  "assigned_to": ["uuid"],
  "expected_deliverables": ["string"],
  "success_criteria": "string"
}
```

#### Update Milestone
```http
PUT /api/v1/projects/{project_id}/milestones/{milestone_id}
```

#### Complete Milestone
```http
POST /api/v1/projects/{project_id}/milestones/{milestone_id}/complete
```
### Project Deliverables

#### List Project Deliverables
```http
GET /api/v1/projects/{project_id}/deliverables?milestone_id=uuid&status=APPROVED
```

#### Submit Deliverable
```http
POST /api/v1/projects/{project_id}/deliverables
Content-Type: multipart/form-data
```

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "deliverable_type": "DOCUMENT|PROTOTYPE|CODE|REPORT|DEMO",
  "milestone_id": "uuid",
  "file": "file",
  "version_number": "1.0",
  "is_public": false
}
```

#### Review Deliverable
```http
POST /api/v1/projects/{project_id}/deliverables/{deliverable_id}/review
```

**Request Body:**
```json
{
  "status": "APPROVED|REJECTED|NEEDS_REVISION",
  "review_notes": "string"
}
```

### Project Proposals

#### Get Project Proposal
```http
GET /api/v1/projects/{project_id}/proposal
```

#### Submit Project Proposal
```http
POST /api/v1/projects/{project_id}/proposal
```

**Request Body:**
```json
{
  "executive_summary": "string",
  "problem_statement": "string", 
  "proposed_solution": "string",
  "methodology": "string",
  "timeline": "string",
  "budget_breakdown": {
    "personnel": 200000,
    "equipment": 150000,
    "materials": 100000,
    "overhead": 50000
  },
  "expected_outcomes": "string",
  "risk_assessment": "string",
  "sustainability_plan": "string"
}
```

#### Update Proposal Status
```http
POST /api/v1/projects/{project_id}/proposal/review
```

## 5. Industry Partnerships

### Industry Partner Endpoints

#### List Industry Partners
```http
GET /api/v1/industry/partners?industry_type=IT&company_size=LARGE&csr_focus=education
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Tata Consultancy Services",
      "industry_type": "IT Services",
      "company_size": "LARGE",
      "website": "https://tcs.com",
      "logo_url": "https://...",
      "expertise_areas": ["Software Development", "AI/ML", "Data Analytics"],
      "csr_focus_areas": ["Education", "Healthcare", "Environment"],
      "collaboration_types": ["FUNDING", "MENTORSHIP", "DEPLOYMENT"],
      "active_partnerships": 12,
      "total_funding_provided": 5000000.00
    }
  ]
}
```

#### Create Industry Partner Profile
```http
POST /api/v1/industry/partners
```

#### Get Industry Partner Details
```http
GET /api/v1/industry/partners/{partner_id}
```

### Partnership Management

#### List Partnerships
```http
GET /api/v1/industry/partnerships?project_id=uuid&partner_id=uuid&status=ACTIVE
```

#### Create Partnership Proposal
```http
POST /api/v1/industry/partnerships
```

**Request Body:**
```json
{
  "project_id": "uuid",
  "industry_partner_id": "uuid",
  "partnership_type": "FUNDING|MENTORSHIP|RESOURCES|DEPLOYMENT",
  "title": "string",
  "description": "string",
  "start_date": "2024-03-01",
  "end_date": "2024-12-31",
  "total_value": 1000000.00,
  "industry_obligations": ["string"],
  "university_obligations": ["string"]
}
```

#### Update Partnership Status
```http
POST /api/v1/industry/partnerships/{partnership_id}/status
```

### Funding Management

#### List Funding
```http
GET /api/v1/industry/funding?project_id=uuid&status=DISBURSED
```

#### Create Funding Agreement
```http
POST /api/v1/industry/funding
```

#### Update Funding Status
```http
POST /api/v1/industry/funding/{funding_id}/disburse
```

### Mentorship Management

#### List Mentorships
```http
GET /api/v1/industry/mentorships?project_id=uuid&mentor_id=uuid&status=ACTIVE
```

#### Create Mentorship
```http
POST /api/v1/industry/mentorships
```

#### Log Mentorship Session
```http
POST /api/v1/industry/mentorships/{mentorship_id}/sessions
```

**Request Body:**
```json
{
  "session_date": "2024-03-15T14:00:00Z",
  "duration_hours": 2.0,
  "topics_discussed": ["string"],
  "next_steps": "string",
  "mentor_notes": "string",
  "mentee_feedback": "string"
}
```
## 6. Analytics & Reporting

### Dashboard Analytics

#### Get Dashboard Overview
```http
GET /api/v1/analytics/dashboard?date_from=2024-01-01&date_to=2024-12-31&role=GOVERNMENT_OFFICER
```

**Response:**
```json
{
  "data": {
    "summary": {
      "total_challenges": 1247,
      "active_projects": 156,
      "completed_projects": 89,
      "participating_universities": 23,
      "industry_partnerships": 45,
      "total_funding": 15000000.00
    },
    "trends": {
      "monthly_submissions": [
        {"month": "2024-01", "challenges": 95, "projects": 12},
        {"month": "2024-02", "challenges": 108, "projects": 15}
      ],
      "status_distribution": {
        "SUBMITTED": 312,
        "VALIDATED": 189,
        "PROJECT_CREATED": 156,
        "COMPLETED": 89
      }
    },
    "geographic_data": [
      {
        "location": "Ranchi",
        "challenges": 245,
        "projects": 34,
        "coordinates": [23.3441, 85.3096]
      }
    ],
    "category_breakdown": [
      {"category": "Water Management", "count": 234, "percentage": 18.8},
      {"category": "Healthcare", "count": 189, "percentage": 15.2}
    ]
  }
}
```

#### Get University Performance
```http
GET /api/v1/analytics/universities?university_id=uuid&metrics=completion_rate,avg_duration
```

#### Get Challenge Analytics
```http
GET /api/v1/analytics/challenges?group_by=category,status&period=quarterly
```

#### Get Impact Metrics
```http
GET /api/v1/analytics/impact?project_id=uuid&metric_category=SOCIAL
```

### Report Generation

#### Generate Custom Report
```http
POST /api/v1/analytics/reports
```

**Request Body:**
```json
{
  "report_type": "CHALLENGE_SUMMARY|PROJECT_PERFORMANCE|IMPACT_ASSESSMENT",
  "filters": {
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "universities": ["uuid"],
    "categories": ["uuid"],
    "status": ["COMPLETED"]
  },
  "format": "PDF|EXCEL|CSV",
  "include_charts": true,
  "delivery_method": "DOWNLOAD|EMAIL"
}
```

#### Get Report Status
```http
GET /api/v1/analytics/reports/{report_id}
```

#### Download Report
```http
GET /api/v1/analytics/reports/{report_id}/download
```

### Data Export

#### Export Challenge Data
```http
GET /api/v1/analytics/export/challenges?format=CSV&filters=...
```

#### Export Project Data  
```http
GET /api/v1/analytics/export/projects?format=EXCEL&date_from=2024-01-01
```

## 7. Notifications

### Notification Management

#### List User Notifications
```http
GET /api/v1/notifications?is_read=false&category=CHALLENGE_UPDATE&page=1
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Challenge Status Updated",
      "message": "Your challenge 'Water shortage in Gumla' has been validated and assigned to IIT(ISM) Dhanbad.",
      "notification_type": "SUCCESS",
      "category": "CHALLENGE_UPDATE",
      "priority": "MEDIUM",
      "is_read": false,
      "action_url": "/challenges/uuid",
      "action_text": "View Challenge",
      "created_at": "2024-03-15T10:30:00Z"
    }
  ]
}
```

#### Mark Notification as Read
```http
POST /api/v1/notifications/{notification_id}/read
```

#### Mark All Notifications as Read
```http
POST /api/v1/notifications/read-all
```

#### Delete Notification
```http
DELETE /api/v1/notifications/{notification_id}
```

### Notification Preferences

#### Get Notification Preferences
```http
GET /api/v1/notifications/preferences
```

**Response:**
```json
{
  "data": {
    "email_notifications": true,
    "sms_notifications": false,
    "push_notifications": true,
    "categories": {
      "CHALLENGE_UPDATE": {"email": true, "sms": false, "push": true},
      "PROJECT_MILESTONE": {"email": true, "sms": false, "push": true},
      "PARTNERSHIP_PROPOSAL": {"email": true, "sms": true, "push": true}
    },
    "frequency": "IMMEDIATE",
    "quiet_hours": {
      "enabled": true,
      "start_time": "22:00",
      "end_time": "07:00"
    }
  }
}
```

#### Update Notification Preferences
```http
PUT /api/v1/notifications/preferences
```

## 8. File Management

### File Upload

#### Upload File
```http
POST /api/v1/uploads/file
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <binary>
folder: "challenges" | "projects" | "profiles" | "documents"
```

**Response:**
```json
{
  "data": {
    "file_id": "uuid",
    "filename": "generated_filename.jpg",
    "original_name": "user_uploaded_file.jpg",
    "file_url": "https://storage.samadhanx.gov.in/challenges/uuid/filename.jpg",
    "file_size": 2048576,
    "mime_type": "image/jpeg",
    "upload_status": "SUCCESS"
  }
}
```

#### Upload Multiple Files
```http
POST /api/v1/uploads/batch
Content-Type: multipart/form-data
```

#### Get File Metadata
```http
GET /api/v1/uploads/{file_id}
```

#### Delete File
```http
DELETE /api/v1/uploads/{file_id}
```
## HTTP Status Codes

The API uses conventional HTTP response codes:

### Success Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully  
- `204 No Content` - Request successful, no response body

### Client Error Codes
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error` - Server error
- `502 Bad Gateway` - Upstream service error
- `503 Service Unavailable` - Service temporarily unavailable

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Authenticated users**: 100 requests per minute
- **Anonymous users**: 20 requests per minute
- **File uploads**: 10 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Validation Errors
```json
{
  "message": "Validation failed",
  "success": false,
  "errors": {
    "email": ["Invalid email format", "Email already exists"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

### Authentication Errors
```json
{
  "message": "Invalid credentials",
  "success": false,
  "error_code": "INVALID_CREDENTIALS"
}
```

### Authorization Errors
```json
{
  "message": "Insufficient permissions to access this resource",
  "success": false,
  "error_code": "INSUFFICIENT_PERMISSIONS",
  "details": {
    "required_role": "GOVERNMENT_OFFICER",
    "user_roles": ["CITIZEN"]
  }
}
```

### Not Found Errors
```json
{
  "message": "Challenge not found",
  "success": false,
  "error_code": "RESOURCE_NOT_FOUND"
}
```

## Pagination

All list endpoints support pagination with consistent parameters:

### Request Parameters
- `page` (int): Page number (1-based, default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)

### Response Format
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_previous": false
}
```

### Navigation Links
Response headers include navigation links:
```http
Link: <https://api.samadhanx.gov.in/challenges?page=2>; rel="next",
      <https://api.samadhanx.gov.in/challenges?page=8>; rel="last"
```

## Search and Filtering

### Full-Text Search
Use the `search` parameter for text-based search:
```http
GET /api/v1/challenges?search=water shortage rural
```

### Multiple Filters
Combine multiple filter parameters:
```http
GET /api/v1/challenges?status=VALIDATED&priority=HIGH&city=Ranchi&date_from=2024-01-01
```

### Sorting
Use `sort_by` and `sort_order` parameters:
```http
GET /api/v1/challenges?sort_by=submission_date&sort_order=desc
```

## Webhooks (Future Implementation)

### Webhook Events
- `challenge.created`
- `challenge.status_changed` 
- `project.milestone_completed`
- `partnership.approved`

### Webhook Payload
```json
{
  "event": "challenge.status_changed",
  "data": {
    "challenge_id": "uuid",
    "old_status": "SUBMITTED",
    "new_status": "VALIDATED"
  },
  "timestamp": "2024-03-15T10:30:00Z"
}
```

## API Versioning

### URL Versioning
Current version is included in the URL: `/api/v1/`

### Version Support
- `v1` - Current stable version
- `v2` - Future version (when available)

### Deprecation Policy
- 6 months notice before deprecation
- 12 months support for deprecated versions
- Clear migration guides provided

## SDK and Client Libraries (Future)

### Official SDKs
- Python SDK
- JavaScript/TypeScript SDK
- React Query hooks

### Community Libraries
- Support for additional languages
- Framework-specific integrations

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
- **Development**: `http://localhost:8000/docs`
- **Production**: `https://api.samadhanx.gov.in/docs`

### API Documentation Formats
- **Swagger UI**: Interactive API explorer
- **ReDoc**: Clean, responsive documentation
- **OpenAPI JSON**: Machine-readable specification

## Testing and Development

### Test Environment
- **Base URL**: `https://api-staging.samadhanx.gov.in`
- **Test data**: Available for development and testing
- **Reset schedule**: Daily at 00:00 UTC

### Sandbox Accounts
- Test user accounts with different roles
- Sample data for all entity types
- No rate limiting in test environment

### API Client Testing
Use tools like Postman, curl, or httpie:

```bash
# Get challenges
curl -H "Authorization: Bearer <token>" \
     https://api.samadhanx.gov.in/api/v1/challenges

# Create challenge
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test Challenge","description":"..."}' \
     https://api.samadhanx.gov.in/api/v1/challenges
```

This API documentation provides a comprehensive reference for integrating with the SamadhanX platform. For specific implementation details and examples, refer to the interactive API documentation available at the `/docs` endpoint.