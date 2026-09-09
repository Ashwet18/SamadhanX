# Industry Collaboration & Partnership Management

## Overview

The Industry Collaboration module enables universities to connect with industry partners for technical mentorship, prototyping support, testing facilities, and other forms of collaboration. This module implements a human-in-the-loop partnership workflow with explainable industry matching.

## Architecture

### Components

1. **Industry Matching Engine** (`industry_matching.py`)
   - Deterministic scoring algorithm
   - Configurable weights
   - Explainable recommendations

2. **Partnership Lifecycle** (`partnership_lifecycle.py`)
   - 8-state state machine
   - Transition validation
   - Terminal state handling

3. **Partnership Service** (`partnership_service.py`)
   - Partnership CRUD
   - Accept/decline workflows
   - Authorization enforcement

4. **Contribution Service** (`contribution_service.py`)
   - Contribution tracking
   - Commitment workflow
   - Delivery verification

## Industry Matching Algorithm

### Scoring Components

The matching algorithm uses **7 weighted factors** to score industry partners:

| Factor | Weight | Description |
|--------|--------|-------------|
| Expertise Match | 40% | Alignment with project's technical needs |
| Domain Fit | 20% | Sector/domain relevance |
| Technical Capability | 15% | Technical infrastructure and capabilities |
| Resources/Infrastructure | 10% | Available resources and facilities |
| Geographic Relevance | 5% | Location proximity to challenge |
| Partnership History | 5% | Previous partnership success |
| Availability | 5% | Current availability status |

### Scoring Formula

```
overall_score = 
    expertise × 0.40 +
    domain_fit × 0.20 +
    technical_capability × 0.15 +
    resources × 0.10 +
    geographic × 0.05 +
    partnership_history × 0.05 +
    availability × 0.05
```

**All scores normalized 0-100. Final score: 0-100.**

### Configurable Weights

Weights are configurable via `IndustryMatchingConfig` class. Default configuration can be overridden for custom matching scenarios.

### Explainability

Every recommendation includes:
- **Overall Score**: Weighted aggregate (0-100)
- **Component Scores**: Individual dimension scores
- **Evidence List**: Concrete reasons for match
- **Explanation**: Human-readable summary

Example:
```json
{
  "industry_name": "AquaTech Solutions",
  "overall_score": 87.5,
  "component_scores": {
    "expertise": 92.0,
    "domain_fit": 88.0,
    "technical_capability": 85.0,
    ...
  },
  "evidence": [
    "Strong expertise alignment (4 relevant areas)",
    "Relevant sector experience: Water Technology",
    "Strong technical capabilities",
    "Located in Ranchi, Jharkhand"
  ],
  "explanation": "Strong match for Smart Water Management with strong expertise alignment, relevant domain experience, and robust technical capabilities."
}
```

### Missing Data Handling

- **No expertise data**: 50.0 (neutral)
- **No domain info**: 50.0 (neutral)
- **No partnership history**: 50.0 (neutral)
- **No capabilities description**: 50.0 (neutral)

The algorithm **never fabricates** industry achievements or partnership history.

## Partnership Lifecycle

### States (8 total)

1. **RECOMMENDED** - Identified by matching algorithm
2. **REQUESTED** - Partnership request sent
3. **UNDER_REVIEW** - Industry reviewing request
4. **ACCEPTED** - Industry accepted
5. **DECLINED** - Industry declined (terminal)
6. **ACTIVE** - Partnership ongoing
7. **COMPLETED** - Successfully finished (terminal)
8. **CANCELLED** - Cancelled (terminal)

### Valid Transitions

```
RECOMMENDED → REQUESTED, CANCELLED
REQUESTED → UNDER_REVIEW, DECLINED, CANCELLED
UNDER_REVIEW → ACCEPTED, DECLINED, CANCELLED
ACCEPTED → ACTIVE, CANCELLED
DECLINED → (terminal)
ACTIVE → COMPLETED, CANCELLED
COMPLETED → (terminal)
CANCELLED → (terminal)
```

