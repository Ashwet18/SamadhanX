"""
Comprehensive tests for Government/Admin Analytics API (Step 9 Phase 1)

Test Coverage:
1. Authorization tests (tests 1-6) - role-based access control
2. Platform overview (tests 7-10)
3. Challenge analytics (tests 11-14)
4. Project pipeline analytics (tests 15-18)
5. University analytics (tests 19-22)
6. Industry analytics (tests 23-26)
7. Impact analytics (tests 27-30)
8. Top insights (tests 31-34)
9. Dashboard summary (tests 35-38)
10. Data privacy/security (tests 39-42)

Total: 42 tests
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.models.user import User, Role, UserRoleAssociation
from app.models.enums import UserRole, ChallengeStatus, ProjectStatus, PartnershipStatus, VerificationStatus, AccountStatus
from app.models.challenge import Challenge
from app.models.project import Project
from app.models.industry import IndustryPartner
from app.models.partnership import Partnership
from app.models.platform import ImpactMetric
from app.models.university import University
from app.core.security import security


# ============================================================================
# FIXTURES - USER ROLES
# ============================================================================

@pytest.fixture
def roles_setup(db_session):
    """Ensure all roles exist in the database"""
    role_names = [
        UserRole.CITIZEN,
        UserRole.STUDENT,
        UserRole.FACULTY,
        UserRole.INDUSTRY,
        UserRole.GOVERNMENT_OFFICER,
        UserRole.PLATFORM_ADMIN
    ]
    
    roles = {}
    for role_name in role_names:
        role = db_session.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name.value} role")
            db_session.add(role)
        roles[role_name] = role
    
    db_session.commit()
    return roles


@pytest.fixture
def government_user(db_session, roles_setup):
    """Government officer user with valid authentication"""
    user = User(
        id=uuid4(),
        email="govt.officer@jharkhand.gov.in",
        name="Government Officer",
        password_hash=security.hash_password("SecurePassword123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Assign GOVERNMENT_OFFICER role
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=roles_setup[UserRole.GOVERNMENT_OFFICER].id
    )
    db_session.add(user_role)
    db_session.commit()
    db_session.refresh(user)
    
    # Create access token
    token = security.create_access_token(subject=str(user.id))
    return {"user": user, "token": token}


@pytest.fixture
def admin_user(db_session, roles_setup):
    """Platform admin user with valid authentication"""
    user = User(
        id=uuid4(),
        email="admin@samadhanx.in",
        name="Platform Admin",
        password_hash=security.hash_password("AdminPassword123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Assign PLATFORM_ADMIN role
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=roles_setup[UserRole.PLATFORM_ADMIN].id
    )
    db_session.add(user_role)
    db_session.commit()
    db_session.refresh(user)
    
    # Create access token
    token = security.create_access_token(subject=str(user.id))
    return {"user": user, "token": token}


@pytest.fixture
def citizen_user(db_session, roles_setup):
    """Citizen user (should NOT have analytics access)"""
    user = User(
        id=uuid4(),
        email="citizen@example.com",
        name="Test Citizen",
        password_hash=security.hash_password("CitizenPassword123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Assign CITIZEN role
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=roles_setup[UserRole.CITIZEN].id
    )
    db_session.add(user_role)
    db_session.commit()
    db_session.refresh(user)
    
    # Create access token
    token = security.create_access_token(subject=str(user.id))
    return {"user": user, "token": token}


@pytest.fixture
def student_user(db_session, roles_setup):
    """Student user (should NOT have analytics access)"""
    user = User(
        id=uuid4(),
        email="student@university.edu",
        name="Test Student",
        password_hash=security.hash_password("StudentPassword123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Assign STUDENT role
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=roles_setup[UserRole.STUDENT].id
    )
    db_session.add(user_role)
    db_session.commit()
    db_session.refresh(user)
    
    # Create access token
    token = security.create_access_token(subject=str(user.id))
    return {"user": user, "token": token}


@pytest.fixture
def faculty_user(db_session, roles_setup):
    """Faculty user (should NOT have analytics access)"""
    user = User(
        id=uuid4(),
        email="faculty@university.edu",
        name="Test Faculty",
        password_hash=security.hash_password("FacultyPassword123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Assign FACULTY role
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=roles_setup[UserRole.FACULTY].id
    )
    db_session.add(user_role)
    db_session.commit()
    db_session.refresh(user)
    
    # Create access token
    token = security.create_access_token(subject=str(user.id))
    return {"user": user, "token": token}


@pytest.fixture
def industry_user(db_session, roles_setup):
    """Industry user (should NOT have analytics access)"""
    user = User(
        id=uuid4(),
        email="industry@company.com",
        name="Test Industry User",
        password_hash=security.hash_password("IndustryPassword123!"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Assign INDUSTRY role
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=roles_setup[UserRole.INDUSTRY].id
    )
    db_session.add(user_role)
    db_session.commit()
    db_session.refresh(user)
    
    # Create access token
    token = security.create_access_token(subject=str(user.id))
    return {"user": user, "token": token}


# ============================================================================
# FIXTURES - SAMPLE DATA
# ============================================================================

@pytest.fixture
def sample_challenges(db_session, citizen_user):
    """Create sample challenges for analytics testing"""
    challenges = []
    
    # Challenge 1: Validated
    c1 = Challenge(
        id=uuid4(),
        challenge_code="CH-JH-2026-00001",
        title="Healthcare Access in Rural Areas",
        description="Limited healthcare facilities in remote villages",
        district="Ranchi",
        status=ChallengeStatus.VALIDATED,
        submitted_by=citizen_user["user"].id
    )
    challenges.append(c1)
    
    # Challenge 2: Submitted
    c2 = Challenge(
        id=uuid4(),
        challenge_code="CH-JH-2026-00002",
        title="Digital Literacy Gap",
        description="Lack of digital education infrastructure",
        district="Dhanbad",
        status=ChallengeStatus.SUBMITTED,
        submitted_by=citizen_user["user"].id
    )
    challenges.append(c2)
    
    # Challenge 3: Matched
    c3 = Challenge(
        id=uuid4(),
        challenge_code="CH-JH-2026-00003",
        title="Crop Yield Optimization",
        description="Low agricultural productivity",
        district="East Singhbhum",
        status=ChallengeStatus.UNIVERSITY_INVITED,
        submitted_by=citizen_user["user"].id
    )
    challenges.append(c3)
    
    db_session.add_all(challenges)
    db_session.commit()
    return challenges


@pytest.fixture
def sample_universities(db_session):
    """Create sample universities for analytics testing"""
    from app.models.enums import UniversityType
    
    universities = []
    
    u1 = University(
        id=uuid4(),
        name="Birla Institute of Technology",
        code="BIT",
        type=UniversityType.PRIVATE,
        district="Ranchi",
        state="Jharkhand"
    )
    universities.append(u1)
    
    u2 = University(
        id=uuid4(),
        name="National Institute of Technology Jamshedpur",
        code="NITJSR",
        type=UniversityType.CENTRAL,
        district="East Singhbhum",
        state="Jharkhand"
    )
    universities.append(u2)
    
    db_session.add_all(universities)
    db_session.commit()
    return universities


@pytest.fixture
def sample_projects(db_session, sample_challenges, sample_universities, student_user):
    """Create sample projects for analytics testing"""
    projects = []
    
    # Project 1: Prototype stage, linked to challenge 1
    p1 = Project(
        id=uuid4(),
        project_code="PRJ-JH-2026-00001",
        name="Mobile Healthcare Clinic",
        description="Mobile clinic for rural healthcare delivery",
        challenge_id=sample_challenges[0].id,
        university_id=sample_universities[0].id,
        status=ProjectStatus.PROTOTYPE,
        created_by=student_user["user"].id,
        start_date=datetime.utcnow().date() - timedelta(days=30)
    )
    projects.append(p1)
    
    # Project 2: Deployed stage, linked to challenge 3
    p2 = Project(
        id=uuid4(),
        project_code="PRJ-JH-2026-00002",
        name="Smart Agriculture Monitoring System",
        description="IoT-based crop monitoring solution",
        challenge_id=sample_challenges[2].id,
        university_id=sample_universities[1].id,
        status=ProjectStatus.DEPLOYED,
        created_by=student_user["user"].id,
        start_date=datetime.utcnow().date() - timedelta(days=90)
    )
    projects.append(p2)
    
    # Project 3: Planning stage
    p3 = Project(
        id=uuid4(),
        project_code="PRJ-JH-2026-00003",
        name="Digital Education Platform",
        description="E-learning platform for remote students",
        challenge_id=sample_challenges[1].id,
        university_id=sample_universities[0].id,
        status=ProjectStatus.PLANNING,
        created_by=student_user["user"].id,
        start_date=datetime.utcnow().date() - timedelta(days=5)
    )
    projects.append(p3)
    
    db_session.add_all(projects)
    db_session.commit()
    return projects


@pytest.fixture
def sample_industry_partners(db_session):
    """Create sample industry partners for analytics testing"""
    from app.models.enums import IndustryType, AvailabilityStatus
    
    partners = []
    
    p1 = IndustryPartner(
        id=uuid4(),
        organization_name="Tech Solutions Pvt Ltd",
        type=IndustryType.CORPORATE,
        description="Software development company",
        website="https://techsolutions.com",
        contact_email="contact@techsolutions.com",
        contact_phone="+91-9876543210",
        capabilities="Software, AI/ML, IoT",
        sectors="Healthcare, Education",
        availability_status=AvailabilityStatus.AVAILABLE
    )
    partners.append(p1)
    
    p2 = IndustryPartner(
        id=uuid4(),
        organization_name="AgriTech Innovations",
        type=IndustryType.STARTUP,
        description="Agricultural technology startup",
        website="https://agritech.com",
        contact_email="info@agritech.com",
        contact_phone="+91-9876543211",
        capabilities="Agriculture, IoT, Data Analytics",
        sectors="Agriculture, Rural Development",
        availability_status=AvailabilityStatus.AVAILABLE
    )
    partners.append(p2)
    
    db_session.add_all(partners)
    db_session.commit()
    return partners


@pytest.fixture
def sample_partnerships(db_session, sample_projects, sample_industry_partners):
    """Create sample partnerships for analytics testing"""
    from app.models.enums import PartnershipType
    
    partnerships = []
    
    # Active partnership for project 1
    ps1 = Partnership(
        id=uuid4(),
        project_id=sample_projects[0].id,
        industry_partner_id=sample_industry_partners[0].id,
        type=PartnershipType.MENTORSHIP,
        status=PartnershipStatus.ACTIVE,
        start_date=datetime.utcnow() - timedelta(days=20)
    )
    partnerships.append(ps1)
    
    # Completed partnership for project 2
    ps2 = Partnership(
        id=uuid4(),
        project_id=sample_projects[1].id,
        industry_partner_id=sample_industry_partners[1].id,
        type=PartnershipType.COLLABORATION,
        status=PartnershipStatus.COMPLETED,
        start_date=datetime.utcnow() - timedelta(days=80),
        end_date=datetime.utcnow() - timedelta(days=15)
    )
    partnerships.append(ps2)
    
    db_session.add_all(partnerships)
    db_session.commit()
    return partnerships


@pytest.fixture
def sample_impact_metrics(db_session, sample_projects):
    """Create sample impact metrics for analytics testing"""
    metrics = []
    
    # Impact metric for deployed project
    im1 = ImpactMetric(
        id=uuid4(),
        project_id=sample_projects[1].id,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=500,
        geographic_area="East Singhbhum District",
        verification_status=VerificationStatus.VERIFIED,
        sustainability_status="Sustainable",
        measured_at=datetime.utcnow() - timedelta(days=5)
    )
    metrics.append(im1)
    
    db_session.add_all(metrics)
    db_session.commit()
    return metrics


# ============================================================================
# TEST SUITE 1: AUTHORIZATION (Tests 1-6)
# ============================================================================

def test_01_government_officer_can_access_overview(client, government_user):
    """Test that government officer can access analytics overview"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_challenges" in data
    assert "total_universities" in data


