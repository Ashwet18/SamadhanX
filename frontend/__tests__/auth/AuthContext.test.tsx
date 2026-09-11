/**
 * Tests for AuthContext and AuthProvider
 */

import { renderHook, act, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/lib/auth/AuthContext'
import * as authApi from '@/lib/api/auth'
import * as tokenUtils from '@/lib/auth/token'
import { UserRole } from '@/types/api'

// Mock dependencies
jest.mock('@/lib/api/auth')
jest.mock('@/lib/auth/token')
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
  usePathname: () => '/',
}))

const mockedAuthApi = authApi as jest.Mocked<typeof authApi>
const mockedTokenUtils = tokenUtils as jest.Mocked<typeof tokenUtils>

// Mock user data
const mockUser = {
  id: '123',
  name: 'Test User',
  email: 'test@example.com',
  phone: '1234567890',
  account_status: 'ACTIVE' as const,
  roles: [UserRole.CITIZEN],
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  is_citizen: true,
  is_government_officer: false,
  is_faculty: false,
  is_student: false,
}

const mockLoginResponse = {
  access_token: 'mock-token',
  token_type: 'bearer',
  user: mockUser,
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockedTokenUtils.getAccessToken.mockReturnValue(null)
    mockedTokenUtils.getUserProfile.mockReturnValue(null)
  })

  describe('Initial State', () => {
    it('should start with loading state', async () => {
      // Mock no token to prevent useEffect from running immediately
      mockedTokenUtils.getAccessToken.mockReturnValue(null)
      
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      // Initial state before useEffect completes
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })

    it('should set loading to false when no token exists', async () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })
  })

  describe('Session Restoration', () => {
    it('should restore session from cached user profile', async () => {
      mockedTokenUtils.getAccessToken.mockReturnValue('mock-token')
      mockedTokenUtils.getUserProfile.mockReturnValue(mockUser)
      mockedAuthApi.getCurrentUser.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual(mockUser)
    })

    it('should clear auth data if token validation fails', async () => {
      mockedTokenUtils.getAccessToken.mockReturnValue('invalid-token')
      mockedTokenUtils.getUserProfile.mockReturnValue(mockUser)
      mockedAuthApi.getCurrentUser.mockRejectedValue(new Error('Invalid token'))

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
      expect(mockedTokenUtils.clearAuthData).toHaveBeenCalled()
    })
  })

  describe('Login', () => {
    it('should login successfully and store token', async () => {
      mockedAuthApi.login.mockResolvedValue(mockLoginResponse)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      await act(async () => {
        await result.current.login({
          email: 'test@example.com',
          password: 'password123',
        })
      })

      expect(mockedAuthApi.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
      expect(mockedTokenUtils.setAccessToken).toHaveBeenCalledWith('mock-token')
      expect(mockedTokenUtils.setUserProfile).toHaveBeenCalledWith(mockUser)
      expect(result.current.isAuthenticated).toBe(true)
      expect(result.current.user).toEqual(mockUser)
    })

    it('should handle login failure', async () => {
      const errorResponse = {
        response: {
          data: {
            message: 'Invalid credentials',
          },
        },
      }
      mockedAuthApi.login.mockRejectedValue(errorResponse)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let loginError: any
      await act(async () => {
        try {
          await result.current.login({
            email: 'test@example.com',
            password: 'wrong',
          })
        } catch (error) {
          loginError = error
        }
      })

      expect(loginError).toEqual(errorResponse)
      
      await waitFor(() => {
        expect(result.current.error).toBe('Invalid credentials')
      })
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  describe('Register', () => {
    it('should register and automatically login', async () => {
      mockedAuthApi.register.mockResolvedValue(mockUser)
      mockedAuthApi.login.mockResolvedValue(mockLoginResponse)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      const registerData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'Password123!',
        role: UserRole.CITIZEN,
      }

      await act(async () => {
        await result.current.register(registerData)
      })

      expect(mockedAuthApi.register).toHaveBeenCalledWith(registerData)
      expect(mockedAuthApi.login).toHaveBeenCalledWith({
        email: registerData.email,
        password: registerData.password,
      })
      expect(result.current.isAuthenticated).toBe(true)
    })

    it('should handle registration failure', async () => {
      const errorResponse = {
        response: {
          data: {
            message: 'Email already exists',
          },
        },
      }
      mockedAuthApi.register.mockRejectedValue(errorResponse)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let registerError: any
      await act(async () => {
        try {
          await result.current.register({
            name: 'Test User',
            email: 'test@example.com',
            password: 'Password123!',
            role: UserRole.CITIZEN,
          })
        } catch (error) {
          registerError = error
        }
      })

      expect(registerError).toEqual(errorResponse)
      
      await waitFor(() => {
        expect(result.current.error).toBe('Email already exists')
      })
    })
  })

  describe('Logout', () => {
    it('should logout and clear auth data', async () => {
      mockedTokenUtils.getAccessToken.mockReturnValue('mock-token')
      mockedTokenUtils.getUserProfile.mockReturnValue(mockUser)
      mockedAuthApi.getCurrentUser.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      await act(async () => {
        await result.current.logout()
      })

      expect(mockedTokenUtils.clearAuthData).toHaveBeenCalled()
      expect(result.current.isAuthenticated).toBe(false)
      expect(result.current.user).toBeNull()
    })
  })

  describe('Role Checking', () => {
    it('should check if user has specific role', async () => {
      mockedTokenUtils.getAccessToken.mockReturnValue('mock-token')
      mockedTokenUtils.getUserProfile.mockReturnValue(mockUser)
      mockedAuthApi.getCurrentUser.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      expect(result.current.hasRole(UserRole.CITIZEN)).toBe(true)
      expect(result.current.hasRole(UserRole.GOVERNMENT_OFFICER)).toBe(false)
    })

    it('should check if user has any of specified roles', async () => {
      mockedTokenUtils.getAccessToken.mockReturnValue('mock-token')
      mockedTokenUtils.getUserProfile.mockReturnValue(mockUser)
      mockedAuthApi.getCurrentUser.mockResolvedValue(mockUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      expect(result.current.hasAnyRole([UserRole.CITIZEN, UserRole.FACULTY])).toBe(true)
      expect(result.current.hasAnyRole([UserRole.FACULTY, UserRole.STUDENT])).toBe(false)
    })

    it('should check if user has all specified roles', async () => {
      const multiRoleUser = {
        ...mockUser,
        roles: [UserRole.CITIZEN, UserRole.RESEARCHER],
      }
      
      mockedTokenUtils.getAccessToken.mockReturnValue('mock-token')
      mockedTokenUtils.getUserProfile.mockReturnValue(multiRoleUser)
      mockedAuthApi.getCurrentUser.mockResolvedValue(multiRoleUser)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true)
      })

      expect(result.current.hasAllRoles([UserRole.CITIZEN, UserRole.RESEARCHER])).toBe(true)
      expect(result.current.hasAllRoles([UserRole.CITIZEN, UserRole.FACULTY])).toBe(false)
    })

    it('should return false for role checks when not authenticated', () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      expect(result.current.hasRole(UserRole.CITIZEN)).toBe(false)
      expect(result.current.hasAnyRole([UserRole.CITIZEN])).toBe(false)
      expect(result.current.hasAllRoles([UserRole.CITIZEN])).toBe(false)
    })
  })

  describe('Clear Error', () => {
    it('should clear error message', async () => {
      const errorResponse = {
        response: {
          data: {
            message: 'Test error',
          },
        },
      }
      mockedAuthApi.login.mockRejectedValue(errorResponse)

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      })

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false)
      })

      let loginError: any
      await act(async () => {
        try {
          await result.current.login({
            email: 'test@example.com',
            password: 'wrong',
          })
        } catch (error) {
          loginError = error
        }
      })

      expect(loginError).toEqual(errorResponse)
      
      await waitFor(() => {
        expect(result.current.error).toBe('Test error')
      })

      act(() => {
        result.current.clearError()
      })

      await waitFor(() => {
        expect(result.current.error).toBeNull()
      })
    })
  })
})
