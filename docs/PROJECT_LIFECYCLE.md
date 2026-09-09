# Project & Solution Lifecycle Management

## Overview

The Project Lifecycle Management module enables universities to convert accepted challenge assignments into structured projects with team management, proposal workflows, milestone tracking, and impact measurement.

This document describes the complete project lifecycle implementation for SamadhanX.

## Architecture

### Components

1. **Project Service** (`project_service.py`)
   - Project CRUD operations
   - Project code generation
   - Status management
   - Dashboard aggregation

2. **Team Service** (`team_service.py`)
   - Team member management
   - Role assignment
   - Cross-university validation

3. **Proposal Service** (`proposal_service.py`)
   - Proposal workflow (draft→submit→approve/reject/revise)
   - Government approval process
   - Human-in-the-loop validation

4. **Milestone Service** (`milestone_service.py`)
   - Milestone creation and tracking
   - Sequence management
   - Completion workflow

5. **Impact Service** (`impact_service.py`)
   - Impact measurement
   - Government verification
   - Evidence tracking

6. **Lifecycle Manager** (`lifecycle.py`)
   - 11-state state machine
   - Transition validation
   - Terminal state handling

### Database Models

#### Project
- `project_code`: Unique code (PRJ-JH-YYYY-XXXXX)
- `challenge_id`: Reference to parent challenge
- `university_id`: Owning university
- `department_id`: Optional department
- `status`: Current lifecycle status
- `created_by`: Creator user ID
- `start_date`, `expected_end_date`, `actual_end_date`

#### ProjectMember
- `project_id`: Project reference
- `user_id`: Team member
- `role`: TEAM_LEAD, DEVELOPER, TESTER, RESEARCHER, DOCUMENTATION

#### ProjectProposal
- `project_id`: Project reference
- `title`, `summary`, `problem_statement`, `proposed_solution`
- `innovation`, `expected_outcomes`, `beneficiaries`
- `status`: DRAFT, SUBMITTED, APPROVED, REJECTED, REVISION_REQUESTED, WITHDRAWN
- `submitted_by`, `reviewed_by`, `review_comments`

#### ProjectMilestone
- `project_id`: Project reference
- `title`, `description`, `sequence_number`
- `status`: PLANNED, IN_PROGRESS, COMPLETED, DELAYED, CANCELLED
- `planned_start_date`, `planned_end_date`
- `actual_start_date`, `actual_end_date`
- `evidence`, `notes`

#### ImpactMetric
- `project_id`: Project reference
- `metric_name`: Name of metric
- `beneficiaries_count`, `geographic_area`, `deployment_date`
- `baseline_value`, `target_value`, `actual_value`, `unit`
- `impact_description`, `evidence_reference`
- `verification_status`: PENDING, VERIFIED, REJECTED
- `submitted_by`, `verified_by`, `verified_at`, `review_comments`

## Project Creation Rules

### Prerequisites
1. Challenge must be VALIDATED
2. University must have an ACCEPTED assignment
3. No active project can exist for this challenge-university pair

### Process
1. Validate challenge exists
2. Verify user's university association
3. Check for ACCEPTED assignment
4. Prevent duplicate active projects
5. Generate unique project code
6. Create project with PLANNING status
7. Update challenge status to PROJECT_CREATED
8. Create audit log
9. Notify government officers

### Project Code Format
```
PRJ-JH-YYYY-XXXXX
```
- `PRJ`: Project prefix
- `JH`: Jharkhand state code
- `YYYY`: Current year
- `XXXXX`: 5-digit sequence number (auto-incremented per year)

Example: `PRJ-JH-2024-00001`

## Lifecycle State Machine

### States (11 total)

1. **PLANNING** - Initial state, project setup
2. **TEAM_FORMATION** - Building team
3. **PROPOSAL** - Drafting proposal
4. **APPROVED** - Proposal approved, ready for development
5. **PROTOTYPE** - Building prototype
6. **TESTING** - Testing phase
7. **PILOT** - Pilot deployment
8. **DEPLOYED** - Production deployment
9. **COMPLETED** - Project finished (terminal)
10. **ON_HOLD** - Temporary pause (from any state)
11. **CANCELLED** - Project cancelled (terminal)

### Valid Transitions

