'use client'

/**
 * ChallengeForm Component
 * 
 * Reusable form for creating and editing challenges
 * Handles validation, media upload, location, and categories
 */

import { useState, useEffect, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { FormError } from '@/components/ui/form-error'
import { ButtonLoading } from '@/components/ui/loading-spinner'
import { CategorySelect } from './CategorySelect'
import { MediaUpload } from './MediaUpload'
import { LocationPicker } from './LocationPicker'
import { challengeApi } from '@/lib/api/challenges'
import {
  validateChallengeForm,
  hasValidationErrors,
  type ChallengeValidationErrors,
} from '@/lib/validation/challenge'
import { JHARKHAND_DISTRICTS } from '@/lib/constants/jharkhand'
import type { Challenge, UUID } from '@/types/api'
import { CheckCircle, AlertCircle } from 'lucide-react'

interface ChallengeFormProps {
  mode: 'create' | 'edit'
  challenge?: Challenge
  onSuccess?: (challenge: Challenge) => void
  onCancel?: () => void
}

export function ChallengeForm({
  mode,
  challenge,
  onSuccess,
  onCancel,
}: ChallengeFormProps) {
  const router = useRouter()
  
  // Form state
  const [title, setTitle] = useState(challenge?.title || '')
  const [description, setDescription] = useState(challenge?.description || '')
  const [district, setDistrict] = useState(challenge?.district || '')
  const [block, setBlock] = useState(challenge?.block || '')
  const [village, setVillage] = useState(challenge?.village || '')
  const [latitude, setLatitude] = useState<number | null>(challenge?.latitude ?? null)
  const [longitude, setLongitude] = useState<number | null>(challenge?.longitude ?? null)
  const [affectedPopulation, setAffectedPopulation] = useState<string>(
    challenge?.affected_population?.toString() || ''
  )
  const [selectedCategories, setSelectedCategories] = useState<string[]>(
    challenge?.categories?.map(c => c.id) || []
  )
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  
  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<ChallengeValidationErrors>({})
  const [showSuccess, setShowSuccess] = useState(false)
  const [createdChallenge, setCreatedChallenge] = useState<Challenge | null>(null)

  /**
   * Clear validation error when user starts typing
   */
  const clearFieldError = (field: keyof ChallengeValidationErrors) => {
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const updated = { ...prev }
        delete updated[field]
        return updated
      })
    }
  }

  /**
   * Handle location change
   */
  const handleLocationChange = (lat: number | null, lng: number | null) => {
    setLatitude(lat)
    setLongitude(lng)
    clearFieldError('latitude')
    clearFieldError('longitude')
  }

  /**
   * Validate and submit form
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Clear previous errors
    setSubmitError(null)
    setValidationErrors({})

    // Parse affected population
    const populationValue = affectedPopulation.trim()
      ? parseInt(affectedPopulation, 10)
      : undefined

    // Client-side validation
    const errors = validateChallengeForm({
      title,
      description,
      district,
      block,
      village,
      latitude,
      longitude,
      affected_population: populationValue,
      category_ids: selectedCategories,
    })

    if (hasValidationErrors(errors)) {
      setValidationErrors(errors)
      // Scroll to first error
      window.scrollTo({ top: 0, behavior: 'smooth' })
      return
    }

    setIsSubmitting(true)

    try {
      let resultChallenge: Challenge

      if (mode === 'create') {
        // Create challenge
        resultChallenge = await challengeApi.createChallenge({
          title: title.trim(),
          description: description.trim(),
          district: district.trim(),
          block: block.trim() || undefined,
          village: village.trim() || undefined,
          latitude,
          longitude,
          affected_population: populationValue,
          category_ids: selectedCategories,
        })

        // Upload media files if any
        if (selectedFiles.length > 0) {
          await uploadMediaFiles(resultChallenge.id, selectedFiles)
        }

        // Show success state
        setCreatedChallenge(resultChallenge)
        setShowSuccess(true)

        // Call success callback or redirect after delay
        setTimeout(() => {
          if (onSuccess) {
            onSuccess(resultChallenge)
          } else {
            router.push(`/citizen/challenges/${resultChallenge.id}`)
          }
        }, 2000)
      } else {
        // Update challenge
        resultChallenge = await challengeApi.updateChallenge(challenge!.id, {
          title: title.trim(),
          description: description.trim(),
          district: district.trim(),
          block: block.trim() || undefined,
          village: village.trim() || undefined,
          latitude,
          longitude,
          affected_population: populationValue,
          category_ids: selectedCategories.length > 0 ? selectedCategories : undefined,
        })

        // Upload new media files if any
        if (selectedFiles.length > 0) {
          await uploadMediaFiles(resultChallenge.id, selectedFiles)
        }

        // Show success state
        setCreatedChallenge(resultChallenge)
        setShowSuccess(true)

        // Call success callback or redirect after delay
        setTimeout(() => {
          if (onSuccess) {
            onSuccess(resultChallenge)
          } else {
            router.push(`/citizen/challenges/${resultChallenge.id}`)
          }
        }, 1500)
      }
    } catch (error: any) {
      console.error('Challenge submission failed:', error)
      
      // Extract error message
      let errorMessage = 'Failed to submit challenge. Please try again.'
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((e: any) => e.msg).join(', ')
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      setSubmitError(errorMessage)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * Upload media files sequentially
   */
  const uploadMediaFiles = async (challengeId: UUID, files: File[]) => {
    for (const file of files) {
      try {
        await challengeApi.uploadChallengeMedia(challengeId, file)
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error)
        // Continue with other files
      }
    }
  }

  // Show success state
  if (showSuccess && createdChallenge) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center space-y-4 py-8">
            <div className="flex justify-center">
              <div className="rounded-full bg-green-100 p-3">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                {mode === 'create' ? 'Challenge Submitted Successfully!' : 'Challenge Updated!'}
              </h3>
              <p className="mt-2 text-gray-600">
                {mode === 'create'
                  ? 'Your challenge has been submitted for review.'
                  : 'Your changes have been saved.'}
              </p>
            </div>
            {createdChallenge.challenge_code && (
              <div className="inline-block px-4 py-2 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-gray-600">Challenge Code</p>
                <p className="text-xl font-mono font-bold text-blue-600">
                  {createdChallenge.challenge_code}
                </p>
              </div>
            )}
            <p className="text-sm text-gray-500">
              Redirecting to challenge details...
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div className="space-y-6">
        {/* Server error */}
        {submitError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{submitError}</AlertDescription>
          </Alert>
        )}

        {/* Basic Information */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>
              Provide a clear title and detailed description of the societal challenge
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title" required>
                Challenge Title
              </Label>
              <Input
                id="title"
                name="title"
                type="text"
                placeholder="e.g., Poor road conditions affecting village connectivity"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value)
                  clearFieldError('title')
                }}
                disabled={isSubmitting}
                required
                aria-invalid={!!validationErrors.title}
                aria-describedby={validationErrors.title ? 'title-error' : undefined}
              />
              {validationErrors.title && (
                <FormError id="title-error" message={validationErrors.title} />
              )}
              <p className="text-xs text-gray-500">
                {title.length}/500 characters (minimum 10)
              </p>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description" required>
                Detailed Description
              </Label>
              <Textarea
                id="description"
                name="description"
                placeholder="Describe the challenge in detail: what is the problem, who is affected, what is the current situation, and why it needs to be addressed..."
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value)
                  clearFieldError('description')
                }}
                disabled={isSubmitting}
                required
                rows={6}
                aria-invalid={!!validationErrors.description}
                aria-describedby={validationErrors.description ? 'description-error' : undefined}
              />
              {validationErrors.description && (
                <FormError id="description-error" message={validationErrors.description} />
              )}
              <p className="text-xs text-gray-500">
                {description.length}/5000 characters (minimum 30)
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Categories */}
        <Card>
          <CardHeader>
            <CardTitle>Categories</CardTitle>
            <CardDescription>
              Select one or more categories that best describe this challenge
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CategorySelect
              selectedCategories={selectedCategories}
              onChange={(categories) => {
                setSelectedCategories(categories)
                clearFieldError('category_ids')
              }}
              error={validationErrors.category_ids}
              disabled={isSubmitting}
              required
            />
          </CardContent>
        </Card>

        {/* Location */}
        <Card>
          <CardHeader>
            <CardTitle>Location</CardTitle>
            <CardDescription>
              Specify where this challenge is located in Jharkhand
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* District */}
            <div className="space-y-2">
              <Label htmlFor="district" required>
                District
              </Label>
              <select
                id="district"
                name="district"
                value={district}
                onChange={(e) => {
                  setDistrict(e.target.value)
                  clearFieldError('district')
                }}
                disabled={isSubmitting}
                required
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                aria-invalid={!!validationErrors.district}
                aria-describedby={validationErrors.district ? 'district-error' : undefined}
              >
                <option value="">Select district</option>
                {JHARKHAND_DISTRICTS.map((dist) => (
                  <option key={dist} value={dist}>
                    {dist}
                  </option>
                ))}
              </select>
              {validationErrors.district && (
                <FormError id="district-error" message={validationErrors.district} />
              )}
            </div>

            {/* Block */}
            <div className="space-y-2">
              <Label htmlFor="block">
                Block <span className="text-gray-500 text-sm">(optional)</span>
              </Label>
              <Input
                id="block"
                name="block"
                type="text"
                placeholder="Enter block name"
                value={block}
                onChange={(e) => {
                  setBlock(e.target.value)
                  clearFieldError('block')
                }}
                disabled={isSubmitting}
                aria-invalid={!!validationErrors.block}
                aria-describedby={validationErrors.block ? 'block-error' : undefined}
              />
              {validationErrors.block && (
                <FormError id="block-error" message={validationErrors.block} />
              )}
            </div>

            {/* Village */}
            <div className="space-y-2">
              <Label htmlFor="village">
                Village <span className="text-gray-500 text-sm">(optional)</span>
              </Label>
              <Input
                id="village"
                name="village"
                type="text"
                placeholder="Enter village name"
                value={village}
                onChange={(e) => {
                  setVillage(e.target.value)
                  clearFieldError('village')
                }}
                disabled={isSubmitting}
                aria-invalid={!!validationErrors.village}
                aria-describedby={validationErrors.village ? 'village-error' : undefined}
              />
              {validationErrors.village && (
                <FormError id="village-error" message={validationErrors.village} />
              )}
            </div>

            {/* GPS Coordinates */}
            <LocationPicker
              latitude={latitude}
              longitude={longitude}
              onLocationChange={handleLocationChange}
              latitudeError={validationErrors.latitude}
              longitudeError={validationErrors.longitude}
              disabled={isSubmitting}
            />

            {/* Affected Population */}
            <div className="space-y-2">
              <Label htmlFor="affectedPopulation">
                Estimated Affected Population <span className="text-gray-500 text-sm">(optional)</span>
              </Label>
              <Input
                id="affectedPopulation"
                name="affectedPopulation"
                type="number"
                min="0"
                max="10000000"
                placeholder="e.g., 5000"
                value={affectedPopulation}
                onChange={(e) => {
                  setAffectedPopulation(e.target.value)
                  clearFieldError('affected_population')
                }}
                disabled={isSubmitting}
                aria-invalid={!!validationErrors.affected_population}
                aria-describedby={
                  validationErrors.affected_population ? 'affected-population-error' : undefined
                }
              />
              {validationErrors.affected_population && (
                <FormError
                  id="affected-population-error"
                  message={validationErrors.affected_population}
                />
              )}
              <p className="text-xs text-gray-500">
                Approximate number of people affected by this challenge
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Media Upload */}
        <Card>
          <CardHeader>
            <CardTitle>
              Evidence & Media <span className="text-gray-500 text-sm font-normal">(optional)</span>
            </CardTitle>
            <CardDescription>
              Upload photos, videos, or documents that help illustrate the challenge (maximum 5 files)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <MediaUpload
              files={selectedFiles}
              onChange={setSelectedFiles}
              disabled={isSubmitting}
            />
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex gap-4">
          <Button
            type="submit"
            disabled={isSubmitting}
            className="flex-1"
          >
            {isSubmitting ? (
              <ButtonLoading />
            ) : mode === 'create' ? (
              'Submit Challenge'
            ) : (
              'Save Changes'
            )}
          </Button>

          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}
        </div>
      </div>
    </form>
  )
}
