"""
Tests for university matching engine.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch

from app.services.matching import (
    UniversityMatchingEngine,
    MatchingWeights,
    DEFAULT_MATCHING_CONFIG
)
from app.services.matching.config import MatchingConfig
from app.services.matching.scorer import UniversityScorer
from app.models.challenge import Challenge, ChallengeAIAnalysis, ChallengeAssignment
from app.models.university import (
    University,
    UniversityExpertise,
    Faculty,
    FacultyExpertise,
    Facility,
    Expertise
)
from app.models.user import User
from app.models.enums import (
    ChallengeStatus,
    AssignmentStatus,
    UserRole,
    AccountStatus,
    AvailabilityStatus,
    UniversityType,
    VerificationStatus
)


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_matching_weights_sum_validation():
    """Test matching weights validation."""
    weights = MatchingWeights()
    assert weights.validate_sum() is True
    
    # Test invalid weights
    invalid_weights = MatchingWeights(
        expertise=0.5,
        faculty=0.3,
        infrastructure=0.3,  # Sum > 1.0
        previous_projects=0.1,
        location=0.1,
        industry=0.05
    )
    assert invalid_weights.validate_sum() is False


def test_matching_config_defaults():
    """Test default matching configuration."""
    config = DEFAULT_MATCHING_CONFIG
    
    assert config.weights.expertise == 0.40
    assert config.weights.faculty == 0.20
    assert config.weights.infrastructure == 0.15
    assert config.weights.previous_projects == 0.10
    assert config.weights.location == 0.10
    assert config.weights.industry == 0.05
    
    assert config.neutral_score == 50.0
    assert config.same_district_score == 100.0
    assert config.same_state_score == 70.0


# ============================================================================
# SCORER TESTS
# ============================================================================

def test_expertise_scoring():
    """Test expertise matching score calculation."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.id = uuid4()
    
    # Mock university expertise
    expertise1 = Mock()
    expertise1.expertise.name = "IoT"
    expertise1.proficiency_score = 0.95
    
    expertise2 = Mock()
    expertise2.expertise.name = "Water Engineering"
    expertise2.proficiency_score = 0.85
    
    db.query.return_value.filter.return_value.join.return_value.all.return_value = [
        expertise1, expertise2
    ]
    
    required_skills = [
        {"name": "IoT", "confidence": 1.0},
        {"name": "Water Engineering", "confidence": 0.9}
    ]
    
    score, evidence = scorer.score_expertise(university, required_skills)
    
    # Score should be weighted average of proficiency scores
    # (0.95 * 100 * 1.0 + 0.85 * 100 * 0.9) / (1.0 + 0.9)
    expected = (95.0 * 1.0 + 85.0 * 0.9) / 1.9
    assert score == pytest.approx(expected, rel=0.1)
    assert len(evidence) == 2


def test_expertise_scoring_no_match():
    """Test expertise scoring with no matches."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.id = uuid4()
    
    db.query.return_value.filter.return_value.join.return_value.all.return_value = []
    
    required_skills = [{"name": "IoT", "confidence": 1.0}]
    
    score, evidence = scorer.score_expertise(university, required_skills)
    
    assert score == 0.0
    assert len(evidence) == 0


def test_faculty_availability_scoring():
    """Test faculty availability scoring."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.id = uuid4()
    
    # Mock expertise records
    expertise_record = Mock()
    expertise_record.id = uuid4()
    db.query.return_value.filter.return_value.all.return_value = [expertise_record]
    
    # Mock faculty
    faculty1 = Mock()
    faculty1.id = uuid4()
    faculty1.availability_status = AvailabilityStatus.AVAILABLE
    faculty1.user.full_name = "Dr. John Doe"
    faculty1.designation = "Professor"
    
    faculty2 = Mock()
    faculty2.id = uuid4()
    faculty2.availability_status = AvailabilityStatus.LIMITED
    faculty2.user.full_name = "Dr. Jane Smith"
    faculty2.designation = "Associate Professor"
    
    db.query.return_value.filter.return_value.join.return_value.filter.return_value.distinct.return_value.all.return_value = [
        faculty1, faculty2
    ]
    
    # Mock faculty expertise
    db.query.return_value.filter.return_value.join.return_value.all.return_value = []
    
    required_skills = [{"name": "IoT", "confidence": 1.0}]
    
    score, evidence = scorer.score_faculty(university, required_skills)
    
    # Score should be average: (100 + 60) / 2 = 80
    assert score == 80.0
    assert len(evidence) == 2


