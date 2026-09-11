'use client'

/**
 * MediaUpload Component
 * 
 * Allows users to select up to 5 media files for challenge submission
 * Shows preview, file details, and allows removal
 */

import { useState, useRef } from 'react'
import { X, Upload, FileIcon, Image as ImageIcon, Video, Music, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  validateMediaFile,
  formatFileSize,
  isImageFile,
  isVideoFile,
  getAcceptAttribute,
} from '@/lib/utils/mediaValidation'

interface MediaUploadProps {
  files: File[]
  onChange: (files: File[]) => void
  maxFiles?: number
  disabled?: boolean
}

export function MediaUpload({
  files,
  onChange,
  maxFiles = 5,
  disabled = false,
}: MediaUploadProps) {
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    if (selectedFiles.length === 0) return

    setError(null)

    // Check total count
    const totalFiles = files.length + selectedFiles.length
    if (totalFiles > maxFiles) {
      setError(`Maximum ${maxFiles} files allowed. You can add ${maxFiles - files.length} more file(s).`)
      return
    }

    // Validate each file
    for (const file of selectedFiles) {
      const validation = validateMediaFile(file)
      if (!validation.valid) {
        setError(validation.error || 'Invalid file')
        return
      }
    }

    // Add to existing files
    onChange([...files, ...selectedFiles])

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleRemoveFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    onChange(newFiles)
    setError(null)
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const canAddMore = files.length < maxFiles

  return (
    <div className="space-y-4">
      {/* File input (hidden) */}
      <input
        ref={fileInputRef}
        type="file"
        accept={getAcceptAttribute()}
        multiple
        onChange={handleFileSelect}
        disabled={disabled || !canAddMore}
        className="hidden"
        aria-label="Select media files"
      />

      {/* Upload button */}
      <div className="flex items-center gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={handleBrowseClick}
          disabled={disabled || !canAddMore}
          className="gap-2"
        >
          <Upload className="h-4 w-4" />
          Select Files
        </Button>
        <span className="text-sm text-gray-600">
          {files.length} / {maxFiles} files selected
        </span>
      </div>

      {/* Info */}
      <p className="text-sm text-gray-500">
        Supported: JPEG, PNG, WebP images (10 MB); MP4, WebM videos (50 MB); MP3, WAV, OGG audio (20 MB); PDF (10 MB)
      </p>

      {/* Error message */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Selected Files:</p>
          <div className="space-y-2">
            {files.map((file, index) => (
              <FilePreview
                key={`${file.name}-${index}`}
                file={file}
                onRemove={() => handleRemoveFile(index)}
                disabled={disabled}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * FilePreview Component
 * Shows individual file with preview and remove button
 */
interface FilePreviewProps {
  file: File
  onRemove: () => void
  disabled?: boolean
}

function FilePreview({ file, onRemove, disabled }: FilePreviewProps) {
  const [preview, setPreview] = useState<string | null>(null)

  // Generate preview for images
  useState(() => {
    if (isImageFile(file)) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview)
      }
    }
  })

  // Get appropriate icon
  const FileIconComponent = () => {
    if (isImageFile(file)) return <ImageIcon className="h-8 w-8 text-blue-500" />
    if (isVideoFile(file)) return <Video className="h-8 w-8 text-purple-500" />
    if (file.type.startsWith('audio/')) return <Music className="h-8 w-8 text-green-500" />
    if (file.type === 'application/pdf') return <FileText className="h-8 w-8 text-red-500" />
    return <FileIcon className="h-8 w-8 text-gray-500" />
  }

  return (
    <div className="flex items-center gap-4 p-3 border rounded-lg bg-gray-50">
      {/* Preview or icon */}
      <div className="flex-shrink-0">
        {preview ? (
          <img
            src={preview}
            alt={file.name}
            className="h-16 w-16 object-cover rounded"
          />
        ) : (
          <div className="h-16 w-16 flex items-center justify-center bg-white rounded border">
            <FileIconComponent />
          </div>
        )}
      </div>

      {/* File details */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate" title={file.name}>
          {file.name}
        </p>
        <p className="text-xs text-gray-500">
          {formatFileSize(file.size)} • {file.type || 'Unknown type'}
        </p>
      </div>

      {/* Remove button */}
      <button
        type="button"
        onClick={onRemove}
        disabled={disabled}
        className="flex-shrink-0 p-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label={`Remove ${file.name}`}
      >
        <X className="h-5 w-5 text-gray-600" />
      </button>
    </div>
  )
}
