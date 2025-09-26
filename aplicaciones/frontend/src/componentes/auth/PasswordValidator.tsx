import React, { useState, useEffect } from 'react'
import { Card, CardContent } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { 
  CheckCircle, 
  XCircle, 
  Eye, 
  EyeOff, 
  Shield,
  AlertTriangle
} from 'lucide-react'

interface PasswordValidatorProps {
  password: string
  onValidationChange: (isValid: boolean, score: number) => void
  showStrength?: boolean
  showRequirements?: boolean
}

interface PasswordRequirement {
  id: string
  text: string
  test: (password: string) => boolean
  weight: number
}

const requirements: PasswordRequirement[] = [
  {
    id: 'length',
    text: 'Al menos 8 caracteres',
    test: (pwd) => pwd.length >= 8,
    weight: 1
  },
  {
    id: 'uppercase',
    text: 'Al menos una letra mayúscula',
    test: (pwd) => /[A-Z]/.test(pwd),
    weight: 1
  },
  {
    id: 'lowercase',
    text: 'Al menos una letra minúscula',
    test: (pwd) => /[a-z]/.test(pwd),
    weight: 1
  },
  {
    id: 'number',
    text: 'Al menos un número',
    test: (pwd) => /\d/.test(pwd),
    weight: 1
  },
  {
    id: 'special',
    text: 'Al menos un carácter especial',
    test: (pwd) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd),
    weight: 2
  },
  {
    id: 'no_common',
    text: 'No usar contraseñas comunes',
    test: (pwd) => !isCommonPassword(pwd),
    weight: 2
  },
  {
    id: 'no_personal',
    text: 'No usar información personal',
    test: (pwd) => !containsPersonalInfo(pwd),
    weight: 2
  }
]

const commonPasswords = [
  'password', '123456', '123456789', 'qwerty', 'abc123',
  'password123', 'admin', 'letmein', 'welcome', 'monkey',
  '1234567890', 'password1', 'qwerty123', 'dragon', 'master'
]

function isCommonPassword(password: string): boolean {
  return commonPasswords.some(common => 
    password.toLowerCase().includes(common.toLowerCase())
  )
}

function containsPersonalInfo(password: string): boolean {
  // Esta función debería verificar contra datos del usuario
  // Por ahora, solo verificamos patrones básicos
  const personalPatterns = [
    /(19|20)\d{2}/, // Años
    /\d{4}/, // Códigos postales
    /(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)/i
  ]
  
  return personalPatterns.some(pattern => pattern.test(password))
}

function calculatePasswordScore(password: string): number {
  let score = 0
  let totalWeight = 0
  
  requirements.forEach(req => {
    totalWeight += req.weight
    if (req.test(password)) {
      score += req.weight
    }
  })
  
  return totalWeight > 0 ? (score / totalWeight) * 100 : 0
}

function getPasswordStrength(score: number): {
  label: string
  color: string
  description: string
} {
  if (score < 30) {
    return {
      label: 'Muy Débil',
      color: 'bg-red-500',
      description: 'Fácil de adivinar'
    }
  } else if (score < 50) {
    return {
      label: 'Débil',
      color: 'bg-orange-500',
      description: 'Necesita mejoras'
    }
  } else if (score < 70) {
    return {
      label: 'Regular',
      color: 'bg-yellow-500',
      description: 'Aceptable pero mejorable'
    }
  } else if (score < 90) {
    return {
      label: 'Fuerte',
      color: 'bg-blue-500',
      description: 'Buena seguridad'
    }
  } else {
    return {
      label: 'Muy Fuerte',
      color: 'bg-green-500',
      description: 'Excelente seguridad'
    }
  }
}

export const PasswordValidator: React.FC<PasswordValidatorProps> = ({
  password,
  onValidationChange,
  showStrength = true,
  showRequirements = true
}) => {
  const [showPassword, setShowPassword] = useState(false)
  const [score, setScore] = useState(0)
  const [isValid, setIsValid] = useState(false)

  useEffect(() => {
    const newScore = calculatePasswordScore(password)
    const newIsValid = newScore >= 70 // Mínimo 70% para ser válida
    
    setScore(newScore)
    setIsValid(newIsValid)
    onValidationChange(newIsValid, newScore)
  }, [password, onValidationChange])

  const strength = getPasswordStrength(score)
  const validRequirements = requirements.filter(req => req.test(password))
  const invalidRequirements = requirements.filter(req => !req.test(password))

  return (
    <div className="space-y-4">
      {/* Indicador de fortaleza */}
      {showStrength && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Fortaleza de la contraseña</span>
                <Badge 
                  variant={score >= 70 ? "default" : "destructive"}
                  className="text-xs"
                >
                  {strength.label}
                </Badge>
              </div>
              
              <div className="space-y-2">
                <Progress value={score} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  {strength.description}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Requisitos de contraseña */}
      {showRequirements && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm font-medium">Requisitos de seguridad</span>
              </div>
              
              <div className="space-y-2">
                {requirements.map((req) => {
                  const isValid = req.test(password)
                  return (
                    <div
                      key={req.id}
                      className={`flex items-center space-x-2 text-sm ${
                        isValid ? 'text-green-600' : 'text-gray-500'
                      }`}
                    >
                      {isValid ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <XCircle className="w-4 h-4" />
                      )}
                      <span>{req.text}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Advertencias de seguridad */}
      {password.length > 0 && (
        <div className="space-y-2">
          {isCommonPassword(password) && (
            <div className="flex items-center space-x-2 text-sm text-red-600">
              <AlertTriangle className="w-4 h-4" />
              <span>Esta contraseña es muy común y fácil de adivinar</span>
            </div>
          )}
          
          {containsPersonalInfo(password) && (
            <div className="flex items-center space-x-2 text-sm text-red-600">
              <AlertTriangle className="w-4 h-4" />
              <span>Evita usar información personal en tu contraseña</span>
            </div>
          )}
          
          {password.length < 8 && (
            <div className="flex items-center space-x-2 text-sm text-yellow-600">
              <AlertTriangle className="w-4 h-4" />
              <span>La contraseña debe tener al menos 8 caracteres</span>
            </div>
          )}
        </div>
      )}

      {/* Botón para mostrar/ocultar contraseña */}
      <div className="flex items-center space-x-2">
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="flex items-center space-x-2 text-sm text-muted-foreground hover:text-foreground"
        >
          {showPassword ? (
            <>
              <EyeOff className="w-4 h-4" />
              <span>Ocultar contraseña</span>
            </>
          ) : (
            <>
              <Eye className="w-4 h-4" />
              <span>Mostrar contraseña</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

