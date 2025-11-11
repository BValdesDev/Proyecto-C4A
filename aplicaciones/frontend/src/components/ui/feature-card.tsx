import { cn } from "../../utilidades/cn"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card"
import { Badge } from "./badge"
import { LucideIcon } from "lucide-react"

interface FeatureCardProps {
  title: string
  description: string
  icon: LucideIcon
  badge?: string
  isHighlighted?: boolean
  className?: string
}

export function FeatureCard({
  title,
  description,
  icon: Icon,
  badge,
  isHighlighted = false,
  className,
}: FeatureCardProps) {
  return (
    <Card className={cn(
      "relative transition-all hover:shadow-md",
      isHighlighted && "ring-2 ring-primary",
      className
    )}>
      {badge && (
        <div className="absolute -top-2 right-4">
          <Badge variant="secondary">{badge}</Badge>
        </div>
      )}
      <CardHeader>
        <div className="flex items-center space-x-2">
          <Icon className="h-5 w-5 text-primary" />
          <CardTitle className="text-lg">{title}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="text-sm leading-relaxed">
          {description}
        </CardDescription>
      </CardContent>
    </Card>
  )
}

