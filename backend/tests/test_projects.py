"""
Tests for project lifecycle management.

Covers:
- Project creation
- Team management
- Proposal workflow
- Milestone management
- Lifecycle state machine
- Impact measurement
- Authorization
- Integration
"""

import pytest
from datetime import date, datetime, timedelta
from uuid import uuid4

from app.models.user import User
from app.models.university import University, Faculty, Student, Department
from app.models.challenge import Challenge, ChallengeAssignment
from app.models.project import Project, ProjectMember, ProjectProposal, ProjectMilestone
from app.models.platform import ImpactMetric, Notification, AuditLog
from app.models.enums import (
    UserRole,
    ChallengeStatus,
    AssignmentStatus,
    ProjectStatus,
    ProposalStatus,
    MilestoneStatus,
    ProjectMemberRole,
    VerificationStatus
)
from app.services.projects.project_service import ProjectService
from app.services.projects.team_service import TeamService
from app.services.projects.proposal_service import ProposalService
from app.services.projects.milestone_service import MilestoneService
from app.services.projects.impact_service import ImpactService
from app.services.projects.lifecycle import ProjectLifecycleManager
from app.core.security import SecurityManager


# ==================== FIXTURES ====================

@pytest.fixture
def university(db_session):
    """Create test university."""
    univ = University(
        name="Test University",
        code="TEST",
        district="Test District",
        state="Jharkhand",
        address="Test Address",
        email="test@university.edu",
        phone="1234567890"
    )
    db_session.add(univ)
    db_session.commit()
    db_session.refresh(univ)
    return univ


