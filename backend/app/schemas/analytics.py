"""
Analytics response schemas for Government/Admin dashboards.
"""

from pydantic import Field
from typing import Dict, List, Optional
from datetime import date

from app.schemas.base import BaseSchema


# ==================== PLATFORM OVERVIEW SCHEMAS ====================

class StatusDistribution(BaseSchema):
    """Distribution of items by status."""
    status: str
    count: int


class CategoryDistribution(BaseSchema):
    """Distribution of items by category."""
    category: str
    count: int


class PlatformOverviewResponse(BaseSchema):
    """Schema for platform-wide statistics overview."""
    
    # Challenge metrics
    total_challenges: int = 0
    challenges_by_status: List[StatusDistribution] = []
    validated_challenges: int = 0
    
    # University metrics
    total_universities: int = 0
    participating_universities: int = 0
    total_students: int = 0
    total_faculty: int = 0
    
    # Industry metrics
    total_industry_partners: int = 0
    active_industry_partners: int = 0
    
    # Project metrics
    total_projects: int = 0
    projects_by_status: List[StatusDistribution] = []
    completed_projects: int = 0
    deployed_projects: int = 0
    
    # Partnership metrics
    total_partnerships: int = 0
    active_partnerships: int = 0
    completed_partnerships: int = 0
    
    # Impact metrics
    total_reported_beneficiaries: int = 0
    total_verified_beneficiaries: int = 0
    projects_with_verified_impact: int = 0


# ==================== CHALLENGE ANALYTICS SCHEMAS ====================

class GeographicDistribution(BaseSchema):
    """Geographic distribution (district or state)."""
    location: str
    count: int


class PriorityDistribution(BaseSchema):
    """Distribution by priority level."""
    priority: str
    count: int


class TimeSeriesPoint(BaseSchema):
    """Single point in time series."""
    date: str  # ISO date string
    count: int


class ChallengeAnalyticsResponse(BaseSchema):
    """Schema for challenge-specific analytics."""
    
    total_challenges: int = 0
    status_distribution: List[StatusDistribution] = []
    category_distribution: List[CategoryDistribution] = []
    priority_distribution: List[PriorityDistribution] = []
    geographic_distribution: List[GeographicDistribution] = []
    
    # Rates and conversions
    validation_rate: float = 0.0  # % of submitted challenges validated
    duplicate_rate: float = 0.0  # % marked as duplicates
    
    # Timing metrics
    avg_days_to_validation: Optional[float] = None
    
    # Trends
    submission_trend: List[TimeSeriesPoint] = []


# ==================== PROJECT PIPELINE SCHEMAS ====================

class PipelineStageMetrics(BaseSchema):
    """Metrics for a single pipeline stage."""
    stage: str
    count: int
    percentage: float = 0.0


class ProjectPipelineAnalyticsResponse(BaseSchema):
    """Schema for project pipeline analytics."""
    
    total_projects: int = 0
    pipeline_stages: List[PipelineStageMetrics] = []
    
    # Conversion rates (percentage moving to next stage)
    planning_to_approved: float = 0.0
    approved_to_prototype: float = 0.0
    prototype_to_pilot: float = 0.0
    pilot_to_deployed: float = 0.0
    
    # Timing metrics
    avg_days_planning_to_approved: Optional[float] = None
    avg_days_approved_to_deployed: Optional[float] = None


# ==================== UNIVERSITY ANALYTICS SCHEMAS ====================

class UniversityMetrics(BaseSchema):
    """Metrics for a single university."""
    university_id: str
    university_name: str
    challenges_matched: int = 0
    invitations_sent: int = 0
    invitations_accepted: int = 0
    projects_created: int = 0
    projects_completed: int = 0
    students_participating: int = 0
    faculty_participating: int = 0


