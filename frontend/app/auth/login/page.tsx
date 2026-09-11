'use client'

/**
 * Login Page
 * 
 * Provides authentication interface for all user types.
 * After successful login, redirects to appropriate dashboard based on role.
 */

import { useState, useEffect, FormEvent } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { FormError } from '@/components/ui/form-error'
import { ButtonLoading } from '@/components/ui/loading-spinner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { login, isAuthenticated, isLoading: authLoading, error: authError, clearError } = useAuth()

  // Form state
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [validationErrors, setValidationErrors] = useState<{
    email?: string
    password?: string
  }>({})

  // Get redirect destination from query params
  const redirectTo = searchParams.get('redirect') || '/dashboard'
  const message = searchParams.get('message')

  /**
   * Redirect authenticated users away from login page
   */
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      router.push(redirectTo)
    }
  }, [isAuthenticated, authLoading, router, redirectTo])

  /**
   * Clear auth error when component unmounts or user starts typing
   */
  useEffect(() => {
    return () => {
      clearError()
    }
  }, [clearError])

  /**
   * Client-side validation
   */
  const validateForm = (): boolean => {
    const errors: { email?: string; password?: string } = {}

    // Email validation
    if (!email.trim()) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Please enter a valid email address'
    }

    // Password validation
    if (!password) {
      errors.password = 'Password is required'
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Clear previous errors
    clearError()
    setValidationErrors({})

    // Validate form
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      await login({ email: email.trim(), password })
      
      // Success - redirect will happen via useEffect
      // No need to do anything here
    } catch (error: any) {
      // Error is already set in AuthContext
      console.error('Login failed:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * Clear validation error when user starts typing
   */
  const handleEmailChange = (value: string) => {
    setEmail(value)
    if (validationErrors.email) {
      setValidationErrors(prev => ({ ...prev, email: undefined }))
    }
    if (authError) {
      clearError()
    }
  }

  const handlePasswordChange = (value: string) => {
    setPassword(value)
    if (validationErrors.password) {
      setValidationErrors(prev => ({ ...prev, password: undefined }))
    }
    if (authError) {
      clearError()
    }
  }

  // Show loading state during initial auth check
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <ButtonLoading />
      </div>
    )
  }

  // Don't render form if already authenticated (will redirect)
  if (isAuthenticated) {
    return null
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Sign in to SamadhanX
          </CardTitle>
          <CardDescription className="text-center">
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>

        <CardContent>
          {/* Info message from query params */}
          {message && (
            <Alert className="mb-4">
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}

          {/* Server error */}
          {authError && (
            <FormError message={authError} className="mb-4" />
          )}

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {/* Email field */}
            <div className="space-y-2">
              <Label htmlFor="email" required>
                Email
              </Label>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                disabled={isSubmitting}
                required
                aria-invalid={!!validationErrors.email}
                aria-describedby={validationErrors.email ? 'email-error' : undefined}
              />
              {validationErrors.email && (
                <FormError id="email-error" message={validationErrors.email} />
              )}
            </div>

            {/* Password field */}
            <div className="space-y-2">
              <Label htmlFor="password" required>
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => handlePasswordChange(e.target.value)}
                  disabled={isSubmitting}
                  required
                  aria-invalid={!!validationErrors.password}
                  aria-describedby={validationErrors.password ? 'password-error' : undefined}
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              {validationErrors.password && (
                <FormError id="password-error" message={validationErrors.password} />
              )}
            </div>

            {/* Submit button */}
            <Button
              type="submit"
              className="w-full"
              disabled={isSubmitting}
            >
              {isSubmitting ? <ButtonLoading /> : 'Sign in'}
            </Button>
          </form>
        </CardContent>

        <CardFooter className="flex flex-col space-y-4">
          <div className="text-sm text-center text-gray-600">
            Don't have an account?{' '}
            <Link
              href="/auth/register"
              className="font-medium text-primary hover:underline"
            >
              Register as a citizen
            </Link>
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
