/**
 * Tests for Registration Page
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import RegisterPage from '@/app/auth/register/page'
import { useAuth } from '@/lib/auth/AuthContext'
import { UserRole } from '@/types/api'
import type { AuthContextType } from '@/lib/auth/AuthContext'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock AuthContext
jest.mock('@/lib/auth/AuthContext', () => ({
  useAuth: jest.fn(),
}))

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Eye: () => <div data-testid="eye-icon">Eye</div>,
  EyeOff: () => <div data-testid="eyeoff-icon">EyeOff</div>,
  CheckCircle2: () => <div data-testid="check-icon">Check</div>,
  XCircle: () => <div data-testid="x-icon">X</div>,
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

describe('RegisterPage', () => {
  const mockRegister = jest.fn()
  const mockClearError = jest.fn()

  const defaultAuthContext: Partial<AuthContextType> = {
    register: mockRegister,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    clearError: mockClearError,
    user: null,
    login: jest.fn(),
    logout: jest.fn(),
    refreshUser: jest.fn(),
    hasRole: jest.fn(),
    hasAnyRole: jest.fn(),
    hasAllRoles: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useAuth as jest.Mock).mockReturnValue(defaultAuthContext)
  })

  describe('Page Rendering', () => {
    it('should render registration page with all elements', () => {
      render(<RegisterPage />)

      expect(screen.getByText('Create Citizen Account')).toBeInTheDocument()
      expect(screen.getByText(/register to submit challenges/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/phone number/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/create a strong password/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
    })

    it('should display role restriction notice', () => {
      render(<RegisterPage />)

      expect(screen.getByText('Citizen Registration')).toBeInTheDocument()
      expect(screen.getByText(/this form is for citizen accounts only/i)).toBeInTheDocument()
      expect(screen.getByText(/government officers.*must contact.*platform admin/i)).toBeInTheDocument()
    })

    it('should show link to login page', () => {
      render(<RegisterPage />)

      const loginLink = screen.getByText(/sign in/i)
      expect(loginLink).toBeInTheDocument()
      expect(loginLink.closest('a')).toHaveAttribute('href', '/auth/login')
    })

    it('should show loading spinner when auth is loading', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isLoading: true,
      })

      render(<RegisterPage />)

      expect(screen.queryByText('Create Citizen Account')).not.toBeInTheDocument()
    })

    it('should not render form when authenticated', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        isLoading: false,
      })

      const { container } = render(<RegisterPage />)

      expect(container.firstChild).toBeNull()
    })
  })

  describe('Form Fields', () => {
    it('should allow typing in all fields', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement
      const phoneInput = screen.getByLabelText(/phone number/i) as HTMLInputElement
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i) as HTMLInputElement
      const confirmInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(phoneInput, '+91 1234567890')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')

      expect(nameInput.value).toBe('Test User')
      expect(emailInput.value).toBe('test@example.com')
      expect(phoneInput.value).toBe('+91 1234567890')
      expect(passwordInput.value).toBe('Password123!')
      expect(confirmInput.value).toBe('Password123!')
    })

    it('should indicate phone field is optional', () => {
      render(<RegisterPage />)

      const phoneLabel = screen.getByText(/phone number/i)
      expect(phoneLabel).toHaveTextContent('(optional)')
    })

    it('should toggle password visibility', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const passwordInput = screen.getByPlaceholderText(/create a strong password/i) as HTMLInputElement
      const toggleButtons = screen.getAllByLabelText(/show password/i)

      expect(passwordInput.type).toBe('password')

      await user.click(toggleButtons[0])
      expect(passwordInput.type).toBe('text')

      await user.click(toggleButtons[0])
      expect(passwordInput.type).toBe('password')
    })

    it('should toggle confirm password visibility', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const confirmInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement
      const toggleButtons = screen.getAllByLabelText(/show password/i)

      expect(confirmInput.type).toBe('password')

      await user.click(toggleButtons[1])
      expect(confirmInput.type).toBe('text')
    })
  })

  describe('Password Validation', () => {
    it('should show password requirements when typing', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)

      // Requirements should not be visible initially
      expect(screen.queryByText(/at least 8 characters/i)).not.toBeInTheDocument()

      // Type in password field
      await user.type(passwordInput, 'P')

      // Requirements should now be visible
      await waitFor(() => {
        expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument()
        expect(screen.getByText(/one uppercase letter/i)).toBeInTheDocument()
        expect(screen.getByText(/one lowercase letter/i)).toBeInTheDocument()
        expect(screen.getAllByText(/one number/i)[0]).toBeInTheDocument()
        expect(screen.getByText(/one special character/i)).toBeInTheDocument()
      })
    })

    it('should update password requirements as user types', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)

      await user.type(passwordInput, 'Pass')

      await waitFor(() => {
        expect(screen.getByText(/one uppercase letter/i)).toBeInTheDocument()
      })

      // Add more characters to meet requirements
      await user.clear(passwordInput)
      await user.type(passwordInput, 'Password123!')

      // All requirements should be met
      await waitFor(() => {
        const requirements = screen.getByText(/at least 8 characters/i).closest('div')
        expect(requirements).toBeInTheDocument()
      })
    })

    it('should disable submit button when password is invalid', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(passwordInput, 'weak')

      expect(submitButton).toBeDisabled()
    })

    it('should enable submit button when password is valid', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(passwordInput, 'Password123!')

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })
  })

  describe('Client-side Validation', () => {
    it('should validate required name field', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const submitButton = screen.getByRole('button', { name: /create account/i })
      
      // Enable button by entering valid password
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      await user.type(passwordInput, 'Password123!')

      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument()
      })

      expect(mockRegister).not.toHaveBeenCalled()
    })

    it('should validate name minimum length', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'A')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/name must be at least 2 characters/i)).toBeInTheDocument()
      })
    })

    it('should validate email format', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(emailInput, 'invalid-email')
      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument()
      })
    })

    it('should validate phone format when provided', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const phoneInput = screen.getByLabelText(/phone number/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(phoneInput, 'invalid-phone-ABC')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid phone number/i)).toBeInTheDocument()
      })
    })

    it('should validate password confirmation matches', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Different123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
      })
    })

    it('should clear validation errors when user starts typing', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(passwordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument()
      })

      await user.type(nameInput, 'T')

      await waitFor(() => {
        expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
      })
    })
  })

  describe('Registration Submission', () => {
    it('should call register with CITIZEN role', async () => {
      const user = userEvent.setup()
      mockRegister.mockResolvedValue(undefined)

      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          name: 'Test User',
          email: 'test@example.com',
          phone: undefined,
          password: 'Password123!',
          role: UserRole.CITIZEN,
        })
      })
    })

    it('should include phone number when provided', async () => {
      const user = userEvent.setup()
      mockRegister.mockResolvedValue(undefined)

      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const phoneInput = screen.getByLabelText(/phone number/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(phoneInput, '+91 1234567890')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          name: 'Test User',
          email: 'test@example.com',
          phone: '+91 1234567890',
          password: 'Password123!',
          role: UserRole.CITIZEN,
        })
      })
    })

    it('should trim whitespace from name and email', async () => {
      const user = userEvent.setup()
      mockRegister.mockResolvedValue(undefined)

      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, '  Test User  ')
      await user.type(emailInput, '  test@example.com  ')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          name: 'Test User',
          email: 'test@example.com',
          phone: undefined,
          password: 'Password123!',
          role: UserRole.CITIZEN,
        })
      })
    })

    it('should show loading state during submission', async () => {
      const user = userEvent.setup()
      let resolveRegister: any
      mockRegister.mockImplementation(() => new Promise(resolve => { resolveRegister = resolve }))

      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(submitButton).toBeDisabled()
      })

      resolveRegister()
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })

    it('should disable form fields during submission', async () => {
      const user = userEvent.setup()
      let resolveRegister: any
      mockRegister.mockImplementation(() => new Promise(resolve => { resolveRegister = resolve }))

      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i) as HTMLInputElement
      const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'test@example.com')
      await user.type(screen.getByPlaceholderText(/create a strong password/i), 'Password123!')
      await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(nameInput).toBeDisabled()
        expect(emailInput).toBeDisabled()
      })

      resolveRegister()
      await waitFor(() => {
        expect(nameInput).not.toBeDisabled()
      })
    })
  })

  describe('Error Handling', () => {
    it('should display server error from AuthContext', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        error: 'Email already exists',
      })

      render(<RegisterPage />)

      expect(screen.getByText('Email already exists')).toBeInTheDocument()
    })

    it('should handle duplicate email error', async () => {
      const user = userEvent.setup()
      const errorMessage = 'Email already exists'
      mockRegister.mockRejectedValue(new Error(errorMessage))

      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        error: errorMessage,
      })

      render(<RegisterPage />)

      const nameInput = screen.getByLabelText(/full name/i)
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      const confirmInput = screen.getByLabelText(/confirm password/i)
      const submitButton = screen.getByRole('button', { name: /create account/i })

      await user.type(nameInput, 'Test User')
      await user.type(emailInput, 'existing@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })
  })

  describe('Navigation', () => {
    it('should redirect authenticated users to dashboard', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        isLoading: false,
      })

      render(<RegisterPage />)

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard')
    })
  })

  describe('Role Safety', () => {
    it('should only register with CITIZEN role', async () => {
      const user = userEvent.setup()
      mockRegister.mockResolvedValue(undefined)

      render(<RegisterPage />)

      // Fill form
      await user.type(screen.getByLabelText(/full name/i), 'Test User')
      await user.type(screen.getByLabelText(/email/i), 'test@example.com')
      await user.type(screen.getByPlaceholderText(/create a strong password/i), 'Password123!')
      await user.type(screen.getByLabelText(/confirm password/i), 'Password123!')
      await user.click(screen.getByRole('button', { name: /create account/i }))

      // Should only call with CITIZEN role
      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith(
          expect.objectContaining({
            role: UserRole.CITIZEN,
          })
        )
      })

      // Should NOT be called with privileged roles
      expect(mockRegister).not.toHaveBeenCalledWith(
        expect.objectContaining({
          role: UserRole.GOVERNMENT_OFFICER,
        })
      )
      expect(mockRegister).not.toHaveBeenCalledWith(
        expect.objectContaining({
          role: UserRole.PLATFORM_ADMIN,
        })
      )
      expect(mockRegister).not.toHaveBeenCalledWith(
        expect.objectContaining({
          role: UserRole.UNIVERSITY_ADMIN,
        })
      )
    })

    it('should not have role selection dropdown', () => {
      render(<RegisterPage />)

      // Should not find any role selection UI elements (dropdowns, radios, checkboxes)
      expect(screen.queryByLabelText(/role/i)).not.toBeInTheDocument()
      expect(screen.queryByLabelText(/select.*role/i)).not.toBeInTheDocument()
      expect(screen.queryByRole('combobox', { name: /role/i })).not.toBeInTheDocument()
      expect(screen.queryByRole('radio', { name: /government officer/i })).not.toBeInTheDocument()
      expect(screen.queryByRole('radio', { name: /platform admin/i })).not.toBeInTheDocument()
      
      // But should show informational text about role restrictions
      expect(screen.getByText(/this form is for citizen accounts only/i)).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper labels for all form fields', () => {
      render(<RegisterPage />)

      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/phone number/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/create a strong password/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    })

    it('should indicate required fields', () => {
      render(<RegisterPage />)

      const nameLabel = screen.getByText(/full name/i).closest('label')
      const emailLabel = screen.getByText(/email/i).closest('label')
      const passwordLabel = screen.getAllByText(/^password$/i)[0].closest('label')

      expect(nameLabel).toHaveTextContent('*')
      expect(emailLabel).toHaveTextContent('*')
      expect(passwordLabel).toHaveTextContent('*')
    })

    it('should associate errors with inputs via aria-describedby', async () => {
      const user = userEvent.setup()
      render(<RegisterPage />)

      const passwordInput = screen.getByPlaceholderText(/create a strong password/i)
      await user.type(passwordInput, 'Password123!')

      const submitButton = screen.getByRole('button', { name: /create account/i })
      await user.click(submitButton)

      await waitFor(() => {
        const nameInput = screen.getByLabelText(/full name/i)
        expect(nameInput).toHaveAttribute('aria-invalid', 'true')
        expect(nameInput).toHaveAttribute('aria-describedby', 'name-error')
      })
    })
  })
})
