import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { 
  FileText, 
  BarChart3, 
  Users, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Plus
} from 'lucide-react'
import { api } from '../../utilidades/apiClient'
import { Evaluacion, EstadisticasDashboard } from '../../tipos'
import { toast } from 'sonner'

export const DashboardPage: React.FC = () => {
  const { usuario } = useAuth()
  const navigate = useNavigate()
  const [estadisticas, setEstadisticas] = useState<EstadisticasDashboard | null>(null)
  const [evaluaciones, setEvaluaciones] = useState<Evaluacion[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (usuario) {
      cargarDatos()
    }
  }, [usuario])

  const cargarDatos = async () => {
    try {
      setLoading(true)
      
      if (!usuario) return
      
      // Cargar estadísticas del dashboard (usar estadísticas de la organización)
      const statsResponse = await api.get(`/api/v1/organizaciones/${usuario.organizacion.id}/estadisticas`)
      setEstadisticas(statsResponse)
      
      // Cargar evaluaciones recientes
      const evaluacionesResponse = await api.get('/api/v1/evaluaciones/')
      setEvaluaciones(evaluacionesResponse.evaluaciones || [])
      
    } catch (error) {
          console.error('Error cargando datos del dashboard:', error)
      // En caso de error, usar datos por defecto
      setEstadisticas({
        total_evaluaciones: 0,
        evaluaciones_completadas: 0,
        puntuacion_promedio: 0,
        evaluaciones_en_progreso: 0,
        uso_mensual: 0,
        limite_mensual: 0
      })
      setEvaluaciones([])
    } finally {
      setLoading(false)
    }
  }

  const getNivelBadgeColor = (nivel: string) => {
    switch (nivel) {
      case 'gratuito':
        return 'bg-gray-100 text-gray-800'
      case 'pro':
        return 'bg-c4a-blue-100 text-c4a-blue-800'
      case 'empresarial':
        return 'bg-c4a-purple-100 text-c4a-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getEstadoBadgeColor = (estado: string) => {
    switch (estado) {
      case 'completada':
        return 'bg-green-100 text-green-800'
      case 'en_progreso':
        return 'bg-yellow-100 text-yellow-800'
      case 'borrador':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Funciones para acciones rápidas
  const handleCrearNuevaEvaluacion = async () => {
    try {
      console.log('Obteniendo cuestionario principal...')
      
      // Obtener el cuestionario principal según el nivel de suscripción
      const cuestionario = await api.get('/api/v1/cuestionarios/principal')
      
      console.log('Cuestionario obtenido:', {
        id: cuestionario.id,
        nombre: cuestionario.nombre,
        nivel: cuestionario.nivel
      })
      
      // Navegar directamente a las preguntas del cuestionario
      const ruta = `/app/diagnosticos/${cuestionario.id}/responder`
      console.log('Navegando a:', ruta)
      navigate(ruta)
      
    } catch (error: any) {
      console.error('Error al obtener cuestionario principal:', error)
      console.error('Error response:', error.response)
      console.error('Error message:', error.message)
      console.error('Error details:', error.response?.data)
      toast.error('Error al cargar el cuestionario. Inténtalo de nuevo.')
    }
  }

  const handleVerReportes = () => {
    navigate('/app/reportes')
  }

  const handleGestionarUsuarios = () => {
    navigate('/app/usuarios')
  }

  const handleActualizarPlan = () => {
    navigate('/app/suscripciones')
  }

  const getNivelPreguntas = () => {
    const limites = usuario?.organizacion?.limites
    if (limites) {
      return `${limites.preguntas_evaluacion} preguntas (${limites.tiempo_estimado})`
    }
    
    // Fallback si no hay límites
    const nivel = usuario?.organizacion?.nivel_suscripcion || 'gratuito'
    switch (nivel) {
      case 'gratuito': return '10 preguntas (5-7 minutos)'
      case 'pro': return '50 preguntas (15-20 minutos)'
      case 'empresarial': return '100 preguntas (30-45 minutos)'
      default: return '10 preguntas (5-7 minutos)'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="loading-skeleton h-8 w-64"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="loading-skeleton h-32"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground">
            Bienvenido, {usuario?.nombres}. Aquí tienes un resumen de tu actividad.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Badge className={getNivelBadgeColor(usuario?.organizacion?.nivel_suscripcion || 'gratuito')}>
            Plan {usuario?.organizacion?.nivel_suscripcion?.toUpperCase()}
          </Badge>
          <span className="text-sm text-muted-foreground">
            {getNivelPreguntas()}
          </span>
          {usuario?.organizacion?.nivel_suscripcion === 'gratuito' && (
            <Button variant="outline" size="sm" onClick={handleActualizarPlan}>
              Actualizar Plan
            </Button>
          )}
        </div>
      </div>

      {/* Estadísticas principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Evaluaciones</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estadisticas?.total_evaluaciones || 0}</div>
            <p className="text-xs text-muted-foreground">
              {estadisticas?.evaluaciones_completadas || 0} completadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Puntuación Promedio</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {estadisticas?.puntuacion_promedio?.toFixed(1) || '0.0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Sobre 100 puntos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">En Progreso</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estadisticas?.evaluaciones_en_progreso || 0}</div>
            <p className="text-xs text-muted-foreground">
              Evaluaciones activas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uso Mensual</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {estadisticas?.uso_mensual?.evaluaciones_usadas || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              de {estadisticas?.uso_mensual?.evaluaciones_limite || 0} disponibles
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Evaluaciones recientes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Evaluaciones Recientes</CardTitle>
                <CardDescription>
                  Tus últimas evaluaciones de ciberseguridad
                </CardDescription>
              </div>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => navigate('/app/evaluaciones')}
              >
                <Plus className="w-4 h-4 mr-2" />
                Ver Todas
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {evaluaciones.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No tienes evaluaciones aún</p>
                  <Button 
                    className="mt-4" 
                    size="sm"
                    onClick={handleCrearNuevaEvaluacion}
                  >
                    Crear Primera Evaluación
                  </Button>
                </div>
              ) : (
                evaluaciones.map((evaluacion) => (
                  <div key={evaluacion.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{evaluacion.nombre}</h4>
                      <p className="text-sm text-muted-foreground">
                        {evaluacion.framework?.nombre_mostrar || evaluacion.framework?.nombre || 'N/A'}
                      </p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Badge className={getEstadoBadgeColor(evaluacion.estado)}>
                          {evaluacion.estado.replace('_', ' ')}
                        </Badge>
                        {evaluacion.puntuacion_global && (
                          <span className="text-sm font-medium">
                            {evaluacion.puntuacion_global.toFixed(1)}/100
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-muted-foreground">
                        {new Date(evaluacion.fecha_creacion).toLocaleDateString('es-CL')}
                      </div>
                      {evaluacion.estado === 'en_progreso' && evaluacion.porcentaje_completado && (
                        <div className="text-xs text-c4a-blue-600">
                          {evaluacion.porcentaje_completado.toFixed(0)}% completado
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Acciones rápidas */}
        <Card>
          <CardHeader>
            <CardTitle>Acciones Rápidas</CardTitle>
            <CardDescription>
              Accede a las funciones más utilizadas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button 
                className="w-full justify-start" 
                variant="outline"
                onClick={handleCrearNuevaEvaluacion}
              >
                <FileText className="w-4 h-4 mr-2" />
                Crear Nueva Evaluación
              </Button>
              <Button 
                className="w-full justify-start" 
                variant="outline"
                onClick={handleVerReportes}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                Ver Reportes
              </Button>
              <Button 
                className="w-full justify-start" 
                variant="outline"
                onClick={handleGestionarUsuarios}
              >
                <Users className="w-4 h-4 mr-2" />
                Gestionar Usuarios
              </Button>
              <Button 
                className="w-full justify-start" 
                variant="outline"
                onClick={handleActualizarPlan}
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                Actualizar Plan
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alertas y notificaciones */}
      {usuario?.organizacion?.nivel_suscripcion === 'gratuito' && (
        <Card className="border-c4a-blue-200 bg-c4a-blue-50">
          <CardHeader>
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-c4a-blue-600" />
              <CardTitle className="text-c4a-blue-800">Actualiza tu Plan</CardTitle>
            </div>
            <CardDescription className="text-c4a-blue-700">
              Desbloquea más funciones con nuestros planes Pro y Empresarial
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-c4a-blue-700">
                  • Más preguntas de evaluación
                </p>
                <p className="text-sm text-c4a-blue-700">
                  • Reportes sin marca de agua
                </p>
                <p className="text-sm text-c4a-blue-700">
                  • Benchmarking sectorial
                </p>
              </div>
              <Button 
                className="bg-c4a-blue-600 hover:bg-c4a-blue-700"
                onClick={handleActualizarPlan}
              >
                Ver Planes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

    </div>
  )
}