```
PLANNING → TEAM_FORMATION, ON_HOLD, CANCELLED
TEAM_FORMATION → PROPOSAL, PLANNING, ON_HOLD, CANCELLED
PROPOSAL → APPROVED, TEAM_FORMATION, ON_HOLD, CANCELLED
APPROVED → PROTOTYPE, ON_HOLD, CANCELLED
PROTOTYPE → TESTING, APPROVED, ON_HOLD, CANCELLED
TESTING → PILOT, PROTOTYPE, ON_HOLD, CANCELLED
PILOT → DEPLOYED, TESTING, ON_HOLD, CANCELLED
DEPLOYED → COMPLETED, ON_HOLD, CANCELLED
ON_HOLD → (previous state), CANCELLED
COMPLETED → (terminal, no transitions)
CANCELLED → (terminal, no transitions)
```

### Special Rules
- **ON_HOLD** can be reached from any non-terminal state
- **CANCELLED** can be reached from any non-terminal state
- **COMPLETED** and **CANCELLED** are terminal states
- Status transitions are validated by `ProjectLifecycleManager.is_valid_transition()`

## Team Management

### Roles
- **TEAM_LEAD**: Project leader, full permissions
- **DEVELOPER**: Development work
- **TESTER**: Testing activities
- **RESEARCHER**: Research tasks
- **DOCUMENTATION**: Documentation work

### Authorization
- **Add/Remove Members**: Project faculty, university admin
- **Update Roles**: Project faculty, university admin
- **View Team**: Any authorized project viewer

### Rules
- Team members must belong to project's university
- No duplicate memberships
- Cannot remove last team lead

## Proposal Workflow

### States
1. **DRAFT** - Editable by university
2. **SUBMITTED** - Under government review
3. **APPROVED** - Approved by government
4. **REJECTED** - Rejected by government
5. **REVISION_REQUESTED** - Needs revisions
6. **WITHDRAWN** - Withdrawn by university

### Workflow

```
DRAFT → (edit) → SUBMIT → SUBMITTED
SUBMITTED → (govt review) → APPROVED / REJECTED / REVISION_REQUESTED
REVISION_REQUESTED → (edit) → SUBMIT → SUBMITTED
APPROVED → (project continues)
REJECTED → (project may be cancelled or revised)
```

### Human-in-the-Loop
- **Approval**: Only GOVERNMENT_OFFICER can approve
- **Rejection**: Only GOVERNMENT_OFFICER can reject
- **Revision Request**: Only GOVERNMENT_OFFICER can request revisions
- **Comments**: Required for reject and revision requests

### Authorization Matrix

| Action | University Admin | Faculty | Student | Government | Citizen |
|--------|-----------------|---------|---------|------------|---------|
| Create Draft | ✓ | ✓ | ✗ | ✗ | ✗ |
| Edit Draft | ✓ | ✓ | ✗ | ✗ | ✗ |
| Submit | ✓ | ✓ | ✗ | ✗ | ✗ |
| Approve | ✗ | ✗ | ✗ | ✓ | ✗ |
| Reject | ✗ | ✗ | ✗ | ✓ | ✗ |
| Request Revision | ✗ | ✗ | ✗ | ✓ | ✗ |
| View | ✓ | ✓ | ✗ | ✓ | ✗ |

## Milestone Management

### Lifecycle
1. Create milestone with sequence number
2. Mark as IN_PROGRESS when work begins
3. Complete with evidence and notes
4. Track actual dates for completion metrics

### Sequence Management
- Sequence numbers must be unique per project
- Sequence numbers determine milestone order
- Used for "current" and "next" milestone identification

### Completion
- Sets `actual_end_date` to current date
- Changes status to COMPLETED
- Creates audit log
- Updates project completion percentage

### Authorization
- **Create/Edit**: Project team, faculty, university admin
- **Complete**: Project team, faculty, university admin
- **View**: Any authorized project viewer

## Impact Measurement

### Purpose
Track real-world impact of deployed solutions with government verification.

### Separation of Concerns
- **Project Completion**: Technical/implementation success
- **Impact Verification**: Real-world societal impact

A project can be COMPLETED without verified impact.
Impact verification is a separate, government-led process.

### Workflow

```
PENDING → (university edits) → SUBMIT
SUBMITTED → (govt review) → VERIFIED / REJECTED
REJECTED → (university edits) → SUBMIT
```

