/**
 * ChallengeCard Component
 * 
 * Displays challenge information in a card format for list views
 */

import Link from 'next/link'
import { Calendar, MapPin, Users } from 'lucide-react'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ChallengeStatus } from './ChallengeStatus'
import type { ChallengeListItem } from '@/lib/api/challenges'

interface ChallengeCardProps {
  challenge: ChallengeListItem
}

export function ChallengeCard({ challenge }: ChallengeCardProps) {
  const formattedDate = new Date(challenge.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-sm font-mono text-gray-500">
                {challenge.challenge_code}
              </span>
              <ChallengeStatus status={challenge.status} />
              {challenge.priority_level && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  challenge.priority_level === 'CRITICAL'
                    ? 'bg-red-100 text-red-700'
                    : challenge.priority_level === 'HIGH'
                    ? 'bg-orange-100 text-orange-700'
                    : challenge.priority_level === 'MEDIUM'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {challenge.priority_level}
                </span>
              )}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
              {challenge.title}
            </h3>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Location */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <MapPin className="h-4 w-4 flex-shrink-0" />
          <span className="truncate">{challenge.district}</span>
        </div>

        {/* Date */}
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4 flex-shrink-0" />
          <span>Submitted on {formattedDate}</span>
        </div>

        {/* Affected Population */}
        {challenge.affected_population && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Users className="h-4 w-4 flex-shrink-0" />
            <span>{challenge.affected_population.toLocaleString()} people affected</span>
          </div>
        )}

        {/* Metadata */}
        <div className="flex gap-4 text-xs text-gray-500">
          <span>{challenge.category_count} {challenge.category_count === 1 ? 'category' : 'categories'}</span>
          <span>{challenge.media_count} {challenge.media_count === 1 ? 'file' : 'files'}</span>
        </div>
      </CardContent>

      <CardFooter>
        <Link href={`/citizen/challenges/${challenge.id}`} className="w-full">
          <Button variant="outline" className="w-full">
            View Details
          </Button>
        </Link>
      </CardFooter>
    </Card>
  )
}
