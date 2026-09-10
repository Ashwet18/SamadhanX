"""
Core analytics service for Government/Admin dashboards.

Provides platform-wide aggregations and metrics.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_, extract
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date
from uuid import UUID

from app.models.challenge import Challenge, ChallengeAssignment, Category, ChallengeCategory
from app.models.project import Project, ProjectMember
from app.models.university import University, Faculty, Student
from app.models.industry import IndustryPartner
from app.models.partnership import Partnership, Contribution
from app.models.platform import ImpactMetric
from app.models.enums import (
    ChallengeStatus, ProjectStatus, PartnershipStatus, ContributionStatus,
    VerificationStatus, AssignmentStatus, PriorityLevel, AvailabilityStatus
)


class AnalyticsService:
    """Core analytics service with aggregation methods."""
    
    def __init__(self, db: Session):
        """Initialize analytics service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    # ==================== PLATFORM OVERVIEW ====================
    
    def get_platform_overview(self) -> Dict[str, Any]:
        """
        Get platform-wide statistics overview.
        
        Returns:
            Dictionary with platform metrics
        """
        # Challenge metrics
        total_challenges = self.db.query(Challenge).count()
        challenges_by_status = self._get_challenges_by_status()
        validated_challenges = self.db.query(Challenge).filter(
            Challenge.status == ChallengeStatus.VALIDATED
        ).count()
        
        # University metrics
        total_universities = self.db.query(University).count()
        participating_universities = self.db.query(University).join(
            Project, University.id == Project.university_id
        ).distinct().count()
        total_students = self.db.query(Student).count()
        total_faculty = self.db.query(Faculty).count()
        
        # Industry metrics
        total_industry_partners = self.db.query(IndustryPartner).count()
        active_industry_partners = self.db.query(IndustryPartner).filter(
            IndustryPartner.availability_status == AvailabilityStatus.AVAILABLE
        ).count()
        
        # Project metrics
        total_projects = self.db.query(Project).count()
        projects_by_status = self._get_projects_by_status()
        completed_projects = self.db.query(Project).filter(
            Project.status == ProjectStatus.COMPLETED
        ).count()
        deployed_projects = self.db.query(Project).filter(
            Project.status == ProjectStatus.DEPLOYED
        ).count()
        
        # Partnership metrics
        total_partnerships = self.db.query(Partnership).count()
        active_partnerships = self.db.query(Partnership).filter(
            Partnership.status == PartnershipStatus.ACTIVE
        ).count()
        completed_partnerships = self.db.query(Partnership).filter(
            Partnership.status == PartnershipStatus.COMPLETED
        ).count()
        
        # Impact metrics
        impact_stats = self._get_impact_summary()
        
        return {
            "total_challenges": total_challenges,
            "challenges_by_status": challenges_by_status,
            "validated_challenges": validated_challenges,
            "total_universities": total_universities,
            "participating_universities": participating_universities,
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_industry_partners": total_industry_partners,
            "active_industry_partners": active_industry_partners,
            "total_projects": total_projects,
            "projects_by_status": projects_by_status,
            "completed_projects": completed_projects,
            "deployed_projects": deployed_projects,
            "total_partnerships": total_partnerships,
            "active_partnerships": active_partnerships,
            "completed_partnerships": completed_partnerships,
            "total_reported_beneficiaries": impact_stats["total_reported"],
            "total_verified_beneficiaries": impact_stats["total_verified"],
            "projects_with_verified_impact": impact_stats["projects_verified"]
        }
    
    # ==================== CHALLENGE ANALYTICS ====================
    
    def get_challenge_analytics(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get challenge-specific analytics.
        
        Args:
            from_date: Optional start date for filtering
            to_date: Optional end date for filtering
            
        Returns:
            Dictionary with challenge metrics
        """
        # Base query with optional date filter
        base_query = self.db.query(Challenge)
        if from_date:
            base_query = base_query.filter(func.date(Challenge.created_at) >= from_date)
        if to_date:
            base_query = base_query.filter(func.date(Challenge.created_at) <= to_date)
        
        total_challenges = base_query.count()
        
        # Status distribution
        status_dist = self._get_challenges_by_status(from_date, to_date)
        
        # Category distribution
        category_dist = self._get_challenges_by_category()
        
        # Priority distribution
        priority_dist = self._get_challenges_by_priority()
        
        # Geographic distribution
        geographic_dist = self._get_challenges_by_location()
        
        # Validation rate
        submitted = base_query.filter(
            Challenge.status.in_([
                ChallengeStatus.SUBMITTED,
                ChallengeStatus.PENDING_REVIEW,
                ChallengeStatus.VALIDATED,
                ChallengeStatus.MATCHING
            ])
        ).count()
        validated = base_query.filter(Challenge.status == ChallengeStatus.VALIDATED).count()
        validation_rate = (validated / submitted * 100) if submitted > 0 else 0.0
        
        # Duplicate rate
        duplicates = base_query.filter(Challenge.status == ChallengeStatus.DUPLICATE).count()
        duplicate_rate = (duplicates / total_challenges * 100) if total_challenges > 0 else 0.0
        
        # Average days to validation
        avg_days = self._calculate_avg_validation_time()
        
        # Submission trend (last 30 days)
        submission_trend = self._get_submission_trend(days=30)
        
        return {
            "total_challenges": total_challenges,
            "status_distribution": status_dist,
            "category_distribution": category_dist,
            "priority_distribution": priority_dist,
            "geographic_distribution": geographic_dist,
            "validation_rate": round(validation_rate, 2),
            "duplicate_rate": round(duplicate_rate, 2),
            "avg_days_to_validation": avg_days,
            "submission_trend": submission_trend
        }
    
    # ==================== PROJECT PIPELINE ANALYTICS ====================
    
    def get_project_pipeline_analytics(self) -> Dict[str, Any]:
        """
        Get project pipeline and conversion analytics.
        
        Returns:
            Dictionary with pipeline metrics
        """
        total_projects = self.db.query(Project).count()
        
        # Pipeline stages with counts
        pipeline_stages = self._get_pipeline_stages()
        
        # Conversion rates
        planning = self.db.query(Project).filter(Project.status == ProjectStatus.PLANNING).count()
        approved = self.db.query(Project).filter(Project.status == ProjectStatus.APPROVED).count()
        prototype = self.db.query(Project).filter(Project.status == ProjectStatus.PROTOTYPE).count()
        pilot = self.db.query(Project).filter(Project.status == ProjectStatus.PILOT).count()
        deployed = self.db.query(Project).filter(Project.status == ProjectStatus.DEPLOYED).count()
        
        planning_to_approved = (approved / planning * 100) if planning > 0 else 0.0
        approved_to_prototype = (prototype / approved * 100) if approved > 0 else 0.0
        prototype_to_pilot = (pilot / prototype * 100) if prototype > 0 else 0.0
        pilot_to_deployed = (deployed / pilot * 100) if pilot > 0 else 0.0
        
        # Timing metrics (using created_at as proxy)
        avg_planning_to_approved = self._calculate_stage_duration(
            ProjectStatus.PLANNING, ProjectStatus.APPROVED
        )
        avg_approved_to_deployed = self._calculate_stage_duration(
            ProjectStatus.APPROVED, ProjectStatus.DEPLOYED
        )
        
        return {
            "total_projects": total_projects,
            "pipeline_stages": pipeline_stages,
            "planning_to_approved": round(planning_to_approved, 2),
            "approved_to_prototype": round(approved_to_prototype, 2),
            "prototype_to_pilot": round(prototype_to_pilot, 2),
            "pilot_to_deployed": round(pilot_to_deployed, 2),
            "avg_days_planning_to_approved": avg_planning_to_approved,
            "avg_days_approved_to_deployed": avg_approved_to_deployed
        }
    
    # ==================== UNIVERSITY ANALYTICS ====================
    
    def get_university_analytics(self) -> Dict[str, Any]:
        """
        Get university participation analytics.
        
        Returns:
            Dictionary with university metrics
        """
        total_universities = self.db.query(University).count()
        participating = self.db.query(University).join(
            Project, University.id == Project.university_id
        ).distinct().count()
        
        # Assignment metrics
        total_invitations = self.db.query(ChallengeAssignment).filter(
            ChallengeAssignment.status.in_([AssignmentStatus.INVITED, AssignmentStatus.ACCEPTED])
        ).count()
        total_acceptances = self.db.query(ChallengeAssignment).filter(
            ChallengeAssignment.status == AssignmentStatus.ACCEPTED
        ).count()
        acceptance_rate = (total_acceptances / total_invitations * 100) if total_invitations > 0 else 0.0
        
        # Top universities
        top_universities = self._get_top_universities(limit=10)
        
        return {
            "total_universities": total_universities,
            "participating_universities": participating,
            "total_invitations": total_invitations,
            "total_acceptances": total_acceptances,
            "acceptance_rate": round(acceptance_rate, 2),
            "top_universities": top_universities
        }
    
    # ==================== INDUSTRY ANALYTICS ====================
    
    def get_industry_analytics(self) -> Dict[str, Any]:
        """
        Get industry collaboration analytics.
        
        Returns:
            Dictionary with industry metrics
        """
        total_partners = self.db.query(IndustryPartner).count()
        active_partners = self.db.query(IndustryPartner).filter(
            IndustryPartner.availability_status == AvailabilityStatus.AVAILABLE
        ).count()
        
        # Partnership metrics
        total_partnerships = self.db.query(Partnership).count()
        partnerships_by_status = self._get_partnerships_by_status()
        partnerships_by_type = self._get_partnerships_by_type()
        
        # Contribution metrics
        total_contributions = self.db.query(Contribution).count()
        contributions_by_type = self._get_contributions_by_type()
        contributions_by_status = self._get_contributions_by_status()
        
        # Top partners
        top_partners = self._get_top_industry_partners(limit=10)
        
        return {
            "total_industry_partners": total_partners,
            "active_partners": active_partners,
            "total_partnerships": total_partnerships,
            "partnerships_by_status": partnerships_by_status,
            "partnerships_by_type": partnerships_by_type,
            "total_contributions": total_contributions,
            "contributions_by_type": contributions_by_type,
            "contributions_by_status": contributions_by_status,
            "top_partners": top_partners
        }
    
    # ==================== IMPACT ANALYTICS ====================
    
    def get_impact_analytics(self) -> Dict[str, Any]:
        """
        Get impact measurement analytics.
        
        Returns:
            Dictionary with impact metrics
        """
        total_metrics = self.db.query(ImpactMetric).count()
        verified_metrics = self.db.query(ImpactMetric).filter(
            ImpactMetric.verification_status == VerificationStatus.VERIFIED
        ).count()
        verification_rate = (verified_metrics / total_metrics * 100) if total_metrics > 0 else 0.0
        
        # Beneficiaries
        reported_beneficiaries = self.db.query(
            func.sum(ImpactMetric.beneficiaries_count)
        ).scalar() or 0
        
        verified_beneficiaries = self.db.query(
            func.sum(ImpactMetric.beneficiaries_count)
        ).filter(
            ImpactMetric.verification_status == VerificationStatus.VERIFIED
        ).scalar() or 0
        
        # Projects with impact
        projects_with_impact = self.db.query(ImpactMetric.project_id).distinct().count()
        projects_with_verified = self.db.query(ImpactMetric.project_id).filter(
            ImpactMetric.verification_status == VerificationStatus.VERIFIED
        ).distinct().count()
        
        # Deployed projects
        deployed = self.db.query(Project).filter(
            Project.status.in_([ProjectStatus.DEPLOYED, ProjectStatus.COMPLETED])
        ).count()
        
        # Geographic distribution
        impact_by_location = self._get_impact_by_location()
        
        # Category distribution (using project → challenge → category)
        impact_by_category = self._get_impact_by_category()
        
        return {
            "total_impact_metrics": total_metrics,
            "verified_impact_metrics": verified_metrics,
            "verification_rate": round(verification_rate, 2),
            "total_reported_beneficiaries": int(reported_beneficiaries),
            "total_verified_beneficiaries": int(verified_beneficiaries),
            "projects_with_impact": projects_with_impact,
            "projects_with_verified_impact": projects_with_verified,
            "projects_deployed": deployed,
            "impact_by_location": impact_by_location,
            "impact_by_category": impact_by_category
        }
    
    # ==================== TOP INSIGHTS ====================
    
    def get_top_insights(self) -> Dict[str, Any]:
        """
        Get ranked/top insights for dashboard.
        
        Returns:
            Dictionary with top insights
        """
        # High-impact projects
        highest_impact = self._get_highest_impact_projects(limit=5)
        
        # Most active universities
        most_active_universities = self._get_top_universities(limit=5)
        
        # Most active industry partners
        most_active_partners = self._get_top_industry_partners(limit=5)
        
        # Challenges needing attention (high priority, pending validation)
        challenges_attention = self._get_challenges_needing_attention(limit=10)
        
        return {
            "highest_impact_projects": highest_impact,
            "most_active_universities": most_active_universities,
            "most_active_industry_partners": most_active_partners,
            "challenges_needing_attention": challenges_attention
        }
    
    # ==================== HELPER METHODS ====================
    
    def _get_challenges_by_status(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get challenge count by status."""
        query = self.db.query(
            Challenge.status,
            func.count(Challenge.id).label('count')
        )
        
        if from_date:
            query = query.filter(func.date(Challenge.created_at) >= from_date)
        if to_date:
            query = query.filter(func.date(Challenge.created_at) <= to_date)
        
        results = query.group_by(Challenge.status).all()
        
        return [{"status": str(r.status.value), "count": r.count} for r in results]
    
    def _get_projects_by_status(self) -> List[Dict[str, Any]]:
        """Get project count by status."""
        results = self.db.query(
            Project.status,
            func.count(Project.id).label('count')
        ).group_by(Project.status).all()
        
        return [{"status": str(r.status.value), "count": r.count} for r in results]
    
    def _get_challenges_by_category(self) -> List[Dict[str, Any]]:
        """Get challenge count by category."""
        results = self.db.query(
            Category.name,
            func.count(ChallengeCategory.challenge_id).label('count')
        ).join(
            ChallengeCategory, Category.id == ChallengeCategory.category_id
        ).group_by(Category.name).order_by(func.count(ChallengeCategory.challenge_id).desc()).limit(10).all()
        
        return [{"category": r.name, "count": r.count} for r in results]
    
    def _get_challenges_by_priority(self) -> List[Dict[str, Any]]:
        """Get challenge count by priority."""
        results = self.db.query(
            Challenge.priority_level,
            func.count(Challenge.id).label('count')
        ).filter(Challenge.priority_level.isnot(None)).group_by(Challenge.priority_level).all()
        
        return [{"priority": str(r.priority_level.value), "count": r.count} for r in results]
    
    def _get_challenges_by_location(self) -> List[Dict[str, Any]]:
        """Get challenge count by district."""
        results = self.db.query(
            Challenge.district,
            func.count(Challenge.id).label('count')
        ).filter(Challenge.district.isnot(None)).group_by(Challenge.district).order_by(func.count(Challenge.id).desc()).limit(20).all()
        
        return [{"location": r.district, "count": r.count} for r in results]
    
    def _get_impact_summary(self) -> Dict[str, int]:
        """Get impact summary statistics."""
        total_reported = self.db.query(
            func.sum(ImpactMetric.beneficiaries_count)
        ).scalar() or 0
        
        total_verified = self.db.query(
            func.sum(ImpactMetric.beneficiaries_count)
        ).filter(
            ImpactMetric.verification_status == VerificationStatus.VERIFIED
        ).scalar() or 0
        
        projects_verified = self.db.query(ImpactMetric.project_id).filter(
            ImpactMetric.verification_status == VerificationStatus.VERIFIED
        ).distinct().count()
        
        return {
            "total_reported": int(total_reported),
            "total_verified": int(total_verified),
            "projects_verified": projects_verified
        }
    
    def _calculate_avg_validation_time(self) -> Optional[float]:
        """Calculate average days from submission to validation."""
        # This is approximate using created_at as we don't have explicit validated_at timestamp
        # Would need audit logs or status change tracking for precise calculation
        return None
    
    def _get_submission_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get challenge submission trend over last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            func.date(Challenge.created_at).label('date'),
            func.count(Challenge.id).label('count')
        ).filter(
            Challenge.created_at >= cutoff_date
        ).group_by(func.date(Challenge.created_at)).order_by(func.date(Challenge.created_at)).all()
        
        return [{"date": r.date.isoformat(), "count": r.count} for r in results]
    
    def _get_pipeline_stages(self) -> List[Dict[str, Any]]:
        """Get project count by pipeline stage with percentages."""
        total = self.db.query(Project).count()
        
        results = self.db.query(
            Project.status,
            func.count(Project.id).label('count')
        ).group_by(Project.status).all()
        
        stages = []
        for r in results:
            percentage = (r.count / total * 100) if total > 0 else 0.0
            stages.append({
                "stage": str(r.status.value),
                "count": r.count,
                "percentage": round(percentage, 2)
            })
        
        return stages
    
    def _calculate_stage_duration(
        self,
        from_status: ProjectStatus,
        to_status: ProjectStatus
    ) -> Optional[float]:
        """Calculate average duration between project stages."""
        # Would require audit logs or status change timestamps
        # Placeholder for now
        return None
    
    def _get_top_universities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top universities by project count."""
        results = self.db.query(
            University.id,
            University.name,
            func.count(Project.id).label('projects_created'),
            func.count(case((Project.status == ProjectStatus.COMPLETED, 1))).label('projects_completed')
        ).join(
            Project, University.id == Project.university_id
        ).group_by(University.id, University.name).order_by(func.count(Project.id).desc()).limit(limit).all()
        
        top_unis = []
        for r in results:
            # Get student and faculty counts
            students = self.db.query(func.count(Student.id)).filter(Student.university_id == r.id).scalar() or 0
            faculty = self.db.query(func.count(Faculty.id)).filter(Faculty.id == r.id).scalar() or 0
            
            # Get assignment stats
            assignments = self.db.query(ChallengeAssignment).filter(
                ChallengeAssignment.university_id == r.id
            )
            matched = assignments.count()
            invited = assignments.filter(ChallengeAssignment.status == AssignmentStatus.INVITED).count()
            accepted = assignments.filter(ChallengeAssignment.status == AssignmentStatus.ACCEPTED).count()
            
            top_unis.append({
                "university_id": str(r.id),
                "university_name": r.name,
                "challenges_matched": matched,
                "invitations_sent": invited,
                "invitations_accepted": accepted,
                "projects_created": r.projects_created,
                "projects_completed": r.projects_completed,
                "students_participating": students,
                "faculty_participating": faculty
            })
        
        return top_unis
    
    def _get_top_industry_partners(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top industry partners by partnership count."""
        results = self.db.query(
            IndustryPartner.id,
            IndustryPartner.organization_name,
            func.count(Partnership.id).label('total_partnerships'),
            func.count(case((Partnership.status == PartnershipStatus.ACTIVE, 1))).label('active'),
            func.count(case((Partnership.status == PartnershipStatus.COMPLETED, 1))).label('completed')
        ).join(
            Partnership, IndustryPartner.id == Partnership.industry_id
        ).group_by(IndustryPartner.id, IndustryPartner.organization_name).order_by(func.count(Partnership.id).desc()).limit(limit).all()
        
        top_partners = []
        for r in results:
            # Get contribution counts
            contributions = self.db.query(Contribution).join(
                Partnership, Contribution.partnership_id == Partnership.id
            ).filter(Partnership.industry_id == r.id)
            
            total_contributions = contributions.count()
            delivered = contributions.filter(Contribution.status == ContributionStatus.DELIVERED).count()
            
            top_partners.append({
                "partner_id": str(r.id),
                "partner_name": r.organization_name,
                "total_partnerships": r.total_partnerships,
                "active_partnerships": r.active,
                "completed_partnerships": r.completed,
                "contributions_count": total_contributions,
                "delivered_contributions": delivered
            })
        
        return top_partners
    
    def _get_highest_impact_projects(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get projects with highest verified impact."""
        results = self.db.query(
            Project.id,
            Project.project_code,
            Project.name,
            Project.status,
            University.name.label('university_name'),
            func.sum(ImpactMetric.beneficiaries_count).label('beneficiaries')
        ).join(
            ImpactMetric, Project.id == ImpactMetric.project_id
        ).join(
            University, Project.university_id == University.id
        ).filter(
            ImpactMetric.verification_status == VerificationStatus.VERIFIED
        ).group_by(
            Project.id, Project.project_code, Project.name, Project.status, University.name
        ).order_by(func.sum(ImpactMetric.beneficiaries_count).desc()).limit(limit).all()
        
        return [{
            "project_id": str(r.id),
            "project_code": r.project_code,
            "project_name": r.name,
            "beneficiaries": int(r.beneficiaries) if r.beneficiaries else 0,
            "status": str(r.status.value),
            "university_name": r.university_name
        } for r in results]
    
    def _get_challenges_needing_attention(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-priority challenges pending validation."""
        results = self.db.query(
            Challenge.id,
            Challenge.challenge_code,
            Challenge.title,
            Challenge.priority_level,
            Challenge.status,
            Challenge.district,
            Challenge.created_at
        ).filter(
            Challenge.status.in_([ChallengeStatus.SUBMITTED, ChallengeStatus.PENDING_REVIEW]),
            Challenge.priority_level.in_([PriorityLevel.HIGH, PriorityLevel.CRITICAL])
        ).order_by(Challenge.priority_level.desc(), Challenge.created_at).limit(limit).all()
        
        challenges = []
        for r in results:
            days_pending = (datetime.utcnow() - r.created_at).days
            challenges.append({
                "challenge_id": str(r.id),
                "challenge_code": r.challenge_code,
                "title": r.title,
                "priority": str(r.priority_level.value) if r.priority_level else "MEDIUM",
                "status": str(r.status.value),
                "days_pending": days_pending,
                "district": r.district
            })
        
        return challenges
    
    def _get_partnerships_by_status(self) -> List[Dict[str, Any]]:
        """Get partnership count by status."""
        results = self.db.query(
            Partnership.status,
            func.count(Partnership.id).label('count')
        ).group_by(Partnership.status).all()
        
        return [{"status": str(r.status.value), "count": r.count} for r in results]
    
    def _get_partnerships_by_type(self) -> List[Dict[str, Any]]:
        """Get partnership count by type."""
        results = self.db.query(
            Partnership.partnership_type,
            func.count(Partnership.id).label('count')
        ).group_by(Partnership.partnership_type).order_by(func.count(Partnership.id).desc()).all()
        
        return [{"category": str(r.partnership_type.value), "count": r.count} for r in results]
    
    def _get_contributions_by_type(self) -> List[Dict[str, Any]]:
        """Get contribution count by type."""
        results = self.db.query(
            Contribution.contribution_type,
            func.count(Contribution.id).label('count')
        ).group_by(Contribution.contribution_type).order_by(func.count(Contribution.id).desc()).all()
        
        return [{"contribution_type": str(r.contribution_type.value), "count": r.count} for r in results]
    
    def _get_contributions_by_status(self) -> List[Dict[str, Any]]:
        """Get contribution count by status."""
        results = self.db.query(
            Contribution.status,
            func.count(Contribution.id).label('count')
        ).group_by(Contribution.status).all()
        
        return [{"status": str(r.status.value), "count": r.count} for r in results]
    
    def _get_impact_by_location(self) -> List[Dict[str, Any]]:
        """Get impact metrics by geographic location."""
        results = self.db.query(
            ImpactMetric.geographic_area,
            func.count(ImpactMetric.project_id.distinct()).label('projects'),
            func.sum(ImpactMetric.beneficiaries_count).label('beneficiaries')
        ).filter(
            ImpactMetric.geographic_area.isnot(None)
        ).group_by(ImpactMetric.geographic_area).order_by(func.sum(ImpactMetric.beneficiaries_count).desc()).limit(20).all()
        
        return [{
            "location": r.geographic_area,
            "projects_count": r.projects,
            "beneficiaries": int(r.beneficiaries) if r.beneficiaries else 0
        } for r in results]
    
    def _get_impact_by_category(self) -> List[Dict[str, Any]]:
        """Get impact metrics by challenge category."""
        results = self.db.query(
            Category.name,
            func.count(ImpactMetric.project_id.distinct()).label('projects'),
            func.sum(ImpactMetric.beneficiaries_count).label('total_beneficiaries'),
            func.sum(
                case(
                    (ImpactMetric.verification_status == VerificationStatus.VERIFIED, ImpactMetric.beneficiaries_count),
                    else_=0
                )
            ).label('verified_beneficiaries')
        ).join(
            ImpactMetric, ImpactMetric.project_id == Project.id
        ).join(
            Project, ImpactMetric.project_id == Project.id
        ).join(
            Challenge, Project.challenge_id == Challenge.id
        ).join(
            ChallengeCategory, Challenge.id == ChallengeCategory.challenge_id
        ).join(
            Category, ChallengeCategory.category_id == Category.id
        ).group_by(Category.name).order_by(func.sum(ImpactMetric.beneficiaries_count).desc()).limit(10).all()
        
        return [{
            "category": r.name,
            "projects_count": r.projects,
            "beneficiaries": int(r.total_beneficiaries) if r.total_beneficiaries else 0,
            "verified_beneficiaries": int(r.verified_beneficiaries) if r.verified_beneficiaries else 0
        } for r in results]

