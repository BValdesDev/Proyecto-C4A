import React, { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { toast } from 'sonner'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: string
  requiredSubscription?: string
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole,
  requiredSubscription 
}) => {
  const { usuario, loading, isTokenExpired, refreshAuthToken } = useAuth()
  const location = useLocation()

  // Manejar token expirado
  useEffect(() => {
    if (isTokenExpired && usuario) {
      toast.warning('Tu sesión ha expirado. Renovando...')
      refreshAuthToken()
    }
  }, [isTokenExpired, usuario, refreshAuthToken])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
          <p className="text-gray-600">Verificando autenticación...</p>
        </div>
      </div>
    )
  }

  if (!usuario) {
    return <Navigate to="/" state={{ from: location }} replace />
  }

  // Verificar rol requerido
  if (requiredRole && usuario.rol.nombre !== requiredRole) {
    toast.error('No tienes permisos para acceder a esta sección')
    return <Navigate to="/app/dashboard" replace />
  }

  // Verificar nivel de suscripción requerido
  if (requiredSubscription) {
    const subscriptionLevels = ['gratuito', 'pro', 'empresarial']
    const userLevel = subscriptionLevels.indexOf(usuario.organizacion.nivel_suscripcion)
    const requiredLevel = subscriptionLevels.indexOf(requiredSubscription)
    
    if (userLevel < requiredLevel) {
      toast.error('Se requiere una suscripción superior para acceder a esta función')
      return <Navigate to="/app/suscripciones" replace />
    }
  }

  // Verificar estado de la cuenta
  if (usuario.estado_cuenta === 'suspendido') {
    toast.error('Tu cuenta está suspendida. Contacta al soporte')
    return <Navigate to="/" replace />
  }

  if (usuario.estado_cuenta === 'inactivo') {
    toast.error('Tu cuenta está inactiva. Contacta al soporte')
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}