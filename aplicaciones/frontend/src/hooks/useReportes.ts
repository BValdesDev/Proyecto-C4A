import { useState, useEffect, useCallback } from 'react'
import { api } from '../utilidades/apiClient'
import { NivelSuscripcion } from '../tipos'

interface Reporte {
  id: string
  nombre: string
  tipo: 'pdf' | 'excel' | 'html'
  estado: 'generando' | 'completado' | 'error'
  fecha_creacion: string
  fecha_completado?: string
  tamaño_archivo?: number
  url_descarga?: string
  configuracion: ConfiguracionReporte
}

interface ConfiguracionReporte {
  incluir_benchmarking: boolean
  incluir_analytics: boolean
  incluir_hoja_ruta: boolean
  incluir_marca_agua: boolean
  formato: 'basico' | 'detallado' | 'empresarial'
  idioma: string
  moneda: string
}

interface UseReportesProps {
  evaluacionId: string
  nivelUsuario: NivelSuscripcion
}

interface UseReportesReturn {
  reportes: Reporte[]
  loading: boolean
  error: string | null
  generando: boolean
  generarReporte: (configuracion: ConfiguracionReporte) => Promise<void>
  descargarReporte: (reporteId: string) => Promise<void>
  eliminarReporte: (reporteId: string) => Promise<void>
  obtenerConfiguracionPorDefecto: () => ConfiguracionReporte
}

export const useReportes = ({ evaluacionId, nivelUsuario }: UseReportesProps): UseReportesReturn => {
  const [reportes, setReportes] = useState<Reporte[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generando, setGenerando] = useState(false)

  const cargarReportes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get(`/api/v1/evaluaciones/${evaluacionId}/reportes`)
      setReportes(response.reportes)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando reportes')
      console.error('Error cargando reportes:', err)
    } finally {
      setLoading(false)
    }
  }, [evaluacionId])

  const generarReporte = useCallback(async (configuracion: ConfiguracionReporte) => {
    try {
      setGenerando(true)
      setError(null)
      
      const response = await api.post(`/api/v1/evaluaciones/${evaluacionId}/generar-reporte`, {
        configuracion
      })
      
      // Agregar el nuevo reporte a la lista
      setReportes(prev => [...prev, response.reporte])
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error generando reporte')
      console.error('Error generando reporte:', err)
    } finally {
      setGenerando(false)
    }
  }, [evaluacionId])

  const descargarReporte = useCallback(async (reporteId: string) => {
    try {
      setError(null)
      
      const response = await api.get(`/api/v1/reportes/${reporteId}/descargar`)
      
      // Crear enlace de descarga
      const link = document.createElement('a')
      link.href = response.url_descarga
      link.download = response.nombre_archivo
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error descargando reporte')
      console.error('Error descargando reporte:', err)
    }
  }, [])

  const eliminarReporte = useCallback(async (reporteId: string) => {
    try {
      setError(null)
      
      await api.delete(`/api/v1/reportes/${reporteId}`)
      
      // Remover el reporte de la lista
      setReportes(prev => prev.filter(reporte => reporte.id !== reporteId))
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error eliminando reporte')
      console.error('Error eliminando reporte:', err)
    }
  }, [])

  const obtenerConfiguracionPorDefecto = useCallback((): ConfiguracionReporte => {
    const configuracionesPorNivel = {
      gratuito: {
        incluir_benchmarking: false,
        incluir_analytics: false,
        incluir_hoja_ruta: false,
        incluir_marca_agua: true,
        formato: 'basico' as const,
        idioma: 'es_CL',
        moneda: 'CLP'
      },
      pro: {
        incluir_benchmarking: true,
        incluir_analytics: true,
        incluir_hoja_ruta: false,
        incluir_marca_agua: false,
        formato: 'detallado' as const,
        idioma: 'es_CL',
        moneda: 'CLP'
      },
      empresarial: {
        incluir_benchmarking: true,
        incluir_analytics: true,
        incluir_hoja_ruta: true,
        incluir_marca_agua: false,
        formato: 'empresarial' as const,
        idioma: 'es_CL',
        moneda: 'CLP'
      }
    }
    
    return configuracionesPorNivel[nivelUsuario]
  }, [nivelUsuario])

  // Cargar reportes al montar
  useEffect(() => {
    cargarReportes()
  }, [cargarReportes])

  return {
    reportes,
    loading,
    error,
    generando,
    generarReporte,
    descargarReporte,
    eliminarReporte,
    obtenerConfiguracionPorDefecto
  }
}

