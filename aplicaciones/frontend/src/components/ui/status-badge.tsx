import { cn } from "../../utilidades/cn"
import { Badge } from "./badge"
import { CheckCircle, XCircle, Clock, AlertCircle } from "lucide-react"

interface StatusBadgeProps {
  status: "active" | "inactive" | "pending" | "error" | "success" | "warning"
  label?: string
  showIcon?: boolean
  className?: string
}

export function StatusBadge({
  status,
  label,
  showIcon = true,
  className,
}: StatusBadgeProps) {
  const statusConfig = {
    active: {
      variant: "default" as const,
      icon: CheckCircle,
      defaultLabel: "Activo",
      className: "bg-green-100 text-green-800 hover:bg-green-100",
    },
    inactive: {
      variant: "secondary" as const,
      icon: XCircle,
      defaultLabel: "Inactivo",
      className: "bg-gray-100 text-gray-800 hover:bg-gray-100",
    },
    pending: {
      variant: "secondary" as const,
      icon: Clock,
      defaultLabel: "Pendiente",
      className: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
    },
    error: {
      variant: "destructive" as const,
      icon: XCircle,
      defaultLabel: "Error",
      className: "bg-red-100 text-red-800 hover:bg-red-100",
    },
    success: {
      variant: "default" as const,
      icon: CheckCircle,
      defaultLabel: "Éxito",
      className: "bg-green-100 text-green-800 hover:bg-green-100",
    },
    warning: {
      variant: "secondary" as const,
      icon: AlertCircle,
      defaultLabel: "Advertencia",
      className: "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
    },
  }

  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <Badge
      variant={config.variant}
      className={cn(config.className, className)}
    >
      {showIcon && <Icon className="mr-1 h-3 w-3" />}
      {label || config.defaultLabel}
    </Badge>
  )
}

