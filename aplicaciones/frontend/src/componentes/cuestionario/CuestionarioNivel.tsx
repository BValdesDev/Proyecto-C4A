import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Progress } from '../../components/ui/progress'
import { Badge } from '../../components/ui/badge'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { 
  ArrowLeft, 
  ArrowRight, 
  Save, 
  CheckCircle, 
  AlertCircle,
  Shield,
  Clock,
  Users
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesCuestionario {
  nivel: 'gratuito' | 'pro' | 'empresarial'
  idEvaluacion: string
  alCompletar: (resultados: ResultadosEvaluacion) => void
  autoGuardado: (respuestas: Respuesta[]) => void
}

interface Pregunta {
  id: string
  codigo: string
  texto_pregunta: string
  texto_ayuda?: string
  categoria: string
  peso: number
  tipo_respuesta: 'likert_5'
}

interface Respuesta {
  pregunta_id: string
  valor: number
  texto_evidencia?: string
  comentarios?: string
  nivel_confianza?: number
}

interface ResultadosEvaluacion {
  puntuacion_global: number
  puntuaciones_dominio: Record<string, number>
  recomendaciones: Recomendacion[]
  nivel_usado: string
}

interface Recomendacion {
  titulo: string
  descripcion: string
  esfuerzo: 'BAJO' | 'MEDIO' | 'ALTO'
  impacto: 'BAJO' | 'MEDIO' | 'ALTO'
  plazo: string
  estimacion_costo: string
}

// Componente principal según prompt maestro
export const CuestionarioNivel: React.FC<PropiedadesCuestionario> = ({ 
  nivel, 
  idEvaluacion, 
  alCompletar, 
  autoGuardado 
}) => {
  const navigate = useNavigate()
  const [preguntas, setPreguntas] = useState<Pregunta[]>([])
  const [preguntaActual, setPreguntaActual] = useState(0)
  const [respuestas, setRespuestas] = useState<Record<string, Respuesta>>({})
  const [cargando, setCargando] = useState(true)
  const [guardando, setGuardando] = useState(false)
  const [mostrarPromptActualizacion, setMostrarPromptActualizacion] = useState(false)

  // Configuración por nivel según prompt maestro
  const configuracionNivel = {
    gratuito: { maxPreguntas: 10, tiempoEstimado: '5-7 minutos' },
    pro: { maxPreguntas: 50, tiempoEstimado: '15-20 minutos' },
    empresarial: { maxPreguntas: 100, tiempoEstimado: '30-45 minutos' }
  }

  const config = configuracionNivel[nivel]
  const progreso = ((preguntaActual + 1) / config.maxPreguntas) * 100

  useEffect(() => {
    cargarPreguntas()
  }, [nivel, idEvaluacion])

  const cargarPreguntas = async () => {
    try {
      setCargando(true)
      const response = await api.get(`/api/v1/cuestionarios/nivel/${nivel}`)
      setPreguntas(response.data.preguntas)
    } catch (error) {
      console.error('Error cargando preguntas:', error)
      toast.error('Error al cargar las preguntas del cuestionario')
    } finally {
      setCargando(false)
    }
  }

  const manejarRespuesta = (preguntaId: string, valor: number, evidencia?: string) => {
    const nuevaRespuesta: Respuesta = {
      pregunta_id: preguntaId,
      valor,
      texto_evidencia: evidencia,
      nivel_confianza: 3 // Valor por defecto
    }

    setRespuestas(prev => ({
      ...prev,
      [preguntaId]: nuevaRespuesta
    }))

    // Auto-guardado para niveles Pro+ según prompt maestro
    if (nivel !== 'gratuito') {
      autoGuardado(Object.values({ ...respuestas, [preguntaId]: nuevaRespuesta }))
    }
  }

  const siguientePregunta = () => {
    if (preguntaActual < preguntas.length - 1) {
      setPreguntaActual(prev => prev + 1)
    } else {
      completarEvaluacion()
    }
  }

  const preguntaAnterior = () => {
    if (preguntaActual > 0) {
      setPreguntaActual(prev => prev - 1)
    }
  }

  const guardarProgreso = async () => {
    try {
      setGuardando(true)
      await api.post(`/api/v1/evaluaciones/${idEvaluacion}/respuestas`, {
        respuestas: Object.values(respuestas)
      })
      toast.success('Progreso guardado exitosamente')
    } catch (error) {
      console.error('Error guardando progreso:', error)
      toast.error('Error al guardar el progreso')
    } finally {
      setGuardando(false)
    }
  }

  const completarEvaluacion = async () => {
    try {
      setGuardando(true)
      
      // Enviar respuestas finales
      await api.post(`/api/v1/evaluaciones/${idEvaluacion}/respuestas`, {
        respuestas: Object.values(respuestas),
        completar: true
      })

      // Obtener resultados
      const response = await api.get(`/api/v1/evaluaciones/${idEvaluacion}/puntuacion`)
      const resultados: ResultadosEvaluacion = response.data

      toast.success('¡Evaluación completada exitosamente!')
      alCompletar(resultados)
      
    } catch (error) {
      toast.error('Error al completar la evaluación')
    } finally {
      setGuardando(false)
    }
  }

  const mostrarPromptActualizar = () => {
    setMostrarPromptActualizacion(true)
  }

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando cuestionario...</p>
        </div>
      </div>
    )
  }

  if (preguntas.length === 0) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-semibold mb-2">No hay preguntas disponibles</h3>
        <p className="text-muted-foreground mb-4">
          No se encontraron preguntas para el nivel {nivel}
        </p>
        <Button onClick={() => navigate('/app/evaluaciones')}>
          Volver a Evaluaciones
        </Button>
      </div>
    )
  }

  const pregunta = preguntas[preguntaActual]
  const respuestaActual = respuestas[pregunta.id]

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header con información del nivel */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-c4a-blue-600" />
                <span>Evaluación de Ciberseguridad</span>
                <Badge variant="outline" className="ml-2">
                  {nivel.toUpperCase()}
                </Badge>
              </CardTitle>
              <CardDescription>
                Nivel {nivel} - {config.tiempoEstimado} estimados
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span>{config.tiempoEstimado}</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Users className="w-4 h-4" />
                <span>{config.maxPreguntas} preguntas</span>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Barra de progreso para niveles Pro+ según prompt maestro */}
      {nivel !== 'gratuito' && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progreso</span>
                <span>{preguntaActual + 1} de {config.maxPreguntas}</span>
              </div>
              <Progress value={progreso} className="h-2" />
              <div className="text-xs text-muted-foreground text-center">
                {Math.round(progreso)}% completado
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pregunta actual */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">
                Pregunta {preguntaActual + 1} de {config.maxPreguntas}
              </CardTitle>
              <CardDescription>
                {pregunta.categoria} • Peso: {pregunta.peso}/5
              </CardDescription>
            </div>
            <Badge variant="outline">
              {pregunta.codigo}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Texto de la pregunta */}
          <div>
            <h3 className="text-lg font-medium mb-4">
              {pregunta.texto_pregunta}
            </h3>
            {pregunta.texto_ayuda && (
              <Alert>
                <AlertCircle className="w-4 h-4" />
                <AlertDescription>
                  {pregunta.texto_ayuda}
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Escala de respuesta Likert 5 */}
          <div className="space-y-4">
            <h4 className="font-medium">Seleccione su respuesta:</h4>
            <div className="grid grid-cols-5 gap-2">
              {[1, 2, 3, 4, 5].map((valor) => (
                <Button
                  key={valor}
                  variant={respuestaActual?.valor === valor ? "default" : "outline"}
                  onClick={() => manejarRespuesta(pregunta.id, valor)}
                  className="h-12 flex flex-col items-center justify-center"
                >
                  <span className="text-lg font-bold">{valor}</span>
                  <span className="text-xs">
                    {valor === 1 ? 'Muy Bajo' : 
                     valor === 2 ? 'Bajo' : 
                     valor === 3 ? 'Medio' : 
                     valor === 4 ? 'Alto' : 'Muy Alto'}
                  </span>
                </Button>
              ))}
            </div>
          </div>

          {/* Evidencia adicional para niveles Pro+ */}
          {nivel !== 'gratuito' && respuestaActual?.valor && (
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Evidencia o comentarios adicionales (opcional):
              </label>
              <textarea
                className="w-full p-3 border rounded-md resize-none"
                rows={3}
                placeholder="Describa la evidencia que respalda su respuesta..."
                value={respuestaActual?.texto_evidencia || ''}
                onChange={(e) => {
                  const nuevaRespuesta = { ...respuestaActual, texto_evidencia: e.target.value }
                  setRespuestas(prev => ({ ...prev, [pregunta.id]: nuevaRespuesta }))
                }}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Controles de navegación */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={preguntaAnterior}
          disabled={preguntaActual === 0}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Anterior
        </Button>

        <div className="flex items-center space-x-2">
          {/* Botón guardar para niveles Pro+ según prompt maestro */}
          {nivel !== 'gratuito' && (
            <Button
              variant="outline"
              onClick={guardarProgreso}
              disabled={guardando}
            >
              <Save className="w-4 h-4 mr-2" />
              {guardando ? 'Guardando...' : 'Guardar'}
            </Button>
          )}

          {/* Botón siguiente/completar */}
          <Button
            onClick={siguientePregunta}
            disabled={!respuestaActual?.valor}
          >
            {preguntaActual === preguntas.length - 1 ? (
              <>
                <CheckCircle className="w-4 h-4 mr-2" />
                Completar Evaluación
              </>
            ) : (
              <>
                Siguiente
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Prompt de actualización para nivel gratuito según prompt maestro */}
      {nivel === 'gratuito' && preguntaActual === Math.floor(config.maxPreguntas * 0.7) && (
        <Alert className="border-c4a-blue-200 bg-c4a-blue-50">
          <AlertCircle className="w-4 h-4 text-c4a-blue-600" />
          <AlertDescription className="text-c4a-blue-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">¿Necesita más análisis?</p>
                <p className="text-sm">
                  Actualice a Pro para obtener 50 preguntas detalladas, 
                  benchmarking sectorial y recomendaciones prioritizadas.
                </p>
              </div>
              <Button 
                size="sm" 
                className="bg-c4a-blue-600 hover:bg-c4a-blue-700"
                onClick={mostrarPromptActualizar}
              >
                Ver Planes
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Modal de actualización de plan */}
      {mostrarPromptActualizacion && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Actualizar Plan</CardTitle>
              <CardDescription>
                Desbloquee más funciones con nuestros planes Pro y Empresarial
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-medium">Beneficios del Plan Pro:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• 50 preguntas detalladas</li>
                  <li>• Benchmarking sectorial</li>
                  <li>• Reportes sin marca de agua</li>
                  <li>• Soporte prioritario</li>
                </ul>
              </div>
              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  onClick={() => setMostrarPromptActualizacion(false)}
                  className="flex-1"
                >
                  Continuar Gratis
                </Button>
                <Button 
                  onClick={() => navigate('/app/suscripciones')}
                  className="flex-1"
                >
                  Ver Planes
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

    </div>
  )
}