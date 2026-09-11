'use client'

/**
 * Authentication Context and Provider
 * 
 * Manages authentication state across the application:
 * - User authentication status
 * - Current user profile
 * - Login/logout actions
 * - Token management
 * - Session restoration from localStorage
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import type { User, LoginCredentials, RegisterData, LoginResponse } from '@/types/api'
import * as authApi from '../api/auth'
import {
  getAccessToken,
  setAccessToken,
  removeAccessToken,
  setUserProfile,
  getUserProfile,
  clearAuthData,
} from './token'

// Authentication state type
interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

// Authentication context type
interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  clearError: () => void
  hasRole: (role: string) => boolean
  hasAnyRole: (roles: string[]) => boolean
  hasAllRoles: (roles: string[]) => boolean
}

// Create context with undefined default (will be provided by AuthProvider)
const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * Custom hook to use auth context
 * Must be used within AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

/**
 * AuthProvider component
 * Wraps the application and provides authentication state
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true, // Start with loading to restore session
    error: null,
  })

  /**
   * Clear error message
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  /**
   * Restore user session from localStorage on mount
   */
  useEffect(() => {
    const restoreSession = async () => {
      const token = getAccessToken()
      const cachedUser = getUserProfile()

      // If no token, mark as not loading
      if (!token) {
        setState(prev => ({ ...prev, isLoading: false }))
        return
      }

      // If we have cached user, use it immediately (then validate in background)
      if (cachedUser) {
        setState({
          user: cachedUser,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
      }

      // Validate token with backend
      try {
        const user = await authApi.getCurrentUser()
        setUserProfile(user)
        setState({
          user,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        })
      } catch (error) {
        // Token is invalid or expired, clear auth data
        clearAuthData()
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        })
      }
    }

    restoreSession()
  }, [])

  /**
   * Login with email and password
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))

      const response: LoginResponse = await authApi.login(credentials)
      
      // Store token and user profile
      setAccessToken(response.access_token)
      setUserProfile(response.user)

      setState({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          'Login failed. Please check your credentials.'
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }))
      
      throw error
    }
  }, [])

  /**
   * Register new user
   */
  const register = useCallback(async (data: RegisterData) => {
    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }))

      // Register returns user profile (without token)
      const user = await authApi.register(data)

      // After successful registration, automatically login
      await login({ email: data.email, password: data.password })
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail ||
                          'Registration failed. Please try again.'
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }))
      
      throw error
    }
  }, [login])

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    try {
      // Clear token and user data
      clearAuthData()

      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })

      // Redirect to home page
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
      // Even if there's an error, clear local state
      clearAuthData()
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })
      router.push('/')
    }
  }, [router])

  /**
   * Refresh current user profile from backend
   */
  const refreshUser = useCallback(async () => {
    if (!state.isAuthenticated) {
      return
    }

    try {
      const user = await authApi.getCurrentUser()
      setUserProfile(user)
      setState(prev => ({ ...prev, user }))
    } catch (error) {
      // If refresh fails, token might be invalid
      console.error('Failed to refresh user:', error)
      await logout()
    }
  }, [state.isAuthenticated, logout])

  /**
   * Check if user has a specific role
   */
  const hasRole = useCallback((role: string): boolean => {
    if (!state.user || !state.isAuthenticated) {
      return false
    }
    return state.user.roles.includes(role)
  }, [state.user, state.isAuthenticated])

  /**
   * Check if user has any of the specified roles
   */
  const hasAnyRole = useCallback((roles: string[]): boolean => {
    if (!state.user || !state.isAuthenticated) {
      return false
    }
    return roles.some(role => state.user!.roles.includes(role))
  }, [state.user, state.isAuthenticated])

  /**
   * Check if user has all of the specified roles
   */
  const hasAllRoles = useCallback((roles: string[]): boolean => {
    if (!state.user || !state.isAuthenticated) {
      return false
    }
    return roles.every(role => state.user!.roles.includes(role))
  }, [state.user, state.isAuthenticated])

  // Context value
  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshUser,
    clearError,
    hasRole,
    hasAnyRole,
    hasAllRoles,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Export context for testing purposes
export { AuthContext }