@pytest.fixture
def department(db_session, university):
    """Create test department."""
    dept = Department(
        university_id=university.id,
        name="Computer Science",
        code="CS"
    )
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def government_user(db_session):
    """Create government officer user."""
    user = User(
        email="govt@jharkhand.gov.in",
        phone="9999999999",
        password_hash=SecurityManager.hash_password("password123"),
        role=UserRole.GOVERNMENT_OFFICER,
        first_name="Government",
        last_name="Officer",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def faculty_user(db_session, university):
    """Create faculty user."""
    user = User(
        email="faculty@test.edu",
        phone="8888888888",
        password_hash=SecurityManager.hash_password("password123"),
        role=UserRole.FACULTY,
        first_name="Faculty",
        last_name="Member",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    faculty = Faculty(
        user_id=user.id,
        university_id=university.id,
        employee_id="FAC001",
        designation="Professor"
    )
    db_session.add(faculty)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_user(db_session, university):
    """Create student user."""
    user = User(
        email="student@test.edu",
        phone="7777777777",
        password_hash=SecurityManager.hash_password("password123"),
        role=UserRole.STUDENT,
        first_name="Student",
        last_name="Name",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    student = Student(
        user_id=user.id,
        university_id=university.id,
        enrollment_number="STU001",
        program="B.Tech"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def citizen_user(db_session):
    """Create citizen user."""
    user = User(
        email="citizen@example.com",
        phone="6666666666",
        password_hash=SecurityManager.hash_password("password123"),
        role=UserRole.CITIZEN,
        first_name="Citizen",
        last_name="User",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def challenge(db_session, citizen_user):
    """Create a validated challenge."""
    challenge = Challenge(
        challenge_code="CHL-JH-2024-00001",
        submitted_by=citizen_user.id,
        title="Test Challenge for Project",
        description="A validated challenge ready for university matching",
        district="Ranchi",
        status=ChallengeStatus.VALIDATED
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge


@pytest.fixture
def accepted_assignment(db_session, challenge, university):
    """Create an accepted challenge assignment."""
    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        university_id=university.id,
        status=AssignmentStatus.ACCEPTED,
        match_score=0.95,
        match_explanation={"reason": "Perfect match"}
    )
    db_session.add(assignment)
    db_session.commit()
    
    # Update challenge status
    challenge.status = ChallengeStatus.ACCEPTED
    db_session.commit()
    db_session.refresh(assignment)
    return assignment


# ==================== PROJECT CREATION TESTS ====================

def test_create_project_from_accepted_assignment(db_session, faculty_user, challenge, accepted_assignment):
    """Test successful project creation from accepted assignment."""
    service = ProjectService(db_session)
    
    project = service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="A test project for solving the challenge",
        objective="Solve the challenge effectively"
    )
    
    assert project is not None
    assert project.project_code.startswith("PRJ-JH-")
    assert project.status == ProjectStatus.PLANNING
    assert project.challenge_id == challenge.id
    assert project.created_by == faculty_user.id
    assert project.name == "Test Project"


def test_reject_project_from_recommended_assignment(db_session, faculty_user, challenge, university):
    """Test that project cannot be created from RECOMMENDED assignment."""
    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        university_id=university.id,
        status=AssignmentStatus.RECOMMENDED,
        match_score=0.85,
        match_explanation={}
    )
    db_session.add(assignment)
    db_session.commit()
    
    service = ProjectService(db_session)
    
    with pytest.raises(ValueError, match="No ACCEPTED assignment"):
        service.create_project(
            challenge_id=challenge.id,
            current_user=faculty_user,
            name="Test Project",
            description="Should fail"
        )


def test_reject_project_from_invited_assignment(db_session, faculty_user, challenge, university):
    """Test that project cannot be created from INVITED assignment."""
    assignment = ChallengeAssignment(
        challenge_id=challenge.id,
        university_id=university.id,
        status=AssignmentStatus.INVITED,
        match_score=0.90,
        match_explanation={}
    )
    db_session.add(assignment)
    db_session.commit()
    
    service = ProjectService(db_session)
    
    with pytest.raises(ValueError, match="No ACCEPTED assignment"):
        service.create_project(
            challenge_id=challenge.id,
            current_user=faculty_user,
            name="Test Project",
            description="Should fail"
        )


def test_reject_project_without_accepted_assignment(db_session, faculty_user, challenge):
    """Test that project requires accepted assignment."""
    service = ProjectService(db_session)
    
    with pytest.raises(ValueError, match="No ACCEPTED assignment"):
        service.create_project(
            challenge_id=challenge.id,
            current_user=faculty_user,
            name="Test Project",
            description="Should fail"
        )


def test_prevent_duplicate_active_project(db_session, faculty_user, challenge, accepted_assignment):
    """Test that duplicate active projects are prevented."""
    service = ProjectService(db_session)
    
    # Create first project
    project1 = service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="First Project",
        description="First project"
    )
    
    # Try to create second project for same challenge/university
    with pytest.raises(ValueError, match="active project already exists"):
        service.create_project(
            challenge_id=challenge.id,
            current_user=faculty_user,
            name="Second Project",
            description="Should fail"
        )


def test_project_code_generation(db_session, faculty_user, challenge, accepted_assignment):
    """Test project code generation format."""
    service = ProjectService(db_session)
    
    project = service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Format: PRJ-JH-YYYY-XXXXX
    assert project.project_code.startswith("PRJ-JH-")
    parts = project.project_code.split("-")
    assert len(parts) == 4
    assert parts[0] == "PRJ"
    assert parts[1] == "JH"
    assert parts[2] == str(datetime.now().year)
    assert len(parts[3]) == 5
    assert parts[3].isdigit()


def test_project_creation_authorization(db_session, citizen_user, challenge, accepted_assignment):
    """Test that citizens cannot create projects."""
    service = ProjectService(db_session)
    
    with pytest.raises(ValueError, match="not associated with a university"):
        service.create_project(
            challenge_id=challenge.id,
            current_user=citizen_user,
            name="Test Project",
            description="Should fail"
        )


# ==================== TEAM MANAGEMENT TESTS ====================

def test_add_team_member(db_session, faculty_user, student_user, challenge, accepted_assignment):
    """Test adding a team member."""
    # Create project
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Add team member
    team_service = TeamService(db_session)
    member = team_service.add_team_member(
        project_id=project.id,
        current_user=faculty_user,
        user_id=student_user.id,
        role=ProjectMemberRole.DEVELOPER
    )
    
    assert member is not None
    assert member.user_id == student_user.id
    assert member.role == ProjectMemberRole.DEVELOPER
    assert member.project_id == project.id


def test_prevent_duplicate_team_membership(db_session, faculty_user, student_user, challenge, accepted_assignment):
    """Test that duplicate team membership is prevented."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    team_service = TeamService(db_session)
    
    # Add member once
    team_service.add_team_member(
        project_id=project.id,
        current_user=faculty_user,
        user_id=student_user.id,
        role=ProjectMemberRole.DEVELOPER
    )
    
    # Try to add again
    with pytest.raises(ValueError, match="already a member"):
        team_service.add_team_member(
            project_id=project.id,
            current_user=faculty_user,
            user_id=student_user.id,
            role=ProjectMemberRole.TESTER
        )


def test_remove_team_member(db_session, faculty_user, student_user, challenge, accepted_assignment):
    """Test removing a team member."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    team_service = TeamService(db_session)
    member = team_service.add_team_member(
        project_id=project.id,
        current_user=faculty_user,
        user_id=student_user.id,
        role=ProjectMemberRole.DEVELOPER
    )
    
    # Remove member
    team_service.remove_team_member(
        member_id=member.id,
        current_user=faculty_user
    )
    
    # Verify removed
    removed_member = db_session.query(ProjectMember).filter(ProjectMember.id == member.id).first()
    assert removed_member is None


def test_update_team_member_role(db_session, faculty_user, student_user, challenge, accepted_assignment):
    """Test updating team member role."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    team_service = TeamService(db_session)
    member = team_service.add_team_member(
        project_id=project.id,
        current_user=faculty_user,
        user_id=student_user.id,
        role=ProjectMemberRole.DEVELOPER
    )
    
    # Update role
    updated_member = team_service.update_team_member(
        member_id=member.id,
        current_user=faculty_user,
        role=ProjectMemberRole.TEAM_LEAD
    )
    
    assert updated_member.role == ProjectMemberRole.TEAM_LEAD


def test_team_authorization(db_session, faculty_user, student_user, citizen_user, challenge, accepted_assignment):
    """Test team management authorization."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    team_service = TeamService(db_session)
    
    # Citizen cannot add team members
    with pytest.raises((ValueError, PermissionError)):
        team_service.add_team_member(
            project_id=project.id,
            current_user=citizen_user,
            user_id=student_user.id,
            role=ProjectMemberRole.DEVELOPER
        )


# ==================== PROPOSAL WORKFLOW TESTS ====================

def test_create_proposal(db_session, faculty_user, challenge, accepted_assignment):
    """Test creating a project proposal."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="A test proposal summary",
        problem_statement="The problem we are solving",
        proposed_solution="Our proposed solution approach",
        innovation="Innovative aspects",
        expected_outcomes="Expected outcomes"
    )
    
    assert proposal is not None
    assert proposal.status == ProposalStatus.DRAFT
    assert proposal.title == "Test Proposal"


def test_update_draft_proposal(db_session, faculty_user, challenge, accepted_assignment):
    """Test updating a draft proposal."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Initial Proposal",
        summary="Initial summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    # Update
    updated_proposal = proposal_service.update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Updated Proposal",
        summary="Updated summary"
    )
    
    assert updated_proposal.title == "Updated Proposal"
    assert updated_proposal.summary == "Updated summary"


def test_submit_proposal(db_session, faculty_user, challenge, accepted_assignment):
    """Test submitting a proposal for review."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="Summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    # Submit
    submitted_proposal = proposal_service.submit_proposal(
        project_id=project.id,
        current_user=faculty_user
    )
    
    assert submitted_proposal.status == ProposalStatus.SUBMITTED
    assert submitted_proposal.submitted_at is not None


def test_government_approve_proposal(db_session, faculty_user, government_user, challenge, accepted_assignment):
    """Test government approval of proposal."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="Summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    proposal_service.submit_proposal(project_id=project.id, current_user=faculty_user)
    
    # Government approves
    approved_proposal = proposal_service.approve_proposal(
        project_id=project.id,
        current_user=government_user,
        comments="Approved for implementation"
    )
    
    assert approved_proposal.status == ProposalStatus.APPROVED
    assert approved_proposal.reviewed_by == government_user.id


def test_government_request_revision(db_session, faculty_user, government_user, challenge, accepted_assignment):
    """Test government requesting revision."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="Summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    proposal_service.submit_proposal(project_id=project.id, current_user=faculty_user)
    
    # Request revision
    revised_proposal = proposal_service.request_revision(
        project_id=project.id,
        current_user=government_user,
        comments="Please provide more details on implementation"
    )
    
    assert revised_proposal.status == ProposalStatus.REVISION_REQUESTED
    assert revised_proposal.review_comments == "Please provide more details on implementation"


def test_government_reject_proposal(db_session, faculty_user, government_user, challenge, accepted_assignment):
    """Test government rejecting proposal."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="Summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    proposal_service.submit_proposal(project_id=project.id, current_user=faculty_user)
    
    # Reject
    rejected_proposal = proposal_service.reject_proposal(
        project_id=project.id,
        current_user=government_user,
        comments="Does not meet requirements"
    )
    
    assert rejected_proposal.status == ProposalStatus.REJECTED


def test_invalid_proposal_transition(db_session, faculty_user, challenge, accepted_assignment):
    """Test invalid proposal status transition."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="Summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    # Cannot update after submission without revision request
    proposal_service.submit_proposal(project_id=project.id, current_user=faculty_user)
    
    with pytest.raises(ValueError, match="Cannot edit"):
        proposal_service.update_proposal(
            project_id=project.id,
            current_user=faculty_user,
            title="Updated"
        )


def test_unauthorized_proposal_approval(db_session, faculty_user, student_user, challenge, accepted_assignment):
    """Test that students cannot approve proposals."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    proposal_service = ProposalService(db_session)
    proposal = proposal_service.create_or_update_proposal(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Proposal",
        summary="Summary",
        problem_statement="Problem",
        proposed_solution="Solution"
    )
    
    proposal_service.submit_proposal(project_id=project.id, current_user=faculty_user)
    
    # Student cannot approve
    with pytest.raises(ValueError, match="Only government"):
        proposal_service.approve_proposal(
            project_id=project.id,
            current_user=student_user,
            comments="Unauthorized"
        )


# ==================== MILESTONE TESTS ====================

def test_create_milestone(db_session, faculty_user, challenge, accepted_assignment):
    """Test creating a project milestone."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    milestone_service = MilestoneService(db_session)
    milestone = milestone_service.create_milestone(
        project_id=project.id,
        current_user=faculty_user,
        title="First Milestone",
        description="Initial milestone",
        sequence_number=1,
        planned_end_date=date.today() + timedelta(days=30)
    )
    
    assert milestone is not None
    assert milestone.status == MilestoneStatus.PLANNED
    assert milestone.sequence_number == 1


def test_milestone_sequence_uniqueness(db_session, faculty_user, challenge, accepted_assignment):
    """Test that milestone sequence numbers are unique per project."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    milestone_service = MilestoneService(db_session)
    
    # Create first milestone
    milestone_service.create_milestone(
        project_id=project.id,
        current_user=faculty_user,
        title="First Milestone",
        sequence_number=1
    )
    
    # Try to create duplicate sequence
    with pytest.raises(ValueError, match="Sequence number 1 already exists"):
        milestone_service.create_milestone(
            project_id=project.id,
            current_user=faculty_user,
            title="Second Milestone",
            sequence_number=1
        )


def test_update_milestone(db_session, faculty_user, challenge, accepted_assignment):
    """Test updating a milestone."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    milestone_service = MilestoneService(db_session)
    milestone = milestone_service.create_milestone(
        project_id=project.id,
        current_user=faculty_user,
        title="Original Title",
        sequence_number=1
    )
    
    # Update
    updated_milestone = milestone_service.update_milestone(
        milestone_id=milestone.id,
        current_user=faculty_user,
        title="Updated Title",
        description="Updated description"
    )
    
    assert updated_milestone.title == "Updated Title"
    assert updated_milestone.description == "Updated description"


def test_complete_milestone(db_session, faculty_user, challenge, accepted_assignment):
    """Test completing a milestone."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    milestone_service = MilestoneService(db_session)
    milestone = milestone_service.create_milestone(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Milestone",
        sequence_number=1
    )
    
    # Complete
    completed_milestone = milestone_service.complete_milestone(
        milestone_id=milestone.id,
        current_user=faculty_user
    )
    
    assert completed_milestone.status == MilestoneStatus.COMPLETED
    assert completed_milestone.actual_end_date is not None


def test_invalid_milestone_operation(db_session, faculty_user, challenge, accepted_assignment):
    """Test invalid milestone operations."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    milestone_service = MilestoneService(db_session)
    milestone = milestone_service.create_milestone(
        project_id=project.id,
        current_user=faculty_user,
        title="Test Milestone",
        sequence_number=1
    )
    
    # Complete twice
    milestone_service.complete_milestone(milestone_id=milestone.id, current_user=faculty_user)
    
    with pytest.raises(ValueError, match="Cannot complete milestone"):
        milestone_service.complete_milestone(milestone_id=milestone.id, current_user=faculty_user)


# ==================== LIFECYCLE STATE MACHINE TESTS ====================

def test_valid_status_transition(db_session, faculty_user, challenge, accepted_assignment):
    """Test valid project status transitions."""
    lifecycle = ProjectLifecycleManager()
    
    # Test valid transitions
    assert lifecycle.is_valid_transition(ProjectStatus.PLANNING, ProjectStatus.TEAM_FORMATION)
    assert lifecycle.is_valid_transition(ProjectStatus.TEAM_FORMATION, ProjectStatus.PROPOSAL)
    assert lifecycle.is_valid_transition(ProjectStatus.APPROVED, ProjectStatus.PROTOTYPE)
    assert lifecycle.is_valid_transition(ProjectStatus.DEPLOYED, ProjectStatus.COMPLETED)


def test_invalid_status_transition(db_session):
    """Test invalid project status transitions."""
    lifecycle = ProjectLifecycleManager()
    
    # Test invalid transitions
    assert not lifecycle.is_valid_transition(ProjectStatus.PLANNING, ProjectStatus.DEPLOYED)
    assert not lifecycle.is_valid_transition(ProjectStatus.PROTOTYPE, ProjectStatus.PLANNING)
    assert not lifecycle.is_valid_transition(ProjectStatus.COMPLETED, ProjectStatus.TESTING)


def test_on_hold_transition(db_session):
    """Test that ON_HOLD can be reached from any state."""
    lifecycle = ProjectLifecycleManager()
    
    for status in ProjectStatus:
        if status != ProjectStatus.ON_HOLD:
            assert lifecycle.is_valid_transition(status, ProjectStatus.ON_HOLD)


def test_cancellation_transition(db_session):
    """Test that CANCELLED can be reached from any state."""
    lifecycle = ProjectLifecycleManager()
    
    for status in ProjectStatus:
        if status != ProjectStatus.CANCELLED:
            assert lifecycle.is_valid_transition(status, ProjectStatus.CANCELLED)


def test_deployment_transition(db_session, faculty_user, challenge, accepted_assignment):
    """Test deployment transition."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Progress through valid states to DEPLOYED
    project.status = ProjectStatus.PILOT
    db_session.commit()
    
    updated_project = project_service.update_project_status(
        project_id=project.id,
        new_status=ProjectStatus.DEPLOYED,
        current_user=faculty_user
    )
    
    assert updated_project.status == ProjectStatus.DEPLOYED


def test_completion_transition(db_session, faculty_user, challenge, accepted_assignment):
    """Test completion sets end date."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Progress to DEPLOYED
    project.status = ProjectStatus.DEPLOYED
    db_session.commit()
    
    # Complete
    completed_project = project_service.update_project_status(
        project_id=project.id,
        new_status=ProjectStatus.COMPLETED,
        current_user=faculty_user
    )
    
    assert completed_project.status == ProjectStatus.COMPLETED
    assert completed_project.actual_end_date is not None


# ==================== IMPACT MEASUREMENT TESTS ====================

def test_create_impact_record(db_session, faculty_user, challenge, accepted_assignment):
    """Test creating an impact measurement."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    impact_service = ImpactService(db_session)
    impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1000,
        geographic_area="Ranchi District",
        baseline_value=0.0,
        actual_value=1000.0,
        unit="people"
    )
    
    assert impact is not None
    assert impact.metric_name == "Beneficiaries Reached"
    assert impact.beneficiaries_count == 1000
    assert impact.verification_status == VerificationStatus.PENDING


