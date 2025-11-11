import { cn } from "../../utilidades/cn"
import { LucideIcon } from "lucide-react"

interface TimelineItem {
  id: string
  title: string
  description?: string
  date?: string
  icon?: LucideIcon
  status?: "completed" | "current" | "upcoming"
}

interface TimelineProps {
  items: TimelineItem[]
  className?: string
}

export function Timeline({ items, className }: TimelineProps) {
  return (
    <div className={cn("relative", className)}>
      {/* Vertical line */}
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />
      
      <div className="space-y-6">
        {items.map((item, index) => (
          <div key={item.id} className="relative flex items-start space-x-4">
            {/* Icon/Status indicator */}
            <div
              className={cn(
                "relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 bg-background",
                item.status === "completed"
                  ? "border-primary bg-primary text-primary-foreground"
                  : item.status === "current"
                  ? "border-primary bg-background text-primary"
                  : "border-muted bg-background text-muted-foreground"
              )}
            >
              {item.icon ? (
                <item.icon className="h-4 w-4" />
              ) : (
                <div className="h-2 w-2 rounded-full bg-current" />
              )}
            </div>
            
            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h3
                  className={cn(
                    "text-sm font-medium",
                    item.status === "completed" || item.status === "current"
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {item.title}
                </h3>
                {item.date && (
                  <time className="text-xs text-muted-foreground">
                    {item.date}
                  </time>
                )}
              </div>
              {item.description && (
                <p className="mt-1 text-sm text-muted-foreground">
                  {item.description}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

