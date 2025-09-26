import React from 'react'
import { Card, CardContent } from '../ui/card'
import { Skeleton } from '../ui/skeleton'
import { Alert, AlertDescription } from '../ui/alert'
import { Button } from '../ui/button'
import { 
  Loader2, 
  AlertCircle, 
  RefreshCw, 
  CheckCircle,
  Clock,
  TrendingUp
} from 'lucide-react'

interface LoadingSpinnerProps {
  mensaje?: string
  tamaño?: 'sm' | 'md' | 'lg'
  className?: string
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  mensaje = 'Cargando...',
  tamaño = 'md',
  className = ''
}) => {
  const tamaños = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  }

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className="text-center">
        <Loader2 className={`animate-spin ${tamaños[tamaño]} text-c4a-blue-600 mx-auto mb-4`} />
        <p className="text-muted-foreground text-sm">{mensaje}</p>
      </div>
    </div>
  )
}

interface LoadingSkeletonProps {
  tipo: 'card' | 'list' | 'table' | 'form'
  cantidad?: number
  className?: string
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  tipo,
  cantidad = 3,
  className = ''
}) => {
  const renderSkeleton = () => {
    switch (tipo) {
      case 'card':
        return (
          <div className="space-y-4">
            {Array.from({ length: cantidad }).map((_, i) => (
              <Card key={i} className={className}>
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-4 w-2/3" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )
      
      case 'list':
        return (
          <div className="space-y-3">
            {Array.from({ length: cantidad }).map((_, i) => (
              <div key={i} className="flex items-center space-x-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        )
      
      case 'table':
        return (
          <div className="space-y-2">
            {Array.from({ length: cantidad }).map((_, i) => (
              <div key={i} className="flex space-x-4">
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-4 w-1/4" />
              </div>
            ))}
          </div>
        )
      
      case 'form':
        return (
          <div className="space-y-4">
            {Array.from({ length: cantidad }).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-1/3" />
                <Skeleton className="h-10 w-full" />
              </div>
            ))}
          </div>
        )
      
      default:
        return <Skeleton className="h-4 w-full" />
    }
  }

  return <div className={className}>{renderSkeleton()}</div>
}

interface ErrorStateProps {
  titulo?: string
  mensaje?: string
  accion?: {
    texto: string
    onClick: () => void
  }
  tipo?: 'error' | 'warning' | 'info'
  className?: string
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  titulo = 'Algo salió mal',
  mensaje = 'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.',
  accion,
  tipo = 'error',
  className = ''
}) => {
  const iconos = {
    error: AlertCircle,
    warning: AlertCircle,
    info: AlertCircle
  }

  const colores = {
    error: 'border-red-200 bg-red-50 text-red-800',
    warning: 'border-yellow-200 bg-yellow-50 text-yellow-800',
    info: 'border-blue-200 bg-blue-50 text-blue-800'
  }

  const Icono = iconos[tipo]

  return (
    <div className={`flex items-center justify-center min-h-[200px] ${className}`}>
      <Alert className={`max-w-md ${colores[tipo]}`}>
        <Icono className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-3">
            <h3 className="font-semibold">{titulo}</h3>
            <p className="text-sm">{mensaje}</p>
            {accion && (
              <Button
                onClick={accion.onClick}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>{accion.texto}</span>
              </Button>
            )}
          </div>
        </AlertDescription>
      </Alert>
    </div>
  )
}

interface EmptyStateProps {
  titulo?: string
  mensaje?: string
  accion?: {
    texto: string
    onClick: () => void
  }
  icono?: React.ReactNode
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  titulo = 'No hay datos',
  mensaje = 'No se encontraron elementos para mostrar.',
  accion,
  icono,
  className = ''
}) => {
  return (
    <div className={`flex items-center justify-center min-h-[200px] ${className}`}>
      <div className="text-center space-y-4">
        {icono || <div className="w-16 h-16 bg-muted rounded-full mx-auto" />}
        <div className="space-y-2">
          <h3 className="font-semibold text-lg">{titulo}</h3>
          <p className="text-muted-foreground text-sm">{mensaje}</p>
        </div>
        {accion && (
          <Button onClick={accion.onClick} variant="outline">
            {accion.texto}
          </Button>
        )}
      </div>
    </div>
  )
}

interface SuccessStateProps {
  titulo?: string
  mensaje?: string
  accion?: {
    texto: string
    onClick: () => void
  }
  className?: string
}

export const SuccessState: React.FC<SuccessStateProps> = ({
  titulo = '¡Éxito!',
  mensaje = 'La operación se completó correctamente.',
  accion,
  className = ''
}) => {
  return (
    <div className={`flex items-center justify-center min-h-[200px] ${className}`}>
      <Alert className="max-w-md border-green-200 bg-green-50">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <div className="space-y-3">
            <h3 className="font-semibold">{titulo}</h3>
            <p className="text-sm">{mensaje}</p>
            {accion && (
              <Button
                onClick={accion.onClick}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <span>{accion.texto}</span>
              </Button>
            )}
          </div>
        </AlertDescription>
      </Alert>
    </div>
  )
}

interface ProgressStateProps {
  mensaje?: string
  progreso?: number
  tiempoEstimado?: string
  className?: string
}

export const ProgressState: React.FC<ProgressStateProps> = ({
  mensaje = 'Procesando...',
  progreso = 0,
  tiempoEstimado,
  className = ''
}) => {
  return (
    <div className={`flex items-center justify-center min-h-[200px] ${className}`}>
      <div className="text-center space-y-4 max-w-md">
        <div className="space-y-2">
          <TrendingUp className="h-8 w-8 text-c4a-blue-600 mx-auto" />
          <h3 className="font-semibold">{mensaje}</h3>
          {tiempoEstimado && (
            <p className="text-sm text-muted-foreground">
              Tiempo estimado: {tiempoEstimado}
            </p>
          )}
        </div>
        
        {progreso > 0 && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progreso</span>
              <span>{Math.round(progreso)}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className="bg-c4a-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progreso}%` }}
              />
            </div>
          </div>
        )}
        
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>Por favor, no cierres esta ventana</span>
        </div>
      </div>
    </div>
  )
}

