import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Progress } from '../../components/ui/progress'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Target,
  Shield,
  Users,
  FileText,
  BarChart3,
  Award,
  Clock,
  DollarSign
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesDashboard {
  evaluacion: Evaluacion
  nivelUsuario: 'gratuito' | 'pro' | 'empresarial'
}

interface Evaluacion {
  id: string
  nombre: string
  organizacion: {
    id: string
    nombre: string
    sector: string
    tamaño: string
  }
  framework: {
    nombre: string
    version: string
  }
  puntuacion_global: number
  puntuaciones_dominio: Record<string, number>
  fecha_completada: string
  nivel_usado: string
}

interface Benchmarking {
  sector: string
  promedio_sector: number
  percentil: number
  comparacion: 'superior' | 'igual' | 'inferior'
}

interface Recomendacion {
  id: string
  titulo: string
  descripcion: string
  esfuerzo: 'BAJO' | 'MEDIO' | 'ALTO'
  impacto: 'BAJO' | 'MEDIO' | 'ALTO'
  plazo: string
  estimacion_costo: string
  prioridad: number
}

interface AnalyticsAvanzado {
  tendencias: Array<{
    fecha: string
    puntuacion: number
  }>
  matriz_riesgo: Array<{
    categoria: string
    probabilidad: number
    impacto: number
  }>
  cumplimiento: Array<{
    norma: string
    porcentaje: number
  }>
}

