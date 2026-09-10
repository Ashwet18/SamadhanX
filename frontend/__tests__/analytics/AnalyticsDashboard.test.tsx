/**
 * Tests for Government/Admin Analytics Dashboard (Phase 2)
 * 
 * Test Coverage:
 * - Authorization and access control
 * - Data rendering from API
 * - Loading states
 * - Empty states
 * - Error states
 * - No hardcoded values
 */

import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import AnalyticsDashboardPage from '@/app/analytics/page'
import { analyticsApi } from '@/lib/api/analytics'

// Mock the analytics API
jest.mock('@/lib/api/analytics')

// Mock Chart.js to avoid canvas errors in tests
jest.mock('react-chartjs-2', () => ({
  Bar: () => <div data-testid="bar-chart">Bar Chart</div>,
  Doughnut: () => <div data-testid="doughnut-chart">Doughnut Chart</div>,
  Pie: () => <div data-testid="pie-chart">Pie Chart</div>,
}))

jest.mock('chart.js', () => ({
  Chart: {
    register: jest.fn(),
  },
  CategoryScale: {},
  LinearScale: {},
  BarElement: {},
  ArcElement: {},
  Title: {},
  Tooltip: {},
  Legend: {},
}))

// Mock data matching Phase 1 API responses
const mockOverviewData = {
  total_challenges: 150,
  challenges_by_status: {
    VALIDATED: 45,
    SUBMITTED: 30,
    UNIVERSITY_INVITED: 20,
  },
  challenges_by_category: {
    Healthcare: 40,
    Education: 35,
    Agriculture: 30,
  },
  challenges_by_priority: {
    HIGH: 50,
    MEDIUM: 70,
    LOW: 30,
  },
  total_validated_challenges: 45,
  total_universities: 25,
  total_projects: 85,
  projects_by_status: {
    PLANNING: 20,
    PROTOTYPE: 30,
    DEPLOYED: 15,
  },
  total_industry_partners: 40,
  total_partnerships: 60,
  active_partnerships: 35,
  total_reported_beneficiaries: 15000,
  total_verified_beneficiaries: 12000,
}

const mockChallengesData = {
  total_challenges: 150,
  status_distribution: {
    SUBMITTED: 30,
    VALIDATED: 45,
  },
  category_distribution: {
    Healthcare: 40,
    Education: 35,
  },
  priority_distribution: {
    HIGH: 50,
    MEDIUM: 70,
  },
  geographic_distribution: {
    Ranchi: 45,
    Dhanbad: 30,
  },
  validation_rate: 75.5,
  duplicate_rate: 5.2,
  avg_days_to_validation: null,
  submission_trend: [
    { month: '2026-01', count: 15 },
    { month: '2026-02', count: 22 },
  ],
}

const mockPipelineData = {
  total_projects: 85,
  pipeline_stages: [
    { stage: 'PLANNING', count: 20, percentage: 23.53 },
    { stage: 'PROTOTYPE', count: 30, percentage: 35.29 },
    { stage: 'DEPLOYED', count: 15, percentage: 17.65 },
  ],
  conversion_rates: {
    planning_to_approved: null,
    approved_to_prototype: null,
    prototype_to_pilot: null,
    pilot_to_deployed: null,
  },
}

const mockUniversitiesData = {
  total_universities: 25,
  participating_universities: 20,
  challenges_matched: 120,
  invitations_sent: 150,
  invitations_accepted: 100,
  acceptance_rate: 66.67,
  projects_created: 85,
  projects_completed: 25,
  total_students: 450,
  total_faculty: 120,
  top_universities: [
    {
      university_id: 'uuid-1',
      university_name: 'Birla Institute of Technology',
      project_count: 15,
      completed_projects: 5,
      active_projects: 10,
    },
  ],
}