### Fields
- **Beneficiaries**: Count and description
- **Geographic Area**: Coverage area
- **Deployment Date**: When solution was deployed
- **Baseline/Target/Actual**: Measurable values
- **Evidence**: Reference to supporting evidence
- **Sustainability**: Long-term viability status

### Government Verification
- Only GOVERNMENT_OFFICER can verify impact
- Verification requires field inspection or evidence review
- Comments document verification process
- Students CANNOT verify impact

### Authorization Matrix

| Action | University Admin | Faculty | Student | Government | Citizen |
|--------|-----------------|---------|---------|------------|---------|
| Create/Edit | ✓ | ✓ | ✗ | ✗ | ✗ |
| Submit | ✓ | ✓ | ✗ | ✗ | ✗ |
| Verify | ✗ | ✗ | ✗ | ✓ | ✗ |
| Request Revision | ✗ | ✗ | ✗ | ✓ | ✗ |
| View | ✓ | ✓ | ✗ | ✓ | ✗ |

### Integrity Rules
- Impact cannot be auto-calculated or invented
- VERIFIED status requires government verification
- COMPLETED project status does not imply verified impact
- Evidence references must be traceable

## API Endpoints

### Project Management

#### Create Project
```
POST /api/v1/challenges/{challenge_id}/projects
Authorization: Required (Faculty/University Admin)
```
**Request:**
```json
{
  "name": "Smart Water Management System",
  "description": "IoT-based water quality monitoring",
  "objective": "Improve water quality in rural areas",
  "expected_start_date": "2024-03-01",
  "expected_end_date": "2024-12-31"
}
```

#### List Projects
```
GET /api/v1/projects?status=PLANNING&university_id=...&page=1&page_size=20
Authorization: Required
```
**Authorization:**
- Government/Admin: All projects
- University users: Own university only
- Students: Projects they're members of

#### Get Project Dashboard
```
GET /api/v1/projects/{project_id}
Authorization: Required
```
**Response:**
```json
{
  "project": {...},
  "challenge": {...},
  "university": {...},
  "department": {...},
  "team_count": 5,
  "milestone_count": 8,
  "completed_milestones": 3,
  "completion_percentage": 37.5,
  "current_milestone": {...},
  "next_milestone": {...},
  "impact_summary": {...}
}
```

#### Update Project
```
PATCH /api/v1/projects/{project_id}
Authorization: Required (Team/Faculty/University Admin)
```

#### Update Project Status
```
POST /api/v1/projects/{project_id}/status
Authorization: Required (Faculty/University Admin)
```
**Request:**
```json
{
  "status": "PROTOTYPE",
  "reason": "Proposal approved, starting development"
}
```
**Note:** Validates transition using lifecycle state machine.

### Team Management

#### Add Team Member
```
POST /api/v1/projects/{project_id}/team
Authorization: Required (Faculty/University Admin)
```
**Request:**
```json
{
  "user_id": "uuid",
  "role": "DEVELOPER"
}
```

#### List Team
```
GET /api/v1/projects/{project_id}/team
Authorization: Required
```

#### Update Team Member
```
PATCH /api/v1/projects/{project_id}/team/{member_id}
Authorization: Required (Faculty/University Admin)
```

#### Remove Team Member
```
DELETE /api/v1/projects/{project_id}/team/{member_id}
Authorization: Required (Faculty/University Admin)
```

### Proposal Management

#### Create/Update Proposal
```
POST /api/v1/projects/{project_id}/proposal
Authorization: Required (Faculty/University Admin)
```
**Request:**
```json
{
  "title": "Smart Water Management Proposal",
  "summary": "Executive summary...",
  "problem_statement": "Current challenges...",
  "proposed_solution": "Our approach...",
  "innovation": "Novel aspects...",
  "expected_outcomes": "Expected results...",
  "beneficiaries": "Target communities...",
  "required_resources": "Hardware, software...",
  "implementation_plan": "Phase-wise plan...",
  "risks": "Risk assessment...",
  "sustainability_plan": "Long-term viability...",
  "budget_estimate": 500000.00
}
```

#### Get Proposal
```
GET /api/v1/projects/{project_id}/proposal
Authorization: Required
```

#### Submit Proposal
```
POST /api/v1/projects/{project_id}/proposal/submit
Authorization: Required (Faculty/University Admin)
```

#### Approve Proposal (Government Only)
```
POST /api/v1/projects/{project_id}/proposal/approve
Authorization: Required (Government Officer)
```
**Request:**
```json
{
  "comments": "Approved for implementation. Excellent approach."
}
```