### Human-in-the-Loop

- **Industry partner must explicitly accept or decline** partnership requests
- No automatic partnerships from matching
- Government/university cannot force industry acceptance
- Decline requires reason
- Cancellation requires reason

## Partnership Types

- **TECHNICAL_MENTORSHIP** - Industry mentor support
- **PROTOTYPING** - Prototype development assistance
- **TESTING** - Testing facilities and support
- **FIELD_PILOT** - Field pilot deployment support
- **INFRASTRUCTURE** - Infrastructure/facility access
- **EQUIPMENT** - Equipment provision
- **DOMAIN_EXPERTISE** - Domain expert consultation
- **FUNDING_SUPPORT** - Financial support commitment (record only, no payment processing)
- **CSR_SUPPORT** - CSR initiative support
- **IMPLEMENTATION** - Implementation assistance
- **OTHER** - Other partnership types

**Note:** FUNDING_SUPPORT and CSR_SUPPORT are **commitment records only**. No payment gateway or financial transactions are implemented.

## Contribution Tracking

### Contribution Lifecycle

```
PLANNED → COMMITTED → IN_PROGRESS → DELIVERED
PLANNED/COMMITTED/IN_PROGRESS → CANCELLED
```

### Contribution Types

- Technical Mentoring
- Cloud Credits
- Equipment
- Lab Access
- Field Testing
- Software/Tools
- Domain Expertise
- Funding Commitment (record only)
- Staff Time
- Other

### Fields

- **contribution_type**: Type of contribution
- **description**: What is being contributed
- **estimated_value**: Optional estimated value (not required)
- **status**: Current status
- **committed_date**: When committed
- **delivered_date**: When delivered
- **evidence_reference**: Evidence/documentation reference

### Authorization

- **Create**: University or industry users
- **Commit**: Industry users only
- **Deliver**: University or industry users
- **Cancel**: University or industry users

## Authorization Matrix

| Action | Government | Platform Admin | University Admin | Faculty | Industry User | Student | Citizen |
|--------|------------|---------------|-----------------|---------|---------------|---------|---------|
| Trigger Matching | ✓ | ✓ | ✓ (own) | ✓ (own) | ✗ | ✗ | ✗ |
| View Matches | ✓ | ✓ | ✓ (own) | ✓ (own) | ✗ | ✗ | ✗ |
| Create Partnership | ✓ | ✓ | ✓ (own) | ✓ (own) | ✗ | ✗ | ✗ |
| Accept Partnership | ✗ | ✗ | ✗ | ✗ | ✓ (own org) | ✗ | ✗ |
| Decline Partnership | ✗ | ✗ | ✗ | ✗ | ✓ (own org) | ✗ | ✗ |
| Activate Partnership | ✓ | ✓ | ✓ (own) | ✓ (own) | ✓ (own org) | ✗ | ✗ |
| Complete Partnership | ✓ | ✓ | ✓ (own) | ✓ (own) | ✓ (own org) | ✗ | ✗ |
| Cancel Partnership | ✓ | ✓ | ✓ (own) | ✓ (own) | ✓ (own org) | ✗ | ✗ |
| View Partnerships | ✓ | ✓ | ✓ (own) | ✓ (own) | ✓ (own org) | ✓ (team) | ✗ |
| Create Contribution | ✓ | ✓ | ✓ (own) | ✓ (own) | ✓ (own org) | ✗ | ✗ |
| Commit Contribution | ✗ | ✗ | ✗ | ✗ | ✓ (own org) | ✗ | ✗ |
| Deliver Contribution | ✓ | ✓ | ✓ (own) | ✓ (own) | ✓ (own org) | ✗ | ✗ |

## User-Industry Organization Relationship

### Architecture

The system uses a **profile-based architecture** to link industry users to their organizations, following the same pattern as existing user profiles (Citizen, GovernmentOfficer, Faculty, Student).

### IndustryProfile Model

