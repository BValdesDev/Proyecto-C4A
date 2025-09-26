import { useState, useEffect, useCallback } from 'react'
import { api } from '../utilidades/apiClient'
import { Evaluacion, Pregunta, Respuesta, NivelSuscripcion } from '../tipos'

interface UseEvaluacionProps {
  evaluacionId: string
  nivel: NivelSuscripcion
}

interface UseEvaluacionReturn {
  evaluacion: Evaluacion | null
  preguntas: Pregunta[]
  respuestas: Record<string, Respuesta>
  loading: boolean
  error: string | null
  progreso: number
  tiempoTranscurrido: number
  guardarRespuesta: (preguntaId: string, valor: any) => void
  autoGuardar: () => Promise<void>
  finalizarEvaluacion: () => Promise<void>
  cargarEvaluacion: () => Promise<void>
}

export const useEvaluacion = ({ evaluacionId, nivel }: UseEvaluacionProps): UseEvaluacionReturn => {
  const [evaluacion, setEvaluacion] = useState<Evaluacion | null>(null)
  const [preguntas, setPreguntas] = useState<Pregunta[]>([])
  const [respuestas, setRespuestas] = useState<Record<string, Respuesta>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tiempoInicio, setTiempoInicio] = useState<Date>(new Date())
  const [tiempoTranscurrido, setTiempoTranscurrido] = useState(0)

  // Configuración por nivel
  const configuracionNivel = {
    gratuito: {
      maxPreguntas: 10,
      tiempoEstimado: 5,
      permitirGuardarContinuar: false,
      autoGuardarInterval: 0
    },
    pro: {
      maxPreguntas: 50,
      tiempoEstimado: 20,
      permitirGuardarContinuar: true,
      autoGuardarInterval: 30000 // 30 segundos
    },
    empresarial: {
      maxPreguntas: 100,
      tiempoEstimado: 45,
      permitirGuardarContinuar: true,
      autoGuardarInterval: 15000 // 15 segundos
    }
  }

  const config = configuracionNivel[nivel]

  // Timer para tiempo transcurrido
  useEffect(() => {
    const interval = setInterval(() => {
      setTiempoTranscurrido(Math.floor((new Date().getTime() - tiempoInicio.getTime()) / 1000))
    }, 1000)

    return () => clearInterval(interval)
  }, [tiempoInicio])

  // Auto-guardar para niveles Pro y Empresarial
  useEffect(() => {
    if (config.autoGuardarInterval > 0) {
      const interval = setInterval(() => {
        if (Object.keys(respuestas).length > 0) {
          autoGuardar()
        }
      }, config.autoGuardarInterval)

      return () => clearInterval(interval)
    }
  }, [respuestas, config.autoGuardarInterval])

  const cargarEvaluacion = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Cargar evaluación
      const evaluacionResponse = await api.get(`/api/v1/evaluaciones/${evaluacionId}`)
      setEvaluacion(evaluacionResponse)
      
      // Cargar preguntas según nivel
      const preguntasResponse = await api.get(`/api/v1/cuestionarios/nivel/${nivel}`)
      setPreguntas(preguntasResponse.preguntas)
      
      setTiempoInicio(new Date())
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando evaluación')
      console.error('Error cargando evaluación:', err)
    } finally {
      setLoading(false)
    }
  }, [evaluacionId, nivel])

  const guardarRespuesta = useCallback((preguntaId: string, valor: any) => {
    const nuevaRespuesta: Respuesta = {
      id: `resp_${preguntaId}_${Date.now()}`,
      evaluacion_id: evaluacionId,
      pregunta_id: preguntaId,
      valor,
      texto_evidencia: '',
      comentarios: '',
      nivel_confianza: 3,
      respondido_por: '', // Se llenará desde el contexto de autenticación
      fecha_respuesta: new Date().toISOString()
    }

    setRespuestas(prev => ({
      ...prev,
      [preguntaId]: nuevaRespuesta
    }))
  }, [evaluacionId])

  const autoGuardar = useCallback(async () => {
    try {
      if (Object.keys(respuestas).length === 0) return
      
      const respuestasArray = Object.values(respuestas)
      
      await api.post(`/api/v1/evaluaciones/${evaluacionId}/respuestas`, {
        respuestas: respuestasArray
      })
      
    } catch (err) {
      console.error('Error en auto-guardado:', err)
    }
  }, [evaluacionId, respuestas])

  const finalizarEvaluacion = useCallback(async () => {
    try {
      setLoading(true)
      
      // Guardar respuestas finales
      await autoGuardar()
      
      // Marcar evaluación como completada
      await api.post(`/api/v1/evaluaciones/${evaluacionId}/finalizar`)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error finalizando evaluación')
      console.error('Error finalizando evaluación:', err)
    } finally {
      setLoading(false)
    }
  }, [evaluacionId, autoGuardar])

  // Cargar evaluación al montar
  useEffect(() => {
    cargarEvaluacion()
  }, [cargarEvaluacion])

  const progreso = preguntas.length > 0 ? (Object.keys(respuestas).length / preguntas.length) * 100 : 0

  return {
    evaluacion,
    preguntas,
    respuestas,
    loading,
    error,
    progreso,
    tiempoTranscurrido,
    guardarRespuesta,
    autoGuardar,
    finalizarEvaluacion,
    cargarEvaluacion
  }
}

