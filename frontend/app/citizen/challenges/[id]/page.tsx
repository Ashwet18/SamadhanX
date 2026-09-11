'use client'

/**
 * Challenge Detail Page
 * 
 * Displays full details of a challenge with edit/delete actions
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import {
  ArrowLeft,
  Calendar,
  MapPin,
  Users,
  Edit,
  Trash2,
  Loader2,
  AlertCircle,
  FileText,
  Image as ImageIcon,
  Video,
  Music,
} from 'lucide-react'
import { useAuth } from '@/lib/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { ButtonLoading } from '@/components/ui/loading-spinner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { ChallengeStatus } from '@/components/challenges/ChallengeStatus'
import { challengeApi, type ChallengeMediaResponse } from '@/lib/api/challenges'
import type { Challenge } from '@/types/api'

interface Props {
  params: { id: string }
}

export default function ChallengeDetailPage({ params }: Props) {
  const router = useRouter()
  const { user } = useAuth()

  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [media, setMedia] = useState<ChallengeMediaResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    loadChallenge()
  }, [params.id])

  const loadChallenge = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const [challengeData, mediaData] = await Promise.all([
        challengeApi.getChallenge(params.id),
        challengeApi.getChallengeMedia(params.id),
      ])

      setChallenge(challengeData)
      setMedia(mediaData)
    } catch (err: any) {
      console.error('Failed to load challenge:', err)
      setError(err.response?.data?.detail || 'Challenge not found')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!challenge) return

    setIsDeleting(true)

    try {
      await challengeApi.deleteChallenge(challenge.id)
      router.push('/citizen/challenges')
    } catch (err: any) {
      console.error('Failed to delete challenge:', err)
      alert(err.response?.data?.detail || 'Failed to delete challenge')
    } finally {
      setIsDeleting(false)
      setShowDeleteConfirm(false)
    }
  }

  // Check if user can edit/delete
  const canEdit = challenge && (
    challenge.status === 'DRAFT' || challenge.status === 'SUBMITTED'
  ) && challenge.submitted_by === user?.id

  const canDelete = challenge &&
    challenge.status === 'DRAFT' &&
    challenge.submitted_by === user?.id

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
        <Link href="/citizen/challenges">
          <Button variant="outline" className="mt-4 gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to My Challenges
          </Button>
        </Link>
      </div>
    )
  }

  const formattedDate = new Date(challenge.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-4 gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>

        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-sm font-mono text-gray-500">
                {challenge.challenge_code}
              </span>
              <ChallengeStatus status={challenge.status} />
              {challenge.priority_level && (
                <Badge variant="outline">{challenge.priority_level}</Badge>
              )}
            </div>
            <h1 className="text-3xl font-bold text-gray-900">
              {challenge.title}
            </h1>
          </div>

          {/* Actions */}
          {(canEdit || canDelete) && (
            <div className="flex gap-2">
              {canEdit && (
                <Link href={`/citizen/challenges/${challenge.id}/edit`}>
                  <Button variant="outline" size="sm" className="gap-2">
                    <Edit className="h-4 w-4" />
                    Edit
                  </Button>
                </Link>
              )}
              {canDelete && (
                <Button
                  variant="destructive"
                  size="sm"
                  className="gap-2"
                  onClick={() => setShowDeleteConfirm(true)}
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>
            <p className="font-medium mb-2">Are you sure you want to delete this challenge?</p>
            <p className="text-sm mb-4">This action cannot be undone.</p>
            <div className="flex gap-2">
              <Button
                variant="destructive"
                size="sm"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? <ButtonLoading /> : 'Delete Challenge'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>Submitted on {formattedDate}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <MapPin className="h-4 w-4" />
          <span>{challenge.district}</span>
        </div>
        {challenge.affected_population && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Users className="h-4 w-4" />
            <span>{challenge.affected_population.toLocaleString()} affected</span>
          </div>
        )}
      </div>

      {/* Description */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Description</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-700 whitespace-pre-wrap">{challenge.description}</p>
        </CardContent>
      </Card>

      {/* Categories */}
      {challenge.categories && challenge.categories.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Categories</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {challenge.categories.map((category) => (
                <Badge key={category.id} variant="secondary">
                  {category.name}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Location Details */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Location</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">District</p>
              <p className="font-medium">{challenge.district}</p>
            </div>
            {challenge.block && (
              <div>
                <p className="text-sm text-gray-600">Block</p>
                <p className="font-medium">{challenge.block}</p>
              </div>
            )}
            {challenge.village && (
              <div>
                <p className="text-sm text-gray-600">Village</p>
                <p className="font-medium">{challenge.village}</p>
              </div>
            )}
          </div>
          {challenge.latitude && challenge.longitude && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600 mb-2">GPS Coordinates</p>
              <p className="font-mono text-sm">
                {challenge.latitude.toFixed(6)}, {challenge.longitude.toFixed(6)}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Media */}
      {media.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Media & Evidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {media.map((file) => (
                <MediaPreview key={file.id} media={file} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

/**
 * Media Preview Component
 */
function MediaPreview({ media }: { media: ChallengeMediaResponse }) {
  const getIcon = () => {
    switch (media.media_type) {
      case 'IMAGE':
        return <ImageIcon className="h-8 w-8" />
      case 'VIDEO':
        return <Video className="h-8 w-8" />
      case 'AUDIO':
        return <Music className="h-8 w-8" />
      default:
        return <FileText className="h-8 w-8" />
    }
  }

  const formatSize = (bytes?: number) => {
    if (!bytes) return 'Unknown size'
    const kb = bytes / 1024
    const mb = kb / 1024
    return mb > 1 ? `${mb.toFixed(2)} MB` : `${kb.toFixed(2)} KB`
  }

  return (
    <a
      href={media.file_url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
    >
      <div className="flex-shrink-0 text-gray-400">
        {getIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {media.file_name}
        </p>
        <p className="text-xs text-gray-500">
          {formatSize(media.file_size)}
        </p>
      </div>
    </a>
  )
}
