import { useState, useEffect, useCallback } from 'react'
import { api } from '../utilidades/apiClient'
import { NivelSuscripcion } from '../tipos'

interface Suscripcion {
  id: string
  nivel: NivelSuscripcion
  estado: 'activa' | 'cancelada' | 'suspendida'
  fecha_inicio: string
  fecha_vencimiento: string
  precio_mensual: number
  moneda: string
  caracteristicas: CaracteristicasSuscripcion
}

interface CaracteristicasSuscripcion {
  max_evaluaciones: number
  max_usuarios: number
  incluye_benchmarking: boolean
  incluye_analytics: boolean
  incluye_reportes_avanzados: boolean
  incluye_soporte_prioritario: boolean
  incluye_api: boolean
  incluye_marca_blanca: boolean
}

interface UseSuscripcionReturn {
  suscripcion: Suscripcion | null
  loading: boolean
  error: string | null
  cambiarPlan: (nuevoNivel: NivelSuscripcion) => Promise<void>
  cancelarSuscripcion: () => Promise<void>
  renovarSuscripcion: () => Promise<void>
  verificarLimites: (tipo: 'evaluaciones' | 'usuarios') => boolean
  obtenerCaracteristicas: () => CaracteristicasSuscripcion
}

export const useSuscripcion = (): UseSuscripcionReturn => {
  const [suscripcion, setSuscripcion] = useState<Suscripcion | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const cargarSuscripcion = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await api.get('/api/v1/suscripciones/actual')
      setSuscripcion(response)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cargando suscripción')
      console.error('Error cargando suscripción:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const cambiarPlan = useCallback(async (nuevoNivel: NivelSuscripcion) => {
    try {
      setLoading(true)
      setError(null)
      
      await api.post('/api/v1/suscripciones/cambiar-plan', {
        nuevo_nivel: nuevoNivel
      })
      
      // Recargar suscripción
      await cargarSuscripcion()
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cambiando plan')
      console.error('Error cambiando plan:', err)
    } finally {
      setLoading(false)
    }
  }, [cargarSuscripcion])

  const cancelarSuscripcion = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      await api.post('/api/v1/suscripciones/cancelar')
      
      // Recargar suscripción
      await cargarSuscripcion()
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error cancelando suscripción')
      console.error('Error cancelando suscripción:', err)
    } finally {
      setLoading(false)
    }
  }, [cargarSuscripcion])

  const renovarSuscripcion = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      await api.post('/api/v1/suscripciones/renovar')
      
      // Recargar suscripción
      await cargarSuscripcion()
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error renovando suscripción')
      console.error('Error renovando suscripción:', err)
    } finally {
      setLoading(false)
    }
  }, [cargarSuscripcion])

  const verificarLimites = useCallback((tipo: 'evaluaciones' | 'usuarios'): boolean => {
    if (!suscripcion) return false
    
    // Lógica para verificar límites según el tipo
    // Esto debería integrarse con el estado real de la organización
    return true // Por ahora siempre permite
  }, [suscripcion])

  const obtenerCaracteristicas = useCallback((): CaracteristicasSuscripcion => {
    if (!suscripcion) {
      // Características por defecto para nivel gratuito
      return {
        max_evaluaciones: 1,
        max_usuarios: 1,
        incluye_benchmarking: false,
        incluye_analytics: false,
        incluye_reportes_avanzados: false,
        incluye_soporte_prioritario: false,
        incluye_api: false,
        incluye_marca_blanca: false
      }
    }
    
    return suscripcion.caracteristicas
  }, [suscripcion])

  // Cargar suscripción al montar
  useEffect(() => {
    cargarSuscripcion()
  }, [cargarSuscripcion])

  return {
    suscripcion,
    loading,
    error,
    cambiarPlan,
    cancelarSuscripcion,
    renovarSuscripcion,
    verificarLimites,
    obtenerCaracteristicas
  }
}

