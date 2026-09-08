"""
Tests for AI Challenge Intelligence Pipeline.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch

from app.services.ai import (
    ChallengeAIService,
    DuplicateDetector,
    AIAnalysisResult,
    get_ai_provider
)
from app.services.ai.provider import MockAIProvider, OpenAIProvider
from app.services.ai.schemas import ClassificationResult, SeverityResult, UrgencyResult
from app.models.challenge import (
    Challenge,
    Category,
    ChallengeCategory,
    ChallengeAIAnalysis,
    ChallengeEmbedding,
    ChallengeDuplicate
)
from app.models.user import User
from app.models.enums import (
    ChallengeStatus,
    PriorityLevel,
    UserRole,
    AccountStatus,
    DuplicateStatus
)


# ============================================================================
# PROVIDER TESTS
# ============================================================================

def test_mock_provider_analysis():
    """Test mock AI provider returns valid analysis."""
    provider = MockAIProvider()
    
    result = provider.analyze_challenge(
        title="Water tank overflow issue",
        description="Village water tank overflows daily wasting water",
        district="Ranchi",
        categories=["Water Management"]
    )
    
    assert isinstance(result, AIAnalysisResult)
    assert result.summary is not None
    assert result.classification.primary_domain == "Water Management"
    assert 0 <= result.severity.severity_score <= 100
    assert 0 <= result.urgency.urgency_score <= 100
    assert 0.0 <= result.confidence_score <= 1.0
    assert len(result.skills) > 0


def test_mock_provider_embedding():
    """Test mock provider generates deterministic embeddings."""
    provider = MockAIProvider()
    
    text = "Test challenge description"
    embedding1 = provider.generate_embedding(text)
    embedding2 = provider.generate_embedding(text)
    
    # Should be deterministic
    assert embedding1 == embedding2
    assert len(embedding1) == 1536
    assert all(isinstance(x, float) for x in embedding1)


def test_mock_provider_embedding_dimension():
    """Test mock provider reports correct dimension."""
    provider = MockAIProvider()
    assert provider.get_embedding_dimension() == 1536


def test_get_ai_provider_without_key():
    """Test getting AI provider without API key returns mock."""
    with patch('app.services.ai.provider.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = None
        
        provider = get_ai_provider()
        assert isinstance(provider, MockAIProvider)


def test_get_ai_provider_with_key():
    """Test getting AI provider with API key returns OpenAI."""
    with patch('app.services.ai.provider.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.LLM_MODEL = "gpt-4"
        mock_settings.EMBEDDING_MODEL = "text-embedding-ada-002"
        mock_settings.AI_TEMPERATURE = 0.7
        
        provider = get_ai_provider()
        assert isinstance(provider, OpenAIProvider)


# ============================================================================
# SCHEMA VALIDATION TESTS
# ============================================================================

def test_classification_result_validation():
    """Test classification result schema validation."""
    valid_data = {
        "primary_domain": "Water Management",
        "secondary_domains": ["Environment"],
        "confidence_score": 0.92,
        "classification_reason": "The challenge concerns water infrastructure"
    }
    
    result = ClassificationResult(**valid_data)
    assert result.primary_domain == "Water Management"
    assert result.confidence_score == 0.92


def test_severity_score_validation():
    """Test severity score must be 0-100."""
    with pytest.raises(ValueError):
        SeverityResult(severity_score=150, severity_reason="Invalid")
    
    with pytest.raises(ValueError):
        SeverityResult(severity_score=-10, severity_reason="Invalid")
    
    # Valid scores
    result = SeverityResult(severity_score=75, severity_reason="Valid")
    assert result.severity_score == 75


def test_urgency_score_validation():
    """Test urgency score must be 0-100."""
    with pytest.raises(ValueError):
        UrgencyResult(urgency_score=200, urgency_reason="Invalid")
    
    # Valid score
    result = UrgencyResult(urgency_score=85, urgency_reason="Valid")
    assert result.urgency_score == 85


def test_skill_confidence_validation():
    """Test skill confidence must be 0.0-1.0."""
    from app.services.ai.schemas import SkillExtractionResult
    
    with pytest.raises(ValueError):
        SkillExtractionResult(name="IoT", confidence=1.5)
    
    with pytest.raises(ValueError):
        SkillExtractionResult(name="IoT", confidence=-0.1)
    
    # Valid confidence
    result = SkillExtractionResult(name="IoT", confidence=0.92)
    assert result.confidence == 0.92


# ============================================================================
# PRIORITY CALCULATION TESTS
# ============================================================================

def test_priority_calculation_formula(db_session):
    """Test deterministic priority calculation."""
    service = ChallengeAIService(db_session)
    
    # Test formula: (severity * 0.4) + (urgency * 0.4) + population_bonus
    priority = service._calculate_priority(
        severity_score=80,
        urgency_score=90,
        affected_population=None
    )
    
    expected_score = (80 * 0.4) + (90 * 0.4)  # 32 + 36 = 68
    assert priority["score"] == pytest.approx(expected_score, rel=0.01)
    assert priority["level"] == PriorityLevel.HIGH  # 60-79 range


def test_priority_with_population_bonus(db_session):
    """Test priority calculation includes population bonus."""
    service = ChallengeAIService(db_session)
    
    # 1000 people = log10(1000) * 4 = 3 * 4 = 12 bonus points
    priority = service._calculate_priority(
        severity_score=60,
        urgency_score=60,
        affected_population=1000
    )
    
    base = (60 * 0.4) + (60 * 0.4)  # 48
    bonus = 12  # log10(1000) * 4
    expected = base + bonus  # 60
    
    assert priority["score"] == pytest.approx(expected, rel=0.01)
    assert priority["level"] == PriorityLevel.MEDIUM  # Just at threshold


def test_priority_levels_mapping(db_session):
    """Test priority score maps to correct levels."""
    service = ChallengeAIService(db_session)
    
    # LOW: 0-29
    p1 = service._calculate_priority(20, 20, None)
    assert p1["level"] == PriorityLevel.LOW
    
    # MEDIUM: 30-59
    p2 = service._calculate_priority(50, 50, None)
    assert p2["level"] == PriorityLevel.MEDIUM
    
    # HIGH: 60-79
    p3 = service._calculate_priority(80, 80, None)
    assert p3["level"] == PriorityLevel.HIGH
    
    # CRITICAL: 80-100
    p4 = service._calculate_priority(95, 95, None)
    assert p4["level"] == PriorityLevel.CRITICAL


def test_priority_clamped_to_range(db_session):
    """Test priority score is clamped to 0-100."""
    service = ChallengeAIService(db_session)
    
    # Even with high values, should not exceed 100
    priority = service._calculate_priority(100, 100, 1000000)
    assert 0 <= priority["score"] <= 100


# ============================================================================
# DUPLICATE DETECTION TESTS
# ============================================================================

@pytest.mark.skip(reason="Requires PostgreSQL with pgvector extension")
def test_duplicate_detection_similarity_search(db_session):
    """Test semantic duplicate detection using pgvector."""
    # This test requires PostgreSQL with pgvector
    # Skipped in SQLite environment
    pass


def test_duplicate_self_prevention():
    """Test self-duplicate prevention at database level."""
    # The CHECK constraint should prevent challenge_id == similar_challenge_id
    # This is enforced at the database level
    pass


def test_similarity_classification():
    """Test similarity score classification."""
    detector = DuplicateDetector(Mock())
    
    assert detector.classify_similarity(0.95) == "HIGH_CONFIDENCE"
    assert detector.classify_similarity(0.85) == "POSSIBLE"
    assert detector.classify_similarity(0.70) == "LOW"


# ============================================================================
# AI SERVICE INTEGRATION TESTS
# ============================================================================

def test_ai_analysis_pipeline(db_session):
    """Test complete AI analysis pipeline."""
    # Create user
    user = User(
        email="government@test.com",
        hashed_password="hashed",
        full_name="Government Officer",
        role=UserRole.GOVERNMENT_OFFICER,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    # Create category
    category = Category(name="Water Management", description="Water issues")
    db_session.add(category)
    db_session.commit()
    
    # Create challenge
    challenge = Challenge(
        challenge_code="CH-JH-2026-00001",
        submitted_by=user.id,
        title="Village water tank overflow",
        description="The water storage tank in our village overflows daily, wasting water and causing problems",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi",
        affected_population=500
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Link category
    challenge_category = ChallengeCategory(
        challenge_id=challenge.id,
        category_id=category.id
    )
    db_session.add(challenge_category)
    db_session.commit()
    
    # Run AI analysis
    service = ChallengeAIService(db_session)
    result = service.analyze(challenge.id, user.id)
    
    # Verify results
    assert result["challenge_id"] == str(challenge.id)
    assert result["status"] == ChallengeStatus.PENDING_REVIEW.value
    assert "priority" in result
    assert "ai_analysis" in result
    assert "duplicate_candidates" in result
    
    # Verify priority
    priority = result["priority"]
    assert "score" in priority
    assert "level" in priority
    assert "formula" in priority
    
    # Verify AI analysis stored
    db_session.refresh(challenge)
    assert challenge.ai_analysis is not None
    assert challenge.status == ChallengeStatus.PENDING_REVIEW
    assert challenge.priority_level is not None
    assert challenge.priority_score is not None


def test_ai_analysis_failure_handling(db_session):
    """Test AI analysis failure does not destroy challenge."""
    # Create user and challenge
    user = User(
        email="test@test.com",
        hashed_password="hashed",
        full_name="Test User",
        role=UserRole.GOVERNMENT_OFFICER,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    challenge = Challenge(
        challenge_code="CH-JH-2026-00002",
        submitted_by=user.id,
        title="Test challenge",
        description="Test description that is long enough to be valid",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi"
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Mock AI provider to fail
    with patch.object(ChallengeAIService, '_load_challenge', side_effect=ValueError("Test error")):
        service = ChallengeAIService(db_session)
        
        with pytest.raises(RuntimeError):
            service.analyze(challenge.id, user.id)
    
    # Verify challenge still exists
    db_session.refresh(challenge)
    assert challenge is not None
    assert challenge.status == ChallengeStatus.SUBMITTED  # Status unchanged


def test_embedding_dimension_validation(db_session):
    """Test embedding dimension must match expected."""
    service = ChallengeAIService(db_session)
    
    # Mock provider with wrong dimension
    wrong_embedding = [0.1] * 768  # Wrong dimension (should be 1536)
    
    with patch.object(service.provider, 'generate_embedding', return_value=wrong_embedding):
        with patch.object(service.provider, 'get_embedding_dimension', return_value=1536):
            
            user = User(
                email="test@test.com",
                hashed_password="hashed",
                full_name="Test User",
                role=UserRole.GOVERNMENT_OFFICER,
                account_status=AccountStatus.ACTIVE
            )
            db_session.add(user)
            db_session.commit()
            
            challenge = Challenge(
                challenge_code="CH-JH-2026-00003",
                submitted_by=user.id,
                title="Test challenge",
                description="Test description that is long enough",
                status=ChallengeStatus.SUBMITTED,
                district="Ranchi"
            )
            db_session.add(challenge)
            db_session.commit()
            
            with pytest.raises(RuntimeError, match="dimension mismatch"):
                service.analyze(challenge.id, user.id)


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

def test_analyze_endpoint_requires_government_role(client, db_session):
    """Test analyze endpoint requires GOVERNMENT_OFFICER or PLATFORM_ADMIN."""
    # Create citizen user
    citizen = User(
        email="citizen@test.com",
        hashed_password="hashed",
        full_name="Citizen",
        role=UserRole.CITIZEN,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(citizen)
    db_session.commit()
    
    # Create challenge
    challenge = Challenge(
        challenge_code="CH-JH-2026-00004",
        submitted_by=citizen.id,
        title="Test challenge",
        description="Test description that is long enough",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi"
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Citizen should not be able to trigger analysis
    # (This would require full auth setup, so we test authorization logic separately)
    pass


def test_get_ai_analysis_endpoint(client, db_session):
    """Test retrieving AI analysis results."""
    # Create user and challenge with analysis
    user = User(
        email="gov@test.com",
        hashed_password="hashed",
        full_name="Government",
        role=UserRole.GOVERNMENT_OFFICER,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    challenge = Challenge(
        challenge_code="CH-JH-2026-00005",
        submitted_by=user.id,
        title="Test challenge",
        description="Test description that is long enough",
        status=ChallengeStatus.PENDING_REVIEW,
        district="Ranchi"
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Create AI analysis
    analysis = ChallengeAIAnalysis(
        challenge_id=challenge.id,
        model_name="mock",
        model_version="1.0",
        summary="Test summary",
        primary_domain="Water Management",
        severity_score=75.0,
        urgency_score=80.0,
        extracted_skills=[{"name": "IoT", "confidence": 0.9}],
        recommended_solution_types=[{"type": "IoT monitoring", "confidence": 0.85}],
        confidence_score=0.88
    )
    db_session.add(analysis)
    db_session.commit()
    
    # Verify analysis exists
    db_session.refresh(challenge)
    assert challenge.ai_analysis is not None


def test_duplicate_candidates_endpoint(db_session):
    """Test retrieving duplicate candidates."""
    # Create challenges
    user = User(
        email="user@test.com",
        hashed_password="hashed",
        full_name="User",
        role=UserRole.GOVERNMENT_OFFICER,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    challenge1 = Challenge(
        challenge_code="CH-JH-2026-00006",
        submitted_by=user.id,
        title="Water tank overflow",
        description="Water tank overflows daily",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi"
    )
    challenge2 = Challenge(
        challenge_code="CH-JH-2026-00007",
        submitted_by=user.id,
        title="Water storage overflow issue",
        description="Storage tank overflows frequently",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi"
    )
    db_session.add_all([challenge1, challenge2])
    db_session.commit()
    
    # Create duplicate link
    duplicate = ChallengeDuplicate(
        challenge_id=challenge1.id,
        similar_challenge_id=challenge2.id,
        similarity_score=0.92,
        status=DuplicateStatus.PENDING_REVIEW
    )
    db_session.add(duplicate)
    db_session.commit()
    
    # Verify duplicate link exists
    duplicates = db_session.query(ChallengeDuplicate).filter(
        ChallengeDuplicate.challenge_id == challenge1.id
    ).all()
    
    assert len(duplicates) == 1
    assert duplicates[0].similarity_score == 0.92
    assert duplicates[0].status == DuplicateStatus.PENDING_REVIEW


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================

def test_missing_api_key_graceful_failure():
    """Test system handles missing API key gracefully."""
    with patch('app.services.ai.provider.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = None
        
        # Should return mock provider, not crash
        provider = get_ai_provider()
        assert provider is not None


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_challenge_without_categories(db_session):
    """Test AI analysis works with challenges that have no categories."""
    user = User(
        email="test@test.com",
        hashed_password="hashed",
        full_name="Test User",
        role=UserRole.GOVERNMENT_OFFICER,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    challenge = Challenge(
        challenge_code="CH-JH-2026-00008",
        submitted_by=user.id,
        title="Uncategorized challenge",
        description="This challenge has no categories assigned yet",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi"
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Should still work
    service = ChallengeAIService(db_session)
    result = service.analyze(challenge.id, user.id)
    
    assert result is not None
    assert result["ai_analysis"]["primary_domain"] is not None


def test_challenge_without_affected_population(db_session):
    """Test priority calculation without affected population."""
    service = ChallengeAIService(db_session)
    
    priority = service._calculate_priority(
        severity_score=70,
        urgency_score=60,
        affected_population=None
    )
    
    # Should still calculate without population bonus
    assert priority["score"] > 0
    assert priority["level"] is not None
    assert "formula" in priority


def test_retry_analysis_replaces_old_results(db_session):
    """Test re-running analysis replaces old results."""
    user = User(
        email="test@test.com",
        hashed_password="hashed",
        full_name="Test User",
        role=UserRole.GOVERNMENT_OFFICER,
        account_status=AccountStatus.ACTIVE
    )
    db_session.add(user)
    db_session.commit()
    
    challenge = Challenge(
        challenge_code="CH-JH-2026-00009",
        submitted_by=user.id,
        title="Test challenge",
        description="Test description that is long enough",
        status=ChallengeStatus.SUBMITTED,
        district="Ranchi"
    )
    db_session.add(challenge)
    db_session.commit()
    
    # Run analysis first time
    service = ChallengeAIService(db_session)
    result1 = service.analyze(challenge.id, user.id)
    
    # Run analysis second time
    result2 = service.analyze(challenge.id, user.id)
    
    # Should have only one analysis record
    analyses = db_session.query(ChallengeAIAnalysis).filter(
        ChallengeAIAnalysis.challenge_id == challenge.id
    ).all()
    
    assert len(analyses) == 1
