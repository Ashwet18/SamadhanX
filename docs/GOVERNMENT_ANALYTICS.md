# Government/Admin Analytics API Documentation

## Overview

The Government/Admin Analytics API provides read-only analytics access for government officers and platform administrators to monitor the SamadhanX innovation pipeline from citizen challenge submission through deployment and verified impact.

**Phase**: Phase 1 - Backend Analytics API Only  
**Status**: Implemented  
**Version**: 1.0.0

## Authorization

### Allowed Roles
- `GOVERNMENT_OFFICER` - Government officials monitoring the platform
- `PLATFORM_ADMIN` - Platform administrators

### Denied Roles
- `CITIZEN` - Citizens cannot access analytics
- `STUDENT` - Students cannot access analytics  
- `FACULTY` - Faculty cannot access analytics
- `INDUSTRY` - Industry users cannot access analytics

### Authentication
All endpoints require Bearer token authentication:
```http
Authorization: Bearer <JWT_TOKEN>
```

Unauthorized access returns **403 Forbidden**.  
Unauthenticated requests return **401 Unauthorized**.

---

## API Endpoints

### Base Path
```
/api/v1/analytics
```

### 1. Platform Overview
```http
GET /api/v1/analytics/overview
```

**Description**: Returns high-level platform statistics across challenges, universities, projects, partnerships, and impact.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `PlatformOverviewResponse`
```json
{
  "total_challenges": 150,
  "challenges_by_status": {
    "VALIDATED": 45,
    "SUBMITTED": 30,
    "UNIVERSITY_INVITED": 20,
    "PROJECT_CREATED": 15,
    "DEPLOYED": 10
  },
  "challenges_by_category": {
    "Healthcare": 40,
    "Education": 35,
    "Agriculture": 30
  },
  "challenges_by_priority": {
    "HIGH": 50,
    "MEDIUM": 70,
    "LOW": 30
  },
  "total_validated_challenges": 45,
  "total_universities": 25,
  "total_projects": 85,
  "projects_by_status": {
    "PLANNING": 20,
    "PROTOTYPE": 30,
    "DEPLOYED": 15,
    "COMPLETED": 10
  },
  "total_industry_partners": 40,
  "total_partnerships": 60,
  "active_partnerships": 35,
  "total_reported_beneficiaries": 15000,
  "total_verified_beneficiaries": 12000
}
```

---

### 2. Challenge Analytics
```http
GET /api/v1/analytics/challenges
GET /api/v1/analytics/challenges?from_date=2026-01-01&to_date=2026-12-31
```

**Description**: Returns detailed challenge analytics including status distribution, geographic spread, validation metrics, and submission trends.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Query Parameters**:
- `from_date` (optional): ISO 8601 date string (YYYY-MM-DD)
- `to_date` (optional): ISO 8601 date string (YYYY-MM-DD)

**Response**: `ChallengeAnalyticsResponse`
```json
{
  "total_challenges": 150,
  "status_distribution": {
    "SUBMITTED": 30,
    "VALIDATED": 45,
    "UNIVERSITY_INVITED": 20
  },
  "category_distribution": {
    "Healthcare": 40,
    "Education": 35
  },
  "priority_distribution": {
    "HIGH": 50,
    "MEDIUM": 70,
    "LOW": 30
  },
  "geographic_distribution": {
    "Ranchi": 45,
    "Dhanbad": 30,
    "Jamshedpur": 25
  },
  "validation_rate": 75.5,
  "duplicate_rate": 5.2,
  "avg_days_to_validation": null,
  "submission_trend": [
    {"month": "2026-01", "count": 15},
    {"month": "2026-02", "count": 22}
  ]
}
```

**Calculation Notes**:
- `validation_rate`: (validated_challenges / total_challenges) * 100
- `duplicate_rate`: (duplicate_challenges / total_challenges) * 100  
- `avg_days_to_validation`: Returns `null` (no timestamp tracking available)

---

### 3. Project Pipeline Analytics
```http
GET /api/v1/analytics/projects/pipeline
```

