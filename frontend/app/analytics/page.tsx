'use client'

import { useEffect, useState } from 'react'
import { 
  FileText, 
  Users, 
  GraduationCap, 
  Building2, 
  Handshake, 
  TrendingUp,
  CheckCircle2,
  RefreshCw,
  Calendar,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { KPICard } from '@/components/analytics/KPICard'
import { KPICardSkeleton } from '@/components/analytics/KPICardSkeleton'
import { DistributionChart } from '@/components/analytics/DistributionChart'
import { PipelineVisualization } from '@/components/analytics/PipelineVisualization'
import { RankingsTable } from '@/components/analytics/RankingsTable'
import { Badge } from '@/components/ui/badge'
import { formatDateTime } from '@/lib/utils'
import { analyticsApi } from '@/lib/api/analytics'
import type {
  PlatformOverviewResponse,
  ChallengeAnalyticsResponse,
  ProjectPipelineAnalyticsResponse,
  UniversityAnalyticsResponse,
  IndustryAnalyticsResponse,
  ImpactAnalyticsResponse,
  TopInsightsResponse,
} from '@/types/analytics'

export default function AnalyticsDashboardPage() {
  // State for analytics data
  const [overview, setOverview] = useState<PlatformOverviewResponse | null>(null)
  const [challenges, setChallenges] = useState<ChallengeAnalyticsResponse | null>(null)
  const [pipeline, setPipeline] = useState<ProjectPipelineAnalyticsResponse | null>(null)
  const [universities, setUniversities] = useState<UniversityAnalyticsResponse | null>(null)
  const [industry, setIndustry] = useState<IndustryAnalyticsResponse | null>(null)
  const [impact, setImpact] = useState<ImpactAnalyticsResponse | null>(null)
  const [insights, setInsights] = useState<TopInsightsResponse | null>(null)

  // Loading and error states
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Date filter state
  const [dateFilter, setDateFilter] = useState<{ from_date?: string; to_date?: string }>({})

  // Fetch all analytics data
  const fetchAnalyticsData = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Fetch all endpoints in parallel
      const [
        overviewData,
        challengesData,
        pipelineData,
        universitiesData,
        industryData,
        impactData,
        insightsData,
      ] = await Promise.all([
        analyticsApi.getPlatformOverview(),
        analyticsApi.getChallengeAnalytics(dateFilter),
        analyticsApi.getProjectPipeline(),
        analyticsApi.getUniversityAnalytics(),
        analyticsApi.getIndustryAnalytics(),
        analyticsApi.getImpactAnalytics(),
        analyticsApi.getTopInsights(),
      ])

      setOverview(overviewData)
      setChallenges(challengesData)
      setPipeline(pipelineData)
      setUniversities(universitiesData)
      setIndustry(industryData)
      setImpact(impactData)
      setInsights(insightsData)
      setLastUpdated(new Date())
    } catch (err: any) {
      console.error('Error fetching analytics:', err)
      
      // Handle different error types
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in.')
      } else if (err.response?.status === 403) {
        setError('Access denied. You do not have permission to view analytics.')
      } else if (err.response?.status === 404) {
        setError('Analytics service not found.')
      } else if (err.code === 'ERR_NETWORK') {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to load analytics data. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    fetchAnalyticsData()
  }, [])

  // Refresh handler
  const handleRefresh = () => {
    fetchAnalyticsData()
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                    <span className="text-xl">⚠️</span>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-red-900 mb-2">
                    Error Loading Analytics
                  </h3>
                  <p className="text-red-700 mb-4">{error}</p>
                  <Button onClick={handleRefresh} variant="outline" size="sm">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Try Again
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header Skeleton */}
          <div className="mb-8 animate-pulse">
            <div className="h-8 w-64 bg-gray-200 rounded mb-2" />
            <div className="h-4 w-96 bg-gray-200 rounded" />
          </div>

          {/* KPI Cards Skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <KPICardSkeleton key={i} />
            ))}
          </div>

          {/* Content Skeleton */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardHeader>
                  <div className="h-6 w-32 bg-gray-200 rounded animate-pulse" />
                </CardHeader>
                <CardContent>
                  <div className="h-72 bg-gray-100 rounded animate-pulse" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Government Analytics Dashboard
              </h1>
              <p className="text-gray-600 mt-1">
                SamadhanX Innovation Pipeline Monitoring
              </p>
            </div>
            <div className="flex items-center gap-4">
              {lastUpdated && (
                <div className="text-sm text-gray-500 flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  <span>Last updated: {formatDateTime(lastUpdated)}</span>
                </div>
              )}
              <Button onClick={handleRefresh} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* KPI Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Total Challenges"
            value={overview?.total_challenges || 0}
            subtitle={`${overview?.total_validated_challenges || 0} validated`}
            icon={FileText}
            iconBgColor="bg-blue-100"
            iconColor="text-blue-600"
          />
          <KPICard
            title="Active Projects"
            value={overview?.total_projects || 0}
            subtitle="Across all stages"
            icon={TrendingUp}
            iconBgColor="bg-green-100"
            iconColor="text-green-600"
          />
          <KPICard
            title="Universities"
            value={overview?.total_universities || 0}
            subtitle={`${universities?.participating_universities || 0} participating`}
            icon={GraduationCap}
            iconBgColor="bg-purple-100"
            iconColor="text-purple-600"
          />
          <KPICard
            title="Verified Beneficiaries"
            value={overview?.total_verified_beneficiaries?.toLocaleString() || '0'}
            subtitle={`${overview?.total_reported_beneficiaries?.toLocaleString() || '0'} reported`}
            icon={CheckCircle2}
            iconBgColor="bg-emerald-100"
            iconColor="text-emerald-600"
          />
        </div>

        {/* Secondary KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Industry Partners"
            value={overview?.total_industry_partners || 0}
            subtitle={`${overview?.active_partnerships || 0} active partnerships`}
            icon={Building2}
            iconBgColor="bg-orange-100"
            iconColor="text-orange-600"
          />
          <KPICard
            title="Total Partnerships"
            value={overview?.total_partnerships || 0}
            subtitle="With industry"
            icon={Handshake}
            iconBgColor="bg-indigo-100"
            iconColor="text-indigo-600"
          />
          <KPICard
            title="Students Participating"
            value={universities?.total_students || 0}
            subtitle="Across universities"
            icon={Users}
            iconBgColor="bg-pink-100"
            iconColor="text-pink-600"
          />
          <KPICard
            title="Faculty Involved"
            value={universities?.total_faculty || 0}
            subtitle="Guiding projects"
            icon={GraduationCap}
            iconBgColor="bg-teal-100"
            iconColor="text-teal-600"
          />
        </div>

        {/* Challenge Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <DistributionChart
            title="Challenges by Status"
            description="Distribution of challenges across lifecycle stages"
            data={overview?.challenges_by_status || {}}
            type="doughnut"
          />
          <DistributionChart
            title="Challenges by Priority"
            description="Priority distribution of submitted challenges"
            data={overview?.challenges_by_priority || {}}
            type="bar"
            colors={[
              'rgb(239, 68, 68)',    // red for HIGH
              'rgb(245, 158, 11)',   // amber for MEDIUM
              'rgb(59, 130, 246)',   // blue for LOW
              'rgb(139, 92, 246)',   // purple for CRITICAL
            ]}
          />
        </div>

        {/* Project Pipeline */}
        {pipeline && (
          <div className="mb-8">
            <PipelineVisualization
              stages={pipeline.pipeline_stages}
              totalProjects={pipeline.total_projects}
            />
          </div>
        )}

        {/* University & Industry Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {universities && universities.top_universities.length > 0 && (
            <RankingsTable
              title="Top Universities"
              description="Most active universities by project count"
              items={universities.top_universities.map((uni, index) => ({
                rank: index + 1,
                name: uni.university_name,
                value: uni.project_count,
                subtitle: `${uni.completed_projects} completed • ${uni.active_projects} active`,
              }))}
              valueLabel="Projects"
            />
          )}

          {industry && industry.top_partners && industry.top_partners.length > 0 && (
            <RankingsTable
              title="Top Industry Partners"
              description="Most engaged industry partners"
              items={industry.top_partners.map((partner, index) => ({
                rank: index + 1,
                name: partner.organization_name,
                value: partner.partnership_count,
                subtitle: `${partner.contribution_count} contributions`,
              }))}
              valueLabel="Partnerships"
            />
          )}
        </div>

        {/* Impact Analytics */}
        {impact && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <DistributionChart
              title="Impact by Geographic Area"
              description="Verified beneficiaries by location"
              data={impact.geographic_distribution || {}}
              type="bar"
            />
            <Card>
              <CardHeader>
                <CardTitle>Impact Verification</CardTitle>
                <CardDescription>Projects with measured and verified impact</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Projects with Impact</p>
                      <p className="text-2xl font-bold text-gray-900 mt-1">
                        {impact.projects_with_impact}
                      </p>
                    </div>
                    <Badge variant="secondary">Total</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-green-700">Verified Impact</p>
                      <p className="text-2xl font-bold text-green-900 mt-1">
                        {impact.projects_with_verified_impact}
                      </p>
                    </div>
                    <Badge variant="success">Verified</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-blue-700">Verification Rate</p>
                      <p className="text-2xl font-bold text-blue-900 mt-1">
                        {impact.verification_rate.toFixed(1)}%
                      </p>
                    </div>
                    <Badge variant="blue">Rate</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* High Impact Projects */}
        {insights && insights.highest_impact_projects && insights.highest_impact_projects.length > 0 && (
          <div className="mb-8">
            <RankingsTable
              title="Highest Impact Projects"
              description="Top 5 projects by verified beneficiaries reached"
              items={insights.highest_impact_projects.map((project, index) => ({
                rank: index + 1,
                name: project.project_name,
                value: project.beneficiaries,
                subtitle: `${project.university_name} • ${project.status}`,
                badge: project.project_code,
              }))}
              valueLabel="Beneficiaries"
            />
          </div>
        )}

        {/* Attention Required */}
        {insights && insights.challenges_needing_attention && insights.challenges_needing_attention.length > 0 && (
          <Card className="border-amber-200 bg-amber-50">
            <CardHeader>
              <CardTitle className="text-amber-900">Challenges Requiring Attention</CardTitle>
              <CardDescription className="text-amber-700">
                High-priority challenges pending validation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {insights.challenges_needing_attention.slice(0, 5).map((challenge) => (
                  <div
                    key={challenge.challenge_code}
                    className="flex items-center justify-between p-3 bg-white rounded-lg border border-amber-200"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="warning">{challenge.priority_level}</Badge>
                        <span className="text-xs text-gray-500">{challenge.challenge_code}</span>
                      </div>
                      <p className="text-sm font-medium text-gray-900">{challenge.title}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        Status: {challenge.status} • Pending for {challenge.days_pending} days
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