// Componente principal según prompt maestro
export const DashboardNivel: React.FC<PropiedadesDashboard> = ({ 
  evaluacion, 
  nivelUsuario 
}) => {
  const [benchmarking, setBenchmarking] = useState<Benchmarking | null>(null)
  const [recomendaciones, setRecomendaciones] = useState<Recomendacion[]>([])
  const [analytics, setAnalytics] = useState<AnalyticsAvanzado | null>(null)
  const [cargando, setCargando] = useState(true)

  // Configuración por nivel según prompt maestro
  const mostrarBenchmarking = nivelUsuario !== 'gratuito'
  const mostrarGraficosAvanzados = nivelUsuario === 'empresarial'
  const permitirMultiplesEvaluaciones = nivelUsuario !== 'gratuito'
  const maxRecomendaciones = nivelUsuario === 'gratuito' ? 3 : nivelUsuario === 'pro' ? 15 : 50

  useEffect(() => {
    cargarDatosDashboard()
  }, [evaluacion.id, nivelUsuario])

  const cargarDatosDashboard = async () => {
    try {
      setCargando(true)
      
      // Cargar recomendaciones
      const recResponse = await api.get(`/api/v1/evaluaciones/${evaluacion.id}/recomendaciones`)
      setRecomendaciones(recResponse.data.recomendaciones)

      // Cargar benchmarking para niveles Pro+
      if (mostrarBenchmarking) {
        const benchResponse = await api.get(`/api/v1/evaluaciones/${evaluacion.id}/benchmarks`)
        setBenchmarking(benchResponse.data)
      }

      // Cargar analytics avanzado para nivel empresarial
      if (mostrarGraficosAvanzados) {
        const analyticsResponse = await api.get(`/api/v1/analytics/tendencias/${evaluacion.organizacion.id}`)
        setAnalytics(analyticsResponse.data)
      }

    } catch (error) {
      console.error('Error cargando datos del dashboard:', error)
      toast.error('Error al cargar los datos del dashboard')
    } finally {
      setCargando(false)
    }
  }

  const getColorPuntuacion = (puntuacion: number) => {
    if (puntuacion >= 4) return 'text-green-600'
    if (puntuacion >= 3) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getIconoPuntuacion = (puntuacion: number) => {
    if (puntuacion >= 4) return <CheckCircle className="w-5 h-5 text-green-600" />
    if (puntuacion >= 3) return <AlertTriangle className="w-5 h-5 text-yellow-600" />
    return <AlertTriangle className="w-5 h-5 text-red-600" />
  }

  const prepararDatosRadar = () => {
    return Object.entries(evaluacion.puntuaciones_dominio).map(([dominio, puntuacion]) => ({
      dominio: dominio.replace('_', ' ').toUpperCase(),
      puntuacion,
      fullMark: 5
    }))
  }

  const prepararDatosBarras = () => {
    return Object.entries(evaluacion.puntuaciones_dominio).map(([dominio, puntuacion]) => ({
      dominio: dominio.replace('_', ' ').toUpperCase(),
      puntuacion,
      meta: 4
    }))
  }

  const prepararDatosPie = () => {
    const total = Object.values(evaluacion.puntuaciones_dominio).reduce((sum, val) => sum + val, 0)
    return Object.entries(evaluacion.puntuaciones_dominio).map(([dominio, puntuacion]) => ({
      name: dominio.replace('_', ' ').toUpperCase(),
      value: puntuacion,
      percentage: ((puntuacion / total) * 100).toFixed(1)
    }))
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header con información de la evaluación */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-6 h-6 text-c4a-blue-600" />
                <span>{evaluacion.nombre}</span>
                <Badge variant="outline">
                  {evaluacion.nivel_usado.toUpperCase()}
                </Badge>
              </CardTitle>
              <CardDescription>
                {evaluacion.organizacion.nombre} • {evaluacion.framework.nombre} {evaluacion.framework.version}
              </CardDescription>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-c4a-blue-600">
                {evaluacion.puntuacion_global.toFixed(1)}/5.0
              </div>
              <div className="text-sm text-muted-foreground">
                Puntuación Global
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Resumen de puntuación */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              {getIconoPuntuacion(evaluacion.puntuacion_global)}
              <div>
                <p className="text-sm font-medium">Puntuación Global</p>
                <p className={`text-2xl font-bold ${getColorPuntuacion(evaluacion.puntuacion_global)}`}>
                  {evaluacion.puntuacion_global.toFixed(1)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-c4a-blue-600" />
              <div>
                <p className="text-sm font-medium">Dominios Evaluados</p>
                <p className="text-2xl font-bold">
                  {Object.keys(evaluacion.puntuaciones_dominio).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-c4a-blue-600" />
              <div>
                <p className="text-sm font-medium">Recomendaciones</p>
                <p className="text-2xl font-bold">
                  {recomendaciones.length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-c4a-blue-600" />
              <div>
                <p className="text-sm font-medium">Completada</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(evaluacion.fecha_completada).toLocaleDateString('es-CL')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Benchmarking sectorial para niveles Pro+ */}
      {mostrarBenchmarking && benchmarking && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Comparación Sectorial</span>
            </CardTitle>
            <CardDescription>
              Su organización vs. promedio del sector {benchmarking.sector}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-c4a-blue-600">
                  {evaluacion.puntuacion_global.toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground">Su Organización</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">
                  {benchmarking.promedio_sector.toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground">Promedio Sector</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {benchmarking.percentil}%
                </div>
                <div className="text-sm text-muted-foreground">Percentil</div>
              </div>
            </div>
            <div className="mt-4">
              <div className="flex items-center space-x-2">
                {benchmarking.comparacion === 'superior' ? (
                  <TrendingUp className="w-4 h-4 text-green-600" />
                ) : benchmarking.comparacion === 'inferior' ? (
                  <TrendingDown className="w-4 h-4 text-red-600" />
                ) : (
                  <Target className="w-4 h-4 text-yellow-600" />
                )}
                <span className="text-sm">
                  Su organización está {benchmarking.comparacion} al promedio del sector
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Gráficos según nivel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gráfico de radar */}
        <Card>
          <CardHeader>
            <CardTitle>Puntuaciones por Dominio</CardTitle>
            <CardDescription>
              Evaluación de madurez por área de ciberseguridad
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={prepararDatosRadar()}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dominio" />
                <PolarRadiusAxis angle={90} domain={[0, 5]} />
                <Radar
                  name="Puntuación"
                  dataKey="puntuacion"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Gráfico de barras */}
        <Card>
          <CardHeader>
            <CardTitle>Comparación con Meta</CardTitle>
            <CardDescription>
              Progreso hacia la meta de 4.0 por dominio
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={prepararDatosBarras()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="dominio" />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Bar dataKey="puntuacion" fill="#3B82F6" />
                <Bar dataKey="meta" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Analytics avanzado para nivel empresarial */}
      {mostrarGraficosAvanzados && analytics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Analytics Avanzado</span>
            </CardTitle>
            <CardDescription>
              Análisis de tendencias y matriz de riesgo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Tendencias */}
              <div>
                <h4 className="font-medium mb-4">Tendencias Históricas</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={analytics.tendencias}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fecha" />
                    <YAxis domain={[0, 5]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="puntuacion" stroke="#3B82F6" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Matriz de riesgo */}
              <div>
                <h4 className="font-medium mb-4">Matriz de Riesgo</h4>
                <ResponsiveContainer width="100%" height={200}>
                  <ScatterChart data={analytics.matriz_riesgo}>
                    <CartesianGrid />
                    <XAxis dataKey="probabilidad" />
                    <YAxis dataKey="impacto" />
                    <Tooltip />
                    <Scatter dataKey="categoria" fill="#3B82F6" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Panel de recomendaciones */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Recomendaciones Prioritizadas</span>
          </CardTitle>
          <CardDescription>
            {maxRecomendaciones} recomendaciones basadas en su evaluación
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recomendaciones.slice(0, maxRecomendaciones).map((rec, index) => (
              <div key={rec.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium">{rec.titulo}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {rec.descripcion}
                    </p>
                    <div className="flex items-center space-x-4 mt-2 text-xs text-muted-foreground">
                      <span>Esfuerzo: {rec.esfuerzo}</span>
                      <span>Impacto: {rec.impacto}</span>
                      <span>Plazo: {rec.plazo}</span>
                      <span>{rec.estimacion_costo}</span>
                    </div>
                  </div>
                  <Badge variant="outline">
                    #{index + 1}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Aviso de limitaciones para nivel gratuito */}
      {!permitirMultiplesEvaluaciones && (
        <Alert className="border-c4a-blue-200 bg-c4a-blue-50">
          <AlertTriangle className="w-4 h-4 text-c4a-blue-600" />
          <AlertDescription className="text-c4a-blue-800">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Limitaciones del Plan Gratuito</p>
                <p className="text-sm">
                  Solo puede realizar 1 evaluación por mes. Actualice a Pro para 
                  evaluaciones ilimitadas, benchmarking sectorial y más recomendaciones.
                </p>
              </div>
              <Button size="sm" className="bg-c4a-blue-600 hover:bg-c4a-blue-700">
                Ver Planes
              </Button>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}