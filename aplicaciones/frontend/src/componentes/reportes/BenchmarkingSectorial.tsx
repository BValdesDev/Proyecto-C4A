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
  Scatter
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
  Star
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesBenchmarking {
  evaluacionId: string
  organizacion: {
    id: string
    nombre: string
    sector: string
    tamaño: string
    pais: string
  }
  puntuacionActual: number
  nivelUsuario: 'gratuito' | 'pro' | 'empresarial'
}

interface BenchmarkingSector {
  sector: string
  promedio_sector: number
  mediana_sector: number
  percentil_25: number
  percentil_75: number
  percentil_90: number
  total_organizaciones: number
  tendencia_anual: number
  mejores_practicas: string[]
  areas_mejora: string[]
}

interface ComparacionTamaño {
  tamaño: string
  promedio: number
  rango: [number, number]
  total_organizaciones: number
}

interface BenchmarkingGlobal {
  promedio_global: number
  mediana_global: number
  distribucion: Array<{
    rango: string
    porcentaje: number
    cantidad: number
  }>
  tendencias: Array<{
    fecha: string
    promedio: number
    sector: string
  }>
}

interface RankingSector {
  posicion: number
  total: number
  percentil: number
  comparacion: 'superior' | 'igual' | 'inferior'
  diferencia: number
}