def test_02_platform_admin_can_access_overview(client, admin_user):
    """Test that platform admin can access analytics overview"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_challenges" in data
    assert "total_universities" in data


def test_03_citizen_cannot_access_analytics(client, citizen_user):
    """Test that citizen user receives 403 for analytics"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {citizen_user['token']}"}
    )
    assert response.status_code == 403


def test_04_student_cannot_access_analytics(client, student_user):
    """Test that student user receives 403 for analytics"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {student_user['token']}"}
    )
    assert response.status_code == 403


def test_05_faculty_cannot_access_analytics(client, faculty_user):
    """Test that faculty user receives 403 for analytics"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {faculty_user['token']}"}
    )
    assert response.status_code == 403


def test_06_industry_user_cannot_access_analytics(client, industry_user):
    """Test that industry user receives 403 for analytics"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {industry_user['token']}"}
    )
    assert response.status_code == 403


# ============================================================================
# TEST SUITE 2: PLATFORM OVERVIEW (Tests 7-10)
# ============================================================================

def test_07_overview_with_sample_data(
    client, government_user, sample_challenges, sample_universities,
    sample_projects, sample_industry_partners, sample_impact_metrics
):
    """Test overview endpoint returns correct aggregations with sample data"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify challenge counts
    assert data["total_challenges"] == 3
    assert data["challenges_by_status"]["VALIDATED"] >= 1
    assert data["challenges_by_status"]["PENDING_VALIDATION"] >= 1
    
    # Verify university count
    assert data["total_universities"] >= 2
    
    # Verify project counts
    assert data["total_projects"] == 3
    assert data["projects_by_status"]["PROTOTYPE"] >= 1
    assert data["projects_by_status"]["DEPLOYED"] >= 1
    
    # Verify industry counts
    assert data["total_industry_partners"] >= 2
    
    # Verify impact metrics
    assert data["total_verified_beneficiaries"] >= 500


