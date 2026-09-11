/**
 * Tests for auth API client
 */

import axios from 'axios'
import {
  register,
  login,
  getCurrentUser,
  changePassword,
  validateToken,
} from '@/lib/api/auth'
import { UserRole } from '@/types/api'

jest.mock('axios')
jest.mock('@/lib/auth/token', () => ({
  getAccessToken: jest.fn(() => 'mock-token'),
}))

const mockedAxios = axios as jest.Mocked<typeof axios>

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

describe('Auth API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('register', () => {
    it('should call POST /api/v1/auth/register', async () => {
      mockedAxios.post.mockResolvedValue({ data: mockUser })

      const registerData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'Password123!',
        role: UserRole.CITIZEN,
      }

      const result = await register(registerData)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/auth/register'),
        registerData
      )
      expect(result).toEqual(mockUser)
    })

    it('should throw error on registration failure', async () => {
      const error = {
        response: {
          data: { message: 'Email already exists' },
          status: 409,
        },
      }
      mockedAxios.post.mockRejectedValue(error)

      await expect(
        register({
          name: 'Test User',
          email: 'test@example.com',
          password: 'Password123!',
          role: UserRole.CITIZEN,
        })
      ).rejects.toEqual(error)
    })
  })

  describe('login', () => {
    it('should call POST /api/v1/auth/login', async () => {
      mockedAxios.post.mockResolvedValue({ data: mockLoginResponse })

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      }

      const result = await login(credentials)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/auth/login'),
        credentials
      )
      expect(result).toEqual(mockLoginResponse)
    })

    it('should throw error on login failure', async () => {
      const error = {
        response: {
          data: { message: 'Invalid credentials' },
          status: 401,
        },
      }
      mockedAxios.post.mockRejectedValue(error)

      await expect(
        login({
          email: 'test@example.com',
          password: 'wrong',
        })
      ).rejects.toEqual(error)
    })
  })

  describe('getCurrentUser', () => {
    it('should call GET /api/v1/auth/me with auth header', async () => {
      mockedAxios.get.mockResolvedValue({ data: mockUser })

      const result = await getCurrentUser()

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token',
          }),
        })
      )
      expect(result).toEqual(mockUser)
    })

    it('should throw error if token is invalid', async () => {
      const error = {
        response: {
          data: { message: 'Invalid token' },
          status: 401,
        },
      }
      mockedAxios.get.mockRejectedValue(error)

      await expect(getCurrentUser()).rejects.toEqual(error)
    })
  })

  describe('changePassword', () => {
    it('should call POST /api/v1/auth/change-password with auth header', async () => {
      const successResponse = {
        message: 'Password changed successfully',
        success: true,
      }
      mockedAxios.post.mockResolvedValue({ data: successResponse })

      const result = await changePassword('oldPass123!', 'newPass123!')

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/auth/change-password'),
        {
          current_password: 'oldPass123!',
          new_password: 'newPass123!',
        },
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer mock-token',
          }),
        })
      )
      expect(result).toEqual(successResponse)
    })

    it('should throw error if current password is incorrect', async () => {
      const error = {
        response: {
          data: { message: 'Current password incorrect' },
          status: 401,
        },
      }
      mockedAxios.post.mockRejectedValue(error)

      await expect(
        changePassword('wrongPass', 'newPass123!')
      ).rejects.toEqual(error)
    })
  })

  describe('validateToken', () => {
    it('should return true if token is valid', async () => {
      mockedAxios.get.mockResolvedValue({ data: mockUser })

      const result = await validateToken()

      expect(result).toBe(true)
    })

    it('should return false if token is invalid', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Invalid token'))

      const result = await validateToken()

      expect(result).toBe(false)
    })
  })
})
