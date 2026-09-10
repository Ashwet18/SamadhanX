"""
Government/Admin Analytics API endpoints.

Provides platform-wide analytics and metrics for decision-makers.
Authorization: GOVERNMENT_OFFICER and PLATFORM_ADMIN only.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.database import get_db
from app.core.dependencies import require_admin_or_government, get_current_user
from app.models.user import User
from app.models.enums import UserRole
from app.services.analytics.analytics_service import AnalyticsService
from app.schemas.analytics import (
    PlatformOverviewResponse,
    ChallengeAnalyticsResponse,
    ProjectPipelineAnalyticsResponse,
    UniversityAnalyticsResponse,
    IndustryAnalyticsResponse,
    ImpactAnalyticsResponse,
    TopInsightsResponse,
    DashboardSummaryResponse
)


router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


# ==================== PLATFORM OVERVIEW ====================

@router.get(
    "/overview",
    response_model=PlatformOverviewResponse,
    summary="Get platform overview statistics",
    description="Get comprehensive platform-wide statistics. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_platform_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get platform-wide overview statistics.
    
    Returns:
        Platform overview with key metrics across all modules
    """
    service = AnalyticsService(db)
    return service.get_platform_overview()


# ==================== CHALLENGE ANALYTICS ====================

@router.get(
    "/challenges",
    response_model=ChallengeAnalyticsResponse,
    summary="Get challenge analytics",
    description="Get comprehensive challenge statistics and trends. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_challenge_analytics(
    from_date: Optional[date] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get challenge-specific analytics.
    
    Args:
        from_date: Optional start date for filtering
        to_date: Optional end date for filtering
        
    Returns:
        Challenge analytics including status, category, priority distributions
    """
    service = AnalyticsService(db)
    return service.get_challenge_analytics(from_date=from_date, to_date=to_date)


# ==================== PROJECT PIPELINE ANALYTICS ====================

@router.get(
    "/projects/pipeline",
    response_model=ProjectPipelineAnalyticsResponse,
    summary="Get project pipeline analytics",
    description="Get project lifecycle and conversion metrics. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_project_pipeline_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get project pipeline and conversion analytics.
    
    Returns:
        Project pipeline statistics with stage counts and conversion rates
    """
    service = AnalyticsService(db)
    return service.get_project_pipeline_analytics()


# ==================== UNIVERSITY ANALYTICS ====================

@router.get(
    "/universities",
    response_model=UniversityAnalyticsResponse,
    summary="Get university participation analytics",
    description="Get university engagement and performance metrics. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_university_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get university participation analytics.
    
    Returns:
        University engagement metrics and top performers
    """
    service = AnalyticsService(db)
    return service.get_university_analytics()


# ==================== INDUSTRY ANALYTICS ====================

@router.get(
    "/industry",
    response_model=IndustryAnalyticsResponse,
    summary="Get industry collaboration analytics",
    description="Get industry partnership and contribution metrics. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_industry_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get industry collaboration analytics.
    
    Returns:
        Industry partnership statistics and contribution metrics
    """
    service = AnalyticsService(db)
    return service.get_industry_analytics()


# ==================== IMPACT ANALYTICS ====================

@router.get(
    "/impact",
    response_model=ImpactAnalyticsResponse,
    summary="Get impact measurement analytics",
    description="Get verified impact metrics and beneficiary statistics. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_impact_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get impact measurement analytics.
    
    Returns:
        Impact metrics including verified beneficiaries and geographic distribution
    """
    service = AnalyticsService(db)
    return service.get_impact_analytics()


# ==================== TOP INSIGHTS ====================

@router.get(
    "/insights",
    response_model=TopInsightsResponse,
    summary="Get top insights and rankings",
    description="Get ranked lists of high-impact projects, active participants, and challenges needing attention. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_top_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get top insights and rankings.
    
    Returns:
        Ranked lists and highlights for decision-making
    """
    service = AnalyticsService(db)
    return service.get_top_insights()


# ==================== CONSOLIDATED DASHBOARD ====================

@router.get(
    "/dashboard",
    response_model=DashboardSummaryResponse,
    summary="Get consolidated government dashboard",
    description="Get all key metrics in one response for main dashboard. Requires GOVERNMENT_OFFICER or PLATFORM_ADMIN role."
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_government)
):
    """
    Get consolidated dashboard summary.
    
    Returns:
        All key platform metrics and insights in one response
    """
    service = AnalyticsService(db)
    
    # Get all analytics
    overview = service.get_platform_overview()
    insights = service.get_top_insights()
    
    # Extract summary data for charts
    challenge_status = [
        {"status": s["status"], "count": s["count"]}
        for s in overview["challenges_by_status"]
    ]
    
    project_pipeline = service.get_project_pipeline_analytics()["pipeline_stages"]
    
    # Get partnership status from industry analytics
    industry_data = service.get_industry_analytics()
    partnership_status = industry_data["partnerships_by_status"]
    
    return {
        "platform_overview": overview,
        "top_insights": insights,
        "challenge_status_summary": challenge_status,
        "project_pipeline_summary": project_pipeline,
        "partnership_status_summary": partnership_status
    }