const mockIndustryData = {
  total_industry_partners: 40,
  active_partners: 30,
  total_partnerships: 60,
  partnerships_by_status: {
    ACTIVE: 35,
    COMPLETED: 15,
  },
  partnerships_by_type: {
    TECHNICAL_MENTORSHIP: 25,
    FUNDING_SUPPORT: 10,
  },
  total_contributions: 150,
  contributions_by_type: {
    TECHNICAL_MENTORING: 50,
    CLOUD_CREDITS: 30,
  },
  contributions_by_status: {
    DELIVERED: 80,
    IN_PROGRESS: 40,
  },
  top_partners: [
    {
      partner_id: 'uuid-1',
      organization_name: 'Tech Solutions Pvt Ltd',
      partnership_count: 12,
      contribution_count: 30,
    },
  ],
}

const mockImpactData = {
  total_beneficiaries: 15000,
  verified_beneficiaries: 12000,
  projects_with_impact: 45,
  projects_with_verified_impact: 35,
  verification_rate: 77.78,
  geographic_distribution: {
    Ranchi: 5000,
    Dhanbad: 4000,
  },
  category_distribution: {
    Healthcare: 6000,
    Education: 5000,
  },
  sustainability_status: {
    Sustainable: 30,
    'Needs Support': 10,
  },
}

const mockInsightsData = {
  highest_impact_projects: [
    {
      project_code: 'PRJ-JH-2026-00042',
      project_name: 'Rural Healthcare Mobile App',
      beneficiaries: 5000,
      status: 'DEPLOYED',
      university_name: 'BIT Mesra',
    },
  ],
  most_active_universities: [
    {
      university_name: 'Birla Institute of Technology',
      project_count: 15,
      completed_projects: 5,
    },
  ],
  most_active_industry_partners: [
    {
      organization_name: 'Tech Solutions Pvt Ltd',
      partnership_count: 12,
    },
  ],
  challenges_needing_attention: [
    {
      challenge_code: 'CH-JH-2026-00023',
      title: 'Water Scarcity in Rural Areas',
      priority_level: 'HIGH',
      status: 'SUBMITTED',
      days_pending: 45,
    },
  ],
}

describe('Analytics Dashboard - Authorization', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should handle 403 Forbidden error for unauthorized users', async () => {
    const mockError = {
      response: {
        status: 403,
        data: { message: 'Access denied' },
      },
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getTopInsights as jest.Mock).mockRejectedValue(mockError)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText(/Access denied/i)).toBeInTheDocument()
      expect(screen.getByText(/You do not have permission to view analytics/i)).toBeInTheDocument()
    })
  })

  test('should handle 401 Unauthorized error for unauthenticated users', async () => {
    const mockError = {
      response: {
        status: 401,
        data: { message: 'Unauthorized' },
      },
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getTopInsights as jest.Mock).mockRejectedValue(mockError)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText(/Authentication required/i)).toBeInTheDocument()
      expect(screen.getByText(/Please log in/i)).toBeInTheDocument()
    })
  })
})

describe('Analytics Dashboard - Data Rendering', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    
    // Mock successful API responses
    ;(analyticsApi.getPlatformOverview as jest.Mock).mockResolvedValue(mockOverviewData)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockResolvedValue(mockChallengesData)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockResolvedValue(mockPipelineData)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockResolvedValue(mockUniversitiesData)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockResolvedValue(mockIndustryData)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockResolvedValue(mockImpactData)
    ;(analyticsApi.getTopInsights as jest.Mock).mockResolvedValue(mockInsightsData)
  })

  test('should render dashboard title and description', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Government Analytics Dashboard')).toBeInTheDocument()
      expect(screen.getByText('SamadhanX Innovation Pipeline Monitoring')).toBeInTheDocument()
    })
  })

  test('should render overview metrics from API data', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      // Check that values come from API, not hardcoded
      expect(screen.getByText('150')).toBeInTheDocument() // total_challenges
      expect(screen.getByText('85')).toBeInTheDocument() // total_projects
      expect(screen.getByText('25')).toBeInTheDocument() // total_universities
      expect(screen.getByText('12,000')).toBeInTheDocument() // verified_beneficiaries
    })
  })

  test('should render challenge analytics', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Challenges by Status')).toBeInTheDocument()
      expect(screen.getByText('Challenges by Priority')).toBeInTheDocument()
    })
  })

  test('should render project pipeline with stages', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Project Pipeline')).toBeInTheDocument()
      expect(screen.getByText('Planning')).toBeInTheDocument()
      expect(screen.getByText('Prototype')).toBeInTheDocument()
      expect(screen.getByText('Deployed')).toBeInTheDocument()
    })
  })

  test('should render university analytics', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Top Universities')).toBeInTheDocument()
      expect(screen.getByText('Birla Institute of Technology')).toBeInTheDocument()
    })
  })

  test('should render industry analytics', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Top Industry Partners')).toBeInTheDocument()
      expect(screen.getByText('Tech Solutions Pvt Ltd')).toBeInTheDocument()
    })
  })

  test('should render impact analytics', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Impact Verification')).toBeInTheDocument()
      expect(screen.getByText('77.8%')).toBeInTheDocument() // verification_rate
    })
  })

  test('should render high impact projects', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Highest Impact Projects')).toBeInTheDocument()
      expect(screen.getByText('Rural Healthcare Mobile App')).toBeInTheDocument()
    })
  })

  test('should render challenges requiring attention', async () => {
    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText('Challenges Requiring Attention')).toBeInTheDocument()
      expect(screen.getByText('Water Scarcity in Rural Areas')).toBeInTheDocument()
    })
  })
})

