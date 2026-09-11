'use client'

/**
 * Citizen Dashboard
 * 
 * Main dashboard for citizens showing challenge overview and quick actions
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Plus, FileText, Clock, CheckCircle, Loader2 } from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ChallengeCard } from '@/components/challenges/ChallengeCard'
import { challengeApi } from '@/lib/api/challenges'
import type { ChallengeListItem } from '@/lib/api/challenges'

export default function CitizenDashboard() {
  const router = useRouter()
  const { user, isLoading: authLoading } = useAuth()

  const [recentChallenges, setRecentChallenges] = useState<ChallengeListItem[]>([])
  const [stats, setStats] = useState({
    total: 0,
    submitted: 0,
    validated: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!authLoading) {
      loadDashboardData()
    }
  }, [authLoading])

  const loadDashboardData = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Fetch recent challenges (first page)
      const response = await challengeApi.getMyChallenges(1, 5)
      
      setRecentChallenges(response.items)
      
      // Calculate stats from all challenges
      // In a real app, this could be a separate API endpoint
      const allChallenges = await challengeApi.getMyChallenges(1, 100)
      const total = allChallenges.total
      const submitted = allChallenges.items.filter(c => c.status === 'SUBMITTED').length
      const validated = allChallenges.items.filter(c => c.status === 'VALIDATED').length
      
      setStats({ total, submitted, validated })
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err)
      setError(err.response?.data?.detail || 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome, {user?.name || 'Citizen'}
        </h1>
        <p className="mt-2 text-gray-600">
          Submit and track societal challenges in Jharkhand
        </p>
      </div>

      {/* Primary Action */}
      <div className="mb-8">
        <Link href="/citizen/challenges/new">
          <Button size="lg" className="gap-2">
            <Plus className="h-5 w-5" />
            Submit a New Challenge
          </Button>
        </Link>
      </div>

      {/* Error State */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>
            {error}
            <button
              onClick={loadDashboardData}
              className="ml-2 underline hover:no-underline"
            >
              Try again
            </button>
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Challenges
            </CardTitle>
            <FileText className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-gray-500 mt-1">
              All challenges submitted
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Under Review
            </CardTitle>
            <Clock className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.submitted}</div>
            <p className="text-xs text-gray-500 mt-1">
              Awaiting government review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Validated
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-gray-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.validated}</div>
            <p className="text-xs text-gray-500 mt-1">
              Approved challenges
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Challenges */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Recent Challenges</CardTitle>
              <CardDescription>Your latest submitted challenges</CardDescription>
            </div>
            <Link href="/citizen/challenges">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          {recentChallenges.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                No challenges yet
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Get started by submitting your first challenge
              </p>
              <Link href="/citizen/challenges/new">
                <Button className="mt-4 gap-2">
                  <Plus className="h-4 w-4" />
                  Submit Challenge
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {recentChallenges.map((challenge) => (
                <ChallengeCard key={challenge.id} challenge={challenge} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
