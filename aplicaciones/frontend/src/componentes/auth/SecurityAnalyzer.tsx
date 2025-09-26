import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Alert, AlertDescription } from '../ui/alert'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Eye, 
  Lock,
  Globe,
  Smartphone,
  Monitor,
  Wifi,
  MapPin
} from 'lucide-react'
import { api } from '../../utilidades/apiClient'

interface SecurityAnalyzerProps {
  usuarioId: string
  onThreatDetected: (threat: SecurityThreat) => void
  onRiskAssessment: (risk: RiskAssessment) => void
}

interface SecurityThreat {
  id: string
  tipo: 'suspicious_login' | 'brute_force' | 'geographic_anomaly' | 'device_anomaly' | 'time_anomaly'
  severidad: 'low' | 'medium' | 'high' | 'critical'
  descripcion: string
  timestamp: string
  ubicacion?: {
    pais: string
    ciudad: string
    coordenadas: [number, number]
  }
  dispositivo?: {
    tipo: string
    navegador: string
    sistema_operativo: string
  }
  accion_requerida: boolean
}

interface RiskAssessment {
  score: number
  nivel: 'low' | 'medium' | 'high' | 'critical'
  factores: RiskFactor[]
  recomendaciones: string[]
}

interface RiskFactor {
  id: string
  nombre: string
  impacto: number
  descripcion: string
  mitigado: boolean
}

interface LoginAttempt {
  id: string
  timestamp: string
  ip: string
  user_agent: string
  ubicacion: {
    pais: string
    ciudad: string
    coordenadas: [number, number]
  }
  exitoso: boolean
  razon_fallo?: string
}

