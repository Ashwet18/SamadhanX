/**
 * ChallengeStatus Component
 * 
 * Displays challenge status as a colored badge
 */

import { Badge } from '@/components/ui/badge'
import type { ChallengeStatus as StatusType } from '@/types/api'

interface ChallengeStatusProps {
  status: StatusType
  className?: string
}

const STATUS_CONFIG: Record<
  StatusType,
  { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }
> = {
  DRAFT: { label: 'Draft', variant: 'secondary' },
  SUBMITTED: { label: 'Submitted', variant: 'default' },
  AI_ANALYSIS: { label: 'Analyzing', variant: 'default' },
  PENDING_REVIEW: { label: 'Pending Review', variant: 'default' },
  VALIDATED: { label: 'Validated', variant: 'default' },
  MATCHING: { label: 'Matching Universities', variant: 'default' },
  UNIVERSITY_INVITED: { label: 'University Invited', variant: 'default' },
  ACCEPTED: { label: 'Accepted', variant: 'default' },
  PROJECT_CREATED: { label: 'Project Created', variant: 'default' },
  REJECTED: { label: 'Rejected', variant: 'destructive' },
  DUPLICATE: { label: 'Duplicate', variant: 'outline' },
  ON_HOLD: { label: 'On Hold', variant: 'outline' },
  CANCELLED: { label: 'Cancelled', variant: 'outline' },
}

export function ChallengeStatus({ status, className }: ChallengeStatusProps) {
  const config = STATUS_CONFIG[status] || { label: status, variant: 'default' as const }

  return (
    <Badge variant={config.variant} className={className}>
      {config.label}
    </Badge>
  )
}
