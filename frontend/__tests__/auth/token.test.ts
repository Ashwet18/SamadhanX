/**
 * Tests for token storage utilities
 */

import {
  getAccessToken,
  setAccessToken,
  removeAccessToken,
  hasAccessToken,
  clearAuthData,
  setUserProfile,
  getUserProfile,
} from '@/lib/auth/token'
import { STORAGE_KEYS } from '@/lib/api/config'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
})

describe('Token Storage Utilities', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('getAccessToken', () => {
    it('should return token from localStorage', () => {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'test-token')
      expect(getAccessToken()).toBe('test-token')
    })

    it('should return null if no token exists', () => {
      expect(getAccessToken()).toBeNull()
    })
  })

  describe('setAccessToken', () => {
    it('should store token in localStorage', () => {
      setAccessToken('new-token')
      expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBe('new-token')
    })
  })

  describe('removeAccessToken', () => {
    it('should remove token from localStorage', () => {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'test-token')
      removeAccessToken()
      expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBeNull()
    })
  })

  describe('hasAccessToken', () => {
    it('should return true if token exists', () => {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'test-token')
      expect(hasAccessToken()).toBe(true)
    })

    it('should return false if token does not exist', () => {
      expect(hasAccessToken()).toBe(false)
    })
  })

  describe('clearAuthData', () => {
    it('should remove all auth-related data', () => {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, 'test-token')
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, '{"id": "123"}')
      
      clearAuthData()
      
      expect(localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)).toBeNull()
      expect(localStorage.getItem(STORAGE_KEYS.USER_PROFILE)).toBeNull()
    })
  })

  describe('setUserProfile', () => {
    it('should store user profile as JSON string', () => {
      const user = { id: '123', name: 'Test User', email: 'test@example.com' }
      setUserProfile(user)
      
      const stored = localStorage.getItem(STORAGE_KEYS.USER_PROFILE)
      expect(stored).toBe(JSON.stringify(user))
    })
  })

  describe('getUserProfile', () => {
    it('should retrieve and parse user profile', () => {
      const user = { id: '123', name: 'Test User', email: 'test@example.com' }
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user))
      
      const retrieved = getUserProfile()
      expect(retrieved).toEqual(user)
    })

    it('should return null if no profile exists', () => {
      expect(getUserProfile()).toBeNull()
    })

    it('should return null if profile is invalid JSON', () => {
      localStorage.setItem(STORAGE_KEYS.USER_PROFILE, 'invalid-json')
      expect(getUserProfile()).toBeNull()
    })
  })
})
