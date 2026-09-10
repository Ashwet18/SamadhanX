/**
 * API configuration and base setup for SamadhanX frontend
 */

// Base API configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  API_VERSION: 'v1',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
} as const

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    RESET_PASSWORD: '/auth/reset-password',
    CHANGE_PASSWORD: '/auth/change-password',
  },
  
  // Users
  USERS: {
    BASE: '/users',
    PROFILE: '/users/me',
    UPDATE_PROFILE: '/users/me',
    AVATAR: '/users/me/avatar',
  },
  
  // Challenges
  CHALLENGES: {
    BASE: '/challenges',
    CREATE: '/challenges',
    SUBMIT: (id: string) => `/challenges/${id}/submit`,
    MEDIA: (id: string) => `/challenges/${id}/media`,
    DUPLICATE_CHECK: '/challenges/duplicate-check',
    CATEGORIES: '/challenges/categories',
  },
  
  // Universities
  UNIVERSITIES: {
    BASE: '/universities',
    CAPABILITIES: (id: string) => `/universities/${id}/capabilities`,
    DEPARTMENTS: (id: string) => `/universities/${id}/departments`,
    FACULTY: (id: string) => `/universities/${id}/faculty`,
    STUDENTS: (id: string) => `/universities/${id}/students`,
  },
  
  // Projects
  PROJECTS: {
    BASE: '/projects',
    CREATE: '/projects',
    MEMBERS: (id: string) => `/projects/${id}/members`,
    MILESTONES: (id: string) => `/projects/${id}/milestones`,
    DELIVERABLES: (id: string) => `/projects/${id}/deliverables`,
    PROPOSALS: (id: string) => `/projects/${id}/proposals`,
  },
  
  // Industry
  INDUSTRY: {
    PARTNERS: '/industry/partners',
    PARTNERSHIPS: '/industry/partnerships',
    FUNDING: '/industry/funding',
    MENTORSHIPS: '/industry/mentorships',
  },
  
  // Analytics
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard',
    REPORTS: '/analytics/reports',
    METRICS: '/analytics/metrics',
    EXPORT: '/analytics/export',
  },
  
  // Notifications
  NOTIFICATIONS: {
    BASE: '/notifications',
    MARK_READ: (id: string) => `/notifications/${id}/read`,
    MARK_ALL_READ: '/notifications/read-all',
    PREFERENCES: '/notifications/preferences',
  },
  
  // File Upload
  UPLOADS: {
    IMAGE: '/uploads/image',
    DOCUMENT: '/uploads/document',
    MEDIA: '/uploads/media',
  },
} as const

// HTTP status codes
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const

// Error types
export const ERROR_TYPES = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const

// Content types
export const CONTENT_TYPES = {
  JSON: 'application/json',
  FORM_DATA: 'multipart/form-data',
  URL_ENCODED: 'application/x-www-form-urlencoded',
  TEXT: 'text/plain',
} as const

// Request headers
export const DEFAULT_HEADERS = {
  'Content-Type': CONTENT_TYPES.JSON,
  'Accept': CONTENT_TYPES.JSON,
} as const

// Storage keys
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'samadhanx_access_token',
  REFRESH_TOKEN: 'samadhanx_refresh_token',
  USER_PROFILE: 'samadhanx_user_profile',
  THEME: 'samadhanx_theme',
  LANGUAGE: 'samadhanx_language',
  NOTIFICATIONS_ENABLED: 'samadhanx_notifications_enabled',
} as const

// API response types
export interface ApiResponse<T = any> {
  data?: T
  message: string
  success: boolean
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface ApiError {
  message: string
  error_code?: string
  details?: Record<string, any>
  success: false
}

// Request configuration interface
export interface RequestConfig {
  headers?: Record<string, string>
  timeout?: number
  retries?: number
  retryDelay?: number
}

// File upload configuration
export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
  ],
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks for large file uploads
} as const

// Pagination defaults
export const PAGINATION_DEFAULTS = {
  PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  DEFAULT_PAGE: 1,
} as const

// API helper functions
export function getApiUrl(endpoint: string): string {
  const baseUrl = API_CONFIG.BASE_URL.replace(/\/$/, '')
  const version = API_CONFIG.API_VERSION
  const cleanEndpoint = endpoint.replace(/^\//, '')
  
  return `${baseUrl}/api/${version}/${cleanEndpoint}`
}

export function isApiError(response: any): response is ApiError {
  return response && typeof response === 'object' && response.success === false
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  
  if (isApiError(error)) {
    return error.message
  }
  
  if (typeof error === 'string') {
    return error
  }
  
  return 'An unknown error occurred'
}