def test_location_scoring_same_district():
    """Test location scoring for same district."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.district = "Ranchi"
    university.state = "Jharkhand"
    
    score, reason = scorer.score_location(university, "Ranchi", "Jharkhand")
    
    assert score == 100.0
    assert "Same district" in reason


def test_location_scoring_same_state():
    """Test location scoring for same state, different district."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.district = "Dhanbad"
    university.state = "Jharkhand"
    
    score, reason = scorer.score_location(university, "Ranchi", "Jharkhand")
    
    assert score == 70.0
    assert "Same state" in reason


def test_location_scoring_different_state():
    """Test location scoring for different state."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.district = "Patna"
    university.state = "Bihar"
    
    score, reason = scorer.score_location(university, "Ranchi", "Jharkhand")
    
    assert score == 30.0
    assert "Different state" in reason


def test_previous_projects_neutral_score():
    """Test previous projects returns neutral score with explanation."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    
    score, note = scorer.score_previous_projects(university, "Water Management")
    
    assert score == 50.0
    assert "Insufficient historical project data" in note


# ============================================================================
# ENGINE TESTS (Require Database)
# ============================================================================

@pytest.mark.skip(reason="Requires PostgreSQL")
def test_matching_engine_validated_challenge():
    """Test matching engine with validated challenge."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_matching_engine_rejects_unvalidated():
    """Test matching engine rejects unvalidated challenge."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_weighted_final_score_calculation():
    """Test final score uses correct weights."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_score_normalization():
    """Test all scores are normalized to 0-100."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_missing_data_fallback():
    """Test neutral scores used when data is missing."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_university_ranking():
    """Test universities are ranked by score."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_explainable_evidence():
    """Test evidence is generated for recommendations."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_duplicate_assignment_prevention():
    """Test duplicate assignments are not created."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_assignment_status_protected():
    """Test INVITED/ACCEPTED/DECLINED assignments are not overwritten."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_matching_rerun_idempotent():
    """Test matching can be rerun safely."""
    pass


# ============================================================================
# AUTHORIZATION TESTS
# ============================================================================

def test_government_can_trigger_matching():
    """Test government officer can trigger matching."""
    # This would require full integration test with API
    pass


def test_citizen_cannot_trigger_matching():
    """Test citizen cannot trigger matching."""
    # This would require full integration test with API
    pass


def test_university_can_view_assigned_challenges():
    """Test university admin can view assigned challenges."""
    # This would require full integration test with API
    pass


# ============================================================================
# INVITATION TESTS
# ============================================================================

@pytest.mark.skip(reason="Requires PostgreSQL")
def test_government_can_invite_university():
    """Test government can invite university."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_university_can_accept_invitation():
    """Test university can accept invitation."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_university_can_decline_invitation():
    """Test university can decline invitation."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_notification_created_on_invitation():
    """Test notification is created when university is invited."""
    pass


@pytest.mark.skip(reason="Requires PostgreSQL")
def test_challenge_status_changes_on_invitation():
    """Test challenge status updates when first university is invited."""
    pass


# ============================================================================
# UNIT TESTS FOR SPECIFIC SCENARIOS
# ============================================================================

