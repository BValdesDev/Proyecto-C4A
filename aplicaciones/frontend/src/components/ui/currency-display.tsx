import React from "react"
import { cn } from "../../utilidades/cn"
import { formatCLP } from "../../utilidades/localization"

interface CurrencyDisplayProps {
  amount: number
  showSymbol?: boolean
  className?: string
  size?: "sm" | "md" | "lg"
  color?: "default" | "success" | "warning" | "error"
}

export function CurrencyDisplay({
  amount,
  showSymbol = true,
  className,
  size = "md",
  color = "default",
}: CurrencyDisplayProps) {
  const sizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg font-semibold",
  }

  const colorClasses = {
    default: "text-foreground",
    success: "text-green-600",
    warning: "text-yellow-600",
    error: "text-red-600",
  }

  const formattedAmount = formatCLP(amount, showSymbol)

  return (
    <span
      className={cn(
        "font-mono",
        sizeClasses[size],
        colorClasses[color],
        className
      )}
    >
      {formattedAmount}
    </span>
  )
}
















