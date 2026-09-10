import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface RankingItem {
  rank?: number
  name: string
  value: number
  subtitle?: string
  badge?: string
}

interface RankingsTableProps {
  title: string
  description?: string
  items: RankingItem[]
  valueLabel?: string
  emptyMessage?: string
}

export function RankingsTable({
  title,
  description,
  items,
  valueLabel = 'Count',
  emptyMessage = 'No data available',
}: RankingsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {items.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="text-left py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="text-right py-3 px-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {valueLabel}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {items.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-2">
                      <div className="flex items-center">
                        <span className="text-sm font-semibold text-gray-900 w-8">
                          #{item.rank !== undefined ? item.rank : index + 1}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-2">
                      <div className="flex flex-col">
                        <span className="text-sm font-medium text-gray-900">
                          {item.name}
                        </span>
                        {item.subtitle && (
                          <span className="text-xs text-gray-500 mt-0.5">
                            {item.subtitle}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-2 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {item.badge && (
                          <Badge variant="secondary" className="text-xs">
                            {item.badge}
                          </Badge>
                        )}
                        <span className="text-sm font-semibold text-gray-900">
                          {item.value.toLocaleString()}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500 text-sm">
            {emptyMessage}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
