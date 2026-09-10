/**
 * TypeScript type definitions for Government/Admin Analytics
 * Based on Phase 1 Backend Analytics API
 */

// Platform Overview Types
export interface PlatformOverviewResponse {
  total_challenges: number
  challenges_by_status: Record<string, number>
  challenges_by_category: Record<string, number>
  challenges_by_priority: Record<string, number>
  total_validated_challenges: number
  total_universities: number
  total_projects: number
  projects_by_status: Record<string, number>
  total_industry_partners: number
  total_partnerships: number
  active_partnerships: number
  total_reported_beneficiaries: number
  total_verified_beneficiaries: number
}

// Challenge Analytics Types
export interface ChallengeAnalyticsResponse {
  total_challenges: number
  status_distribution: Record<string, number>
  category_distribution: Record<string, number>
  priority_distribution: Record<string, number>
  geographic_distribution: Record<string, number>
  validation_rate: number
  duplicate_rate: number
  avg_days_to_validation: number | null
  submission_trend: Array<{
    month: string
    count: number
  }>
}

// Project Pipeline Types
export interface PipelineStage {
  stage: string
  count: number
  percentage: number
}

export interface ProjectPipelineAnalyticsResponse {
  total_projects: number
  pipeline_stages: PipelineStage[]
  conversion_rates: {
    planning_to_approved: number | null
    approved_to_prototype: number | null
    prototype_to_pilot: number | null
    pilot_to_deployed: number | null
  }
}

// University Analytics Types
export interface UniversityRanking {
  university_id: string
  university_name: string
  project_count: number
  completed_projects: number
  active_projects: number
}

export interface UniversityAnalyticsResponse {
  total_universities: number
  participating_universities: number
  challenges_matched: number
  invitations_sent: number
  invitations_accepted: number
  acceptance_rate: number
  projects_created: number
  projects_completed: number
  total_students: number
  total_faculty: number
  top_universities: UniversityRanking[]
}

// Industry Analytics Types
export interface IndustryPartnerRanking {
  partner_id: string
  organization_name: string
  partnership_count: number
  contribution_count: number
}

export interface IndustryAnalyticsResponse {
  total_industry_partners: number
  active_partners: number
  total_partnerships: number
  partnerships_by_status: Record<string, number>
  partnerships_by_type: Record<string, number>
  total_contributions: number
  contributions_by_type: Record<string, number>
  contributions_by_status: Record<string, number>
  top_partners: IndustryPartnerRanking[]
}

// Impact Analytics Types
export interface ImpactAnalyticsResponse {
  total_beneficiaries: number
  verified_beneficiaries: number
  projects_with_impact: number
  projects_with_verified_impact: number
  verification_rate: number
  geographic_distribution: Record<string, number>
  category_distribution: Record<string, number>
  sustainability_status: Record<string, number>
}

// Top Insights Types
export interface HighImpactProject {
  project_code: string
  project_name: string
  beneficiaries: number
  status: string
  university_name: string
}

export interface ActiveUniversity {
  university_name: string
  project_count: number
  completed_projects: number
}

export interface ActiveIndustryPartner {
  organization_name: string
  partnership_count: number
}

export interface ChallengeNeedingAttention {
  challenge_code: string
  title: string
  priority_level: string
  status: string
  days_pending: number
}

export interface TopInsightsResponse {
  highest_impact_projects: HighImpactProject[]
  most_active_universities: ActiveUniversity[]
  most_active_industry_partners: ActiveIndustryPartner[]
  challenges_needing_attention: ChallengeNeedingAttention[]
}

// Dashboard Summary Types
export interface DashboardOverview {
  total_challenges: number
  total_projects: number
  total_universities: number
  total_partnerships: number
  verified_beneficiaries: number
}

export interface StatusSummary {
  status: string
  count: number
}

export interface PipelineStageSummary {
  stage: string
  count: number
  percentage: number
}

export interface TopEntity {
  name: string
  projects?: number
  partnerships?: number
}

export interface ImpactSummary {
  verified_projects: number
  total_beneficiaries: number
}

export interface Alert {
  type: string
  count: number
}

export interface DashboardSummaryResponse {
  overview: DashboardOverview
  challenge_status_summary: StatusSummary[]
  project_pipeline_summary: PipelineStageSummary[]
  top_universities: TopEntity[]
  top_partners: TopEntity[]
  impact_summary: ImpactSummary
  alerts: Alert[]
}

// API Query Parameters
export interface AnalyticsDateFilter {
  from_date?: string  // ISO 8601 date (YYYY-MM-DD)
  to_date?: string    // ISO 8601 date (YYYY-MM-DD)
}
