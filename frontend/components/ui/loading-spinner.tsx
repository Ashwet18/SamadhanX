import * as React from "react"
import { cn } from "@/lib/utils"

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  text?: string
}

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-8 w-8 border-2',
  lg: 'h-12 w-12 border-3',
  xl: 'h-16 w-16 border-4',
}

export function LoadingSpinner({ size = 'md', className, text }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2">
      <div
        className={cn(
          "animate-spin rounded-full border-b-primary-600 border-t-transparent border-l-transparent border-r-transparent",
          sizeClasses[size],
          className
        )}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
      {text && (
        <p className="text-sm text-gray-600 dark:text-gray-400">{text}</p>
      )}
    </div>
  )
}

/**
 * FullPageLoading - Loading spinner centered on full page
 */
export function FullPageLoading({ text }: { text?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner size="lg" text={text || "Loading..."} />
    </div>
  )
}

/**
 * ButtonLoading - Small spinner for buttons
 */
export function ButtonLoading({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-spin rounded-full h-4 w-4 border-2 border-b-current border-t-transparent border-l-transparent border-r-transparent",
        className
      )}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  )
}
