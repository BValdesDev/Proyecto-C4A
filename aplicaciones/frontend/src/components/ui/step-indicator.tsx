import { cn } from "../../utilidades/cn"
import { Check } from "lucide-react"

interface Step {
  id: string
  title: string
  description?: string
  completed?: boolean
  current?: boolean
}

interface StepIndicatorProps {
  steps: Step[]
  className?: string
}

export function StepIndicator({ steps, className }: StepIndicatorProps) {
  return (
    <nav className={cn("flex items-center justify-center", className)}>
      <ol className="flex items-center space-x-8">
        {steps.map((step, index) => (
          <li key={step.id} className="flex items-center">
            <div className="flex items-center">
              {/* Step circle */}
              <div
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-medium",
                  step.completed
                    ? "border-primary bg-primary text-primary-foreground"
                    : step.current
                    ? "border-primary bg-background text-primary"
                    : "border-muted bg-background text-muted-foreground"
                )}
              >
                {step.completed ? (
                  <Check className="h-4 w-4" />
                ) : (
                  index + 1
                )}
              </div>
              
              {/* Step content */}
              <div className="ml-4 min-w-0">
                <div
                  className={cn(
                    "text-sm font-medium",
                    step.completed || step.current
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {step.title}
                </div>
                {step.description && (
                  <div className="text-xs text-muted-foreground">
                    {step.description}
                  </div>
                )}
              </div>
            </div>
            
            {/* Connector line */}
            {index < steps.length - 1 && (
              <div
                className={cn(
                  "ml-8 h-0.5 w-16",
                  step.completed ? "bg-primary" : "bg-muted"
                )}
              />
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}












