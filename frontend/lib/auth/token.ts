/**
 * Token storage utilities for JWT authentication
 * 
 * Security Note: localStorage is used for token storage, which is vulnerable to XSS attacks.
 * For production, consider:
 * - httpOnly cookies for token storage
 * - Short-lived access tokens (5-15 minutes)
 * - Refresh token rotation
 * - Content Security Policy (CSP) headers
 */

import { STORAGE_KEYS } from '../api/config'

/**
 * Get access token from localStorage
 * Returns null if not found or if running on server
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') {
    return null
  }
  
  try {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
  } catch (error) {
    console.error('Error reading token from storage:', error)
    return null
  }
}

/**
 * Store access token in localStorage
 */
export function setAccessToken(token: string): void {
  if (typeof window === 'undefined') {
    return
  }
  
  try {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token)
  } catch (error) {
    console.error('Error storing token:', error)
  }
}

/**
 * Remove access token from localStorage
 */
export function removeAccessToken(): void {
  if (typeof window === 'undefined') {
    return
  }
  
  try {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
  } catch (error) {
    console.error('Error removing token:', error)
  }
}

/**
 * Check if user has valid token
 * Note: This only checks if token exists, not if it's expired or valid
 * Server will validate token on API calls
 */
export function hasAccessToken(): boolean {
  return getAccessToken() !== null
}

/**
 * Clear all authentication data from storage
 */
export function clearAuthData(): void {
  if (typeof window === 'undefined') {
    return
  }
  
  try {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER_PROFILE)
  } catch (error) {
    console.error('Error clearing auth data:', error)
  }
}

/**
 * Store user profile in localStorage
 */
export function setUserProfile(user: any): void {
  if (typeof window === 'undefined') {
    return
  }
  
  try {
    localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(user))
  } catch (error) {
    console.error('Error storing user profile:', error)
  }
}

/**
 * Get user profile from localStorage
 */
export function getUserProfile(): any | null {
  if (typeof window === 'undefined') {
    return null
  }
  
  try {
    const profile = localStorage.getItem(STORAGE_KEYS.USER_PROFILE)
    return profile ? JSON.parse(profile) : null
  } catch (error) {
    console.error('Error reading user profile:', error)
    return null
  }
}