```python
class IndustryProfile(BaseModel):
    """Links industry users to their organizations."""
    __tablename__ = "industry_profiles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industry_partners.id"), nullable=False)
    employee_id = Column(String(100), nullable=True)
    designation = Column(String(200), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="industry_profile")
    industry = relationship("IndustryPartner")
```

### User Model Integration

```python
class User(BaseModel):
    # ... existing fields ...
    
    # Profile relationships (one-to-one)
    citizen_profile = relationship("Citizen", back_populates="user", uselist=False)
    government_profile = relationship("GovernmentOfficer", back_populates="user", uselist=False)
    faculty_profile = relationship("Faculty", back_populates="user", uselist=False)
    student_profile = relationship("Student", back_populates="user", uselist=False)
    industry_profile = relationship("IndustryProfile", back_populates="user", uselist=False)  # NEW
    
    # Role relationship (many-to-many)
    roles = relationship("UserRoleAssociation", back_populates="user")
```

### Authorization Pattern

**Server-side determination of organization membership:**

```python
# In partnership_service.py
def _get_user_industry(self, user: User) -> UUID:
    """
    Derive industry organization from authenticated user's profile.
    
    SECURITY: Never accept industry_id from client - always derive from user relationship.
    """
    if not hasattr(user, 'industry_profile') or not user.industry_profile:
        raise ValueError("User is not associated with an industry organization")
    
    return user.industry_profile.industry_id
```

**Role-based access control:**

```python
# Check user roles using relationship pattern
user_roles = {ur.role.name for ur in current_user.roles}

if UserRole.INDUSTRY not in user_roles:
    raise PermissionError("Only industry users can accept partnerships")

# Get organization from server-side profile
industry_id = self._get_user_industry(current_user)
```

### Security Guarantees

1. **Organization derived from server-side relationship**: 
   - Industry user A belongs to Company A via `IndustryProfile.industry_id`
   - System reads `current_user.industry_profile.industry_id`
   - Client **cannot** specify arbitrary `industry_id`

2. **Cross-organization isolation**:
   - User A (Company A) **CANNOT** access partnerships for Company B
   - Returns 403 Forbidden or 404 Not Found for cross-org access
   - Enforced at service layer, not just API layer

3. **Dashboard authorization**:
   ```python
   # GET /api/v1/industry/partnerships
   # Automatically filtered by user's organization
   industry_id = current_user.industry_profile.industry_id
   partnerships = service.list_partnerships(industry_id=industry_id, ...)
   ```

4. **Partnership operations**:
   ```python
   # Accept partnership - validates ownership
   partnership = db.query(Partnership).filter_by(id=partnership_id).first()
   user_industry_id = self._get_user_industry(current_user)
   
   if partnership.industry_partner_id != user_industry_id:
       raise PermissionError("Cannot accept partnership for another organization")
   ```

### Implementation Details

**Created:**
- `backend/app/models/user.py`: Added `IndustryProfile` model
- `backend/app/models/user.py`: Added `industry_profile` relationship to `User`
- `backend/app/models/__init__.py`: Exported `IndustryProfile`

**Modified:**
- `backend/app/services/industry/partnership_service.py`: Uses `_get_user_industry()` for authorization
- `backend/app/services/industry/contribution_service.py`: Uses same pattern
- `backend/app/routers/industry.py`: Dashboard endpoints derive `industry_id` from user

**Database:**
- Table: `industry_profiles`
- Foreign keys: `user_id` → `users.id`, `industry_id` → `industry_partners.id`
- Unique constraint on `user_id` (one profile per user)

### Test Coverage

Tests verify:
1. Industry user has `IndustryProfile` linking to organization (test_001)
2. Different users belong to different organizations (test_003)
3. Student/citizen users have no industry profile (test_004)
4. User A cannot accept Company B partnerships (test_031)
5. Dashboard shows only user's organization data (test_044)
6. GET /partnerships/{id} enforces authorization (test_048)
7. POST /partnerships/{id}/accept enforces authorization (test_049)

### Migration Required

