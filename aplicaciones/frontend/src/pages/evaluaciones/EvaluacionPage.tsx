import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Progress } from '../../components/ui/progress'
import { ArrowLeft, Save, CheckCircle } from 'lucide-react'
import { api } from '../../utilidades/apiClient'
import { Evaluacion, Pregunta, RespuestaForm } from '../../tipos'

export const EvaluacionPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [evaluacion, setEvaluacion] = useState<Evaluacion | null>(null)
  const [preguntas, setPreguntas] = useState<Pregunta[]>([])
  const [respuestas, setRespuestas] = useState<{ [key: string]: RespuestaForm }>({})
  const [preguntaActual, setPreguntaActual] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (id) {
      cargarEvaluacion()
    }
  }, [id])

  const cargarEvaluacion = async () => {
    try {
      setLoading(true)
      
      // Cargar evaluación
      const evaluacionResponse = await api.get(`/api/v1/evaluaciones/${id}`)
      setEvaluacion(evaluacionResponse)
      
      // Cargar preguntas
      const preguntasResponse = await api.get(`/api/v1/evaluaciones/${id}/preguntas`)
      setPreguntas(preguntasResponse)
      
    } catch (error) {
      console.error('Error cargando evaluación:', error)
      navigate('/evaluaciones')
    } finally {
      setLoading(false)
    }
  }

  const handleRespuestaChange = (preguntaId: string, valor: number) => {
    setRespuestas(prev => ({
      ...prev,
      [preguntaId]: {
        pregunta_id: preguntaId,
        valor,
        texto_evidencia: prev[preguntaId]?.texto_evidencia || '',
        comentarios: prev[preguntaId]?.comentarios || '',
        nivel_confianza: prev[preguntaId]?.nivel_confianza || 3
      }
    }))
  }

  const handleGuardarRespuestas = async () => {
    try {
      setSaving(true)
      const respuestasArray = Object.values(respuestas)
      
      await api.post(`/api/v1/evaluaciones/${id}/respuestas`, {
        respuestas: respuestasArray
      })
      
      // Recargar evaluación para obtener estado actualizado
      await cargarEvaluacion()
      
    } catch (error) {
      console.error('Error guardando respuestas:', error)
    } finally {
      setSaving(false)
    }
  }

  const getTextoRespuesta = (valor: number) => {
    const textos = {
      0: 'No implementado',
      1: 'Parcialmente implementado',
      2: 'Implementado básicamente',
      3: 'Bien implementado',
      4: 'Completamente implementado',
      5: 'Excelentemente implementado'
    }
    return textos[valor as keyof typeof textos] || 'No seleccionado'
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="loading-skeleton h-8 w-64"></div>
        <div className="loading-skeleton h-96"></div>
      </div>
    )
  }

  if (!evaluacion) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Evaluación no encontrada</h2>
        <Button onClick={() => navigate('/evaluaciones')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a Evaluaciones
        </Button>
      </div>
    )
  }

  const pregunta = preguntas[preguntaActual]
  const respuestaActual = respuestas[pregunta?.id || '']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => navigate('/evaluaciones')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">{evaluacion.nombre}</h1>
            <p className="text-muted-foreground">
              {evaluacion.framework.nombre_mostrar}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Badge variant="outline">
            {evaluacion.estado.replace('_', ' ')}
          </Badge>
          {evaluacion.puntuacion_global && (
            <Badge variant="secondary">
              {evaluacion.puntuacion_global.toFixed(1)}/100
            </Badge>
          )}
        </div>
      </div>

      {/* Progreso */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progreso de la evaluación</span>
              <span>{evaluacion.porcentaje_completado.toFixed(0)}%</span>
            </div>
            <Progress value={evaluacion.porcentaje_completado} className="h-2" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Pregunta {preguntaActual + 1} de {preguntas.length}</span>
              <span>{evaluacion.preguntas_completadas} completadas</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pregunta actual */}
      {pregunta && (
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-xl">
                  {pregunta.codigo}: {pregunta.texto_pregunta}
                </CardTitle>
                {pregunta.texto_ayuda && (
                  <CardDescription className="mt-2">
                    {pregunta.texto_ayuda}
                  </CardDescription>
                )}
              </div>
              <Badge variant="outline">
                Peso: {pregunta.peso}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Escala de respuesta */}
              <div>
                <label className="text-sm font-medium mb-4 block">
                  ¿Cuál es el nivel de implementación actual?
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {[0, 1, 2, 3, 4, 5].map((valor) => (
                    <button
                      key={valor}
                      onClick={() => handleRespuestaChange(pregunta.id, valor)}
                      className={`p-4 border rounded-lg text-left transition-colors ${
                        respuestaActual?.valor === valor
                          ? 'border-c4a-blue-500 bg-c4a-blue-50'
                          : 'border-border hover:border-c4a-blue-300'
                      }`}
                    >
                      <div className="font-medium text-lg">{valor}</div>
                      <div className="text-sm text-muted-foreground">
                        {getTextoRespuesta(valor)}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Evidencia */}
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Evidencia o justificación (opcional)
                </label>
                <textarea
                  className="w-full p-3 border rounded-lg resize-none"
                  rows={3}
                  placeholder="Describe la evidencia que respalda tu respuesta..."
                  value={respuestaActual?.texto_evidencia || ''}
                  onChange={(e) => {
                    const preguntaId = pregunta.id
                    setRespuestas(prev => ({
                      ...prev,
                      [preguntaId]: {
                        ...prev[preguntaId],
                        pregunta_id: preguntaId,
                        valor: prev[preguntaId]?.valor || 0,
                        texto_evidencia: e.target.value,
                        comentarios: prev[preguntaId]?.comentarios || '',
                        nivel_confianza: prev[preguntaId]?.nivel_confianza || 3
                      }
                    }))
                  }}
                />
              </div>

              {/* Navegación */}
              <div className="flex items-center justify-between">
                <Button
                  variant="outline"
                  onClick={() => setPreguntaActual(Math.max(0, preguntaActual - 1))}
                  disabled={preguntaActual === 0}
                >
                  Anterior
                </Button>
                
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    onClick={handleGuardarRespuestas}
                    disabled={saving}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Guardando...' : 'Guardar'}
                  </Button>
                  
                  {preguntaActual < preguntas.length - 1 ? (
                    <Button
                      onClick={() => setPreguntaActual(preguntaActual + 1)}
                      disabled={!respuestaActual?.valor && respuestaActual?.valor !== 0}
                    >
                      Siguiente
                    </Button>
                  ) : (
                    <Button
                      onClick={handleGuardarRespuestas}
                      disabled={!respuestaActual?.valor && respuestaActual?.valor !== 0}
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Finalizar
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Evaluación completada */}
      {evaluacion.estado === 'completada' && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-green-800 mb-2">
                ¡Evaluación Completada!
              </h3>
              <p className="text-green-700 mb-4">
                Has completado la evaluación de ciberseguridad.
              </p>
              <div className="flex justify-center space-x-4">
                <Button variant="outline">
                  Ver Reporte
                </Button>
                <Button>
                  Generar PDF
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