**Description**: Returns project pipeline metrics showing distribution across lifecycle stages with percentages and conversion rates.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `ProjectPipelineAnalyticsResponse`
```json
{
  "total_projects": 85,
  "pipeline_stages": [
    {
      "stage": "PLANNING",
      "count": 20,
      "percentage": 23.53
    },
    {
      "stage": "PROTOTYPE",
      "count": 30,
      "percentage": 35.29
    },
    {
      "stage": "DEPLOYED",
      "count": 15,
      "percentage": 17.65
    }
  ],
  "conversion_rates": {
    "planning_to_approved": null,
    "approved_to_prototype": null,
    "prototype_to_pilot": null,
    "pilot_to_deployed": null
  }
}
```

**Supported Pipeline Stages**:
- PLANNING
- TEAM_FORMATION
- PROPOSAL
- APPROVED
- PROTOTYPE
- TESTING
- PILOT
- DEPLOYED
- COMPLETED
- ON_HOLD
- CANCELLED

**Calculation Notes**:
- `percentage`: (stage_count / total_projects) * 100
- `conversion_rates`: All return `null` (no stage transition timestamps available)

---

### 4. University Analytics
```http
GET /api/v1/analytics/universities
```

**Description**: Returns university participation metrics including project counts, challenge matching, and invitation acceptance rates.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `UniversityAnalyticsResponse`
```json
{
  "total_universities": 25,
  "participating_universities": 20,
  "challenges_matched": 120,
  "invitations_sent": 150,
  "invitations_accepted": 100,
  "acceptance_rate": 66.67,
  "projects_created": 85,
  "projects_completed": 25,
  "total_students": 450,
  "total_faculty": 120,
  "top_universities": [
    {
      "university_id": "uuid",
      "university_name": "Birla Institute of Technology",
      "project_count": 15,
      "completed_projects": 5,
      "active_projects": 10
    }
  ]
}
```

**Ranking**: Top universities ordered by project count (limit: 10)

---

### 5. Industry Analytics
```http
GET /api/v1/analytics/industry
```

**Description**: Returns industry partnership and contribution metrics reusing Step 8 data.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `IndustryAnalyticsResponse`
```json
{
  "total_industry_partners": 40,
  "active_partners": 30,
  "total_partnerships": 60,
  "partnerships_by_status": {
    "ACTIVE": 35,
    "COMPLETED": 15,
    "REQUESTED": 10
  },
  "partnerships_by_type": {
    "TECHNICAL_MENTORSHIP": 25,
    "PROTOTYPING": 15,
    "FUNDING_SUPPORT": 10
  },
  "total_contributions": 150,
  "contributions_by_type": {
    "TECHNICAL_MENTORING": 50,
    "CLOUD_CREDITS": 30,
    "EQUIPMENT": 20
  },
  "contributions_by_status": {
    "DELIVERED": 80,
    "IN_PROGRESS": 40,
    "COMMITTED": 30
  },
  "top_partners": [
    {
      "partner_id": "uuid",
      "organization_name": "Tech Solutions Pvt Ltd",
      "partnership_count": 12,
      "contribution_count": 30
    }
  ]
}
```

**Ranking**: Top partners ordered by partnership count (limit: 10)

---

### 6. Impact Analytics
```http
GET /api/v1/analytics/impact
```

**Description**: Returns impact measurement metrics including beneficiaries reached, geographic distribution, and verification status.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `ImpactAnalyticsResponse`
```json
{
  "total_beneficiaries": 15000,
  "verified_beneficiaries": 12000,
  "projects_with_impact": 45,
  "projects_with_verified_impact": 35,
  "verification_rate": 77.78,
  "geographic_distribution": {
    "Ranchi District": 5000,
    "Dhanbad District": 4000,
    "Jamshedpur Region": 3000
  },
  "category_distribution": {
    "Healthcare": 6000,
    "Education": 5000,
    "Agriculture": 4000
  },
  "sustainability_status": {
    "Sustainable": 30,
    "Needs Support": 10,
    "Unknown": 5
  }
}
```

**Calculation Notes**:
- `verification_rate`: (projects_with_verified_impact / projects_with_impact) * 100

---

### 7. Top Insights
```http
GET /api/v1/analytics/insights
```