describe('Analytics Dashboard - Loading State', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should show loading skeletons initially', () => {
    // Make API calls never resolve to keep loading state
    ;(analyticsApi.getPlatformOverview as jest.Mock).mockImplementation(() => new Promise(() => {}))
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockImplementation(() => new Promise(() => {}))
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockImplementation(() => new Promise(() => {}))
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockImplementation(() => new Promise(() => {}))
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockImplementation(() => new Promise(() => {}))
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockImplementation(() => new Promise(() => {}))
    ;(analyticsApi.getTopInsights as jest.Mock).mockImplementation(() => new Promise(() => {}))

    render(<AnalyticsDashboardPage />)

    // Check for loading indicators (skeleton has animate-pulse)
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBeGreaterThan(0)
  })
})

describe('Analytics Dashboard - Empty State', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should handle empty data gracefully', async () => {
    const emptyOverview = {
      total_challenges: 0,
      challenges_by_status: {},
      challenges_by_category: {},
      challenges_by_priority: {},
      total_validated_challenges: 0,
      total_universities: 0,
      total_projects: 0,
      projects_by_status: {},
      total_industry_partners: 0,
      total_partnerships: 0,
      active_partnerships: 0,
      total_reported_beneficiaries: 0,
      total_verified_beneficiaries: 0,
    }

    const emptyPipeline = {
      total_projects: 0,
      pipeline_stages: [],
      conversion_rates: {
        planning_to_approved: null,
        approved_to_prototype: null,
        prototype_to_pilot: null,
        pilot_to_deployed: null,
      },
    }

    const emptyUniversities = {
      ...mockUniversitiesData,
      total_universities: 0,
      top_universities: [],
    }

    const emptyIndustry = {
      ...mockIndustryData,
      total_industry_partners: 0,
      top_partners: [],
    }

    const emptyInsights = {
      highest_impact_projects: [],
      most_active_universities: [],
      most_active_industry_partners: [],
      challenges_needing_attention: [],
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockResolvedValue(emptyOverview)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockResolvedValue(mockChallengesData)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockResolvedValue(emptyPipeline)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockResolvedValue(emptyUniversities)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockResolvedValue(emptyIndustry)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockResolvedValue(mockImpactData)
    ;(analyticsApi.getTopInsights as jest.Mock).mockResolvedValue(emptyInsights)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      // Should show zeros, not errors - verify multiple zeros are displayed
      const zeros = screen.getAllByText('0')
      expect(zeros.length).toBeGreaterThan(0)
    })
  })
})

