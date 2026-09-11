/**
 * Tests for Login Page
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter, useSearchParams } from 'next/navigation'
import LoginPage from '@/app/auth/login/page'
import { useAuth } from '@/lib/auth/AuthContext'
import type { AuthContextType } from '@/lib/auth/AuthContext'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))

// Mock AuthContext
jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: jest.fn(),
}))

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Eye: () => <div data-testid="eye-icon">Eye</div>,
  EyeOff: () => <div data-testid="eyeoff-icon">EyeOff</div>,
  AlertCircle: () => <div data-testid="alert-circle">AlertCircle</div>,
  CheckCircle: () => <div data-testid="check-circle">CheckCircle</div>,
  Info: () => <div data-testid="info">Info</div>,
  AlertTriangle: () => <div data-testid="alert-triangle">AlertTriangle</div>,
  X: () => <div data-testid="x">X</div>,
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
}

const mockSearchParams = {
  get: jest.fn(),
}

describe('LoginPage', () => {
  const mockLogin = jest.fn()
  const mockClearError = jest.fn()

  const defaultAuthContext: Partial<AuthContextType> = {
    login: mockLogin,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    clearError: mockClearError,
    user: null,
    register: jest.fn(),
    logout: jest.fn(),
    refreshUser: jest.fn(),
    hasRole: jest.fn(),
    hasAnyRole: jest.fn(),
    hasAllRoles: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useSearchParams as jest.Mock).mockReturnValue(mockSearchParams)
    ;(useAuth as jest.Mock).mockReturnValue(defaultAuthContext)
    mockSearchParams.get.mockReturnValue(null)
  })

  describe('Page Rendering', () => {
    it('should render login page with all elements', () => {
      render(<LoginPage />)

      expect(screen.getByText('Sign in to SamadhanX')).toBeInTheDocument()
      expect(screen.getByText('Enter your credentials to access your account')).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument()
      expect(screen.getByText(/register as a citizen/i)).toBeInTheDocument()
    })

    it('should render message from query params', () => {
      mockSearchParams.get.mockImplementation((key: string) => {
        if (key === 'message') return 'Please login to continue'
        return null
      })

      render(<LoginPage />)

      expect(screen.getByText('Please login to continue')).toBeInTheDocument()
    })

    it('should show loading spinner when auth is loading', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isLoading: true,
      })

      render(<LoginPage />)

      // Should not render the form
      expect(screen.queryByText('Sign in to SamadhanX')).not.toBeInTheDocument()
    })

    it('should not render form when authenticated', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        isLoading: false,
      })

      const { container } = render(<LoginPage />)

      // Should render nothing (redirect will happen)
      expect(container.firstChild).toBeNull()
    })
  })

  describe('Form Fields', () => {
    it('should allow typing in email field', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement
      await user.type(emailInput, 'test@example.com')

      expect(emailInput.value).toBe('test@example.com')
    })

    it('should allow typing in password field', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement
      await user.type(passwordInput, 'Password123!')

      expect(passwordInput.value).toBe('Password123!')
    })

    it('should toggle password visibility', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement
      const toggleButton = screen.getByLabelText(/show password/i)

      // Initially password type
      expect(passwordInput.type).toBe('password')

      // Click to show
      await user.click(toggleButton)
      expect(passwordInput.type).toBe('text')

      // Click to hide
      await user.click(toggleButton)
      expect(passwordInput.type).toBe('password')
    })
  })

  describe('Client-side Validation', () => {
    it('should show error when email is empty', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('should show error when email is invalid', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'invalid-email')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('should show error when password is empty', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Password is required')).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('should show error when password is too short', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'short')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument()
      })

      expect(mockLogin).not.toHaveBeenCalled()
    })

    it('should clear validation errors when user starts typing', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      // Trigger validation error
      await user.click(submitButton)
      await waitFor(() => {
        expect(screen.getByText('Email is required')).toBeInTheDocument()
      })

      // Start typing
      await user.type(emailInput, 't')

      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText('Email is required')).not.toBeInTheDocument()
      })
    })
  })

  describe('Login Submission', () => {
    it('should call login with correct credentials', async () => {
      const user = userEvent.setup()
      mockLogin.mockResolvedValue(undefined)

      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'Password123!',
        })
      })
    })

    it('should trim email before submitting', async () => {
      const user = userEvent.setup()
      mockLogin.mockResolvedValue(undefined)

      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, '  test@example.com  ')
      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'Password123!',
        })
      })
    })

    it('should show loading state during submission', async () => {
      const user = userEvent.setup()
      let resolveLogin: any
      mockLogin.mockImplementation(() => new Promise(resolve => { resolveLogin = resolve }))

      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      // Should show loading state
      await waitFor(() => {
        expect(submitButton).toBeDisabled()
      })

      // Resolve login
      resolveLogin()
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })

    it('should disable form fields during submission', async () => {
      const user = userEvent.setup()
      let resolveLogin: any
      mockLogin.mockImplementation(() => new Promise(resolve => { resolveLogin = resolve }))

      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement
      const passwordInput = screen.getByPlaceholderText(/enter your password/i) as HTMLInputElement
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      // Fields should be disabled
      await waitFor(() => {
        expect(emailInput).toBeDisabled()
        expect(passwordInput).toBeDisabled()
      })

      // Resolve login
      resolveLogin()
      await waitFor(() => {
        expect(emailInput).not.toBeDisabled()
        expect(passwordInput).not.toBeDisabled()
      })
    })
  })

  describe('Error Handling', () => {
    it('should display server error from AuthContext', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        error: 'Invalid credentials',
      })

      render(<LoginPage />)

      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })

    it('should handle login failure', async () => {
      const user = userEvent.setup()
      const errorMessage = 'Incorrect email or password'
      mockLogin.mockRejectedValue(new Error(errorMessage))

      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        error: errorMessage,
      })

      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'WrongPassword123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('should handle network error', async () => {
      const user = userEvent.setup()
      const errorMessage = 'Network error. Please check your connection.'
      mockLogin.mockRejectedValue(new Error('Network Error'))

      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        error: errorMessage,
      })

      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('should clear error when user starts typing', async () => {
      const user = userEvent.setup()
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        error: 'Invalid credentials',
      })

      render(<LoginPage />)

      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()

      const emailInput = screen.getByLabelText(/email/i)
      await user.type(emailInput, 'a')

      expect(mockClearError).toHaveBeenCalled()
    })
  })

  describe('Navigation', () => {
    it('should have link to registration page', () => {
      render(<LoginPage />)

      const registerLink = screen.getByText(/register as a citizen/i)
      expect(registerLink).toBeInTheDocument()
      expect(registerLink.closest('a')).toHaveAttribute('href', '/auth/register')
    })

    it('should redirect authenticated users', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        isLoading: false,
      })

      render(<LoginPage />)

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard')
    })

    it('should redirect to custom URL from query params', () => {
      mockSearchParams.get.mockImplementation((key: string) => {
        if (key === 'redirect') return '/analytics'
        return null
      })

      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        isLoading: false,
      })

      render(<LoginPage />)

      expect(mockRouter.push).toHaveBeenCalledWith('/analytics')
    })
  })

  describe('Accessibility', () => {
    it('should have proper labels for form fields', () => {
      render(<LoginPage />)

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
    })

    it('should have required indicators', () => {
      render(<LoginPage />)

      const emailLabel = screen.getByText(/email/i).closest('label')
      const passwordLabel = screen.getByText(/^password$/i).closest('label')

      expect(emailLabel).toHaveTextContent('*')
      expect(passwordLabel).toHaveTextContent('*')
    })

    it('should associate errors with inputs via aria-describedby', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)

      await waitFor(() => {
        const emailInput = screen.getByLabelText(/email/i)
        expect(emailInput).toHaveAttribute('aria-invalid', 'true')
        expect(emailInput).toHaveAttribute('aria-describedby', 'email-error')
      })
    })

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })

      // Tab through form
      await user.tab()
      expect(emailInput).toHaveFocus()

      await user.tab()
      expect(passwordInput).toHaveFocus()
    })
  })
})
