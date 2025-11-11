import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Alert, AlertDescription } from '../ui/alert'
import { Button } from '../ui/button'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Llamar callback personalizado si existe
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined })
  }

  render() {
    if (this.state.hasError) {
      // Si hay un fallback personalizado, usarlo
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Fallback por defecto
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <div className="max-w-md w-full">
            <Alert className="border-red-200 bg-red-50">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-lg mb-2">
                      Algo salió mal
                    </h3>
                    <p className="text-sm">
                      Ha ocurrido un error inesperado. Por favor, intenta recargar la página.
                    </p>
                  </div>
                  
                  {process.env.NODE_ENV === 'development' && this.state.error && (
                    <details className="mt-4">
                      <summary className="cursor-pointer text-sm font-medium">
                        Detalles del error (desarrollo)
                      </summary>
                      <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-auto">
                        {this.state.error.toString()}
                      </pre>
                    </details>
                  )}
                  
                  <div className="flex space-x-2 mt-4">
                    <Button
                      onClick={this.handleReset}
                      variant="outline"
                      size="sm"
                      className="flex items-center space-x-2"
                    >
                      <RefreshCw className="h-4 w-4" />
                      <span>Reintentar</span>
                    </Button>
                    
                    <Button
                      onClick={() => window.location.reload()}
                      variant="default"
                      size="sm"
                      className="flex items-center space-x-2"
                    >
                      <RefreshCw className="h-4 w-4" />
                      <span>Recargar página</span>
                    </Button>
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook para usar ErrorBoundary de manera funcional
export const useErrorHandler = () => {
  const [error, setError] = React.useState<Error | null>(null)

  const resetError = React.useCallback(() => {
    setError(null)
  }, [])

  const captureError = React.useCallback((error: Error) => {
    setError(error)
  }, [])

  React.useEffect(() => {
    if (error) {
      throw error
    }
  }, [error])

  return { captureError, resetError }
}

