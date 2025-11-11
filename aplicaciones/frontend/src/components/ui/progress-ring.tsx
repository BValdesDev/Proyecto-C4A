import { cn } from "../../utilidades/cn"

interface ProgressRingProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  className?: string
  showValue?: boolean
  color?: string
  backgroundColor?: string
}

export function ProgressRing({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  className,
  showValue = true,
  color = "hsl(var(--primary))",
  backgroundColor = "hsl(var(--muted))",
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const progress = Math.min(Math.max(value / max, 0), 1)
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - progress * circumference

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-300 ease-in-out"
        />
      </svg>
      {showValue && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-semibold">
            {Math.round(progress * 100)}%
          </span>
        </div>
      )}
    </div>
  )
}

