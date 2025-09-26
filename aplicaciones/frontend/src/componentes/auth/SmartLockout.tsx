import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Alert, AlertDescription } from '../ui/alert'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { 
  Shield, 
  Lock, 
  Clock, 
  AlertTriangle, 
  CheckCircle,
  RefreshCw,
  Mail,
  Phone
} from 'lucide-react'
import { api } from '../../utilidades/apiClient'

interface SmartLockoutProps {
  usuarioId: string
  onUnlockSuccess: () => void
  onUnlockFailure: (error: string) => void
}

interface LockoutStatus {
  bloqueado: boolean
  tipo_bloqueo: 'temporal' | 'permanente' | 'sospechoso'
  razon: string
  timestamp_bloqueo: string
  intentos_fallidos: number
  tiempo_restante?: number
  metodos_desbloqueo: string[]
  puede_desbloquear: boolean
}

interface UnlockMethod {
  id: string
  tipo: 'email' | 'sms' | 'backup_codes' | 'admin'
  nombre: string
  disponible: boolean
  tiempo_espera?: number
}

export const SmartLockout: React.FC<SmartLockoutProps> = ({
  usuarioId,
  onUnlockSuccess,
  onUnlockFailure
}) => {
  const [lockoutStatus, setLockoutStatus] = useState<LockoutStatus | null>(null)
  const [unlockMethods, setUnlockMethods] = useState<UnlockMethod[]>([])
  const [selectedMethod, setSelectedMethod] = useState<string>('')
  const [codigo, setCodigo] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tiempoRestante, setTiempoRestante] = useState(0)
  const [enviandoCodigo, setEnviandoCodigo] = useState(false)

  useEffect(() => {
    verificarEstadoBloqueo()
  }, [usuarioId])

  useEffect(() => {
    if (tiempoRestante > 0) {
      const timer = setTimeout(() => {
        setTiempoRestante(prev => prev - 1000)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [tiempoRestante])

  const verificarEstadoBloqueo = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.get(`/api/v1/auth/security/lockout-status/${usuarioId}`)
      setLockoutStatus(response.status)
      setUnlockMethods(response.metodos_desbloqueo)
      
      if (response.status.tiempo_restante) {
        setTiempoRestante(response.status.tiempo_restante * 1000)
      }

    } catch (err) {
      setError('Error verificando estado de bloqueo')
      console.error('Error verificando bloqueo:', err)
    } finally {
      setLoading(false)
    }
  }

  const enviarCodigoDesbloqueo = async () => {
    try {
      setEnviandoCodigo(true)
      setError(null)

      await api.post(`/api/v1/auth/security/send-unlock-code`, {
        usuario_id: usuarioId,
        metodo: selectedMethod
      })

      setTiempoRestante(300000) // 5 minutos

    } catch (err) {
      setError('Error enviando código de desbloqueo')
    } finally {
      setEnviandoCodigo(false)
    }
  }

  const verificarCodigoDesbloqueo = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.post(`/api/v1/auth/security/verify-unlock-code`, {
        usuario_id: usuarioId,
        metodo: selectedMethod,
        codigo: codigo
      })

      if (response.exitoso) {
        onUnlockSuccess()
      } else {
        onUnlockFailure('Código de desbloqueo incorrecto')
      }

    } catch (err) {
      onUnlockFailure('Error verificando código de desbloqueo')
    } finally {
      setLoading(false)
    }
  }

  const getLockoutIcon = (tipo: string) => {
    switch (tipo) {
      case 'temporal':
        return <Clock className="w-5 h-5 text-yellow-600" />
      case 'permanente':
        return <Lock className="w-5 h-5 text-red-600" />
      case 'sospechoso':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />
      default:
        return <Shield className="w-5 h-5" />
    }
  }

  const getLockoutColor = (tipo: string) => {
    switch (tipo) {
      case 'temporal':
        return 'border-yellow-200 bg-yellow-50'
      case 'permanente':
        return 'border-red-200 bg-red-50'
      case 'sospechoso':
        return 'border-orange-200 bg-orange-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const getMethodIcon = (tipo: string) => {
    switch (tipo) {
      case 'email':
        return <Mail className="w-4 h-4" />
      case 'sms':
        return <Phone className="w-4 h-4" />
      case 'backup_codes':
        return <Shield className="w-4 h-4" />
      case 'admin':
        return <CheckCircle className="w-4 h-4" />
      default:
        return <RefreshCw className="w-4 h-4" />
    }
  }

  const formatTiempoRestante = (ms: number) => {
    const minutos = Math.floor(ms / 60000)
    const segundos = Math.floor((ms % 60000) / 1000)
    return `${minutos}:${segundos.toString().padStart(2, '0')}`
  }

  if (loading && !lockoutStatus) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-c4a-blue-600"></div>
            <span className="ml-2">Verificando estado...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!lockoutStatus?.bloqueado) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Estado del bloqueo */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {getLockoutIcon(lockoutStatus.tipo_bloqueo)}
            <span>Cuenta Bloqueada</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className={getLockoutColor(lockoutStatus.tipo_bloqueo)}>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-2">
                <p className="font-medium">{lockoutStatus.razon}</p>
                <p className="text-sm">
                  Bloqueado el: {new Date(lockoutStatus.timestamp_bloqueo).toLocaleString('es-CL')}
                </p>
                <p className="text-sm">
                  Intentos fallidos: {lockoutStatus.intentos_fallidos}
                </p>
              </div>
            </AlertDescription>
          </Alert>

          {/* Tiempo restante para bloqueos temporales */}
          {lockoutStatus.tipo_bloqueo === 'temporal' && tiempoRestante > 0 && (
            <div className="text-center space-y-2">
              <p className="text-sm text-muted-foreground">
                Tiempo restante para desbloqueo automático:
              </p>
              <div className="text-2xl font-mono text-c4a-blue-600">
                {formatTiempoRestante(tiempoRestante)}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Métodos de desbloqueo */}
      {lockoutStatus.puede_desbloquear && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <RefreshCw className="w-5 h-5" />
              <span>Desbloquear Cuenta</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Selección de método */}
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Selecciona un método de desbloqueo:
              </label>
              <div className="space-y-2">
                {unlockMethods.map((method) => (
                  <div
                    key={method.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedMethod === method.id
                        ? 'border-c4a-blue-500 bg-c4a-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    } ${!method.disponible ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={() => method.disponible && setSelectedMethod(method.id)}
                  >
                    <div className="flex items-center space-x-3">
                      {getMethodIcon(method.tipo)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{method.nombre}</span>
                          {method.disponible ? (
                            <Badge variant="secondary" className="text-xs">
                              Disponible
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-xs">
                              No disponible
                            </Badge>
                          )}
                        </div>
                        {method.tiempo_espera && (
                          <p className="text-xs text-muted-foreground">
                            Tiempo de espera: {method.tiempo_espera} minutos
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Envío de código */}
            {selectedMethod && (
              <div className="space-y-3">
                <Button
                  onClick={enviarCodigoDesbloqueo}
                  disabled={enviandoCodigo || tiempoRestante > 0}
                  className="w-full"
                >
                  {enviandoCodigo ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Enviando código...</span>
                    </div>
                  ) : tiempoRestante > 0 ? (
                    <div className="flex items-center space-x-2">
                      <Clock className="w-4 h-4" />
                      <span>Espera {formatTiempoRestante(tiempoRestante)}</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <Mail className="w-4 h-4" />
                      <span>Enviar código de desbloqueo</span>
                    </div>
                  )}
                </Button>

                {/* Verificación de código */}
                {tiempoRestante === 0 && (
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">
                        Código de desbloqueo:
                      </label>
                      <input
                        type="text"
                        value={codigo}
                        onChange={(e) => setCodigo(e.target.value)}
                        placeholder="Ingresa el código recibido"
                        className="w-full p-3 border rounded-lg text-center text-lg font-mono"
                        maxLength={6}
                      />
                    </div>
                    
                    <Button
                      onClick={verificarCodigoDesbloqueo}
                      disabled={!codigo || loading}
                      className="w-full"
                    >
                      {loading ? (
                        <div className="flex items-center space-x-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Verificando...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="w-4 h-4" />
                          <span>Verificar código</span>
                        </div>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Información adicional */}
      <Card>
        <CardContent className="p-4">
          <div className="text-sm text-muted-foreground space-y-2">
            <p>
              <strong>¿Por qué se bloqueó mi cuenta?</strong>
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li>Múltiples intentos de login fallidos</li>
              <li>Actividad sospechosa detectada</li>
              <li>Intento de acceso desde ubicación inusual</li>
              <li>Violación de políticas de seguridad</li>
            </ul>
            <p className="mt-3">
              <strong>¿Necesitas ayuda?</strong> Contacta a nuestro equipo de soporte 
              si no puedes desbloquear tu cuenta.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