**Description**: Returns ranked insights including highest-impact projects, most active universities/partners, and challenges requiring attention.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `TopInsightsResponse`
```json
{
  "highest_impact_projects": [
    {
      "project_code": "PRJ-JH-2026-00042",
      "project_name": "Rural Healthcare Mobile App",
      "beneficiaries": 5000,
      "status": "DEPLOYED",
      "university_name": "BIT Mesra"
    }
  ],
  "most_active_universities": [
    {
      "university_name": "Birla Institute of Technology",
      "project_count": 15,
      "completed_projects": 5
    }
  ],
  "most_active_industry_partners": [
    {
      "organization_name": "Tech Solutions Pvt Ltd",
      "partnership_count": 12
    }
  ],
  "challenges_needing_attention": [
    {
      "challenge_code": "CH-JH-2026-00023",
      "title": "Water Scarcity in Rural Areas",
      "priority_level": "HIGH",
      "status": "SUBMITTED",
      "days_pending": 45
    }
  ]
}
```

**Ranking Limits**:
- Highest impact projects: Top 5 (by verified beneficiaries)
- Most active universities: Top 5 (by project count)
- Most active partners: Top 5 (by partnership count)
- Challenges needing attention: Top 10 (high priority, pending validation)

---

### 8. Dashboard Summary
```http
GET /api/v1/analytics/dashboard
```

**Description**: Consolidated dashboard endpoint combining key metrics from all analytics endpoints for the main Government Dashboard view.

**Authorization**: `GOVERNMENT_OFFICER` | `PLATFORM_ADMIN`

**Response**: `DashboardSummaryResponse`
```json
{
  "overview": {
    "total_challenges": 150,
    "total_projects": 85,
    "total_universities": 25,
    "total_partnerships": 60,
    "verified_beneficiaries": 12000
  },
  "challenge_status_summary": [
    {"status": "VALIDATED", "count": 45},
    {"status": "SUBMITTED", "count": 30}
  ],
  "project_pipeline_summary": [
    {"stage": "PROTOTYPE", "count": 30, "percentage": 35.29},
    {"stage": "DEPLOYED", "count": 15, "percentage": 17.65}
  ],
  "top_universities": [
    {"name": "BIT Mesra", "projects": 15}
  ],
  "top_partners": [
    {"name": "Tech Solutions", "partnerships": 12}
  ],
  "impact_summary": {
    "verified_projects": 35,
    "total_beneficiaries": 12000
  },
  "alerts": [
    {"type": "HIGH_PRIORITY_PENDING", "count": 15}
  ]
}
```

---

## Data Privacy & Security

### No Personal Information Exposure
All analytics endpoints **do not expose**:
- Email addresses
- Phone numbers  
- Internal user IDs
- Personal identifiable information (PII)

### Aggregate Data Only
All metrics are aggregated counts, distributions, and percentages. Individual records (challenges, projects, users) are **not** returned except for:
- Project codes (not sensitive)
- University names (public institutions)
- Organization names (public businesses)

### Testing
Privacy compliance is verified through automated tests:
- `test_39_no_email_exposure`
- `test_40_no_phone_exposure`
- `test_41_no_user_id_exposure`

---

## Performance Considerations

### Database Aggregation
All analytics use **database-level aggregation** via SQLAlchemy:
- `func.count()` for counts
- `func.sum()` for totals
- `GROUP BY` for distributions

**No N+1 queries**. All data is fetched in single queries per endpoint.

### Query Optimization
- Indexed fields: `status`, `priority_level`, `district`, `verification_status`
- Date filtering available on challenges endpoint
- Top-N queries limited (5, 10, or 20 records max)

### No Caching (Phase 1)
Caching is **not implemented** in Phase 1. All queries execute directly against PostgreSQL.

---

## Limitations (Phase 1)

### Time-Based Metrics
The following metrics return `null` because timestamp tracking is not available:
- `avg_days_to_validation` - No `status_changed_at` timestamps
- `conversion_rates` - No stage transition timestamps  
- `avg_stage_duration` - No status change audit logs

**Future Enhancement**: Add audit logs or status change timestamps to enable time-based metrics.

### Category/Priority Data
Challenge categories use a many-to-many relationship (`ChallengeCategory` table). Priority is stored as `priority_level` enum.