// Componente principal según prompt maestro
export const BenchmarkingSectorial: React.FC<PropiedadesBenchmarking> = ({ 
  evaluacionId, 
  organizacion, 
  puntuacionActual,
  nivelUsuario 
}) => {
  const [benchmarkingSector, setBenchmarkingSector] = useState<BenchmarkingSector | null>(null)
  const [comparacionTamaño, setComparacionTamaño] = useState<ComparacionTamaño | null>(null)
  const [benchmarkingGlobal, setBenchmarkingGlobal] = useState<BenchmarkingGlobal | null>(null)
  const [rankingSector, setRankingSector] = useState<RankingSector | null>(null)
  const [cargando, setCargando] = useState(true)
  const [sectorSeleccionado, setSectorSeleccionado] = useState(organizacion.sector)

  useEffect(() => {
    cargarBenchmarking()
  }, [evaluacionId, sectorSeleccionado])

  const cargarBenchmarking = async () => {
    try {
      setCargando(true)
      
      // Cargar benchmarking del sector
      const sectorResponse = await api.get(`/api/v1/analytics/benchmarks-industria`, {
        params: { sector: sectorSeleccionado }
      })
      setBenchmarkingSector(sectorResponse.data)

      // Cargar comparación por tamaño
      const tamañoResponse = await api.get(`/api/v1/analytics/benchmarks-tamaño`, {
        params: { tamaño: organizacion.tamaño }
      })
      setComparacionTamaño(tamañoResponse.data)

      // Cargar benchmarking global
      const globalResponse = await api.get('/api/v1/analytics/benchmarks-global')
      setBenchmarkingGlobal(globalResponse.data)

      // Cargar ranking del sector
      const rankingResponse = await api.get(`/api/v1/analytics/ranking-sector`, {
        params: { 
          sector: sectorSeleccionado,
          puntuacion: puntuacionActual
        }
      })
      setRankingSector(rankingResponse.data)

    } catch (error) {
      console.error('Error cargando benchmarking:', error)
      toast.error('Error al cargar los datos de benchmarking')
    } finally {
      setCargando(false)
    }
  }

  const prepararDatosComparacion = () => {
    if (!benchmarkingSector) return []
    
    return [
      { 
        categoria: 'Su Organización', 
        puntuacion: puntuacionActual, 
        color: '#3B82F6' 
      },
      { 
        categoria: 'Promedio Sector', 
        puntuacion: benchmarkingSector.promedio_sector, 
        color: '#10B981' 
      },
      { 
        categoria: 'Mediana Sector', 
        puntuacion: benchmarkingSector.mediana_sector, 
        color: '#F59E0B' 
      },
      { 
        categoria: 'Percentil 75', 
        puntuacion: benchmarkingSector.percentil_75, 
        color: '#EF4444' 
      }
    ]
  }

  const prepararDatosDistribucion = () => {
    if (!benchmarkingGlobal) return []
    
    return benchmarkingGlobal.distribucion.map(item => ({
      name: item.rango,
      value: item.porcentaje,
      cantidad: item.cantidad
    }))
  }

  const prepararDatosTendencias = () => {
    if (!benchmarkingGlobal) return []
    
    return benchmarkingGlobal.tendencias.filter(t => t.sector === sectorSeleccionado)
  }

  const getColorComparacion = (comparacion: string) => {
    switch (comparacion) {
      case 'superior': return 'text-green-600'
      case 'igual': return 'text-yellow-600'
      case 'inferior': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getIconoComparacion = (comparacion: string) => {
    switch (comparacion) {
      case 'superior': return <TrendingUp className="w-4 h-4 text-green-600" />
      case 'igual': return <Target className="w-4 h-4 text-yellow-600" />
      case 'inferior': return <TrendingDown className="w-4 h-4 text-red-600" />
      default: return <Target className="w-4 h-4 text-gray-600" />
    }
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando benchmarking sectorial...</p>
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
            <BarChart3 className="w-6 h-6 text-c4a-blue-600" />
            <span>Benchmarking Sectorial</span>
          </CardTitle>
          <CardDescription>
            Compare su organización con el promedio del sector {organizacion.sector}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Resumen de posición */}
      {rankingSector && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Award className="w-5 h-5" />
              <span>Posición en el Sector</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-3xl font-bold text-c4a-blue-600">
                  #{rankingSector.posicion}
                </div>
                <div className="text-sm text-muted-foreground">
                  de {rankingSector.total} organizaciones
                </div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-3xl font-bold text-green-600">
                  {rankingSector.percentil}%
                </div>
                <div className="text-sm text-muted-foreground">Percentil</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-3xl font-bold text-yellow-600">
                  {puntuacionActual.toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground">Su Puntuación</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="flex items-center justify-center space-x-2">
                  {getIconoComparacion(rankingSector.comparacion)}
                  <div>
                    <div className={`text-lg font-bold ${getColorComparacion(rankingSector.comparacion)}`}>
                      {rankingSector.comparacion.toUpperCase()}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      al promedio
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comparación con el sector */}
      {benchmarkingSector && (
        <Card>
          <CardHeader>
            <CardTitle>Comparación con el Sector</CardTitle>
            <CardDescription>
              Su organización vs. promedio del sector {sectorSeleccionado}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Gráfico de barras comparativo */}
              <div>
                <h4 className="font-medium mb-4">Comparación de Puntuaciones</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={prepararDatosComparacion()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="categoria" />
                    <YAxis domain={[0, 5]} />
                    <Tooltip />
                    <Bar dataKey="puntuacion" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Estadísticas del sector */}
              <div className="space-y-4">
                <h4 className="font-medium">Estadísticas del Sector</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 border rounded-lg">
                    <span className="text-sm font-medium">Promedio del Sector</span>
                    <span className="font-bold">{benchmarkingSector.promedio_sector.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 border rounded-lg">
                    <span className="text-sm font-medium">Mediana del Sector</span>
                    <span className="font-bold">{benchmarkingSector.mediana_sector.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 border rounded-lg">
                    <span className="text-sm font-medium">Percentil 75</span>
                    <span className="font-bold">{benchmarkingSector.percentil_75.toFixed(1)}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 border rounded-lg">
                    <span className="text-sm font-medium">Total Organizaciones</span>
                    <span className="font-bold">{benchmarkingSector.total_organizaciones}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comparación por tamaño */}
      {comparacionTamaño && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building className="w-5 h-5" />
              <span>Comparación por Tamaño</span>
            </CardTitle>
            <CardDescription>
              Su organización vs. otras organizaciones de tamaño {organizacion.tamaño}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-c4a-blue-600">
                  {puntuacionActual.toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground">Su Organización</div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {comparacionTamaño.promedio.toFixed(1)}
                </div>
                <div className="text-sm text-muted-foreground">
                  Promedio {comparacionTamaño.tamaño}
                </div>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {comparacionTamaño.total_organizaciones}
                </div>
                <div className="text-sm text-muted-foreground">
                  Organizaciones Similares
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Distribución global */}
      {benchmarkingGlobal && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Globe className="w-5 h-5" />
              <span>Distribución Global</span>
            </CardTitle>
            <CardDescription>
              Distribución de puntuaciones a nivel global
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Gráfico de pastel */}
              <div>
                <h4 className="font-medium mb-4">Distribución por Rangos</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={prepararDatosDistribucion()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {prepararDatosDistribucion().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Tendencias */}
              <div>
                <h4 className="font-medium mb-4">Tendencias del Sector</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={prepararDatosTendencias()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fecha" />
                    <YAxis domain={[0, 5]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="promedio" stroke="#3B82F6" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mejores prácticas y áreas de mejora */}
      {benchmarkingSector && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-green-600" />
                <span>Mejores Prácticas del Sector</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {benchmarkingSector.mejores_practicas.map((practica, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5" />
                    <span className="text-sm">{practica}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-yellow-600" />
                <span>Áreas de Mejora Comunes</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {benchmarkingSector.areas_mejora.map((area, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5" />
                    <span className="text-sm">{area}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Información adicional */}
      <Card>
        <CardHeader>
          <CardTitle>Información del Benchmarking</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
            <div>
              <p><strong>Última actualización:</strong> {new Date().toLocaleDateString('es-CL')}</p>
              <p><strong>Fuente de datos:</strong> Evaluaciones C4A SaaS</p>
            </div>
            <div>
              <p><strong>Sector analizado:</strong> {sectorSeleccionado}</p>
              <p><strong>Total de organizaciones:</strong> {benchmarkingSector?.total_organizaciones || 'N/A'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}