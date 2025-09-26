import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Alert, AlertDescription } from '../ui/alert'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { 
  Shield, 
  Lock, 
  CheckCircle, 
  AlertTriangle,
  Eye,
  Bot,
  Smartphone,
  Mail,
  Key
} from 'lucide-react'
import { MFA } from './MFA'
import { PasswordValidator } from './PasswordValidator'
import { SecurityAnalyzer } from './SecurityAnalyzer'
import { SmartLockout } from './SmartLockout'
import { BotDetection } from './BotDetection'

interface SecuritySystemProps {
  usuarioId: string
  onSecurityComplete: () => void
  onSecurityFailed: (reason: string) => void
}

interface SecurityStatus {
  mfa_required: boolean
  password_validation: boolean
  threat_analysis: boolean
  lockout_check: boolean
  bot_detection: boolean
  overall_score: number
  security_level: 'low' | 'medium' | 'high' | 'critical'
}

export const SecuritySystem: React.FC<SecuritySystemProps> = ({
  usuarioId,
  onSecurityComplete,
  onSecurityFailed
}) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [password, setPassword] = useState('')
  const [passwordValid, setPasswordValid] = useState(false)
  const [mfaVerified, setMfaVerified] = useState(false)
  const [botVerified, setBotVerified] = useState(false)
  const [threatsDetected, setThreatsDetected] = useState(false)

  const securitySteps = [
    { id: 'bot_detection', name: 'Detección de Bots', icon: Bot, required: true },
    { id: 'password_validation', name: 'Validación de Contraseña', icon: Lock, required: true },
    { id: 'threat_analysis', name: 'Análisis de Amenazas', icon: Eye, required: true },
    { id: 'mfa_verification', name: 'Verificación MFA', icon: Smartphone, required: true },
    { id: 'lockout_check', name: 'Verificación de Bloqueo', icon: Shield, required: false }
  ]

  useEffect(() => {
    verificarEstadoSeguridad()
  }, [usuarioId])

  const verificarEstadoSeguridad = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await api.get(`/api/v1/auth/security/status/${usuarioId}`)
      setSecurityStatus(response.status)

      // Determinar paso inicial
      if (response.status.lockout_check) {
        setCurrentStep(4) // Verificación de bloqueo
      } else if (response.status.threat_analysis) {
        setCurrentStep(2) // Análisis de amenazas
      } else {
        setCurrentStep(0) // Detección de bots
      }

    } catch (err) {
      setError('Error verificando estado de seguridad')
      onSecurityFailed('Error en verificación de seguridad')
    } finally {
      setLoading(false)
    }
  }

  const handleStepComplete = (stepId: string, success: boolean, data?: any) => {
    if (!success) {
      onSecurityFailed(`Error en ${stepId}`)
      return
    }

    // Actualizar estado del paso
    switch (stepId) {
      case 'bot_detection':
        setBotVerified(true)
        break
      case 'password_validation':
        setPasswordValid(true)
        break
      case 'threat_analysis':
        setThreatsDetected(data?.threats?.length > 0)
        break
      case 'mfa_verification':
        setMfaVerified(true)
        break
    }

    // Avanzar al siguiente paso
    const nextStep = currentStep + 1
    if (nextStep < securitySteps.length) {
      setCurrentStep(nextStep)
    } else {
      // Todos los pasos completados
      evaluarSeguridadCompleta()
    }
  }

  const evaluarSeguridadCompleta = () => {
    const score = calcularScoreSeguridad()
    
    if (score >= 0.8) {
      onSecurityComplete()
    } else {
      onSecurityFailed('Nivel de seguridad insuficiente')
    }
  }

  const calcularScoreSeguridad = (): number => {
    let score = 0
    let totalSteps = 0

    if (botVerified) { score += 0.2; totalSteps++ }
    if (passwordValid) { score += 0.2; totalSteps++ }
    if (!threatsDetected) { score += 0.2; totalSteps++ }
    if (mfaVerified) { score += 0.2; totalSteps++ }
    if (securityStatus?.lockout_check) { score += 0.2; totalSteps++ }

    return totalSteps > 0 ? score / totalSteps : 0
  }

  const getStepIcon = (stepId: string) => {
    const step = securitySteps.find(s => s.id === stepId)
    return step ? step.icon : Shield
  }

  const getStepColor = (stepId: string, completed: boolean) => {
    if (completed) return 'text-green-600'
    if (currentStep === securitySteps.findIndex(s => s.id === stepId)) return 'text-c4a-blue-600'
    return 'text-gray-400'
  }

  const renderCurrentStep = () => {
    const step = securitySteps[currentStep]
    
    switch (step.id) {
      case 'bot_detection':
        return (
          <BotDetection
            onVerificationComplete={(isHuman, score) => 
              handleStepComplete('bot_detection', isHuman, { score })
            }
            onVerificationFailed={(reason) => 
              onSecurityFailed(`Detección de bots falló: ${reason}`)
            }
          />
        )
      
      case 'password_validation':
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Contraseña:
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Ingresa tu contraseña"
                className="w-full p-3 border rounded-lg"
              />
            </div>
            <PasswordValidator
              password={password}
              onValidationChange={(isValid, score) => {
                setPasswordValid(isValid)
                if (isValid) {
                  handleStepComplete('password_validation', true, { score })
                }
              }}
            />
          </div>
        )
      
      case 'threat_analysis':
        return (
          <SecurityAnalyzer
            usuarioId={usuarioId}
            onThreatDetected={(threat) => {
              setThreatsDetected(true)
              onSecurityFailed(`Amenaza detectada: ${threat.descripcion}`)
            }}
            onRiskAssessment={(risk) => {
              handleStepComplete('threat_analysis', risk.nivel !== 'critical', risk)
            }}
          />
        )
      
      case 'mfa_verification':
        return (
          <MFA
            usuarioId={usuarioId}
            onVerificacionExitosa={() => 
              handleStepComplete('mfa_verification', true)
            }
            onCancelar={() => 
              onSecurityFailed('Verificación MFA cancelada')
            }
          />
        )
      
      case 'lockout_check':
        return (
          <SmartLockout
            usuarioId={usuarioId}
            onUnlockSuccess={() => 
              handleStepComplete('lockout_check', true)
            }
            onUnlockFailure={(reason) => 
              onSecurityFailed(`Desbloqueo falló: ${reason}`)
            }
          />
        )
      
      default:
        return null
    }
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-c4a-blue-600"></div>
            <span className="ml-2">Verificando seguridad...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Progreso de seguridad */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="w-5 h-5" />
            <span>Sistema de Seguridad</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            {securitySteps.map((step, index) => {
              const Icon = step.icon
              const completed = index < currentStep
              const current = index === currentStep
              
              return (
                <div
                  key={step.id}
                  className={`flex items-center space-x-3 p-3 rounded-lg ${
                    current ? 'bg-c4a-blue-50 border border-c4a-blue-200' : ''
                  }`}
                >
                  <Icon className={`w-5 h-5 ${getStepColor(step.id, completed)}`} />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium">{step.name}</span>
                      {completed && <CheckCircle className="w-4 h-4 text-green-600" />}
                      {current && <Badge variant="secondary">En progreso</Badge>}
                    </div>
                    {step.required && (
                      <p className="text-xs text-muted-foreground">Requerido</p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Paso actual */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {React.createElement(getStepIcon(securitySteps[currentStep].id), { className: "w-5 h-5" })}
            <span>{securitySteps[currentStep].name}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderCurrentStep()}
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            {error}
          </AlertDescription>
        </Alert>
      )}

      {/* Información de seguridad */}
      <Card>
        <CardContent className="p-4">
          <div className="text-sm text-muted-foreground space-y-2">
            <p>
              <strong>¿Por qué necesitamos verificar tu identidad?</strong>
            </p>
            <ul className="list-disc list-inside space-y-1">
              <li>Proteger tu cuenta de accesos no autorizados</li>
              <li>Detectar actividad sospechosa</li>
              <li>Cumplir con estándares de seguridad</li>
              <li>Prevenir ataques automatizados</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