def test_update_impact(db_session, faculty_user, challenge, accepted_assignment):
    """Test updating an impact measurement."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    impact_service = ImpactService(db_session)
    impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1000
    )
    
    # Update
    updated_impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1500,
        impact_description="Reached more beneficiaries"
    )
    
    assert updated_impact.beneficiaries_count == 1500
    assert updated_impact.impact_description == "Reached more beneficiaries"


def test_submit_impact(db_session, faculty_user, challenge, accepted_assignment):
    """Test submitting impact for verification."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    impact_service = ImpactService(db_session)
    impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1000
    )
    
    # Submit
    submitted_impact = impact_service.submit_impact(
        impact_id=impact.id,
        current_user=faculty_user
    )
    
    assert submitted_impact.submitted_by == faculty_user.id


def test_government_verify_impact(db_session, faculty_user, government_user, challenge, accepted_assignment):
    """Test government verification of impact."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    impact_service = ImpactService(db_session)
    impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1000
    )
    
    impact_service.submit_impact(impact_id=impact.id, current_user=faculty_user)
    
    # Verify
    verified_impact = impact_service.verify_impact(
        impact_id=impact.id,
        current_user=government_user,
        comments="Verified through field inspection"
    )
    
    assert verified_impact.verification_status == VerificationStatus.VERIFIED
    assert verified_impact.verified_by == government_user.id


def test_impact_revision_request(db_session, faculty_user, government_user, challenge, accepted_assignment):
    """Test government requesting impact revision."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    impact_service = ImpactService(db_session)
    impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1000
    )
    
    impact_service.submit_impact(impact_id=impact.id, current_user=faculty_user)
    
    # Request revision
    revised_impact = impact_service.request_revision(
        impact_id=impact.id,
        current_user=government_user,
        comments="Need more evidence"
    )
    
    assert revised_impact.verification_status == VerificationStatus.REJECTED
    assert revised_impact.review_comments == "Need more evidence"