#### Request Revision (Government Only)
```
POST /api/v1/projects/{project_id}/proposal/request-revision
Authorization: Required (Government Officer)
```
**Request:**
```json
{
  "comments": "Please provide more details on sustainability plan."
}
```

#### Reject Proposal (Government Only)
```
POST /api/v1/projects/{project_id}/proposal/reject
Authorization: Required (Government Officer)
```
**Request:**
```json
{
  "comments": "Does not meet technical feasibility requirements."
}
```

### Milestone Management

#### Create Milestone
```
POST /api/v1/projects/{project_id}/milestones
Authorization: Required (Team/Faculty/University Admin)
```
**Request:**
```json
{
  "title": "Requirements Gathering",
  "description": "Gather and document requirements",
  "sequence_number": 1,
  "planned_start_date": "2024-03-01",
  "planned_end_date": "2024-03-15"
}
```

#### List Milestones
```
GET /api/v1/projects/{project_id}/milestones
Authorization: Required
```

#### Update Milestone
```
PATCH /api/v1/projects/{project_id}/milestones/{milestone_id}
Authorization: Required (Team/Faculty/University Admin)
```

#### Complete Milestone
```
POST /api/v1/projects/{project_id}/milestones/{milestone_id}/complete
Authorization: Required (Team/Faculty/University Admin)
```

### Impact Measurement

#### Create/Update Impact
```
POST /api/v1/projects/{project_id}/impact
Authorization: Required (Faculty/University Admin)
```
**Request:**
```json
{
  "metric_name": "Water Quality Improvement",
  "beneficiaries_count": 5000,
  "geographic_area": "Ranchi District - 10 villages",
  "deployment_date": "2024-12-01",
  "baseline_value": 45.0,
  "target_value": 85.0,
  "actual_value": 82.0,
  "unit": "percentage",
  "impact_description": "Improved water quality from 45% to 82% compliance",
  "evidence_reference": "water_quality_report_2024.pdf",
  "sustainability_status": "Operational with local maintenance"
}
```

#### Get Impact Measurements
```
GET /api/v1/projects/{project_id}/impact
Authorization: Required
```

#### Submit Impact
```
POST /api/v1/projects/{project_id}/impact/{impact_id}/submit
Authorization: Required (Faculty/University Admin)
```

#### Verify Impact (Government Only)
```
POST /api/v1/projects/{project_id}/impact/{impact_id}/verify
Authorization: Required (Government Officer)
```
**Request:**
```json
{
  "comments": "Verified through field inspection on 2024-12-15. Impact validated."
}
```

#### Request Revision (Government Only)
```
POST /api/v1/projects/{project_id}/impact/{impact_id}/request-revision
Authorization: Required (Government Officer)
```
**Request:**
```json
{
  "comments": "Need additional evidence for beneficiary count claim."
}
```

## Security & Authorization

### Cross-University Access Prevention
- University users can only access projects from their university
- University ID is extracted from user's faculty/student profile
- Query filters enforce university-level isolation
- Government and platform admin can access all projects

### IDOR Protection
- All endpoints validate project ownership before operations
- Project ID validation includes authorization check
- Team member operations validate both project and member
- Government actions validated by role check

### Role-Based Access Control

| Role | Project Creation | View Projects | Manage Project | Approve Proposal | Verify Impact |
|------|-----------------|---------------|----------------|------------------|---------------|
| Citizen | ✗ | ✗ | ✗ | ✗ | ✗ |
| Student | ✗ | Own teams | ✗ | ✗ | ✗ |
| Faculty | ✓ | Own university | ✓ | ✗ | ✗ |
| University Admin | ✓ | Own university | ✓ | ✗ | ✗ |
| Government Officer | ✗ | All | ✗ | ✓ | ✓ |
| Platform Admin | ✓ | All | ✓ | ✓ | ✓ |

## Transaction Integrity

### Atomic Operations
Project creation coordinates multiple operations:
1. Validate assignment
2. Create project
3. Update challenge status
4. Create audit log
5. Create notifications

All operations wrapped in transaction - rollback on any failure.

### Concurrency Handling
- Duplicate project check uses database constraints
- Project code generation uses latest sequence query
- Team member uniqueness enforced by database constraint
- Milestone sequence uniqueness validated before insert