def test_08_overview_empty_database(client, government_user):
    """Test overview endpoint returns zeros for empty database"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # All counts should be zero or empty
    assert data["total_challenges"] == 0
    assert data["total_universities"] == 0
    assert data["total_projects"] == 0
    assert data["total_industry_partners"] == 0
    assert data["total_verified_beneficiaries"] == 0


def test_09_overview_response_structure(client, government_user):
    """Test overview response has expected structure"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Required fields
    required_fields = [
        "total_challenges", "challenges_by_status", "challenges_by_category",
        "challenges_by_priority", "total_validated_challenges",
        "total_universities", "total_projects", "projects_by_status",
        "total_industry_partners", "total_partnerships", "active_partnerships",
        "total_reported_beneficiaries", "total_verified_beneficiaries"
    ]
    
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


def test_10_overview_no_pii_leakage(client, government_user, sample_challenges):
    """Test overview does not expose personal information"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Response should not contain email, phone, or user IDs
    response_str = str(data).lower()
    assert "email" not in response_str
    assert "phone" not in response_str
    assert "@" not in response_str


# ============================================================================
# TEST SUITE 3: CHALLENGE ANALYTICS (Tests 11-14)
# ============================================================================

def test_11_challenge_analytics_basic(client, government_user, sample_challenges):
    """Test challenge analytics endpoint with sample data"""
    response = client.get(
        "/api/v1/analytics/challenges",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_challenges"] == 3
    assert "status_distribution" in data
    assert "category_distribution" in data
    assert "priority_distribution" in data
    assert "geographic_distribution" in data


def test_12_challenge_analytics_authorization(client, citizen_user):
    """Test challenge analytics requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/challenges",
        headers={"Authorization": f"Bearer {citizen_user['token']}"}
    )
    assert response.status_code == 403


