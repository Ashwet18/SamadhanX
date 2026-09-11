'use client'

/**
 * My Challenges Page
 * 
 * Lists all challenges submitted by the current citizen
 */

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Plus, Loader2, AlertCircle, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ChallengeCard } from '@/components/challenges/ChallengeCard'
import { challengeApi } from '@/lib/api/challenges'
import type { ChallengeListItem, ChallengeListResponse } from '@/lib/api/challenges'
import type { ChallengeStatus } from '@/types/api'

export default function MyChallengesPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [challenges, setChallenges] = useState<ChallengeListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    pages: 0,
    hasNext: false,
    hasPrevious: false,
  })

  // Status filter
  const statusParam = searchParams.get('status') as ChallengeStatus | null
  const [selectedStatus, setSelectedStatus] = useState<ChallengeStatus | null>(statusParam)

  useEffect(() => {
    loadChallenges()
  }, [pagination.page, selectedStatus])

  const loadChallenges = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await challengeApi.getMyChallenges(
        pagination.page,
        pagination.pageSize,
        selectedStatus || undefined
      )

      setChallenges(response.items)
      setPagination({
        page: response.page,
        pageSize: response.page_size,
        total: response.total,
        pages: response.pages,
        hasNext: response.has_next,
        hasPrevious: response.has_previous,
      })
    } catch (err: any) {
      console.error('Failed to load challenges:', err)
      setError(err.response?.data?.detail || 'Failed to load challenges')
    } finally {
      setIsLoading(false)
    }
  }

  const handleStatusFilter = (status: ChallengeStatus | null) => {
    setSelectedStatus(status)
    setPagination(prev => ({ ...prev, page: 1 }))
    
    // Update URL
    const params = new URLSearchParams()
    if (status) params.set('status', status)
    router.push(`/citizen/challenges?${params.toString()}`)
  }

  const handleNextPage = () => {
    if (pagination.hasNext) {
      setPagination(prev => ({ ...prev, page: prev.page + 1 }))
    }
  }

  const handlePreviousPage = () => {
    if (pagination.hasPrevious) {
      setPagination(prev => ({ ...prev, page: prev.page - 1 }))
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Challenges</h1>
            <p className="mt-2 text-gray-600">
              View and manage all your submitted challenges
            </p>
          </div>
          <Link href="/citizen/challenges/new">
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Challenge
            </Button>
          </Link>
        </div>
      </div>

      {/* Status Filter */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedStatus === null ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter(null)}
            >
              All
            </Button>
            <Button
              variant={selectedStatus === 'SUBMITTED' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('SUBMITTED')}
            >
              Submitted
            </Button>
            <Button
              variant={selectedStatus === 'PENDING_REVIEW' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('PENDING_REVIEW')}
            >
              Pending Review
            </Button>
            <Button
              variant={selectedStatus === 'VALIDATED' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('VALIDATED')}
            >
              Validated
            </Button>
            <Button
              variant={selectedStatus === 'DRAFT' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleStatusFilter('DRAFT')}
            >
              Draft
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
            <button
              onClick={loadChallenges}
              className="ml-2 underline hover:no-underline"
            >
              Try again
            </button>
          </AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      ) : challenges.length === 0 ? (
        /* Empty State */
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                {selectedStatus
                  ? `No ${selectedStatus.toLowerCase()} challenges`
                  : 'No challenges yet'}
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                {selectedStatus
                  ? 'Try changing the filter or submit a new challenge'
                  : 'Get started by submitting your first challenge'}
              </p>
              <Link href="/citizen/challenges/new">
                <Button className="mt-4 gap-2">
                  <Plus className="h-4 w-4" />
                  Submit Challenge
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Results Summary */}
          <div className="mb-4 text-sm text-gray-600">
            Showing {challenges.length} of {pagination.total} {pagination.total === 1 ? 'challenge' : 'challenges'}
            {selectedStatus && ` (${selectedStatus.toLowerCase()})`}
          </div>

          {/* Challenge Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {challenges.map((challenge) => (
              <ChallengeCard key={challenge.id} challenge={challenge} />
            ))}
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={handlePreviousPage}
                disabled={!pagination.hasPrevious}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {pagination.page} of {pagination.pages}
              </span>
              <Button
                variant="outline"
                onClick={handleNextPage}
                disabled={!pagination.hasNext}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
