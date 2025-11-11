import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Progress } from '../../components/ui/progress'
import { ArrowLeft, Save, CheckCircle } from 'lucide-react'
import apiClient, { api } from '../../utilidades/apiClient'
import { Evaluacion, Pregunta, RespuestaForm } from '../../tipos'
import { toast } from 'react-hot-toast'

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

  const cargarPreguntasCuestionario = async (cuestionarioId: string) => {
    try {
      const preguntasResponse = await api.get(`/api/v1/cuestionarios/${cuestionarioId}/preguntas`)
      const preguntasFormateadas: Pregunta[] = preguntasResponse.map((pregunta: any, index: number) => ({
        id: pregunta.pregunta_id,
        codigo: pregunta.codigo_pregunta,
        texto_pregunta: pregunta.texto_pregunta,
        texto_ayuda: pregunta.texto_ayuda,
        categoria: pregunta.seccion,
        peso: pregunta.peso ?? 1,
        tipo_respuesta: 'likert_5',
        orden: pregunta.orden_pregunta ?? index + 1
      }))

      setPreguntas(preguntasFormateadas)
      setPreguntaActual(0)
    } catch (error) {
      console.error('Error cargando preguntas del cuestionario:', error)
      toast.error('No pudimos cargar las preguntas de la evaluación. Intenta nuevamente.')
    }
  }

  const cargarEvaluacion = async () => {
    try {
      setLoading(true)
      
      // Cargar evaluación
      const evaluacionResponse = await api.get(`/api/v1/evaluaciones/${id}`)
      setEvaluacion(evaluacionResponse)
      if (evaluacionResponse.cuestionario_id) {
        await cargarPreguntasCuestionario(evaluacionResponse.cuestionario_id)
      } else {
        setPreguntas([])
      }
      
    } catch (error) {
      console.error('Error cargando evaluación:', error)
      navigate('/app/evaluaciones')
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

  const handleFinalizarEvaluacion = async () => {
    try {
      setSaving(true)
      
      // Finalizar la evaluación
      const response = await api.post(`/api/v1/evaluaciones/${id}/finalizar`)
      
      if (response.success) {
        toast.success('¡Evaluación completada exitosamente!')
        if (evaluacion?.cuestionario_id) {
          try {
            const analisis = await api.get(
              `/api/v1/cuestionarios/${evaluacion.cuestionario_id}/calcular-resultado?evaluacion_id=${id}`
            )

            const respuestasArray = Object.values(respuestas)

            const resultadoParaVista = {
              puntuacion_global: analisis?.puntuacion_global ?? 0,
              nivel_madurez: {
                nombre: analisis?.nivel_madurez?.nombre ?? 'Sin clasificar',
                descripcion: analisis?.nivel_madurez?.descripcion ?? 'Resultado sin descripción',
                color: analisis?.nivel_madurez?.color ?? '#1E3A8A',
                rango: analisis?.nivel_madurez?.rango ?? '0-0'
              },
              puntuaciones_por_seccion: analisis?.puntuaciones_por_seccion ?? {},
              puntuaciones_dominio: analisis?.puntuaciones_por_seccion ?? {},
              recomendaciones: analisis?.recomendaciones ?? [],
              distribucion_respuestas: analisis?.distribucion_respuestas ?? {},
              calidad_respuestas: analisis?.calidad_respuestas ?? {},
              total_preguntas: analisis?.total_preguntas ?? respuestasArray.length,
              preguntas_completadas: analisis?.preguntas_completadas ?? respuestasArray.length,
              cuestionario_nombre: analisis?.cuestionario_nombre ?? evaluacion.nombre
            }

            navigate(`/app/diagnosticos/${evaluacion.cuestionario_id}/resultados`, {
              state: {
                resultado: resultadoParaVista,
                respuestas: respuestasArray,
                evaluacionId: id,
                pdfGenerado: false
              }
            })
          } catch (analisisError) {
            console.error('Error obteniendo análisis de resultados:', analisisError)
            toast.error('No pudimos calcular los resultados. Inténtalo nuevamente.')
          }
        }
      }
      
    } catch (error) {
          console.error('Error al finalizar la evaluación:', error)
      toast.error('Error al finalizar la evaluación')
    } finally {
      setSaving(false)
    }
  }

  const handleGenerarPDF = async () => {
    try {
      const baseURL = apiClient.defaults.baseURL || 'http://localhost:8000'
      const token = localStorage.getItem('c4a_token')

      const response = await fetch(
        `${baseURL}/api/v1/pdf/profesional/diagnostico/profesional/${id}`,
        {
          method: 'GET',
        headers: {
            Authorization: token ? `Bearer ${token}` : ''
          }
        }
      )
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `Reporte_Ciberseguridad_${evaluacion?.nombre.replace(' ', '_')}_${new Date().toISOString().split('T')[0]}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        toast.success('PDF descargado exitosamente')
      } else {
        throw new Error('Error generando PDF')
      }
      
    } catch (error) {
      console.error('Error generando PDF:', error)
      toast.error('Error al generar el PDF')
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

  const getNivelMadurez = (puntuacion: number) => {
    if (puntuacion < 20) return "Inicial"
    if (puntuacion < 40) return "Básico"
    if (puntuacion < 60) return "Intermedio"
    if (puntuacion < 80) return "Gestionado"
    return "Optimizado"
  }

  const getDescripcionNivel = (nivel: string) => {
    const descripciones = {
      "Inicial": "Procesos ad-hoc y no documentados",
      "Básico": "Procesos básicos implementados",
      "Intermedio": "Procesos definidos y documentados",
      "Gestionado": "Procesos medidos y controlados",
      "Optimizado": "Procesos optimizados y mejorados continuamente"
    }
    return descripciones[nivel as keyof typeof descripciones] || "Nivel no determinado"
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
        <Button onClick={() => navigate('/app/evaluaciones')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a Evaluaciones
        </Button>
      </div>
    )
  }

  const totalPreguntas = evaluacion?.total_preguntas || preguntas.length
  const preguntasCompletadas = evaluacion?.preguntas_completadas || 0
  const porcentajeAvance =
    totalPreguntas > 0 ? Math.round((preguntasCompletadas / totalPreguntas) * 100) : 0

  const pregunta = preguntas[preguntaActual]
  const respuestaActual = respuestas[pregunta?.id || '']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" onClick={() => navigate('/app/evaluaciones')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">{evaluacion.nombre}</h1>
            <p className="text-muted-foreground">
              {evaluacion.framework?.nombre_mostrar || evaluacion.framework?.nombre || 'N/A'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Badge variant="outline">
            {evaluacion.estado.replace('_', ' ')}
          </Badge>
        </div>
      </div>

      {/* Progreso */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progreso de la evaluación</span>
              <span>{porcentajeAvance}%</span>
            </div>
            <Progress value={porcentajeAvance} className="h-2" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>
                Pregunta {preguntas.length > 0 ? preguntaActual + 1 : 0} de {totalPreguntas}
              </span>
              <span>{preguntasCompletadas} completadas</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pregunta actual */}
      {evaluacion.estado !== 'completada' && pregunta && (
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
                      onClick={handleFinalizarEvaluacion}
                      disabled={!respuestaActual?.valor && respuestaActual?.valor !== 0}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      {saving ? 'Finalizando...' : 'Finalizar Evaluación'}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resultados de la evaluación completada */}
      {evaluacion.estado === 'completada' && (
        <div className="space-y-6">
          {/* Resultado principal */}
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="pt-8 pb-8">
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-6 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-4xl font-bold">
                    {evaluacion.puntuacion_global?.toFixed(0) || 0}%
                  </span>
                </div>
                
                <h2 className="text-2xl font-bold text-blue-800 mb-2">
                  Nivel de Madurez: {getNivelMadurez(evaluacion.puntuacion_global || 0)}
                </h2>
                <p className="text-blue-700 mb-6">
                  {getDescripcionNivel(getNivelMadurez(evaluacion.puntuacion_global || 0))}
                </p>
                
                {/* Barra de progreso */}
                <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                  <div 
                    className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${evaluacion.puntuacion_global || 0}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-sm text-blue-700">
                  <span>Puntuación Global</span>
                  <span>Rango de puntuación: 61-80%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Métricas resumidas */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Total Preguntas</h3>
                  <p className="text-3xl font-bold text-blue-600">{evaluacion.total_preguntas || 0}</p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Puntuación Promedio</h3>
                  <p className="text-3xl font-bold text-blue-600">
                    {((evaluacion.puntuacion_global || 0) / 20).toFixed(1)} / 5
                  </p>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <h3 className="text-sm font-medium text-gray-500 mb-2">Nivel Alcanzado</h3>
                  <p className="text-3xl font-bold text-blue-600">
                    {getNivelMadurez(evaluacion.puntuacion_global || 0)}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recomendaciones */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg font-semibold">Recomendaciones de Mejora</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">
                Acciones sugeridas para mejorar su nivel de madurez en ciberseguridad
              </p>
              <div className="space-y-3">
                <div className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3">1</span>
                  <span className="text-gray-700">Implementar monitoreo continuo de seguridad</span>
                </div>
                <div className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3">2</span>
                  <span className="text-gray-700">Realizar evaluaciones de vulnerabilidades periódicas</span>
                </div>
                <div className="flex items-start">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3">3</span>
                  <span className="text-gray-700">Mejorar la integración de controles de seguridad</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Botones de acción */}
          <div className="flex justify-center space-x-4">
            <Button 
              onClick={handleGenerarPDF}
              className="bg-blue-600 hover:bg-blue-700"
            >
              📄 Descargar PDF
            </Button>
            <Button 
              variant="outline"
              onClick={() => navigate('/app/reportes')}
            >
              📊 Ver Reportes
            </Button>
            <Button 
              variant="outline"
              onClick={() => navigate('/app/diagnosticos')}
            >
              🔄 Nuevo Diagnóstico
            </Button>
          </div>

          {/* Información adicional */}
          <div className="text-center text-sm text-gray-500">
            Los resultados se guardarán automáticamente en su historial. Puede descargar un informe en PDF o compartir los resultados con su equipo.
          </div>
        </div>
      )}
    </div>
  )
}

