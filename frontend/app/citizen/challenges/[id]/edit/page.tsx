'use client'

/**
 * Edit Challenge Page
 * 
 * Allows editing of DRAFT or SUBMITTED challenges
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Loader2, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ChallengeForm } from '@/components/challenges/ChallengeForm'
import { challengeApi } from '@/lib/api/challenges'
import type { Challenge } from '@/types/api'

interface Props {
  params: { id: string }
}

export default function EditChallengePage({ params }: Props) {
  const router = useRouter()

  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadChallenge()
  }, [params.id])

  const loadChallenge = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await challengeApi.getChallenge(params.id)
      
      // Check if challenge can be edited
      if (data.status !== 'DRAFT' && data.status !== 'SUBMITTED') {
        setError('This challenge cannot be edited in its current status')
        return
      }

      setChallenge(data)
    } catch (err: any) {
      console.error('Failed to load challenge:', err)
      setError(err.response?.data?.detail || 'Failed to load challenge')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuccess = (updatedChallenge: Challenge) => {
    // Redirect to challenge detail page
    router.push(`/citizen/challenges/${updatedChallenge.id}`)
  }

  const handleCancel = () => {
    router.push(`/citizen/challenges/${params.id}`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error || !challenge) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || 'Challenge not found'}
          </AlertDescription>
        </Alert>
        <Button
          variant="outline"
          onClick={() => router.back()}
          className="mt-4 gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Go Back
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-4 gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        
        <h1 className="text-3xl font-bold text-gray-900">
          Edit Challenge
        </h1>
        <p className="mt-2 text-gray-600">
          Update challenge details • {challenge.challenge_code}
        </p>
      </div>

      {/* Form */}
      <ChallengeForm
        mode="edit"
        challenge={challenge}
        onSuccess={handleSuccess}
        onCancel={handleCancel}
      />
    </div>
  )
}
