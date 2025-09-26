import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { 
  FileText, 
  Download, 
  Eye, 
  Share2, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Shield,
  BarChart3,
  TrendingUp,
  Users,
  DollarSign,
  Calendar
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesGeneradorReportes {
  evaluacionId: string
  nivelUsuario: 'gratuito' | 'pro' | 'empresarial'
  organizacion: {
    id: string
    nombre: string
    sector: string
  }
}

interface Reporte {
  id: string
  titulo: string
  tipo: 'basico' | 'detallado' | 'empresarial'
  nivel_generado: string
  fecha_generacion: string
  url_pdf?: string
  url_excel?: string
  tiene_marca_agua: boolean
  tamaño_archivo: number
  estado: 'generando' | 'completado' | 'error'
}

interface ConfiguracionReporte {
  incluir_benchmarking: boolean
  incluir_analytics: boolean
  incluir_hoja_ruta: boolean
  incluir_matriz_riesgo: boolean
  incluir_cumplimiento: boolean
  formato_salida: 'pdf' | 'excel' | 'ambos'
  idioma: 'es' | 'en'
  marca_agua: boolean
}

// Componente principal según prompt maestro
export const GeneradorReportes: React.FC<PropiedadesGeneradorReportes> = ({ 
  evaluacionId, 
  nivelUsuario, 
  organizacion 
}) => {
  const [reportes, setReportes] = useState<Reporte[]>([])
  const [configuracion, setConfiguracion] = useState<ConfiguracionReporte>({
    incluir_benchmarking: nivelUsuario !== 'gratuito',
    incluir_analytics: nivelUsuario === 'empresarial',
    incluir_hoja_ruta: nivelUsuario !== 'gratuito',
    incluir_matriz_riesgo: nivelUsuario === 'empresarial',
    incluir_cumplimiento: nivelUsuario === 'empresarial',
    formato_salida: 'pdf',
    idioma: 'es',
    marca_agua: nivelUsuario === 'gratuito'
  })
  const [generando, setGenerando] = useState(false)
  const [reporteSeleccionado, setReporteSeleccionado] = useState<Reporte | null>(null)

  useEffect(() => {
    cargarReportes()
  }, [evaluacionId])

  const cargarReportes = async () => {
    try {
      const response = await api.get(`/api/v1/evaluaciones/${evaluacionId}/reportes`)
      setReportes(response.data.reportes)
    } catch (error) {
      console.error('Error cargando reportes:', error)
      toast.error('Error al cargar los reportes')
    }
  }

  const generarReporte = async (tipo: 'basico' | 'detallado' | 'empresarial') => {
    try {
      setGenerando(true)
      
      const response = await api.post(`/api/v1/evaluaciones/${evaluacionId}/reporte`, {
        tipo_reporte: tipo,
        configuracion: configuracion
      })

      const nuevoReporte: Reporte = {
        id: response.data.id,
        titulo: `Reporte ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`,
        tipo,
        nivel_generado: nivelUsuario,
        fecha_generacion: new Date().toISOString(),
        url_pdf: response.data.url_pdf,
        url_excel: response.data.url_excel,
        tiene_marca_agua: configuracion.marca_agua,
        tamaño_archivo: response.data.tamaño_archivo,
        estado: 'completado'
      }

      setReportes(prev => [nuevoReporte, ...prev])
      toast.success('Reporte generado exitosamente')
      
    } catch (error) {
      console.error('Error generando reporte:', error)
      toast.error('Error al generar el reporte')
    } finally {
      setGenerando(false)
    }
  }

  const descargarReporte = async (reporte: Reporte) => {
    try {
      if (reporte.url_pdf) {
        const response = await api.get(reporte.url_pdf, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${reporte.titulo}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error descargando reporte:', error)
      toast.error('Error al descargar el reporte')
    }
  }

  const verReporte = (reporte: Reporte) => {
    if (reporte.url_pdf) {
      window.open(reporte.url_pdf, '_blank')
    }
  }

  const compartirReporte = async (reporte: Reporte) => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: reporte.titulo,
          text: `Reporte de evaluación de ciberseguridad - ${organizacion.nombre}`,
          url: reporte.url_pdf
        })
      } else {
        // Fallback para navegadores que no soportan Web Share API
        await navigator.clipboard.writeText(reporte.url_pdf || '')
        toast.success('Enlace copiado al portapapeles')
      }
    } catch (error) {
      console.error('Error compartiendo reporte:', error)
      toast.error('Error al compartir el reporte')
    }
  }

  const getIconoTipo = (tipo: string) => {
    switch (tipo) {
      case 'basico': return <FileText className="w-4 h-4" />
      case 'detallado': return <BarChart3 className="w-4 h-4" />
      case 'empresarial': return <Shield className="w-4 h-4" />
      default: return <FileText className="w-4 h-4" />
    }
  }

  const getColorTipo = (tipo: string) => {
    switch (tipo) {
      case 'basico': return 'bg-gray-100 text-gray-800'
      case 'detallado': return 'bg-blue-100 text-blue-800'
      case 'empresarial': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatearTamaño = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-6 h-6 text-c4a-blue-600" />
            <span>Generador de Reportes</span>
          </CardTitle>
          <CardDescription>
            Genere reportes personalizados según su nivel de suscripción
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Configuración de reporte */}
      <Card>
        <CardHeader>
          <CardTitle>Configuración del Reporte</CardTitle>
          <CardDescription>
            Personalice el contenido y formato de su reporte
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Formato de salida */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Formato de Salida</label>
              <Select 
                value={configuracion.formato_salida} 
                onValueChange={(value: 'pdf' | 'excel' | 'ambos') => 
                  setConfiguracion(prev => ({ ...prev, formato_salida: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="excel">Excel</SelectItem>
                  <SelectItem value="ambos">PDF + Excel</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Idioma */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Idioma</label>
              <Select 
                value={configuracion.idioma} 
                onValueChange={(value: 'es' | 'en') => 
                  setConfiguracion(prev => ({ ...prev, idioma: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="en">English</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Opciones avanzadas para niveles Pro+ */}
          {nivelUsuario !== 'gratuito' && (
            <div className="space-y-4">
              <h4 className="font-medium">Opciones Avanzadas</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={configuracion.incluir_benchmarking}
                    onChange={(e) => setConfiguracion(prev => ({ 
                      ...prev, 
                      incluir_benchmarking: e.target.checked 
                    }))}
                    className="rounded"
                  />
                  <span className="text-sm">Incluir Benchmarking Sectorial</span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={configuracion.incluir_hoja_ruta}
                    onChange={(e) => setConfiguracion(prev => ({ 
                      ...prev, 
                      incluir_hoja_ruta: e.target.checked 
                    }))}
                    className="rounded"
                  />
                  <span className="text-sm">Incluir Hoja de Ruta</span>
                </label>

                {nivelUsuario === 'empresarial' && (
                  <>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={configuracion.incluir_analytics}
                        onChange={(e) => setConfiguracion(prev => ({ 
                          ...prev, 
                          incluir_analytics: e.target.checked 
                        }))}
                        className="rounded"
                      />
                      <span className="text-sm">Incluir Analytics Avanzado</span>
                    </label>

                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={configuracion.incluir_matriz_riesgo}
                        onChange={(e) => setConfiguracion(prev => ({ 
                          ...prev, 
                          incluir_matriz_riesgo: e.target.checked 
                        }))}
                        className="rounded"
                      />
                      <span className="text-sm">Incluir Matriz de Riesgo</span>
                    </label>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Marca de agua para nivel gratuito */}
          {nivelUsuario === 'gratuito' && (
            <Alert className="border-yellow-200 bg-yellow-50">
              <AlertCircle className="w-4 h-4 text-yellow-600" />
              <AlertDescription className="text-yellow-800">
                Los reportes del plan gratuito incluyen marca de agua. 
                Actualice a Pro para reportes sin marca de agua.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Botones de generación */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-gray-600" />
              <span>Reporte Básico</span>
            </CardTitle>
            <CardDescription>
              Resumen ejecutivo y recomendaciones principales
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => generarReporte('basico')}
              disabled={generando}
              className="w-full"
              variant="outline"
            >
              {generando ? 'Generando...' : 'Generar Básico'}
            </Button>
          </CardContent>
        </Card>

        {nivelUsuario !== 'gratuito' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                <span>Reporte Detallado</span>
              </CardTitle>
              <CardDescription>
                Análisis completo con benchmarking y hoja de ruta
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => generarReporte('detallado')}
                disabled={generando}
                className="w-full"
              >
                {generando ? 'Generando...' : 'Generar Detallado'}
              </Button>
            </CardContent>
          </Card>
        )}

        {nivelUsuario === 'empresarial' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-purple-600" />
                <span>Reporte Empresarial</span>
              </CardTitle>
              <CardDescription>
                Análisis completo con matriz de riesgo y cumplimiento
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={() => generarReporte('empresarial')}
                disabled={generando}
                className="w-full bg-purple-600 hover:bg-purple-700"
              >
                {generando ? 'Generando...' : 'Generar Empresarial'}
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Lista de reportes generados */}
      {reportes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Reportes Generados</CardTitle>
            <CardDescription>
              Historial de reportes generados para esta evaluación
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {reportes.map((reporte) => (
                <div key={reporte.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getIconoTipo(reporte.tipo)}
                      <div>
                        <h4 className="font-medium">{reporte.titulo}</h4>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <Badge className={getColorTipo(reporte.tipo)}>
                            {reporte.tipo.toUpperCase()}
                          </Badge>
                          <span>•</span>
                          <span>{formatearTamaño(reporte.tamaño_archivo)}</span>
                          <span>•</span>
                          <span>{new Date(reporte.fecha_generacion).toLocaleDateString('es-CL')}</span>
                          {reporte.tiene_marca_agua && (
                            <Badge variant="outline" className="text-yellow-600">
                              Marca de Agua
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => verReporte(reporte)}
                        disabled={!reporte.url_pdf}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        Ver
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => descargarReporte(reporte)}
                        disabled={!reporte.url_pdf}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Descargar
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => compartirReporte(reporte)}
                        disabled={!reporte.url_pdf}
                      >
                        <Share2 className="w-4 h-4 mr-1" />
                        Compartir
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Información de límites por nivel */}
      <Card>
        <CardHeader>
          <CardTitle>Límites por Nivel de Suscripción</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 border rounded-lg">
              <h4 className="font-medium text-gray-600">Gratuito</h4>
              <p className="text-sm text-muted-foreground mt-2">
                1 reporte por mes<br/>
                Con marca de agua<br/>
                Formato PDF básico
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <h4 className="font-medium text-blue-600">Pro</h4>
              <p className="text-sm text-muted-foreground mt-2">
                10 reportes por mes<br/>
                Sin marca de agua<br/>
                PDF + Excel
              </p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <h4 className="font-medium text-purple-600">Empresarial</h4>
              <p className="text-sm text-muted-foreground mt-2">
                Reportes ilimitados<br/>
                Analytics avanzado<br/>
                Matriz de riesgo
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}