## Notifications

### Event Types
- `PROJECT_CREATED` - Notify government
- `PROPOSAL_SUBMITTED` - Notify government
- `PROPOSAL_APPROVED` - Notify project team
- `PROPOSAL_REVISION_REQUESTED` - Notify project team
- `PROPOSAL_REJECTED` - Notify project team
- `MILESTONE_COMPLETED` - Notify project team
- `PROJECT_STATUS_CHANGED` - Notify relevant parties
- `PROJECT_DEPLOYED` - Notify government and team
- `PROJECT_COMPLETED` - Notify all stakeholders
- `IMPACT_SUBMITTED` - Notify government
- `IMPACT_VERIFIED` - Notify project team
- `IMPACT_REVISION_REQUESTED` - Notify project team

### Recipients
- **Government**: Project created, proposal submitted, impact submitted
- **Project Team**: All status changes, approvals, rejections, revisions
- **University Admin**: Major milestones, completion

## Audit Logging

### Logged Events
- `PROJECT_CREATED`
- `PROJECT_UPDATED`
- `PROJECT_STATUS_CHANGED`
- `TEAM_MEMBER_ADDED`
- `TEAM_MEMBER_REMOVED`
- `TEAM_MEMBER_UPDATED`
- `PROPOSAL_CREATED`
- `PROPOSAL_UPDATED`
- `PROPOSAL_SUBMITTED`
- `PROPOSAL_APPROVED`
- `PROPOSAL_REVISION_REQUESTED`
- `PROPOSAL_REJECTED`
- `MILESTONE_CREATED`
- `MILESTONE_UPDATED`
- `MILESTONE_COMPLETED`
- `PROJECT_DEPLOYED`
- `PROJECT_COMPLETED`
- `IMPACT_CREATED`
- `IMPACT_UPDATED`
- `IMPACT_SUBMITTED`
- `IMPACT_VERIFIED`
- `IMPACT_REVISION_REQUESTED`

### Audit Data
- `user_id`: Who performed the action
- `action`: Event type
- `entity_type`: PROJECT
- `entity_id`: Project UUID
- `timestamp`: When
- `details`: JSON with action-specific data

## Limitations

### Current Implementation
- No project evidence/document storage (metadata only - requires storage integration)
- No automated impact calculation (by design - human verification required)
- No project timeline/Gantt chart visualization (API provides data only)
- No email/SMS notifications (system notifications only)
- No project analytics/dashboards (basic aggregates only)

### Out of Scope for Step 7
- Industry collaboration
- Industry matching
- CSR funding marketplace
- Advanced analytics
- AI project evaluation
- Blockchain verification
- Real-time chat
- Mobile application
- Email/SMS integration

## Testing

### Test Coverage
45+ tests covering:
- Project creation from accepted assignments
- Project code generation
- Duplicate prevention
- Team management
- Proposal workflow
- Milestone tracking
- Lifecycle state machine
- Impact measurement
- Authorization
- IDOR protection
- Cross-university access
- Notification creation
- Audit logging
- Challenge integration
- Transaction rollback
- Pagination/filtering

### Running Tests
```bash
# Run all project tests
pytest backend/tests/test_projects.py -v

# Run specific test
pytest backend/tests/test_projects.py::test_create_project_from_accepted_assignment -v

# Run with coverage
pytest backend/tests/test_projects.py --cov=app.services.projects --cov-report=html
```

### PostgreSQL Tests
Tests requiring PostgreSQL are marked/skipped if unavailable.
SQLite in-memory database used for unit tests.

## Next Steps (Post-Step 7)

1. **Evidence Storage Integration**: Connect evidence_reference to actual file storage
2. **Industry Collaboration**: Industry partner involvement in projects
3. **Funding Module**: CSR funding marketplace
4. **Advanced Analytics**: Project performance metrics, impact dashboards
5. **Mobile Application**: Mobile access for field teams
6. **Email/SMS Notifications**: Alert stakeholders via email/SMS
7. **Project Chat**: Real-time collaboration
8. **AI Project Evaluation**: Automated risk assessment, impact prediction

## References

- [API Documentation](./api.md)
- [Architecture Overview](./architecture.md)
- [Database Schema](./database_schema.md)
- [Challenge Lifecycle](./CHALLENGE_INTELLIGENCE.md)
- [University Matching](./UNIVERSITY_MATCHING.md)