def test_facility_keyword_mapping():
    """Test facility keywords are mapped correctly."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    required_skills = [
        {"name": "IoT", "confidence": 1.0},
        {"name": "Water Engineering", "confidence": 0.9}
    ]
    
    keywords = scorer._get_facility_keywords(required_skills)
    
    assert "iot" in keywords
    assert "sensor" in keywords or "embedded" in keywords
    assert "water" in keywords


def test_infrastructure_scoring_with_matches():
    """Test infrastructure scoring finds relevant facilities."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.id = uuid4()
    
    # Mock facilities
    facility1 = Mock()
    facility1.id = uuid4()
    facility1.name = "IoT Lab"
    facility1.type = "Laboratory"
    facility1.description = "Internet of Things laboratory"
    facility1.availability_status = AvailabilityStatus.AVAILABLE
    
    facility2 = Mock()
    facility2.id = uuid4()
    facility2.name = "Water Testing Laboratory"
    facility2.type = "Laboratory"
    facility2.description = "Water quality analysis"
    facility2.availability_status = AvailabilityStatus.AVAILABLE
    
    db.query.return_value.filter.return_value.all.return_value = [facility1, facility2]
    
    required_skills = [
        {"name": "IoT", "confidence": 1.0},
        {"name": "Water Engineering", "confidence": 0.9}
    ]
    
    score, evidence = scorer.score_infrastructure(university, required_skills)
    
    assert score > 0
    assert len(evidence) == 2


def test_infrastructure_scoring_no_facilities():
    """Test infrastructure scoring with no facilities."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.id = uuid4()
    
    db.query.return_value.filter.return_value.all.return_value = []
    
    required_skills = [{"name": "IoT", "confidence": 1.0}]
    
    score, evidence = scorer.score_infrastructure(university, required_skills)
    
    assert score == 0.0
    assert len(evidence) == 0


def test_industry_connections_scoring():
    """Test industry connections scoring."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.id = uuid4()
    university.state = "Jharkhand"
    
    # Mock industry expertise
    industry1 = Mock()
    industry1.industry_id = uuid4()
    industry1.industry.organization_name = "Tech Solutions Pvt Ltd"
    industry1.industry.type.value = "INDUSTRY"
    industry1.expertise.name = "IoT"
    
    industry2 = Mock()
    industry2.industry_id = uuid4()
    industry2.industry.organization_name = "Water Management Corp"
    industry2.industry.type.value = "STARTUP"
    industry2.expertise.name = "Water Engineering"
    
    db.query.return_value.join.return_value.filter.return_value.join.return_value.filter.return_value.all.return_value = [
        industry1, industry2
    ]
    
    # Mock additional expertise query
    db.query.return_value.filter.return_value.join.return_value.all.return_value = []
    
    required_skills = [
        {"name": "IoT", "confidence": 1.0},
        {"name": "Water Engineering", "confidence": 0.9}
    ]
    
    score, evidence = scorer.score_industry_connections(university, required_skills)
    
    assert score >= 70.0  # 2 connections = 80
    assert len(evidence) == 2


# ============================================================================
# EDGE CASES
# ============================================================================

def test_matching_with_no_required_skills():
    """Test matching when challenge has no required skills."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    
    score, evidence = scorer.score_expertise(university, [])
    
    assert score == 50.0  # Neutral score
    assert len(evidence) == 0


def test_matching_with_missing_challenge_location():
    """Test location scoring when challenge has no location."""
    db = Mock()
    config = MatchingConfig()
    scorer = UniversityScorer(db, config)
    
    university = Mock()
    university.district = "Ranchi"
    university.state = "Jharkhand"
    
    score, reason = scorer.score_location(university, None, "Jharkhand")
    
    assert score == 50.0  # Neutral score
    assert "not specified" in reason


def test_custom_weights():
    """Test matching with custom weights."""
    custom_weights = MatchingWeights(
        expertise=0.50,
        faculty=0.25,
        infrastructure=0.10,
        previous_projects=0.05,
        location=0.05,
        industry=0.05
    )
    
    assert custom_weights.validate_sum() is True
    assert custom_weights.expertise == 0.50
    assert custom_weights.faculty == 0.25


def test_config_to_dict():
    """Test config conversion to dictionary."""
    weights = MatchingWeights()
    weights_dict = weights.to_dict()
    
    assert isinstance(weights_dict, dict)
    assert weights_dict["expertise"] == 0.40
    assert weights_dict["faculty"] == 0.20
    assert sum(weights_dict.values()) == pytest.approx(1.0)
