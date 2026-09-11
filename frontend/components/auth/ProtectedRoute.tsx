'use client'

/**
 * ProtectedRoute component
 * 
 * Wraps components/pages that require authentication or specific roles
 * Redirects to login if not authenticated
 * Shows access denied if authenticated but lacks required role
 */

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth/AuthContext'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireAuth?: boolean
  requiredRoles?: string[]
  requireAllRoles?: boolean // If true, user must have ALL roles; if false, ANY role
  fallback?: React.ReactNode
}

export function ProtectedRoute({
  children,
  requireAuth = true,
  requiredRoles = [],
  requireAllRoles = false,
  fallback = null,
}: ProtectedRouteProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, isLoading, user, hasAnyRole, hasAllRoles } = useAuth()

  useEffect(() => {
    // Wait for auth state to load
    if (isLoading) {
      return
    }

    // Check authentication requirement
    if (requireAuth && !isAuthenticated) {
      // Redirect to login, storing intended destination
      const returnUrl = encodeURIComponent(pathname)
      router.push(`/auth/login?returnUrl=${returnUrl}`)
      return
    }

    // Check role requirements if specified
    if (isAuthenticated && requiredRoles.length > 0) {
      const hasRequiredRoles = requireAllRoles
        ? hasAllRoles(requiredRoles)
        : hasAnyRole(requiredRoles)

      if (!hasRequiredRoles) {
        // User is authenticated but doesn't have required role
        router.push('/unauthorized')
        return
      }
    }
  }, [
    isLoading,
    isAuthenticated,
    requireAuth,
    requiredRoles,
    requireAllRoles,
    hasAnyRole,
    hasAllRoles,
    pathname,
    router,
  ])

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // If not authenticated and auth is required, show fallback or nothing (will redirect)
  if (requireAuth && !isAuthenticated) {
    return <>{fallback}</>
  }

  // If authenticated but lacks required role, show fallback or nothing (will redirect)
  if (isAuthenticated && requiredRoles.length > 0) {
    const hasRequiredRoles = requireAllRoles
      ? hasAllRoles(requiredRoles)
      : hasAnyRole(requiredRoles)

    if (!hasRequiredRoles) {
      return <>{fallback}</>
    }
  }

  // All checks passed, render children
  return <>{children}</>
}

/**
 * RequireAuth - Convenience wrapper for authentication-only protection
 */
export function RequireAuth({ children }: { children: React.ReactNode }) {
  return <ProtectedRoute requireAuth={true}>{children}</ProtectedRoute>
}

/**
 * RequireRole - Convenience wrapper for role-based protection
 */
export function RequireRole({
  children,
  roles,
  requireAll = false,
}: {
  children: React.ReactNode
  roles: string[]
  requireAll?: boolean
}) {
  return (
    <ProtectedRoute
      requireAuth={true}
      requiredRoles={roles}
      requireAllRoles={requireAll}
    >
      {children}
    </ProtectedRoute>
  )
}
