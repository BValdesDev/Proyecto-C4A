import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { LucideIcon } from 'lucide-react'

interface QuickAction {
  title: string
  description: string
  icon: LucideIcon
  onClick: () => void
  variant?: 'default' | 'outline' | 'secondary'
}

interface QuickActionsProps {
  actions: QuickAction[]
  title?: string
  description?: string
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  actions,
  title = 'Acciones Rápidas',
  description = 'Accede a las funciones más utilizadas'
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {actions.map((action, index) => (
            <Button
              key={index}
              className="w-full justify-start"
              variant={action.variant || 'outline'}
              onClick={action.onClick}
            >
              <action.icon className="w-4 h-4 mr-2" />
              {action.title}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