export const SecurityAnalyzer: React.FC<SecurityAnalyzerProps> = ({
  usuarioId,
  onThreatDetected,
  onRiskAssessment
}) => {
  const [threats, setThreats] = useState<SecurityThreat[]>([])
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | null>(null)
  const [loginAttempts, setLoginAttempts] = useState<LoginAttempt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    analizarSeguridad()
  }, [usuarioId])

  const analizarSeguridad = async () => {
    try {
      setLoading(true)
      setError(null)

      // Obtener intentos de login recientes
      const attemptsResponse = await api.get(`/api/v1/auth/security/login-attempts/${usuarioId}`)
      setLoginAttempts(attemptsResponse.attempts)

      // Analizar amenazas
      const threatsResponse = await api.post(`/api/v1/auth/security/analyze-threats`, {
        usuario_id: usuarioId,
        intentos: attemptsResponse.attempts
      })
      setThreats(threatsResponse.threats)

      // Evaluar riesgo
      const riskResponse = await api.post(`/api/v1/auth/security/assess-risk`, {
        usuario_id: usuarioId,
        amenazas: threatsResponse.threats,
        intentos: attemptsResponse.attempts
      })
      setRiskAssessment(riskResponse.assessment)

      // Notificar amenazas críticas
      threatsResponse.threats.forEach((threat: SecurityThreat) => {
        if (threat.severidad === 'critical' || threat.severidad === 'high') {
          onThreatDetected(threat)
        }
      })

      // Notificar evaluación de riesgo
      onRiskAssessment(riskResponse.assessment)

    } catch (err) {
      setError('Error analizando seguridad')
      console.error('Error en análisis de seguridad:', err)
    } finally {
      setLoading(false)
    }
  }

  const getThreatIcon = (tipo: string) => {
    switch (tipo) {
      case 'suspicious_login':
        return <Eye className="w-4 h-4" />
      case 'brute_force':
        return <Lock className="w-4 h-4" />
      case 'geographic_anomaly':
        return <MapPin className="w-4 h-4" />
      case 'device_anomaly':
        return <Monitor className="w-4 h-4" />
      case 'time_anomaly':
        return <Smartphone className="w-4 h-4" />
      default:
        return <Shield className="w-4 h-4" />
    }
  }

  const getThreatColor = (severidad: string) => {
    switch (severidad) {
      case 'critical':
        return 'bg-red-500'
      case 'high':
        return 'bg-orange-500'
      case 'medium':
        return 'bg-yellow-500'
      case 'low':
        return 'bg-blue-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getRiskColor = (nivel: string) => {
    switch (nivel) {
      case 'critical':
        return 'text-red-600'
      case 'high':
        return 'text-orange-600'
      case 'medium':
        return 'text-yellow-600'
      case 'low':
        return 'text-green-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('es-CL', {
      timeZone: 'America/Santiago'
    })
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-c4a-blue-600"></div>
            <span className="ml-2">Analizando seguridad...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Evaluación de riesgo */}
      {riskAssessment && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span>Evaluación de Riesgo</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Nivel de riesgo:</span>
              <Badge 
                variant={riskAssessment.nivel === 'low' ? 'default' : 'destructive'}
                className={getRiskColor(riskAssessment.nivel)}
              >
                {riskAssessment.nivel.toUpperCase()}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Puntuación de riesgo:</span>
                <span className="font-mono">{riskAssessment.score}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    riskAssessment.score < 30 ? 'bg-green-500' :
                    riskAssessment.score < 60 ? 'bg-yellow-500' :
                    riskAssessment.score < 80 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${riskAssessment.score}%` }}
                />
              </div>
            </div>

            {/* Factores de riesgo */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Factores de riesgo:</h4>
              {riskAssessment.factores.map((factor) => (
                <div key={factor.id} className="flex items-center space-x-2 text-sm">
                  {factor.mitigado ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-yellow-600" />
                  )}
                  <span className={factor.mitigado ? 'text-green-600' : 'text-yellow-600'}>
                    {factor.nombre}
                  </span>
                </div>
              ))}
            </div>

            {/* Recomendaciones */}
            {riskAssessment.recomendaciones.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Recomendaciones:</h4>
                <ul className="text-sm space-y-1">
                  {riskAssessment.recomendaciones.map((rec, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <span className="text-c4a-blue-600">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Amenazas detectadas */}
      {threats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span>Amenazas Detectadas</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {threats.map((threat) => (
              <div key={threat.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getThreatIcon(threat.tipo)}
                    <span className="font-medium">{threat.descripcion}</span>
                  </div>
                  <Badge 
                    variant="destructive"
                    className={getThreatColor(threat.severidad)}
                  >
                    {threat.severidad.toUpperCase()}
                  </Badge>
                </div>
                
                <div className="text-sm text-muted-foreground">
                  {formatTimestamp(threat.timestamp)}
                </div>
                
                {threat.ubicacion && (
                  <div className="flex items-center space-x-2 text-sm">
                    <MapPin className="w-4 h-4" />
                    <span>
                      {threat.ubicacion.ciudad}, {threat.ubicacion.pais}
                    </span>
                  </div>
                )}
                
                {threat.dispositivo && (
                  <div className="flex items-center space-x-2 text-sm">
                    <Monitor className="w-4 h-4" />
                    <span>
                      {threat.dispositivo.tipo} - {threat.dispositivo.sistema_operativo}
                    </span>
                  </div>
                )}
                
                {threat.accion_requerida && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-800">
                      Se requiere acción inmediata. Revisa tu cuenta de seguridad.
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Intentos de login recientes */}
      {loginAttempts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="w-5 h-5" />
              <span>Actividad Reciente</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {loginAttempts.slice(0, 5).map((attempt) => (
              <div key={attempt.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  {attempt.exitoso ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-600" />
                  )}
                  <div>
                    <div className="text-sm font-medium">
                      {attempt.ubicacion.ciudad}, {attempt.ubicacion.pais}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {formatTimestamp(attempt.timestamp)}
                    </div>
                  </div>
                </div>
                <Badge variant={attempt.exitoso ? "default" : "destructive"}>
                  {attempt.exitoso ? 'Exitoso' : 'Fallido'}
                </Badge>
              </div>
            ))}
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

      {/* Botón de actualización */}
      <div className="flex justify-center">
        <Button onClick={analizarSeguridad} variant="outline">
          Actualizar Análisis
        </Button>
      </div>
    </div>
  )
}