def test_13_challenge_analytics_date_filtering(client, government_user, sample_challenges):
    """Test challenge analytics supports date filtering"""
    from_date = (datetime.utcnow() - timedelta(days=15)).isoformat()
    to_date = datetime.utcnow().isoformat()
    
    response = client.get(
        f"/api/v1/analytics/challenges?from_date={from_date}&to_date={to_date}",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_challenges" in data


def test_14_challenge_analytics_empty_data(client, government_user):
    """Test challenge analytics with empty database"""
    response = client.get(
        "/api/v1/analytics/challenges",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_challenges"] == 0


# ============================================================================
# TEST SUITE 4: PROJECT PIPELINE ANALYTICS (Tests 15-18)
# ============================================================================

def test_15_project_pipeline_basic(client, government_user, sample_projects):
    """Test project pipeline analytics endpoint"""
    response = client.get(
        "/api/v1/analytics/projects/pipeline",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_projects"] == 3
    assert "pipeline_stages" in data
    assert "PLANNING" in data["pipeline_stages"]
    assert "PROTOTYPE" in data["pipeline_stages"]
    assert "DEPLOYED" in data["pipeline_stages"]


def test_16_project_pipeline_authorization(client, student_user):
    """Test project pipeline requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/projects/pipeline",
        headers={"Authorization": f"Bearer {student_user['token']}"}
    )
    assert response.status_code == 403


def test_17_project_pipeline_percentages(client, government_user, sample_projects):
    """Test project pipeline includes percentage calculations"""
    response = client.get(
        "/api/v1/analytics/projects/pipeline",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check that stages include both count and percentage
    for stage, metrics in data["pipeline_stages"].items():
        assert "count" in metrics
        assert "percentage" in metrics
        assert 0 <= metrics["percentage"] <= 100


def test_18_project_pipeline_empty_data(client, government_user):
    """Test project pipeline with empty database"""
    response = client.get(
        "/api/v1/analytics/projects/pipeline",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_projects"] == 0


# ============================================================================
# TEST SUITE 5: UNIVERSITY ANALYTICS (Tests 19-22)
# ============================================================================

def test_19_university_analytics_basic(client, government_user, sample_universities, sample_projects):
    """Test university analytics endpoint"""
    response = client.get(
        "/api/v1/analytics/universities",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_universities"] >= 2
    assert "top_universities_by_projects" in data


def test_20_university_analytics_authorization(client, faculty_user):
    """Test university analytics requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/universities",
        headers={"Authorization": f"Bearer {faculty_user['token']}"}
    )
    assert response.status_code == 403


def test_21_university_analytics_top_10(client, government_user, sample_universities, sample_projects):
    """Test university analytics returns top 10 universities"""
    response = client.get(
        "/api/v1/analytics/universities",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should return at most 10 universities
    assert len(data["top_universities_by_projects"]) <= 10


def test_22_university_analytics_empty_data(client, government_user):
    """Test university analytics with empty database"""
    response = client.get(
        "/api/v1/analytics/universities",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_universities"] == 0


# ============================================================================
# TEST SUITE 6: INDUSTRY ANALYTICS (Tests 23-26)
# ============================================================================

def test_23_industry_analytics_basic(client, government_user, sample_industry_partners, sample_partnerships):
    """Test industry analytics endpoint"""
    response = client.get(
        "/api/v1/analytics/industry",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_partners"] >= 2
    assert data["total_partnerships"] >= 2
    assert "partnerships_by_status" in data


def test_24_industry_analytics_authorization(client, industry_user):
    """Test industry analytics requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/industry",
        headers={"Authorization": f"Bearer {industry_user['token']}"}
    )
    assert response.status_code == 403


def test_25_industry_analytics_top_partners(client, government_user, sample_industry_partners, sample_partnerships):
    """Test industry analytics returns top partners"""
    response = client.get(
        "/api/v1/analytics/industry",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "top_partners_by_projects" in data
    assert len(data["top_partners_by_projects"]) <= 10


def test_26_industry_analytics_empty_data(client, government_user):
    """Test industry analytics with empty database"""
    response = client.get(
        "/api/v1/analytics/industry",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_partners"] == 0


# ============================================================================
# TEST SUITE 7: IMPACT ANALYTICS (Tests 27-30)
# ============================================================================

def test_27_impact_analytics_basic(client, government_user, sample_projects, sample_impact_metrics):
    """Test impact analytics endpoint"""
    response = client.get(
        "/api/v1/analytics/impact",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_beneficiaries"] >= 500
    assert data["verified_beneficiaries"] >= 500
    assert "projects_with_impact" in data


def test_28_impact_analytics_authorization(client, citizen_user):
    """Test impact analytics requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/impact",
        headers={"Authorization": f"Bearer {citizen_user['token']}"}
    )
    assert response.status_code == 403


def test_29_impact_analytics_geographic_distribution(client, government_user, sample_impact_metrics):
    """Test impact analytics includes geographic distribution"""
    response = client.get(
        "/api/v1/analytics/impact",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "geographic_distribution" in data


def test_30_impact_analytics_empty_data(client, government_user):
    """Test impact analytics with empty database"""
    response = client.get(
        "/api/v1/analytics/impact",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_beneficiaries"] == 0


# ============================================================================
# TEST SUITE 8: TOP INSIGHTS (Tests 31-34)
# ============================================================================

def test_31_top_insights_basic(client, government_user, sample_projects, sample_impact_metrics):
    """Test top insights endpoint"""
    response = client.get(
        "/api/v1/analytics/insights",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "highest_impact_projects" in data
    assert "most_active_universities" in data
    assert "most_active_partners" in data


def test_32_top_insights_authorization(client, student_user):
    """Test top insights requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/insights",
        headers={"Authorization": f"Bearer {student_user['token']}"}
    )
    assert response.status_code == 403


def test_33_top_insights_limits(client, government_user, sample_projects, sample_universities, sample_industry_partners):
    """Test top insights respects limit parameters"""
    response = client.get(
        "/api/v1/analytics/insights",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Top 5 projects, top 5 universities, top 5 partners
    assert len(data["highest_impact_projects"]) <= 5
    assert len(data["most_active_universities"]) <= 5
    assert len(data["most_active_partners"]) <= 5


def test_34_top_insights_empty_data(client, government_user):
    """Test top insights with empty database"""
    response = client.get(
        "/api/v1/analytics/insights",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["highest_impact_projects"]) == 0


# ============================================================================
# TEST SUITE 9: DASHBOARD SUMMARY (Tests 35-38)
# ============================================================================

def test_35_dashboard_summary_basic(client, government_user, sample_challenges, sample_projects, sample_impact_metrics):
    """Test dashboard summary endpoint"""
    response = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should include key sections
    assert "platform_summary" in data
    assert "challenge_summary" in data
    assert "project_summary" in data
    assert "impact_summary" in data


def test_36_dashboard_summary_authorization(client, citizen_user):
    """Test dashboard summary requires proper authorization"""
    response = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {citizen_user['token']}"}
    )
    assert response.status_code == 403


def test_37_dashboard_summary_consolidated(client, government_user, sample_challenges, sample_projects):
    """Test dashboard summary consolidates multiple analytics"""
    response = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should match individual endpoint data
    assert data["platform_summary"]["total_challenges"] == 3
    assert data["platform_summary"]["total_projects"] == 3


def test_38_dashboard_summary_empty_data(client, government_user):
    """Test dashboard summary with empty database"""
    response = client.get(
        "/api/v1/analytics/dashboard",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["platform_summary"]["total_challenges"] == 0


# ============================================================================
# TEST SUITE 10: DATA PRIVACY & SECURITY (Tests 39-42)
# ============================================================================

def test_39_no_email_exposure(client, government_user, sample_challenges, sample_projects):
    """Test that analytics never expose email addresses"""
    endpoints = [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/challenges",
        "/api/v1/analytics/projects/pipeline",
        "/api/v1/analytics/universities",
        "/api/v1/analytics/industry",
        "/api/v1/analytics/impact",
        "/api/v1/analytics/insights",
        "/api/v1/analytics/dashboard"
    ]
    
    for endpoint in endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {government_user['token']}"}
        )
        assert response.status_code == 200
        response_str = str(response.json()).lower()
        
        # Should not contain email addresses
        assert "@" not in response_str, f"Email found in {endpoint}"


def test_40_no_phone_exposure(client, government_user, sample_industry_partners):
    """Test that analytics never expose phone numbers"""
    endpoints = [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/industry"
    ]
    
    for endpoint in endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {government_user['token']}"}
        )
        assert response.status_code == 200
        response_str = str(response.json())
        
        # Should not contain phone numbers
        assert "+91-" not in response_str, f"Phone number found in {endpoint}"


def test_41_no_user_id_exposure(client, government_user, sample_challenges):
    """Test that analytics never expose internal user IDs"""
    response = client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {government_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Response should not contain UUID patterns for user IDs
    response_str = str(data)
    # UUIDs contain specific patterns - check they're not present in sensitive contexts
    # (Note: project_id, challenge_id are acceptable; user_id, submitted_by are not)
    assert "submitted_by" not in response_str.lower()
    assert "user_id" not in response_str.lower()


def test_42_unauthenticated_access_denied(client):
    """Test that analytics endpoints deny unauthenticated requests"""
    endpoints = [
        "/api/v1/analytics/overview",
        "/api/v1/analytics/challenges",
        "/api/v1/analytics/projects/pipeline",
        "/api/v1/analytics/universities",
        "/api/v1/analytics/industry",
        "/api/v1/analytics/impact",
        "/api/v1/analytics/insights",
        "/api/v1/analytics/dashboard"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"
