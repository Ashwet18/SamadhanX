"""
Test database models and relationships.
"""

import pytest
from sqlalchemy import select
from app.models import *
from app.models.enums import *
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def test_user_creation(db_session):
    """Test creating a user."""
    user = User(
        name="Test User",
        email="test@example.com",
        phone="+919876543210",
        password_hash=pwd_context.hash("password123"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    # Verify user was created
    retrieved_user = db_session.execute(
        select(User).where(User.email == "test@example.com")
    ).scalar_one()
    
    assert retrieved_user.name == "Test User"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.id is not None


def test_role_assignment(db_session):
    """Test assigning roles to users."""
    # Create user
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash=pwd_context.hash("password123"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Create role
    role = Role(
        name=UserRole.CITIZEN,
        description="Citizen role"
    )
    db_session.add(role)
    db_session.flush()
    
    # Assign role to user
    user_role = UserRoleAssociation(
        user_id=user.id,
        role_id=role.id
    )
    db_session.add(user_role)
    db_session.commit()
    
    # Verify assignment
    retrieved_user = db_session.execute(
        select(User).where(User.email == "test@example.com")
    ).scalar_one()
    
    assert len(retrieved_user.roles) == 1
    assert retrieved_user.roles[0].role.name == UserRole.CITIZEN


def test_university_creation(db_session):
    """Test creating a university."""
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        description="Test university description",
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    db_session.commit()
    
    # Verify university was created
    retrieved_univ = db_session.execute(
        select(University).where(University.code == "TEST_UNIV")
    ).scalar_one()
    
    assert retrieved_univ.name == "Test University"
    assert retrieved_univ.type == UniversityType.STATE


def test_department_relationship(db_session):
    """Test university-department relationship."""
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    db_session.flush()
    
    department = Department(
        university_id=university.id,
        name="Computer Science",
        description="CS Department"
    )
    db_session.add(department)
    db_session.commit()
    
    # Verify relationship
    assert len(university.departments) == 1
    assert university.departments[0].name == "Computer Science"


def test_university_expertise(db_session):
    """Test university expertise relationship."""
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    
    expertise = Expertise(
        name="AI/ML",
        category="Technology",
        description="Artificial Intelligence and Machine Learning"
    )
    db_session.add(expertise)
    db_session.flush()
    
    univ_expertise = UniversityExpertise(
        university_id=university.id,
        expertise_id=expertise.id,
        proficiency_score=0.85,
        evidence_count=10
    )
    db_session.add(univ_expertise)
    db_session.commit()
    
    # Verify relationship
    assert len(university.expertise) == 1
    assert university.expertise[0].proficiency_score == 0.85


def test_faculty_relationship(db_session):
    """Test faculty relationships."""
    # Create user
    user = User(
        name="Dr. Test Faculty",
        email="faculty@test.com",
        password_hash=pwd_context.hash("password123"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    
    # Create university
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    
    # Create department
    department = Department(
        university_id=university.id,
        name="Computer Science"
    )
    db_session.add(department)
    db_session.flush()
    
    # Create faculty
    faculty = Faculty(
        user_id=user.id,
        university_id=university.id,
        department_id=department.id,
        designation="Professor",
        availability_status=AvailabilityStatus.AVAILABLE
    )
    db_session.add(faculty)
    db_session.commit()
    
    # Verify relationships
    assert faculty.university.name == "Test University"
    assert faculty.department.name == "Computer Science"
    assert faculty.user.name == "Dr. Test Faculty"


def test_challenge_creation(db_session):
    """Test creating a challenge."""
    # Create user
    user = User(
        name="Test Citizen",
        email="citizen@test.com",
        password_hash=pwd_context.hash("password123"),
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.flush()
    
    challenge = Challenge(
        challenge_code="CH2024001",
        submitted_by=user.id,
        title="Test Challenge",
        description="This is a test challenge description",
        status=ChallengeStatus.SUBMITTED,
        priority_level=PriorityLevel.HIGH,
        district="Test District",
        affected_population=1000
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Verify challenge
    retrieved_challenge = db_session.execute(
        select(Challenge).where(Challenge.challenge_code == "CH2024001")
    ).scalar_one()
    
    assert retrieved_challenge.title == "Test Challenge"
    assert retrieved_challenge.status == ChallengeStatus.SUBMITTED


def test_challenge_category_relationship(db_session):
    """Test challenge-category relationship."""
    # Create challenge
    challenge = Challenge(
        challenge_code="CH2024001",
        title="Test Challenge",
        description="Test description",
        status=ChallengeStatus.SUBMITTED,
        priority_level=PriorityLevel.HIGH,
        district="Test District"
    )
    db_session.add(challenge)
    
    # Create category
    category = Category(
        name="Agriculture",
        description="Agriculture related challenges"
    )
    db_session.add(category)
    db_session.flush()
    
    # Link challenge to category
    challenge_cat = ChallengeCategory(
        challenge_id=challenge.id,
        category_id=category.id
    )
    db_session.add(challenge_cat)
    db_session.commit()
    
    # Verify relationship
    assert len(challenge.categories) == 1
    assert challenge.categories[0].category.name == "Agriculture"


def test_ai_analysis_relationship(db_session):
    """Test challenge AI analysis relationship."""
    # Create challenge
    challenge = Challenge(
        challenge_code="CH2024001",
        title="Test Challenge",
        description="Test description",
        status=ChallengeStatus.AI_ANALYSIS,
        priority_level=PriorityLevel.HIGH,
        district="Test District"
    )
    db_session.add(challenge)
    db_session.flush()
    
    # Create AI analysis
    ai_analysis = ChallengeAIAnalysis(
        challenge_id=challenge.id,
        model_name="gpt-4",
        model_version="2024-01",
        summary="AI generated summary",
        primary_domain="Agriculture",
        severity_score=0.75,
        urgency_score=0.80,
        confidence_score=0.85
    )
    db_session.add(ai_analysis)
    db_session.commit()
    
    # Verify relationship
    assert challenge.ai_analysis is not None
    assert challenge.ai_analysis.model_name == "gpt-4"


def test_challenge_assignment(db_session):
    """Test challenge assignment to university."""
    # Create challenge
    challenge = Challenge(
        challenge_code="CH2024001",
        title="Test Challenge",
        description="Test description",
        status=ChallengeStatus.MATCHING,
        priority_level=PriorityLevel.HIGH,
        district="Test District"
    )
    db_session.add(challenge)
    
    # Create university
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    db_session.flush()
    
    # Create assignment
    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        university_id=university.id,
        assignment_score=85,
        reason="Strong expertise match",
        status=AssignmentStatus.RECOMMENDED
    )
    db_session.add(assignment)
    db_session.commit()
    
    # Verify assignment
    assert len(challenge.assignments) == 1
    assert challenge.assignments[0].assignment_score == 85


def test_project_relationship(db_session):
    """Test project relationships."""
    # Create challenge
    challenge = Challenge(
        challenge_code="CH2024001",
        title="Test Challenge",
        description="Test description",
        status=ChallengeStatus.PROJECT_CREATED,
        priority_level=PriorityLevel.HIGH,
        district="Test District"
    )
    db_session.add(challenge)
    
    # Create university
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    db_session.flush()
    
    # Create project
    project = Project(
        challenge_id=challenge.id,
        university_id=university.id,
        name="Test Project",
        description="Project description",
        status=ProjectStatus.PLANNING,
        budget=100000
    )
    db_session.add(project)
    db_session.commit()
    
    # Verify relationships
    assert len(challenge.projects) == 1
    assert challenge.projects[0].name == "Test Project"
    assert project.university.name == "Test University"


def test_project_milestone(db_session):
    """Test project milestone creation."""
    # Create challenge and university
    challenge = Challenge(
        challenge_code="CH2024001",
        title="Test Challenge",
        description="Test description",
        status=ChallengeStatus.PROJECT_CREATED,
        priority_level=PriorityLevel.HIGH,
        district="Test District"
    )
    db_session.add(challenge)
    
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    db_session.flush()
    
    # Create project
    project = Project(
        challenge_id=challenge.id,
        university_id=university.id,
        name="Test Project",
        description="Project description",
        status=ProjectStatus.PLANNING
    )
    db_session.add(project)
    db_session.flush()
    
    # Create milestone
    milestone = ProjectMilestone(
        project_id=project.id,
        name="Phase 1",
        description="First phase",
        status=MilestoneStatus.PENDING,
        completion_percentage=0
    )
    db_session.add(milestone)
    db_session.commit()
    
    # Verify milestone
    assert len(project.milestones) == 1
    assert project.milestones[0].name == "Phase 1"


def test_impact_metric(db_session):
    """Test impact metric creation."""
    # Create minimal project setup
    challenge = Challenge(
        challenge_code="CH2024001",
        title="Test Challenge",
        description="Test",
        status=ChallengeStatus.PROJECT_CREATED,
        priority_level=PriorityLevel.HIGH,
        district="Test District"
    )
    db_session.add(challenge)
    
    university = University(
        name="Test University",
        code="TEST_UNIV",
        type=UniversityType.STATE,
        district="Test District",
        state="Jharkhand",
        verification_status=VerificationStatus.VERIFIED
    )
    db_session.add(university)
    db_session.flush()
    
    project = Project(
        challenge_id=challenge.id,
        university_id=university.id,
        name="Test Project",
        status=ProjectStatus.PLANNING
    )
    db_session.add(project)
    db_session.flush()
    
    # Create impact metric
    metric = ImpactMetric(
        project_id=project.id,
        metric_name="Beneficiaries Reached",
        baseline_value=0,
        target_value=1000,
        actual_value=500,
        unit="people",
        verification_status=VerificationStatus.PENDING
    )
    db_session.add(metric)
    db_session.commit()
    
    # Verify metric
    assert len(project.impact_metrics) == 1
    assert project.impact_metrics[0].metric_name == "Beneficiaries Reached"
