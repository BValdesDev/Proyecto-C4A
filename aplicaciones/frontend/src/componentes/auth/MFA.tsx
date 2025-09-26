import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Alert, AlertDescription } from '../ui/alert'
import { Badge } from '../ui/badge'
import { 
  Shield, 
  Smartphone, 
  Mail, 
  Key, 
  CheckCircle, 
  AlertCircle,
  Clock,
  RefreshCw
} from 'lucide-react'
import { api } from '../../utilidades/apiClient'

interface MFAProps {
  usuarioId: string
  onVerificacionExitosa: () => void
  onCancelar: () => void
}

interface MetodoMFA {
  id: string
  tipo: 'sms' | 'email' | 'totp' | 'backup'
  nombre: string
  configurado: boolean
  ultima_verificacion?: string
}

export const MFA: React.FC<MFAProps> = ({
  usuarioId,
  onVerificacionExitosa,
  onCancelar
}) => {
  const [metodos, setMetodos] = useState<MetodoMFA[]>([])
  const [metodoSeleccionado, setMetodoSeleccionado] = useState<string>('')
  const [codigo, setCodigo] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tiempoRestante, setTiempoRestante] = useState(0)
  const [intentos, setIntentos] = useState(0)
  const [bloqueado, setBloqueado] = useState(false)

  const MAX_INTENTOS = 3
  const TIEMPO_BLOQUEO = 15 * 60 * 1000 // 15 minutos

  useEffect(() => {
    cargarMetodosMFA()
  }, [usuarioId])

  useEffect(() => {
    if (tiempoRestante > 0) {
      const timer = setTimeout(() => {
        setTiempoRestante(prev => prev - 1000)
      }, 1000)
      return () => clearTimeout(timer)
    } else if (bloqueado) {
      setBloqueado(false)
      setIntentos(0)
    }
  }, [tiempoRestante, bloqueado])

  const cargarMetodosMFA = async () => {
    try {
      const response = await api.get(`/api/v1/auth/mfa/metodos/${usuarioId}`)
      setMetodos(response.metodos)
      
      // Seleccionar el primer método configurado
      const metodoDisponible = response.metodos.find((m: MetodoMFA) => m.configurado)
      if (metodoDisponible) {
        setMetodoSeleccionado(metodoDisponible.id)
      }
    } catch (err) {
      setError('Error cargando métodos de autenticación')
    }
  }

  const enviarCodigo = async () => {
    try {
      setLoading(true)
      setError(null)
      
      await api.post(`/api/v1/auth/mfa/enviar-codigo`, {
        usuario_id: usuarioId,
        metodo_id: metodoSeleccionado
      })
      
      setTiempoRestante(60000) // 1 minuto
      
    } catch (err) {
      setError('Error enviando código de verificación')
    } finally {
      setLoading(false)
    }
  }

  const verificarCodigo = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.post(`/api/v1/auth/mfa/verificar`, {
        usuario_id: usuarioId,
        metodo_id: metodoSeleccionado,
        codigo: codigo
      })
      
      if (response.verificado) {
        onVerificacionExitosa()
      } else {
        setIntentos(prev => prev + 1)
        setError('Código de verificación incorrecto')
        
        if (intentos + 1 >= MAX_INTENTOS) {
          setBloqueado(true)
          setTiempoRestante(TIEMPO_BLOQUEO)
          setError('Demasiados intentos fallidos. Cuenta bloqueada temporalmente.')
        }
      }
      
    } catch (err) {
      setError('Error verificando código')
    } finally {
      setLoading(false)
    }
  }

  const getMetodoIcon = (tipo: string) => {
    switch (tipo) {
      case 'sms':
        return <Smartphone className="w-5 h-5" />
      case 'email':
        return <Mail className="w-5 h-5" />
      case 'totp':
        return <Key className="w-5 h-5" />
      case 'backup':
        return <Shield className="w-5 h-5" />
      default:
        return <Shield className="w-5 h-5" />
    }
  }

  const getMetodoNombre = (tipo: string) => {
    switch (tipo) {
      case 'sms':
        return 'SMS'
      case 'email':
        return 'Email'
      case 'totp':
        return 'App Autenticador'
      case 'backup':
        return 'Códigos de Respaldo'
      default:
        return 'Desconocido'
    }
  }

  if (bloqueado) {
    return (
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <span>Cuenta Bloqueada</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              Demasiados intentos fallidos. Tu cuenta ha sido bloqueada por seguridad.
            </AlertDescription>
          </Alert>
          
          <div className="text-center space-y-2">
            <p className="text-sm text-muted-foreground">
              Tiempo restante:
            </p>
            <div className="text-2xl font-mono">
              {Math.floor(tiempoRestante / 60000)}:{(tiempoRestante % 60000 / 1000).toFixed(0).padStart(2, '0')}
            </div>
          </div>
          
          <Button 
            onClick={onCancelar} 
            variant="outline" 
            className="w-full"
          >
            Volver al Login
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="w-5 h-5 text-c4a-blue-600" />
          <span>Verificación de Seguridad</span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Selecciona un método de verificación para continuar
        </p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Métodos disponibles */}
        <div className="space-y-2">
          {metodos.map((metodo) => (
            <div
              key={metodo.id}
              className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                metodoSeleccionado === metodo.id
                  ? 'border-c4a-blue-500 bg-c4a-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              } ${!metodo.configurado ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => metodo.configurado && setMetodoSeleccionado(metodo.id)}
            >
              <div className="flex items-center space-x-3">
                {getMetodoIcon(metodo.tipo)}
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">
                      {getMetodoNombre(metodo.tipo)}
                    </span>
                    {metodo.configurado ? (
                      <Badge variant="secondary" className="text-xs">
                        Configurado
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-xs">
                        No configurado
                      </Badge>
                    )}
                  </div>
                  {metodo.ultima_verificacion && (
                    <p className="text-xs text-muted-foreground">
                      Última verificación: {new Date(metodo.ultima_verificacion).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Código de verificación */}
        {metodoSeleccionado && (
          <div className="space-y-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Código de verificación
              </label>
              <Input
                type="text"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
                placeholder="Ingresa el código"
                maxLength={6}
                className="text-center text-lg font-mono"
              />
            </div>
            
            <div className="flex space-x-2">
              <Button
                onClick={enviarCodigo}
                variant="outline"
                size="sm"
                disabled={loading || tiempoRestante > 0}
                className="flex-1"
              >
                {tiempoRestante > 0 ? (
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span>{Math.ceil(tiempoRestante / 1000)}s</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="w-4 h-4" />
                    <span>Reenviar</span>
                  </div>
                )}
              </Button>
              
              <Button
                onClick={verificarCodigo}
                disabled={!codigo || loading}
                className="flex-1"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Verificando...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4" />
                    <span>Verificar</span>
                  </div>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Intentos restantes */}
        {intentos > 0 && intentos < MAX_INTENTOS && (
          <Alert className="border-yellow-200 bg-yellow-50">
            <AlertCircle className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800">
              Intentos restantes: {MAX_INTENTOS - intentos}
            </AlertDescription>
          </Alert>
        )}

        {/* Botones de acción */}
        <div className="flex space-x-2">
          <Button
            onClick={onCancelar}
            variant="outline"
            className="flex-1"
          >
            Cancelar
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

