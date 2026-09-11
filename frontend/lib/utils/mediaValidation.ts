/**
 * Media file validation utilities
 * Matches backend media validation constraints
 */

export interface MediaValidationResult {
  valid: boolean
  error?: string
}

// Supported MIME types (matches backend)
const SUPPORTED_MIME_TYPES = {
  // Images - max 10 MB
  'image/jpeg': { maxSize: 10 * 1024 * 1024, label: 'JPEG image' },
  'image/png': { maxSize: 10 * 1024 * 1024, label: 'PNG image' },
  'image/webp': { maxSize: 10 * 1024 * 1024, label: 'WebP image' },
  
  // Videos - max 50 MB
  'video/mp4': { maxSize: 50 * 1024 * 1024, label: 'MP4 video' },
  'video/webm': { maxSize: 50 * 1024 * 1024, label: 'WebM video' },
  
  // Audio - max 20 MB
  'audio/mpeg': { maxSize: 20 * 1024 * 1024, label: 'MP3 audio' },
  'audio/mp3': { maxSize: 20 * 1024 * 1024, label: 'MP3 audio' },
  'audio/wav': { maxSize: 20 * 1024 * 1024, label: 'WAV audio' },
  'audio/ogg': { maxSize: 20 * 1024 * 1024, label: 'OGG audio' },
  
  // Documents - max 10 MB
  'application/pdf': { maxSize: 10 * 1024 * 1024, label: 'PDF document' },
}

/**
 * Validate a single media file
 * 
 * @param file - File to validate
 * @returns Validation result with error message if invalid
 */
export function validateMediaFile(file: File): MediaValidationResult {
  // Check if file type is supported
  const mimeConfig = SUPPORTED_MIME_TYPES[file.type as keyof typeof SUPPORTED_MIME_TYPES]
  
  if (!mimeConfig) {
    return {
      valid: false,
      error: `Unsupported file type: ${file.type}. Supported types: JPEG, PNG, WebP images; MP4, WebM videos; MP3, WAV, OGG audio; PDF documents.`,
    }
  }
  
  // Check file size
  if (file.size > mimeConfig.maxSize) {
    const maxSizeMB = Math.round(mimeConfig.maxSize / (1024 * 1024))
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2)
    return {
      valid: false,
      error: `File is too large (${fileSizeMB} MB). Maximum size for ${mimeConfig.label}: ${maxSizeMB} MB.`,
    }
  }
  
  // Check if file has content
  if (file.size === 0) {
    return {
      valid: false,
      error: 'File is empty',
    }
  }
  
  return { valid: true }
}

/**
 * Validate multiple media files
 * 
 * @param files - Array of files to validate
 * @param maxFiles - Maximum number of files allowed (default: 5)
 * @returns Validation result for all files
 */
export function validateMediaFiles(
  files: File[],
  maxFiles: number = 5
): MediaValidationResult {
  // Check maximum number of files
  if (files.length > maxFiles) {
    return {
      valid: false,
      error: `Maximum ${maxFiles} files allowed`,
    }
  }
  
  // Validate each file
  for (const file of files) {
    const result = validateMediaFile(file)
    if (!result.valid) {
      return result
    }
  }
  
  return { valid: true }
}

/**
 * Get media type category from MIME type
 */
export function getMediaType(
  mimeType: string
): 'IMAGE' | 'VIDEO' | 'AUDIO' | 'DOCUMENT' | 'UNKNOWN' {
  if (mimeType.startsWith('image/')) return 'IMAGE'
  if (mimeType.startsWith('video/')) return 'VIDEO'
  if (mimeType.startsWith('audio/')) return 'AUDIO'
  if (mimeType === 'application/pdf') return 'DOCUMENT'
  return 'UNKNOWN'
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

/**
 * Check if file is an image
 */
export function isImageFile(file: File): boolean {
  return file.type.startsWith('image/')
}

/**
 * Check if file is a video
 */
export function isVideoFile(file: File): boolean {
  return file.type.startsWith('video/')
}

/**
 * Get list of supported file extensions
 */
export function getSupportedExtensions(): string[] {
  return [
    'jpg',
    'jpeg',
    'png',
    'webp',
    'mp4',
    'webm',
    'mp3',
    'wav',
    'ogg',
    'pdf',
  ]
}

/**
 * Get accept attribute value for file input
 */
export function getAcceptAttribute(): string {
  return Object.keys(SUPPORTED_MIME_TYPES).join(',')
}