def test_prevent_student_impact_verification(db_session, faculty_user, student_user, challenge, accepted_assignment):
    """Test that students cannot verify impact."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    impact_service = ImpactService(db_session)
    impact = impact_service.create_or_update_impact(
        project_id=project.id,
        current_user=faculty_user,
        metric_name="Beneficiaries Reached",
        beneficiaries_count=1000
    )
    
    with pytest.raises(ValueError, match="Only government"):
        impact_service.verify_impact(
            impact_id=impact.id,
            current_user=student_user,
            comments="Unauthorized"
        )


# ==================== INTEGRATION TESTS ====================

def test_notification_creation(db_session, faculty_user, challenge, accepted_assignment):
    """Test that notifications are created for project events."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Check notification created
    notifications = db_session.query(Notification).filter(
        Notification.reference_type == "PROJECT"
    ).all()
    
    # Should have created notification for government
    assert len(notifications) > 0


def test_audit_event_creation(db_session, faculty_user, challenge, accepted_assignment):
    """Test that audit logs are created for project events."""
    project_service = ProjectService(db_session)
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Check audit log created
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.action == "PROJECT_CREATED"
    ).all()
    
    assert len(audit_logs) > 0


def test_project_challenge_integration(db_session, faculty_user, challenge, accepted_assignment):
    """Test project and challenge lifecycle integration."""
    project_service = ProjectService(db_session)
    
    # Create project
    project = project_service.create_project(
        challenge_id=challenge.id,
        current_user=faculty_user,
        name="Test Project",
        description="Test"
    )
    
    # Check challenge status updated
    db_session.refresh(challenge)
    assert challenge.status == ChallengeStatus.PROJECT_CREATED