describe('Analytics Dashboard - Error Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should handle network errors', async () => {
    const networkError = {
      code: 'ERR_NETWORK',
      message: 'Network Error',
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockRejectedValue(networkError)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockRejectedValue(networkError)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockRejectedValue(networkError)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockRejectedValue(networkError)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockRejectedValue(networkError)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockRejectedValue(networkError)
    ;(analyticsApi.getTopInsights as jest.Mock).mockRejectedValue(networkError)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText(/Network error/i)).toBeInTheDocument()
      expect(screen.getByText(/check your connection/i)).toBeInTheDocument()
    })
  })

  test('should handle 404 errors', async () => {
    const notFoundError = {
      response: {
        status: 404,
        data: { message: 'Not Found' },
      },
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockRejectedValue(notFoundError)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockRejectedValue(notFoundError)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockRejectedValue(notFoundError)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockRejectedValue(notFoundError)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockRejectedValue(notFoundError)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockRejectedValue(notFoundError)
    ;(analyticsApi.getTopInsights as jest.Mock).mockRejectedValue(notFoundError)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(screen.getByText(/Analytics service not found/i)).toBeInTheDocument()
    })
  })

  test('should show Try Again button on error', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { message: 'Server Error' },
      },
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockRejectedValue(mockError)
    ;(analyticsApi.getTopInsights as jest.Mock).mockRejectedValue(mockError)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      const tryAgainButton = screen.getByRole('button', { name: /Try Again/i })
      expect(tryAgainButton).toBeInTheDocument()
    })
  })
})

describe('Analytics Dashboard - No Hardcoded Values', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('should use API data for all metrics, not hardcoded values', async () => {
    const customData = {
      total_challenges: 999,
      challenges_by_status: { VALIDATED: 111 },
      challenges_by_category: {},
      challenges_by_priority: {},
      total_validated_challenges: 111,
      total_universities: 888,
      total_projects: 777,
      projects_by_status: {},
      total_industry_partners: 666,
      total_partnerships: 555,
      active_partnerships: 444,
      total_reported_beneficiaries: 333333,
      total_verified_beneficiaries: 222222,
    }

    ;(analyticsApi.getPlatformOverview as jest.Mock).mockResolvedValue(customData)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockResolvedValue(mockChallengesData)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockResolvedValue(mockPipelineData)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockResolvedValue(mockUniversitiesData)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockResolvedValue(mockIndustryData)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockResolvedValue(mockImpactData)
    ;(analyticsApi.getTopInsights as jest.Mock).mockResolvedValue(mockInsightsData)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      // Verify custom API values are displayed
      expect(screen.getByText('999')).toBeInTheDocument()
      expect(screen.getByText('888')).toBeInTheDocument()
      expect(screen.getByText('777')).toBeInTheDocument()
      expect(screen.getByText('666')).toBeInTheDocument()
      expect(screen.getByText('222,222')).toBeInTheDocument()
    })
  })

  test('should call all API endpoints on mount', async () => {
    ;(analyticsApi.getPlatformOverview as jest.Mock).mockResolvedValue(mockOverviewData)
    ;(analyticsApi.getChallengeAnalytics as jest.Mock).mockResolvedValue(mockChallengesData)
    ;(analyticsApi.getProjectPipeline as jest.Mock).mockResolvedValue(mockPipelineData)
    ;(analyticsApi.getUniversityAnalytics as jest.Mock).mockResolvedValue(mockUniversitiesData)
    ;(analyticsApi.getIndustryAnalytics as jest.Mock).mockResolvedValue(mockIndustryData)
    ;(analyticsApi.getImpactAnalytics as jest.Mock).mockResolvedValue(mockImpactData)
    ;(analyticsApi.getTopInsights as jest.Mock).mockResolvedValue(mockInsightsData)

    render(<AnalyticsDashboardPage />)

    await waitFor(() => {
      expect(analyticsApi.getPlatformOverview).toHaveBeenCalledTimes(1)
      expect(analyticsApi.getChallengeAnalytics).toHaveBeenCalledTimes(1)
      expect(analyticsApi.getProjectPipeline).toHaveBeenCalledTimes(1)
      expect(analyticsApi.getUniversityAnalytics).toHaveBeenCalledTimes(1)
      expect(analyticsApi.getIndustryAnalytics).toHaveBeenCalledTimes(1)
      expect(analyticsApi.getImpactAnalytics).toHaveBeenCalledTimes(1)
      expect(analyticsApi.getTopInsights).toHaveBeenCalledTimes(1)
    })
  })
})
