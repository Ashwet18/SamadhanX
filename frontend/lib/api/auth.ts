/**
 * Authentication API client
 * Handles user registration, login, profile fetching, and logout
 */

import axios from 'axios'
import { getApiUrl } from './config'
import { getAccessToken } from '../auth/token'
import type {
  RegisterData,
  LoginCredentials,
  LoginResponse,
  User,
  ApiResponse,
} from '@/types/api'

/**
 * Create authorization headers with current access token
 */
function createAuthHeaders() {
  const token = getAccessToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Register a new user
 * POST /api/v1/auth/register
 * 
 * @param data - Registration data (name, email, password, role, phone)
 * @returns User profile (without password)
 * @throws 409 - Email already exists
 * @throws 422 - Validation error (weak password, invalid role, etc.)
 */
export async function register(data: RegisterData): Promise<User> {
  const url = getApiUrl('/auth/register')
  const response = await axios.post<User>(url, data)
  return response.data
}

/**
 * Login with email and password
 * POST /api/v1/auth/login
 * 
 * @param credentials - Email and password
 * @returns Access token and user profile
 * @throws 401 - Incorrect email or password
 */
export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  const url = getApiUrl('/auth/login')
  const response = await axios.post<LoginResponse>(url, credentials)
  return response.data
}

/**
 * Get current authenticated user profile
 * GET /api/v1/auth/me
 * 
 * Requires valid JWT token in Authorization header
 * 
 * @returns Current user profile with roles and profile indicators
 * @throws 401 - Invalid or expired token
 */
export async function getCurrentUser(): Promise<User> {
  const url = getApiUrl('/auth/me')
  const response = await axios.get<User>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Change user password
 * POST /api/v1/auth/change-password
 * 
 * @param currentPassword - Current password for verification
 * @param newPassword - New password (must meet strength requirements)
 * @returns Success message
 * @throws 401 - Current password incorrect
 * @throws 422 - New password doesn't meet requirements
 */
export async function changePassword(
  currentPassword: string,
  newPassword: string
): Promise<ApiResponse> {
  const url = getApiUrl('/auth/change-password')
  const response = await axios.post<ApiResponse>(
    url,
    {
      current_password: currentPassword,
      new_password: newPassword,
    },
    {
      headers: createAuthHeaders(),
    }
  )
  return response.data
}

/**
 * Logout (client-side only)
 * 
 * JWT tokens are stateless, so logout is handled by:
 * 1. Removing token from client storage
 * 2. Clearing user state
 * 
 * The backend /auth/logout endpoint exists for documentation purposes only
 */
export async function logout(): Promise<void> {
  // Backend logout endpoint is informational only since JWTs are stateless
  // Token removal happens in AuthContext
  return Promise.resolve()
}

/**
 * Validate if current token is still valid
 * Attempts to fetch current user profile
 * 
 * @returns true if token is valid, false otherwise
 */
export async function validateToken(): Promise<boolean> {
  try {
    await getCurrentUser()
    return true
  } catch (error) {
    return false
  }
}

// Export all auth API functions as a named object
export const authApi = {
  register,
  login,
  getCurrentUser,
  changePassword,
  logout,
  validateToken,
}
