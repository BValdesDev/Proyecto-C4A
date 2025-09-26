import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  AreaChart,
  Area
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Award, 
  BarChart3,
  Users,
  Building,
  Shield,
  AlertCircle,
  CheckCircle,
  Clock,
  DollarSign,
  Globe,
  Star,
  Activity,
  Zap,
  Eye,
  Download,
  Share2
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesAnalyticsAvanzado {
  organizacionId: string
  nivelUsuario: 'empresarial'
  periodo: '30d' | '90d' | '1a' | 'todo'
}

interface Tendencia {
  fecha: string
  puntuacion: number
  evaluaciones: number
  usuarios_activos: number
  tiempo_promedio: number
}

interface MatrizRiesgo {
  categoria: string
  probabilidad: number
  impacto: number
  nivel_riesgo: 'bajo' | 'medio' | 'alto' | 'critico'
  descripcion: string
  recomendaciones: string[]
}

interface Cumplimiento {
  norma: string
  porcentaje: number
  estado: 'cumple' | 'parcial' | 'no_cumple'
  requerimientos: Array<{
    id: string
    descripcion: string
    estado: 'cumple' | 'parcial' | 'no_cumple'
  }>
}

interface AnalyticsAvanzado {
  tendencias: Tendencia[]
  matriz_riesgo: MatrizRiesgo[]
  cumplimiento: Cumplimiento[]
  metricas_clave: {
    uptime: number
    tiempo_respuesta: number
    satisfaccion_usuario: number
    adopcion_funciones: number
  }
  predicciones: {
    proxima_evaluacion: string
    tendencia_puntuacion: 'mejora' | 'estable' | 'deterioro'
    probabilidad_riesgo: number
  }
}

interface FiltroTiempo {
  desde: string
  hasta: string
  granularidad: 'diario' | 'semanal' | 'mensual'
}