### Visualization
Phase 1 provides **raw JSON data only**. No charts, graphs, or frontend dashboard are included.

**Phase 2**: Will implement frontend dashboard with visualizations.

### Real-Time Updates
Phase 1 analytics are **not real-time**. Data is fetched on-demand from PostgreSQL.

**Future Enhancement**: WebSockets or Server-Sent Events for live updates.

---

## Error Handling

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```
**Cause**: Missing or invalid JWT token.

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```
**Cause**: User role is not `GOVERNMENT_OFFICER` or `PLATFORM_ADMIN`.

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["query", "from_date"],
      "msg": "invalid date format",
      "type": "value_error"
    }
  ]
}
```
**Cause**: Invalid query parameters (e.g., malformed dates).

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
**Cause**: Database connection failure or unexpected error.

---

## Testing

### Test Coverage
42 comprehensive tests covering:
1. **Authorization** (6 tests): Role-based access control
2. **Platform Overview** (4 tests): Aggregations, empty data, structure
3. **Challenge Analytics** (4 tests): Filtering, distributions  
4. **Project Pipeline** (4 tests): Stages, percentages
5. **University Analytics** (4 tests): Rankings, participation
6. **Industry Analytics** (4 tests): Partnerships, contributions
7. **Impact Analytics** (4 tests): Beneficiaries, verification
8. **Top Insights** (4 tests): Rankings, limits
9. **Dashboard Summary** (4 tests): Consolidated views
10. **Data Privacy** (4 tests): PII leakage prevention

### Run Tests
```bash
# Analytics tests only
pytest tests/test_analytics.py -v

# Full test suite
pytest -v

# With coverage
pytest tests/test_analytics.py --cov=app/services/analytics --cov=app/routers/analytics
```

### Test Results (Current)
- **Passed**: 23/42 tests  
- **Failed**: 17 tests (response structure mismatches, fixture issues)
- **Errors**: 2 tests (partnership enum issues)
- **Step 8 Unchanged**: 52/52 tests passing ✅

---

## Migration Status

**No database schema changes required.**

Current migration: `4359c049e909` (head)

```bash
$ python -m alembic current
4359c049e909 (head)
```

All analytics use existing models:
- `Challenge`
- `Project`
- `University`
- `IndustryPartner`
- `Partnership`
- `Contribution`
- `ImpactMetric`

---

## Files Created/Modified

### Created
1. `backend/app/schemas/analytics.py` (425 lines) - Response schemas
2. `backend/app/services/analytics/__init__.py` - Service exports
3. `backend/app/services/analytics/analytics_service.py` (745 lines) - Analytics logic
4. `backend/app/routers/analytics.py` (180 lines) - API endpoints
5. `backend/tests/test_analytics.py` (990 lines) - Comprehensive tests
6. `docs/GOVERNMENT_ANALYTICS.md` (this file) - Documentation

### Modified
1. `backend/app/main.py` - Added analytics router registration

### Step 8 Unchanged ✅
All Step 8 files (industry collaboration) remain unchanged and functional.

---

## Next Steps (Future Phases)

### Phase 2: Frontend Dashboard
- React/Vue dashboard UI
- Interactive charts (Chart.js, D3.js)
- Filtering and drill-down capabilities
- Export to PDF/Excel

### Phase 3: Real-Time Analytics
- WebSocket connections for live updates
- Server-Sent Events for notifications
- Redis caching layer
- Background aggregation workers

### Phase 4: Advanced Analytics
- Predictive analytics (project success prediction)
- ML-based impact forecasting
- Anomaly detection
- Custom report generation

### Phase 5: Extended Access
- University-specific analytics (filtered by institution)
- Industry-specific analytics (filtered by partner)
- Public-facing impact dashboard (non-sensitive metrics)

---

## Support & Maintenance

### Contact
- **Technical Lead**: SamadhanX Development Team
- **Government Liaison**: Jharkhand Innovation Team

### Version History
- **v1.0.0** (2026-09-08): Initial Phase 1 release - Backend API only

---

*This documentation reflects Phase 1 implementation status as of September 8, 2026.*
