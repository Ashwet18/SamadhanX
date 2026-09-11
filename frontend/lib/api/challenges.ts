/**
 * Challenge API client
 * Handles challenge submission, retrieval, updates, and media uploads
 */

import axios from 'axios'
import { getApiUrl } from './config'
import { getAccessToken } from '../auth/token'
import type {
  Challenge,
  ChallengeCreate,
  ChallengeUpdate,
  PaginatedResponse,
  MediaFile,
  UUID,
  ChallengeStatus,
  Category,
} from '@/types/api'

/**
 * Create authorization headers with current access token
 */
function createAuthHeaders() {
  const token = getAccessToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Challenge list response structure (matches backend)
 */
export interface ChallengeListItem {
  id: UUID
  challenge_code: string
  title: string
  status: ChallengeStatus
  priority_level?: string
  district: string
  affected_population?: number
  category_count: number
  media_count: number
  created_at: string
}

export interface ChallengeListResponse {
  items: ChallengeListItem[]
  page: number
  page_size: number
  total: number
  pages: number
  has_next: boolean
  has_previous: boolean
}

/**
 * Media response structure (matches backend)
 */
export interface ChallengeMediaResponse {
  id: UUID
  media_type: 'IMAGE' | 'VIDEO' | 'AUDIO' | 'DOCUMENT'
  file_url: string
  file_name: string
  mime_type?: string
  file_size?: number
  created_at: string
}

/**
 * Create a new challenge
 * POST /api/v1/challenges
 * 
 * @param data - Challenge creation data
 * @returns Created challenge with generated code
 * @throws 400 - Validation error
 * @throws 401 - Unauthorized
 */
export async function createChallenge(data: ChallengeCreate): Promise<Challenge> {
  const url = getApiUrl('/challenges')
  const response = await axios.post<Challenge>(url, data, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Get challenges submitted by current user
 * GET /api/v1/challenges/my
 * 
 * @param page - Page number (default: 1)
 * @param pageSize - Items per page (default: 20)
 * @param status - Optional status filter
 * @returns Paginated list of user's challenges
 * @throws 401 - Unauthorized
 */
export async function getMyChallenges(
  page: number = 1,
  pageSize: number = 20,
  status?: ChallengeStatus
): Promise<ChallengeListResponse> {
  const url = getApiUrl('/challenges/my')
  const params: any = { page, page_size: pageSize }
  if (status) params.status = status

  const response = await axios.get<ChallengeListResponse>(url, {
    headers: createAuthHeaders(),
    params,
  })
  return response.data
}

/**
 * Get challenge by ID
 * GET /api/v1/challenges/{id}
 * 
 * @param id - Challenge UUID
 * @returns Complete challenge details
 * @throws 404 - Challenge not found
 */
export async function getChallenge(id: UUID): Promise<Challenge> {
  const url = getApiUrl(`/challenges/${id}`)
  const response = await axios.get<Challenge>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Update challenge
 * PATCH /api/v1/challenges/{id}
 * 
 * @param id - Challenge UUID
 * @param data - Update data
 * @returns Updated challenge
 * @throws 400 - Validation error
 * @throws 401 - Unauthorized
 * @throws 403 - Not challenge owner or cannot edit in current status
 * @throws 404 - Challenge not found
 */
export async function updateChallenge(
  id: UUID,
  data: ChallengeUpdate
): Promise<Challenge> {
  const url = getApiUrl(`/challenges/${id}`)
  const response = await axios.patch<Challenge>(url, data, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Delete challenge
 * DELETE /api/v1/challenges/{id}
 * 
 * Only DRAFT challenges can be deleted
 * 
 * @param id - Challenge UUID
 * @throws 401 - Unauthorized
 * @throws 403 - Not challenge owner or cannot delete in current status
 * @throws 404 - Challenge not found
 */
export async function deleteChallenge(id: UUID): Promise<void> {
  const url = getApiUrl(`/challenges/${id}`)
  await axios.delete(url, {
    headers: createAuthHeaders(),
  })
}

/**
 * Upload media file for challenge
 * POST /api/v1/challenges/{id}/media
 * 
 * @param challengeId - Challenge UUID
 * @param file - File to upload
 * @param onProgress - Optional upload progress callback
 * @returns Uploaded media metadata
 * @throws 400 - Invalid file type or size
 * @throws 401 - Unauthorized
 * @throws 413 - File too large
 */
export async function uploadChallengeMedia(
  challengeId: UUID,
  file: File,
  onProgress?: (progress: number) => void
): Promise<ChallengeMediaResponse> {
  const url = getApiUrl(`/challenges/${challengeId}/media`)
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post<ChallengeMediaResponse>(url, formData, {
    headers: {
      ...createAuthHeaders(),
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    },
  })
  return response.data
}

/**
 * Get challenge media files
 * GET /api/v1/challenges/{id}/media
 * 
 * @param challengeId - Challenge UUID
 * @returns List of media files
 */
export async function getChallengeMedia(
  challengeId: UUID
): Promise<ChallengeMediaResponse[]> {
  const url = getApiUrl(`/challenges/${challengeId}/media`)
  const response = await axios.get<ChallengeMediaResponse[]>(url, {
    headers: createAuthHeaders(),
  })
  return response.data
}

/**
 * Delete challenge media
 * DELETE /api/v1/challenges/{id}/media/{mediaId}
 * 
 * @param challengeId - Challenge UUID
 * @param mediaId - Media UUID
 * @throws 401 - Unauthorized
 * @throws 403 - Not authorized to delete
 * @throws 404 - Media not found
 */
export async function deleteChallengeMedia(
  challengeId: UUID,
  mediaId: UUID
): Promise<void> {
  const url = getApiUrl(`/challenges/${challengeId}/media/${mediaId}`)
  await axios.delete(url, {
    headers: createAuthHeaders(),
  })
}

/**
 * Get all available categories
 * GET /api/v1/categories
 * 
 * @returns List of available challenge categories
 */
export async function getCategories(): Promise<Category[]> {
  const url = getApiUrl('/categories')
  const response = await axios.get<Category[]>(url)
  return response.data
}

// Export all challenge API functions as a named object
export const challengeApi = {
  createChallenge,
  getMyChallenges,
  getChallenge,
  updateChallenge,
  deleteChallenge,
  uploadChallengeMedia,
  getChallengeMedia,
  deleteChallengeMedia,
  getCategories,
}
