/**
 * Citizen Layout
 * 
 * Protects all citizen routes - requires CITIZEN role
 */

import { RequireRole } from '@/components/auth/ProtectedRoute'
import { UserRole } from '@/types/api'

export default function CitizenLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <RequireRole roles={[UserRole.CITIZEN]}>
      {children}
    </RequireRole>
  )
}