class UniversityAnalyticsResponse(BaseSchema):
    """Schema for university participation analytics."""
    
    total_universities: int = 0
    participating_universities: int = 0
    
    # Aggregates
    total_invitations: int = 0
    total_acceptances: int = 0
    acceptance_rate: float = 0.0
    
    # Top universities
    top_universities: List[UniversityMetrics] = []


# ==================== INDUSTRY ANALYTICS SCHEMAS ====================

class IndustryPartnerMetrics(BaseSchema):
    """Metrics for a single industry partner."""
    partner_id: str
    partner_name: str
    total_partnerships: int = 0
    active_partnerships: int = 0
    completed_partnerships: int = 0
    contributions_count: int = 0
    delivered_contributions: int = 0


class ContributionTypeDistribution(BaseSchema):
    """Distribution of contributions by type."""
    contribution_type: str
    count: int


class IndustryAnalyticsResponse(BaseSchema):
    """Schema for industry collaboration analytics."""
    
    total_industry_partners: int = 0
    active_partners: int = 0
    
    # Partnership metrics
    total_partnerships: int = 0
    partnerships_by_status: List[StatusDistribution] = []
    partnerships_by_type: List[CategoryDistribution] = []
    
    # Contribution metrics
    total_contributions: int = 0
    contributions_by_type: List[ContributionTypeDistribution] = []
    contributions_by_status: List[StatusDistribution] = []
    
    # Top partners
    top_partners: List[IndustryPartnerMetrics] = []


# ==================== IMPACT ANALYTICS SCHEMAS ====================

class ImpactByCategory(BaseSchema):
    """Impact metrics by category."""
    category: str
    projects_count: int = 0
    beneficiaries: int = 0
    verified_beneficiaries: int = 0


class ImpactByLocation(BaseSchema):
    """Impact metrics by location."""
    location: str
    projects_count: int = 0
    beneficiaries: int = 0


class ImpactAnalyticsResponse(BaseSchema):
    """Schema for impact measurement analytics."""
    
    total_impact_metrics: int = 0
    verified_impact_metrics: int = 0
    verification_rate: float = 0.0
    
    # Beneficiaries
    total_reported_beneficiaries: int = 0
    total_verified_beneficiaries: int = 0
    
    # Projects with impact
    projects_with_impact: int = 0
    projects_with_verified_impact: int = 0
    
    # Deployment
    projects_deployed: int = 0
    
    # Geographic distribution
    impact_by_location: List[ImpactByLocation] = []
    
    # Category distribution
    impact_by_category: List[ImpactByCategory] = []


# ==================== RANKING/INSIGHTS SCHEMAS ====================

class ProjectRanking(BaseSchema):
    """Ranked project with key metrics."""
    project_id: str
    project_code: str
    project_name: str
    beneficiaries: int = 0
    status: str
    university_name: str


class ChallengeHighlight(BaseSchema):
    """High-priority challenge requiring attention."""
    challenge_id: str
    challenge_code: str
    title: str
    priority: str
    status: str
    days_pending: int = 0
    district: Optional[str] = None


class TopInsightsResponse(BaseSchema):
    """Schema for top/ranked insights."""
    
    # High-impact projects
    highest_impact_projects: List[ProjectRanking] = []
    
    # Active universities (by project count)
    most_active_universities: List[UniversityMetrics] = []
    
    # Active industry partners (by partnership count)
    most_active_industry_partners: List[IndustryPartnerMetrics] = []
    
    # High-priority challenges
    challenges_needing_attention: List[ChallengeHighlight] = []


# ==================== CONSOLIDATED DASHBOARD SCHEMA ====================

class DashboardSummaryResponse(BaseSchema):
    """Schema for consolidated government dashboard."""
    
    # Platform overview
    platform_overview: PlatformOverviewResponse
    
    # Key insights
    top_insights: TopInsightsResponse
    
    # Quick stats for charts
    challenge_status_summary: List[StatusDistribution] = []
    project_pipeline_summary: List[PipelineStageMetrics] = []
    partnership_status_summary: List[StatusDistribution] = []

