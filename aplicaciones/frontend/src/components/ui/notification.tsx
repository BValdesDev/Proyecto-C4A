import { cn } from "../../utilidades/cn"
import { Button } from "./button"
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from "lucide-react"

interface NotificationProps {
  title: string
  description?: string
  type?: "success" | "error" | "warning" | "info"
  onClose?: () => void
  className?: string
}

export function Notification({
  title,
  description,
  type = "info",
  onClose,
  className,
}: NotificationProps) {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  }

  const colors = {
    success: "border-green-200 bg-green-50 text-green-800",
    error: "border-red-200 bg-red-50 text-red-800",
    warning: "border-yellow-200 bg-yellow-50 text-yellow-800",
    info: "border-blue-200 bg-blue-50 text-blue-800",
  }

  const Icon = icons[type]

  return (
    <div
      className={cn(
        "relative rounded-lg border p-4 shadow-sm",
        colors[type],
        className
      )}
    >
      <div className="flex items-start space-x-3">
        <Icon className="h-5 w-5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium">{title}</h4>
          {description && (
            <p className="mt-1 text-sm opacity-90">{description}</p>
          )}
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-6 w-6 p-0 flex-shrink-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  )
}

