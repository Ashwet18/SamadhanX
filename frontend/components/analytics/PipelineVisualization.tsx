'use client'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { PipelineStage } from '@/types/analytics'

interface PipelineVisualizationProps {
  stages: PipelineStage[]
  totalProjects: number
}

const stageColors: Record<string, string> = {
  PLANNING: 'bg-gray-100 text-gray-800 border-gray-300',
  TEAM_FORMATION: 'bg-blue-100 text-blue-800 border-blue-300',
  PROPOSAL: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  APPROVED: 'bg-green-100 text-green-800 border-green-300',
  PROTOTYPE: 'bg-purple-100 text-purple-800 border-purple-300',
  TESTING: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  PILOT: 'bg-orange-100 text-orange-800 border-orange-300',
  DEPLOYED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  COMPLETED: 'bg-teal-100 text-teal-800 border-teal-300',
  ON_HOLD: 'bg-amber-100 text-amber-800 border-amber-300',
  CANCELLED: 'bg-red-100 text-red-800 border-red-300',
}

const stageTitles: Record<string, string> = {
  PLANNING: 'Planning',
  TEAM_FORMATION: 'Team Formation',
  PROPOSAL: 'Proposal',
  APPROVED: 'Approved',
  PROTOTYPE: 'Prototype',
  TESTING: 'Testing',
  PILOT: 'Pilot',
  DEPLOYED: 'Deployed',
  COMPLETED: 'Completed',
  ON_HOLD: 'On Hold',
  CANCELLED: 'Cancelled',
}

export function PipelineVisualization({ stages, totalProjects }: PipelineVisualizationProps) {
  // Sort stages by count descending
  const sortedStages = [...stages].sort((a, b) => b.count - a.count)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Project Pipeline</CardTitle>
        <CardDescription>
          Distribution of {totalProjects} projects across lifecycle stages
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sortedStages.map((stage) => {
            const colorClass = stageColors[stage.stage] || stageColors.PLANNING
            const stageTitle = stageTitles[stage.stage] || stage.stage

            return (
              <div key={stage.stage} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge className={cn('border', colorClass)}>
                      {stageTitle}
                    </Badge>
                    <span className="text-sm font-medium text-gray-700">
                      {stage.count} projects
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">
                    {stage.percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className={cn(
                      'h-2.5 rounded-full transition-all',
                      stage.stage === 'DEPLOYED' || stage.stage === 'COMPLETED'
                        ? 'bg-green-600'
                        : stage.stage === 'CANCELLED' || stage.stage === 'ON_HOLD'
                        ? 'bg-red-500'
                        : 'bg-blue-600'
                    )}
                    style={{ width: `${stage.percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {sortedStages.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No project data available
          </div>
        )}
      </CardContent>
    </Card>
  )
}