// Componente principal según prompt maestro
export const AnalyticsAvanzado: React.FC<PropiedadesAnalyticsAvanzado> = ({ 
  organizacionId, 
  nivelUsuario,
  periodo = '90d'
}) => {
  const [analytics, setAnalytics] = useState<AnalyticsAvanzado | null>(null)
  const [filtroTiempo, setFiltroTiempo] = useState<FiltroTiempo>({
    desde: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    hasta: new Date().toISOString().split('T')[0],
    granularidad: 'semanal'
  })
  const [cargando, setCargando] = useState(true)
  const [vistaActual, setVistaActual] = useState<'tendencias' | 'riesgo' | 'cumplimiento' | 'metricas'>('tendencias')

  useEffect(() => {
    cargarAnalytics()
  }, [organizacionId, filtroTiempo])

  const cargarAnalytics = async () => {
    try {
      setCargando(true)
      
      const response = await api.get(`/api/v1/analytics/avanzado/${organizacionId}`, {
        params: {
          desde: filtroTiempo.desde,
          hasta: filtroTiempo.hasta,
          granularidad: filtroTiempo.granularidad
        }
      })
      
      setAnalytics(response.data)
      
    } catch (error) {
      console.error('Error cargando analytics avanzado:', error)
      toast.error('Error al cargar los analytics avanzados')
    } finally {
      setCargando(false)
    }
  }

  const prepararDatosTendencias = () => {
    if (!analytics) return []
    return analytics.tendencias.map(t => ({
      fecha: new Date(t.fecha).toLocaleDateString('es-CL'),
      puntuacion: t.puntuacion,
      evaluaciones: t.evaluaciones,
      usuarios: t.usuarios_activos,
      tiempo: t.tiempo_promedio
    }))
  }

  const prepararDatosMatrizRiesgo = () => {
    if (!analytics) return []
    return analytics.matriz_riesgo.map(r => ({
      categoria: r.categoria,
      probabilidad: r.probabilidad,
      impacto: r.impacto,
      nivel: r.nivel_riesgo
    }))
  }

  const prepararDatosCumplimiento = () => {
    if (!analytics) return []
    return analytics.cumplimiento.map(c => ({
      norma: c.norma,
      porcentaje: c.porcentaje,
      estado: c.estado
    }))
  }

  const getColorRiesgo = (nivel: string) => {
    switch (nivel) {
      case 'bajo': return '#10B981'
      case 'medio': return '#F59E0B'
      case 'alto': return '#EF4444'
      case 'critico': return '#DC2626'
      default: return '#6B7280'
    }
  }

  const getColorCumplimiento = (estado: string) => {
    switch (estado) {
      case 'cumple': return '#10B981'
      case 'parcial': return '#F59E0B'
      case 'no_cumple': return '#EF4444'
      default: return '#6B7280'
    }
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando analytics avanzados...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-6 h-6 text-c4a-blue-600" />
            <span>Analytics Avanzado</span>
            <Badge className="bg-purple-100 text-purple-800">EMPRESARIAL</Badge>
          </CardTitle>
          <CardDescription>
            Análisis avanzado de tendencias, riesgos y cumplimiento normativo
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Filtros y controles */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros y Controles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Desde</label>
              <input
                type="date"
                value={filtroTiempo.desde}
                onChange={(e) => setFiltroTiempo(prev => ({ ...prev, desde: e.target.value }))}
                className="w-full p-2 border rounded-md"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Hasta</label>
              <input
                type="date"
                value={filtroTiempo.hasta}
                onChange={(e) => setFiltroTiempo(prev => ({ ...prev, hasta: e.target.value }))}
                className="w-full p-2 border rounded-md"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Granularidad</label>
              <Select 
                value={filtroTiempo.granularidad} 
                onValueChange={(value: 'diario' | 'semanal' | 'mensual') => 
                  setFiltroTiempo(prev => ({ ...prev, granularidad: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="diario">Diario</SelectItem>
                  <SelectItem value="semanal">Semanal</SelectItem>
                  <SelectItem value="mensual">Mensual</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Vista</label>
              <Select value={vistaActual} onValueChange={(value: any) => setVistaActual(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tendencias">Tendencias</SelectItem>
                  <SelectItem value="riesgo">Matriz de Riesgo</SelectItem>
                  <SelectItem value="cumplimiento">Cumplimiento</SelectItem>
                  <SelectItem value="metricas">Métricas Clave</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Métricas clave */}
      {analytics?.metricas_clave && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-sm font-medium">Uptime</p>
                  <p className="text-2xl font-bold">{analytics.metricas_clave.uptime}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium">Tiempo Respuesta</p>
                  <p className="text-2xl font-bold">{analytics.metricas_clave.tiempo_respuesta}ms</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-purple-600" />
                <div>
                  <p className="text-sm font-medium">Satisfacción</p>
                  <p className="text-2xl font-bold">{analytics.metricas_clave.satisfaccion_usuario}/5</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-orange-600" />
                <div>
                  <p className="text-sm font-medium">Adopción</p>
                  <p className="text-2xl font-bold">{analytics.metricas_clave.adopcion_funciones}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Vista de tendencias */}
      {vistaActual === 'tendencias' && analytics?.tendencias && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Análisis de Tendencias</span>
            </CardTitle>
            <CardDescription>
              Evolución de la puntuación y métricas a lo largo del tiempo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Gráfico de tendencias */}
              <div>
                <h4 className="font-medium mb-4">Evolución de la Puntuación</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={prepararDatosTendencias()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fecha" />
                    <YAxis domain={[0, 5]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="puntuacion" stroke="#3B82F6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Gráfico de área para evaluaciones */}
              <div>
                <h4 className="font-medium mb-4">Actividad de Evaluaciones</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={prepararDatosTendencias()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fecha" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="evaluaciones" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Vista de matriz de riesgo */}
      {vistaActual === 'riesgo' && analytics?.matriz_riesgo && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5" />
              <span>Matriz de Riesgo</span>
            </CardTitle>
            <CardDescription>
              Análisis de probabilidad e impacto de riesgos identificados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Gráfico de dispersión */}
              <div>
                <h4 className="font-medium mb-4">Matriz de Riesgo</h4>
                <ResponsiveContainer width="100%" height={400}>
                  <ScatterChart data={prepararDatosMatrizRiesgo()}>
                    <CartesianGrid />
                    <XAxis dataKey="probabilidad" name="Probabilidad" />
                    <YAxis dataKey="impacto" name="Impacto" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter dataKey="categoria" fill="#3B82F6" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              {/* Lista de riesgos */}
              <div>
                <h4 className="font-medium mb-4">Riesgos Identificados</h4>
                <div className="space-y-3">
                  {analytics.matriz_riesgo.map((riesgo, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-medium">{riesgo.categoria}</h5>
                        <Badge 
                          style={{ backgroundColor: getColorRiesgo(riesgo.nivel_riesgo) }}
                          className="text-white"
                        >
                          {riesgo.nivel_riesgo.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{riesgo.descripcion}</p>
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                        <span>Probabilidad: {riesgo.probabilidad}/5</span>
                        <span>Impacto: {riesgo.impacto}/5</span>
                      </div>
                      {riesgo.recomendaciones.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs font-medium text-muted-foreground">Recomendaciones:</p>
                          <ul className="text-xs text-muted-foreground list-disc list-inside">
                            {riesgo.recomendaciones.map((rec, i) => (
                              <li key={i}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Vista de cumplimiento */}
      {vistaActual === 'cumplimiento' && analytics?.cumplimiento && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span>Análisis de Cumplimiento</span>
            </CardTitle>
            <CardDescription>
              Estado de cumplimiento con normativas y estándares
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Gráfico de barras de cumplimiento */}
              <div>
                <h4 className="font-medium mb-4">Cumplimiento por Normativa</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prepararDatosCumplimiento()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="norma" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Bar dataKey="porcentaje" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Lista de cumplimiento */}
              <div>
                <h4 className="font-medium mb-4">Detalle de Cumplimiento</h4>
                <div className="space-y-3">
                  {analytics.cumplimiento.map((cumplimiento, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-medium">{cumplimiento.norma}</h5>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-bold">{cumplimiento.porcentaje}%</span>
                          <Badge 
                            style={{ backgroundColor: getColorCumplimiento(cumplimiento.estado) }}
                            className="text-white"
                          >
                            {cumplimiento.estado.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      <div className="space-y-1">
                        {cumplimiento.requerimientos.map((req, i) => (
                          <div key={i} className="flex items-center space-x-2 text-sm">
                            <div 
                              className={`w-2 h-2 rounded-full ${
                                req.estado === 'cumple' ? 'bg-green-500' :
                                req.estado === 'parcial' ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                            />
                            <span className="text-muted-foreground">{req.descripcion}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Predicciones */}
      {analytics?.predicciones && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="w-5 h-5" />
              <span>Predicciones y Proyecciones</span>
            </CardTitle>
            <CardDescription>
              Análisis predictivo basado en tendencias históricas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <h4 className="font-medium">Próxima Evaluación</h4>
                <p className="text-2xl font-bold text-c4a-blue-600">
                  {new Date(analytics.predicciones.proxima_evaluacion).toLocaleDateString('es-CL')}
                </p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <h4 className="font-medium">Tendencia</h4>
                <div className="flex items-center justify-center space-x-2">
                  {analytics.predicciones.tendencia_puntuacion === 'mejora' ? (
                    <TrendingUp className="w-5 h-5 text-green-600" />
                  ) : analytics.predicciones.tendencia_puntuacion === 'deterioro' ? (
                    <TrendingDown className="w-5 h-5 text-red-600" />
                  ) : (
                    <Target className="w-5 h-5 text-yellow-600" />
                  )}
                  <span className="font-bold">
                    {analytics.predicciones.tendencia_puntuacion.toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <h4 className="font-medium">Probabilidad de Riesgo</h4>
                <p className="text-2xl font-bold text-orange-600">
                  {analytics.predicciones.probabilidad_riesgo}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Acciones */}
      <Card>
        <CardHeader>
          <CardTitle>Acciones Disponibles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Exportar Datos
            </Button>
            <Button variant="outline">
              <Share2 className="w-4 h-4 mr-2" />
              Compartir Reporte
            </Button>
            <Button variant="outline">
              <Eye className="w-4 h-4 mr-2" />
              Vista Detallada
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}