import * as React from "react"
import { cn } from "@/lib/utils"
import { AlertCircle } from "lucide-react"

export interface FormErrorProps {
  children?: React.ReactNode
  className?: string
  message?: string
}

export function FormError({ children, className, message }: FormErrorProps) {
  const content = children || message

  if (!content) {
    return null
  }

  return (
    <div
      className={cn(
        "flex items-start gap-2 text-sm text-red-600 dark:text-red-400 mt-1",
        className
      )}
    >
      <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
      <span>{content}</span>
    </div>
  )
}