```sql
-- Create industry_profiles table
CREATE TABLE industry_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    industry_id UUID NOT NULL REFERENCES industry_partners(id) ON DELETE CASCADE,
    employee_id VARCHAR(100),
    designation VARCHAR(200),
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_industry_profiles_user_id ON industry_profiles(user_id);
CREATE INDEX idx_industry_profiles_industry_id ON industry_profiles(industry_id);
```

### Example Usage

```python
# User registration with industry profile
user = User(email="john@techcorp.com", ...)
db.add(user)
db.flush()

# Link to organization
profile = IndustryProfile(
    user_id=user.id,
    industry_id=techcorp_id,
    employee_id="EMP001",
    designation="Partnership Manager",
    is_admin=True
)
db.add(profile)
db.commit()

# Later: Authorization check
user_industry = user.industry_profile.industry_id  # techcorp_id
partnership_industry = partnership.industry_partner_id

if user_industry != partnership_industry:
    raise PermissionError("Access denied")
```

## Security

### Organization Isolation

- **Cross-company isolation**: Industry users can only access their own organization's partnerships
- **Cross-university isolation**: University users can only access their university's partnerships
- **Government/Admin**: Full cross-organization visibility

### IDOR Protection

All endpoints validate:
- Project ownership before partnership creation
- Partnership ownership before accept/decline
- Contribution ownership before updates
- Industry organization membership

Never trust client-provided IDs without server-side authorization.

### Role Enforcement

- Students **cannot** accept, decline, or manage partnerships
- Citizens **cannot** access partnership APIs
- Industry users must belong to the relevant organization
- University users must belong to the project's university

## API Endpoints

### Industry Matching

#### Trigger Matching
```
POST /api/v1/projects/{project_id}/industry-match
Authorization: Government, University Admin, Faculty (own university)
```

#### Get Saved Matches
```
GET /api/v1/projects/{project_id}/industry-matches
Authorization: Government, University Admin, Faculty (own university)
```

### Partnerships

#### Create Partnership Request
```
POST /api/v1/projects/{project_id}/partnerships
Authorization: Government, University Admin, Faculty (own university)
Body: {
  "industry_id": "uuid",
  "partnership_type": "TECHNICAL_MENTORSHIP",
  "objectives": "...",
  "requested_support": "...",
  "expected_contribution": "...",
  "proposed_duration": 12
}
```

#### List Partnerships
```
GET /api/v1/partnerships?status=ACTIVE&page=1&page_size=20
Authorization: Required (filtered by role)
```

#### Get Partnership
```
GET /api/v1/partnerships/{partnership_id}
Authorization: Required
```

#### Accept Partnership
```
POST /api/v1/partnerships/{partnership_id}/accept
Authorization: Industry user (own organization)
Body: { "notes": "..." }
```

#### Decline Partnership
```
POST /api/v1/partnerships/{partnership_id}/decline
Authorization: Industry user (own organization)
Body: { "reason": "..." }
```

#### Activate Partnership
```
POST /api/v1/partnerships/{partnership_id}/activate
Authorization: University or Industry user
Body: { "start_date": "2024-01-01" }
```

#### Complete Partnership
```
POST /api/v1/partnerships/{partnership_id}/complete
Authorization: University or Industry user
Body: { "end_date": "2024-12-31", "notes": "..." }
```

#### Cancel Partnership
```
POST /api/v1/partnerships/{partnership_id}/cancel
Authorization: University or Industry user
Body: { "reason": "..." }
```

### Contributions

#### Create Contribution
```
POST /api/v1/partnerships/{partnership_id}/contributions
Authorization: University or Industry user
Body: {
  "contribution_type": "EQUIPMENT",
  "description": "IoT sensors and gateway",
  "estimated_value": 50000.00,
  "currency": "INR"
}
```

#### List Contributions
```
GET /api/v1/partnerships/{partnership_id}/contributions
Authorization: Required
```

#### Update Contribution
```
PATCH /api/v1/partnerships/{partnership_id}/contributions/{contribution_id}
Authorization: University or Industry user
```

#### Commit Contribution
```
POST /api/v1/partnerships/{partnership_id}/contributions/{contribution_id}/commit
Authorization: Industry user only
Body: { "committed_date": "2024-02-01" }
```

