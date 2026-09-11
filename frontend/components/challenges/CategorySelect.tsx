'use client'

/**
 * CategorySelect Component
 * 
 * Fetches and displays available challenge categories
 * Allows single or multiple category selection
 */

import { useEffect, useState } from 'react'
import { Loader2, AlertCircle } from 'lucide-react'
import { Label } from '@/components/ui/label'
import { FormError } from '@/components/ui/form-error'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { challengeApi } from '@/lib/api/challenges'
import type { Category } from '@/types/api'

interface CategorySelectProps {
  selectedCategories: string[]
  onChange: (categories: string[]) => void
  error?: string
  disabled?: boolean
  multiple?: boolean
  required?: boolean
}

export function CategorySelect({
  selectedCategories,
  onChange,
  error,
  disabled = false,
  multiple = true,
  required = true,
}: CategorySelectProps) {
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    setIsLoading(true)
    setLoadError(null)

    try {
      const data = await challengeApi.getCategories()
      // Sort categories: top-level first, then by name
      const sorted = data.sort((a, b) => {
        // Top-level (no parent) come first
        if (!a.parent_id && b.parent_id) return -1
        if (a.parent_id && !b.parent_id) return 1
        // Then sort alphabetically
        return a.name.localeCompare(b.name)
      })
      setCategories(sorted)
    } catch (err: any) {
      console.error('Failed to load categories:', err)
      setLoadError(err.response?.data?.detail || 'Failed to load categories')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggle = (categoryId: string) => {
    if (disabled) return

    if (multiple) {
      // Multiple selection
      if (selectedCategories.includes(categoryId)) {
        // Remove
        onChange(selectedCategories.filter(id => id !== categoryId))
      } else {
        // Add
        onChange([...selectedCategories, categoryId])
      }
    } else {
      // Single selection
      onChange([categoryId])
    }
  }

  const isSelected = (categoryId: string) => {
    return selectedCategories.includes(categoryId)
  }

  // Group categories by parent
  const topLevelCategories = categories.filter(cat => !cat.parent_id)
  const getCategoryChildren = (parentId: string) => {
    return categories.filter(cat => cat.parent_id === parentId)
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        <Label>
          Categories{required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <div className="flex items-center justify-center p-8 border rounded-md bg-gray-50">
          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
          <span className="ml-2 text-sm text-gray-600">Loading categories...</span>
        </div>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="space-y-2">
        <Label>
          Categories{required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {loadError}
            <button
              type="button"
              onClick={loadCategories}
              className="ml-2 underline hover:no-underline"
            >
              Try again
            </button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (categories.length === 0) {
    return (
      <div className="space-y-2">
        <Label>
          Categories{required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        <Alert>
          <AlertDescription>
            No categories available. Please contact support.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <Label htmlFor="categories">
        Categories{required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      <p className="text-sm text-gray-500">
        {multiple
          ? 'Select one or more categories that best describe this challenge'
          : 'Select the category that best describes this challenge'}
      </p>

      {/* Category grid */}
      <div
        id="categories"
        className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 border rounded-md bg-gray-50"
        role="group"
        aria-label="Challenge categories"
        aria-invalid={!!error}
        aria-describedby={error ? 'categories-error' : undefined}
      >
        {topLevelCategories.map((category) => {
          const children = getCategoryChildren(category.id)
          const hasChildren = children.length > 0

          return (
            <div key={category.id} className="space-y-2">
              {/* Parent category */}
              <CategoryCheckbox
                category={category}
                isSelected={isSelected(category.id)}
                onToggle={handleToggle}
                disabled={disabled}
                isParent={hasChildren}
              />

              {/* Child categories */}
              {hasChildren && (
                <div className="ml-6 space-y-2 border-l-2 border-gray-300 pl-3">
                  {children.map((child) => (
                    <CategoryCheckbox
                      key={child.id}
                      category={child}
                      isSelected={isSelected(child.id)}
                      onToggle={handleToggle}
                      disabled={disabled}
                      isParent={false}
                    />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Selected count */}
      {multiple && selectedCategories.length > 0 && (
        <p className="text-sm text-gray-600">
          {selectedCategories.length} {selectedCategories.length === 1 ? 'category' : 'categories'} selected
        </p>
      )}

      {/* Error message */}
      {error && <FormError id="categories-error" message={error} />}
    </div>
  )
}

/**
 * Individual category checkbox
 */
interface CategoryCheckboxProps {
  category: Category
  isSelected: boolean
  onToggle: (id: string) => void
  disabled: boolean
  isParent: boolean
}

function CategoryCheckbox({
  category,
  isSelected,
  onToggle,
  disabled,
  isParent,
}: CategoryCheckboxProps) {
  return (
    <label
      className={`
        flex items-center gap-2 p-3 rounded-md border cursor-pointer transition-colors
        ${isSelected
          ? 'bg-blue-50 border-blue-500 ring-1 ring-blue-500'
          : 'bg-white border-gray-300 hover:border-gray-400'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${isParent ? 'font-medium' : ''}
      `}
    >
      <input
        type="checkbox"
        checked={isSelected}
        onChange={() => onToggle(category.id)}
        disabled={disabled}
        className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
        aria-label={`Select ${category.name}`}
      />
      <div className="flex-1">
        <div className="text-sm font-medium text-gray-900">{category.name}</div>
        {category.description && (
          <div className="text-xs text-gray-500 mt-0.5">{category.description}</div>
        )}
      </div>
    </label>
  )
}
