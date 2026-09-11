/**
 * Password validation utilities
 * 
 * Matches backend password requirements from auth schema:
 * - Minimum 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one digit
 * - At least one special character
 */

export interface PasswordValidationResult {
  isValid: boolean
  errors: string[]
}

/**
 * Validate password against backend requirements
 * 
 * @param password - Password to validate
 * @returns Validation result with isValid flag and error messages
 */
export function validatePassword(password: string): PasswordValidationResult {
  const errors: string[] = []

  // Check minimum length
  if (!password || password.length < 8) {
    errors.push('Password must be at least 8 characters long')
  }

  // Check for uppercase letter
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  }

  // Check for lowercase letter
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  }

  // Check for digit
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one digit')
  }

  // Check for special character (matches backend pattern)
  if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password)) {
    errors.push('Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)')
  }

  return {
    isValid: errors.length === 0,
    errors,
  }
}

/**
 * Check if password meets minimum length requirement
 */
export function hasMinLength(password: string): boolean {
  return password.length >= 8
}

/**
 * Check if password contains uppercase letter
 */
export function hasUppercase(password: string): boolean {
  return /[A-Z]/.test(password)
}

/**
 * Check if password contains lowercase letter
 */
export function hasLowercase(password: string): boolean {
  return /[a-z]/.test(password)
}

/**
 * Check if password contains digit
 */
export function hasDigit(password: string): boolean {
  return /\d/.test(password)
}

/**
 * Check if password contains special character
 */
export function hasSpecialChar(password: string): boolean {
  return /[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(password)
}

/**
 * Get password strength indicator
 * 
 * @param password - Password to check
 * @returns Strength level: 'weak', 'fair', 'good', 'strong'
 */
export function getPasswordStrength(password: string): 'weak' | 'fair' | 'good' | 'strong' {
  if (!password) return 'weak'

  let score = 0

  // Length scoring
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  if (password.length >= 16) score++

  // Character variety scoring
  if (hasUppercase(password)) score++
  if (hasLowercase(password)) score++
  if (hasDigit(password)) score++
  if (hasSpecialChar(password)) score++

  // Return strength based on score
  if (score <= 2) return 'weak'
  if (score <= 4) return 'fair'
  if (score <= 6) return 'good'
  return 'strong'
}
