import { cn } from "../../utilidades/cn"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card"
import { Button } from "./button"
import { Badge } from "./badge"
import { Check, X } from "lucide-react"

interface PricingCardProps {
  name: string
  description: string
  price: {
    monthly: number
    yearly?: number
  }
  currency?: string
  period?: string
  features: Array<{
    name: string
    included: boolean
  }>
  isPopular?: boolean
  isCurrent?: boolean
  onSelect?: () => void
  className?: string
}

export function PricingCard({
  name,
  description,
  price,
  currency = "CLP",
  period = "mes",
  features,
  isPopular = false,
  isCurrent = false,
  onSelect,
  className,
}: PricingCardProps) {
  const formatPrice = (amount: number) => {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: currency,
      minimumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <Card className={cn(
      "relative transition-all hover:shadow-lg",
      isPopular && "ring-2 ring-primary shadow-lg",
      className
    )}>
      {isPopular && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge className="bg-primary text-primary-foreground">
            Más Popular
          </Badge>
        </div>
      )}
      
      <CardHeader className="text-center">
        <CardTitle className="text-xl">{name}</CardTitle>
        <CardDescription>{description}</CardDescription>
        <div className="mt-4">
          <div className="text-3xl font-bold">
            {formatPrice(price.monthly)}
          </div>
          <div className="text-sm text-muted-foreground">
            por {period}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <ul className="space-y-3">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center space-x-3">
              {feature.included ? (
                <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
              ) : (
                <X className="h-4 w-4 text-red-600 flex-shrink-0" />
              )}
              <span className={cn(
                "text-sm",
                !feature.included && "text-muted-foreground"
              )}>
                {feature.name}
              </span>
            </li>
          ))}
        </ul>
        
        <Button
          className="w-full"
          variant={isPopular ? "default" : "outline"}
          onClick={onSelect}
          disabled={isCurrent}
        >
          {isCurrent ? "Plan Actual" : "Seleccionar Plan"}
        </Button>
      </CardContent>
    </Card>
  )
}

