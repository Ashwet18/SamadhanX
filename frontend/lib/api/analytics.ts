/**
 * Analytics API client for Government/Admin Dashboard
 * Consumes Phase 1 Backend Analytics API
 */

import axios from 'axios'
import { getApiUrl } from './config'
import type {
  PlatformOverviewResponse,
  ChallengeAnalyticsResponse,
  ProjectPipelineAnalyticsResponse,
  UniversityAnalyticsResponse,
  IndustryAnalyticsResponse,
  ImpactAnalyticsResponse,
  TopInsightsResponse,
  DashboardSummaryResponse,
  AnalyticsDateFilter,
} from '@/types/analytics'

// Get auth token from storage (if using localStorage/cookies)
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('samadhanx_access_token')
}

// Create axios instance with auth headers
const createAuthHeaders = () => {
  const token = getAuthToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Fetch platform overview statistics
 */
export async function getPlatformOverview(): Promise<PlatformOverviewResponse> {
  const url = getApiUrl('/analytics/overview')
  const response = await axios.get<PlatformOverviewResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Fetch challenge analytics with optional date filtering
 */
export async function getChallengeAnalytics(
  filters?: AnalyticsDateFilter
): Promise<ChallengeAnalyticsResponse> {
  const url = getApiUrl('/analytics/challenges')
  const response = await axios.get<ChallengeAnalyticsResponse>(url, {
    headers: createAuthHeaders(),
    params: filters,
  })
  return response.data
}

/**
 * Fetch project pipeline analytics
 */
export async function getProjectPipeline(): Promise<ProjectPipelineAnalyticsResponse> {
  const url = getApiUrl('/analytics/projects/pipeline')
  const response = await axios.get<ProjectPipelineAnalyticsResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Fetch university analytics
 */
export async function getUniversityAnalytics(): Promise<UniversityAnalyticsResponse> {
  const url = getApiUrl('/analytics/universities')
  const response = await axios.get<UniversityAnalyticsResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Fetch industry analytics
 */
export async function getIndustryAnalytics(): Promise<IndustryAnalyticsResponse> {
  const url = getApiUrl('/analytics/industry')
  const response = await axios.get<IndustryAnalyticsResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Fetch impact analytics
 */
export async function getImpactAnalytics(): Promise<ImpactAnalyticsResponse> {
  const url = getApiUrl('/analytics/impact')
  const response = await axios.get<ImpactAnalyticsResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Fetch top insights and rankings
 */
export async function getTopInsights(): Promise<TopInsightsResponse> {
  const url = getApiUrl('/analytics/insights')
  const response = await axios.get<TopInsightsResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Fetch consolidated dashboard summary
 */
export async function getDashboardSummary(): Promise<DashboardSummaryResponse> {
  const url = getApiUrl('/analytics/dashboard')
  const response = await axios.get<DashboardSummaryResponse>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

// Export all analytics API functions
export const analyticsApi = {
  getPlatformOverview,
  getChallengeAnalytics,
  getProjectPipeline,
  getUniversityAnalytics,
  getIndustryAnalytics,
  getImpactAnalytics,
  getTopInsights,
  getDashboardSummary,
}