#### Deliver Contribution
```
POST /api/v1/partnerships/{partnership_id}/contributions/{contribution_id}/deliver
Authorization: University or Industry user
Body: {
  "delivered_date": "2024-03-15",
  "evidence_reference": "delivery_receipt_2024.pdf"
}
```

#### Cancel Contribution
```
POST /api/v1/partnerships/{partnership_id}/contributions/{contribution_id}/cancel
Authorization: University or Industry user
Body: { "reason": "..." }
```

## Project Integration

### Relationship

- Partnership references existing **Project** model
- Project lifecycle remains authoritative
- Partnership status does **NOT** automatically change project status
- Industry support enables project progress but doesn't control it

### Example Flow

```
Project: APPROVED
  ↓
Industry Matching
  ↓
Partnership: REQUESTED
  ↓
Partnership: ACCEPTED
  ↓
Partnership: ACTIVE
Contribution: IoT Equipment → DELIVERED
  ↓
Project: PROTOTYPE (manual transition by university)
  ↓
Partnership: ACTIVE (continues)
  ↓
Project: TESTING
  ↓
Project: PILOT
  ↓
Project: DEPLOYED
  ↓
Partnership: COMPLETED (manual)
```

## Notifications

- `INDUSTRY_MATCH_FOUND` - Matching completed
- `PARTNERSHIP_REQUESTED` - Request sent to industry
- `PARTNERSHIP_ACCEPTED` - Industry accepted
- `PARTNERSHIP_DECLINED` - Industry declined
- `PARTNERSHIP_ACTIVATED` - Partnership activated
- `PARTNERSHIP_COMPLETED` - Partnership completed
- `PARTNERSHIP_CANCELLED` - Partnership cancelled
- `CONTRIBUTION_COMMITTED` - Industry committed contribution
- `CONTRIBUTION_DELIVERED` - Contribution delivered

## Audit Events

- `INDUSTRY_MATCHING_STARTED`
- `INDUSTRY_MATCHING_COMPLETED`
- `PARTNERSHIP_REQUESTED`
- `PARTNERSHIP_ACCEPTED`
- `PARTNERSHIP_DECLINED`
- `PARTNERSHIP_ACTIVATED`
- `PARTNERSHIP_CANCELLED`
- `PARTNERSHIP_COMPLETED`
- `CONTRIBUTION_CREATED`
- `CONTRIBUTION_COMMITTED`
- `CONTRIBUTION_DELIVERED`
- `CONTRIBUTION_CANCELLED`

## Limitations

1. **No payment processing** - Funding commitments are records only
2. **No financial transactions** - No payment gateway integration
3. **No automated industry verification** - Manual verification required
4. **No complex scheduling** - Mentorship scheduling not implemented
5. **No email/SMS** - System notifications only
6. **No industry portal frontend** - Industry dashboard APIs exist but frontend not implemented
7. **Tests require PostgreSQL** - SQLite doesn't support UUID columns used in models

## What is NOT Implemented

- Payment gateway or processing
- Financial marketplace
- Stock/equity systems
- Contract management or e-signatures
- Advanced analytics or dashboards
- AI-based partner evaluation
- Blockchain verification
- Real-time chat
- Email/SMS notifications
- Mobile application
- Public industry directory
- Advanced scheduling system

## Future Enhancements

1. Complete user-industry profile relationship
2. Industry onboarding workflow
3. Automated partnership recommendations
4. Impact measurement integration
5. Partnership performance metrics
6. Industry reputation scoring
7. Multi-party partnerships
8. Partnership templates

## Testing

See `backend/tests/test_industry.py` for comprehensive test coverage including:
- Industry matching algorithm
- Partnership lifecycle
- Contribution tracking
- Authorization enforcement
- Organization isolation
- Transaction integrity

---

**Industry collaboration enables universities to leverage industry expertise and resources while maintaining academic control over project execution. All partnerships require explicit human approval and ongoing management.**
