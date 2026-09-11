'use client'

/**
 * Submit New Challenge Page
 * 
 * Allows citizens to submit new societal challenges
 */

import { useRouter } from 'next/navigation'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ChallengeForm } from '@/components/challenges/ChallengeForm'
import type { Challenge } from '@/types/api'

export default function NewChallengePage() {
  const router = useRouter()

  const handleSuccess = (challenge: Challenge) => {
    // Redirect to challenge detail page
    router.push(`/citizen/challenges/${challenge.id}`)
  }

  const handleCancel = () => {
    router.back()
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
          Submit a New Challenge
        </h1>
        <p className="mt-2 text-gray-600">
          Help us identify and address societal challenges in Jharkhand
        </p>
      </div>

      {/* Form */}
      <ChallengeForm
        mode="create"
        onSuccess={handleSuccess}
        onCancel={handleCancel}
      />
    </div>
  )
}