def test_pagination_filtering(db_session, faculty_user, challenge, accepted_assignment, university):
    """Test project list pagination and filtering."""
    project_service = ProjectService(db_session)
    
    # Create multiple projects
    for i in range(5):
        challenge_i = Challenge(
            challenge_code=f"CHL-JH-2024-{i:05d}",
            title=f"Challenge {i}",
            description="Test challenge",
            district="Ranchi",
            status=ChallengeStatus.ACCEPTED,
            submitted_by=faculty_user.id
        )
        db_session.add(challenge_i)
        db_session.commit()
        
        assignment_i = ChallengeAssignment(
            challenge_id=challenge_i.id,
            university_id=university.id,
            status=AssignmentStatus.ACCEPTED,
            match_score=0.9,
            match_explanation={}
        )
        db_session.add(assignment_i)
        db_session.commit()
        
        project_service.create_project(
            challenge_id=challenge_i.id,
            current_user=faculty_user,
            name=f"Project {i}",
            description="Test"
        )
    
    # List with pagination
    projects, total = project_service.list_projects(
        current_user=faculty_user,
        page=1,
        page_size=3
    )
    
    assert len(projects) == 3
    assert total == 5


def test_transaction_rollback(db_session, faculty_user, challenge):
    """Test that transactions rollback on failure."""
    # No accepted assignment - should fail
    project_service = ProjectService(db_session)
    
    try:
        project_service.create_project(
            challenge_id=challenge.id,
            current_user=faculty_user,
            name="Should Fail",
            description="Test"
        )
    except ValueError:
        pass
    
    # No project should be created
    projects = db_session.query(Project).all()
    assert len(projects) == 0


def test_existing_functionality_regression(db_session, citizen_user):
    """Test that existing challenge functionality still works."""
    # Create a challenge
    challenge = Challenge(
        challenge_code="CHL-JH-2024-99999",
        submitted_by=citizen_user.id,
        title="Regression Test Challenge",
        description="Testing that existing functionality works",
        district="Ranchi",
        status=ChallengeStatus.SUBMITTED
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Verify challenge created
    assert challenge.id is not None
    assert challenge.status == ChallengeStatus.SUBMITTED
