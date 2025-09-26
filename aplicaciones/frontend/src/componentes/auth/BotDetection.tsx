import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Alert, AlertDescription } from '../ui/alert'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { 
  Shield, 
  Bot, 
  Eye, 
  MousePointer, 
  Clock,
  CheckCircle,
  AlertTriangle,
  RefreshCw
} from 'lucide-react'
import { api } from '../../utilidades/apiClient'

interface BotDetectionProps {
  onVerificationComplete: (isHuman: boolean, score: number) => void
  onVerificationFailed: (reason: string) => void
}

interface BehaviorAnalysis {
  mouse_movements: number
  keystroke_timing: number[]
  scroll_behavior: number
  click_patterns: number[]
  time_on_page: number
  human_score: number
}

interface CaptchaChallenge {
  id: string
  tipo: 'image' | 'audio' | 'math' | 'text'
  pregunta: string
  opciones?: string[]
  imagen?: string
  audio?: string
  tiempo_limite: number
}

export const BotDetection: React.FC<BotDetectionProps> = ({
  onVerificationComplete,
  onVerificationFailed
}) => {
  const [behaviorData, setBehaviorData] = useState<BehaviorAnalysis | null>(null)
  const [captchaChallenge, setCaptchaChallenge] = useState<CaptchaChallenge | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tiempoRestante, setTiempoRestante] = useState(0)
  const [respuesta, setRespuesta] = useState('')
  const [verificando, setVerificando] = useState(false)
  
  const startTime = useRef<number>(Date.now())
  const mouseMovements = useRef<number>(0)
  const keystrokes = useRef<number[]>([])
  const scrollEvents = useRef<number>(0)
  const clickEvents = useRef<number[]>([])

  useEffect(() => {
    // Iniciar recolección de datos de comportamiento
    iniciarRecoleccionDatos()
    
    // Configurar listeners
    const handleMouseMove = () => mouseMovements.current++
    const handleKeyPress = (e: KeyboardEvent) => {
      keystrokes.current.push(Date.now())
    }
    const handleScroll = () => scrollEvents.current++
    const handleClick = (e: MouseEvent) => {
      clickEvents.current.push(Date.now())
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('keypress', handleKeyPress)
    document.addEventListener('scroll', handleScroll)
    document.addEventListener('click', handleClick)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('keypress', handleKeyPress)
      document.removeEventListener('scroll', handleScroll)
      document.removeEventListener('click', handleClick)
    }
  }, [])

  useEffect(() => {
    if (tiempoRestante > 0) {
      const timer = setTimeout(() => {
        setTiempoRestante(prev => prev - 1000)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [tiempoRestante])

  const iniciarRecoleccionDatos = () => {
    // Simular recolección de datos durante 5 segundos
    setTimeout(() => {
      analizarComportamiento()
    }, 5000)
  }

  const analizarComportamiento = async () => {
    try {
      setLoading(true)
      setError(null)

      const tiempoEnPagina = Date.now() - startTime.current
      
      const analysis: BehaviorAnalysis = {
        mouse_movements: mouseMovements.current,
        keystroke_timing: keystrokes.current,
        scroll_behavior: scrollEvents.current,
        click_patterns: clickEvents.current,
        time_on_page: tiempoEnPagina,
        human_score: calcularScoreHumano()
      }

      setBehaviorData(analysis)

      // Si el score es muy bajo, requerir CAPTCHA
      if (analysis.human_score < 0.3) {
        await solicitarCaptcha()
      } else {
        onVerificationComplete(true, analysis.human_score)
      }

    } catch (err) {
      setError('Error analizando comportamiento')
      onVerificationFailed('Error en análisis de comportamiento')
    } finally {
      setLoading(false)
    }
  }

  const calcularScoreHumano = (): number => {
    let score = 0.5 // Score base

    // Análisis de movimientos del mouse
    if (mouseMovements.current > 10) score += 0.2
    if (mouseMovements.current > 50) score += 0.1

    // Análisis de timing de teclas
    if (keystrokes.current.length > 5) {
      const intervals = keystrokes.current.slice(1).map((time, i) => 
        time - keystrokes.current[i]
      )
      const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length
      
      // Timing humano típico: 100-500ms entre teclas
      if (avgInterval > 100 && avgInterval < 500) score += 0.2
    }

    // Análisis de scroll
    if (scrollEvents.current > 0) score += 0.1

    // Análisis de tiempo en página
    const tiempoEnPagina = Date.now() - startTime.current
    if (tiempoEnPagina > 3000) score += 0.1

    return Math.min(score, 1.0)
  }

  const solicitarCaptcha = async () => {
    try {
      const response = await api.post('/api/v1/auth/security/captcha-challenge', {
        tipo: 'image' // Por defecto, imagen
      })
      
      setCaptchaChallenge(response.challenge)
      setTiempoRestante(response.challenge.tiempo_limite * 1000)

    } catch (err) {
      setError('Error cargando CAPTCHA')
      onVerificationFailed('Error cargando CAPTCHA')
    }
  }

  const verificarCaptcha = async () => {
    try {
      setVerificando(true)
      setError(null)

      const response = await api.post('/api/v1/auth/security/verify-captcha', {
        challenge_id: captchaChallenge?.id,
        respuesta: respuesta
      })

      if (response.correcto) {
        onVerificationComplete(true, 0.8) // Score alto para CAPTCHA resuelto
      } else {
        setError('Respuesta incorrecta. Intenta nuevamente.')
        setRespuesta('')
        await solicitarCaptcha() // Nuevo CAPTCHA
      }

    } catch (err) {
      setError('Error verificando CAPTCHA')
      onVerificationFailed('Error verificando CAPTCHA')
    } finally {
      setVerificando(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600'
    if (score >= 0.4) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 0.7) return 'Comportamiento Humano'
    if (score >= 0.4) return 'Sospechoso'
    return 'Posible Bot'
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center space-y-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-c4a-blue-600 mx-auto"></div>
            <p>Analizando comportamiento...</p>
            <div className="text-sm text-muted-foreground">
              <p>• Movimientos del mouse: {mouseMovements.current}</p>
              <p>• Teclas presionadas: {keystrokes.current.length}</p>
              <p>• Eventos de scroll: {scrollEvents.current}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Análisis de comportamiento */}
      {behaviorData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="w-5 h-5" />
              <span>Análisis de Comportamiento</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Score de humanidad:</span>
              <Badge 
                variant={behaviorData.human_score >= 0.7 ? "default" : "destructive"}
                className={getScoreColor(behaviorData.human_score)}
              >
                {getScoreLabel(behaviorData.human_score)}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Puntuación:</span>
                <span className="font-mono">{Math.round(behaviorData.human_score * 100)}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    behaviorData.human_score >= 0.7 ? 'bg-green-500' :
                    behaviorData.human_score >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${behaviorData.human_score * 100}%` }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Movimientos del mouse:</span>
                <span className="ml-2 font-mono">{behaviorData.mouse_movements}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Teclas presionadas:</span>
                <span className="ml-2 font-mono">{behaviorData.keystroke_timing.length}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Eventos de scroll:</span>
                <span className="ml-2 font-mono">{behaviorData.scroll_behavior}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Tiempo en página:</span>
                <span className="ml-2 font-mono">{Math.round(behaviorData.time_on_page / 1000)}s</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* CAPTCHA Challenge */}
      {captchaChallenge && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bot className="w-5 h-5" />
              <span>Verificación de Seguridad</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert className="border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
              <AlertDescription className="text-yellow-800">
                Se requiere verificación adicional para continuar.
              </AlertDescription>
            </Alert>

            <div className="space-y-4">
              <div className="text-center">
                <h3 className="font-medium mb-2">{captchaChallenge.pregunta}</h3>
                
                {captchaChallenge.tipo === 'image' && captchaChallenge.imagen && (
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <img 
                      src={captchaChallenge.imagen} 
                      alt="CAPTCHA" 
                      className="mx-auto max-w-full h-auto"
                    />
                  </div>
                )}
                
                {captchaChallenge.tipo === 'math' && (
                  <div className="text-2xl font-mono bg-gray-100 p-4 rounded-lg">
                    {captchaChallenge.pregunta}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Respuesta:
                </label>
                <input
                  type="text"
                  value={respuesta}
                  onChange={(e) => setRespuesta(e.target.value)}
                  placeholder="Ingresa tu respuesta"
                  className="w-full p-3 border rounded-lg text-center text-lg font-mono"
                />
              </div>

              {tiempoRestante > 0 && (
                <div className="text-center">
                  <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    <span>Tiempo restante: {Math.ceil(tiempoRestante / 1000)}s</span>
                  </div>
                </div>
              )}

              <Button
                onClick={verificarCaptcha}
                disabled={!respuesta || verificando || tiempoRestante === 0}
                className="w-full"
              >
                {verificando ? (
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

              <Button
                onClick={solicitarCaptcha}
                variant="outline"
                className="w-full"
              >
                <div className="flex items-center space-x-2">
                  <RefreshCw className="w-4 h-4" />
                  <span>Nuevo CAPTCHA</span>
                </div>
              </Button>
            </div>
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
    </div>
  )
}

