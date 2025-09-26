import React, { createContext, useContext, useReducer, useCallback } from 'react'
import { toast } from '../ui/use-toast'
import { 
  CheckCircle, 
  AlertCircle, 
  Info, 
  XCircle,
  AlertTriangle
} from 'lucide-react'

interface Notificacion {
  id: string
  tipo: 'success' | 'error' | 'warning' | 'info'
  titulo: string
  mensaje: string
  duracion?: number
  accion?: {
    texto: string
    onClick: () => void
  }
  persistente?: boolean
}

interface NotificationState {
  notificaciones: Notificacion[]
}

type NotificationAction = 
  | { tipo: 'AGREGAR'; notificacion: Notificacion }
  | { tipo: 'REMOVER'; id: string }
  | { tipo: 'LIMPIAR' }

const initialState: NotificationState = {
  notificaciones: []
}

const notificationReducer = (state: NotificationState, action: NotificationAction): NotificationState => {
  switch (action.tipo) {
    case 'AGREGAR':
      return {
        ...state,
        notificaciones: [...state.notificaciones, action.notificacion]
      }
    case 'REMOVER':
      return {
        ...state,
        notificaciones: state.notificaciones.filter(n => n.id !== action.id)
      }
    case 'LIMPIAR':
      return {
        ...state,
        notificaciones: []
      }
    default:
      return state
  }
}

interface NotificationContextType {
  notificaciones: Notificacion[]
  mostrarNotificacion: (notificacion: Omit<Notificacion, 'id'>) => void
  removerNotificacion: (id: string) => void
  limpiarNotificaciones: () => void
  mostrarExito: (titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => void
  mostrarError: (titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => void
  mostrarAdvertencia: (titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => void
  mostrarInfo: (titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const useNotification = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotification debe usarse dentro de NotificationProvider')
  }
  return context
}

interface NotificationProviderProps {
  children: React.ReactNode
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(notificationReducer, initialState)

  const mostrarNotificacion = useCallback((notificacion: Omit<Notificacion, 'id'>) => {
    const id = `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const nuevaNotificacion: Notificacion = {
      ...notificacion,
      id,
      duracion: notificacion.duracion || 5000
    }

    dispatch({ tipo: 'AGREGAR', notificacion: nuevaNotificacion })

    // Auto-remover si no es persistente
    if (!notificacion.persistente) {
      setTimeout(() => {
        dispatch({ tipo: 'REMOVER', id })
      }, nuevaNotificacion.duracion)
    }

    // Mostrar toast también
    toast({
      title: notificacion.titulo,
      description: notificacion.mensaje,
      variant: notificacion.tipo === 'error' ? 'destructive' : 'default'
    })
  }, [])

  const removerNotificacion = useCallback((id: string) => {
    dispatch({ tipo: 'REMOVER', id })
  }, [])

  const limpiarNotificaciones = useCallback(() => {
    dispatch({ tipo: 'LIMPIAR' })
  }, [])

  const mostrarExito = useCallback((titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => {
    mostrarNotificacion({
      tipo: 'success',
      titulo,
      mensaje,
      ...opciones
    })
  }, [mostrarNotificacion])

  const mostrarError = useCallback((titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => {
    mostrarNotificacion({
      tipo: 'error',
      titulo,
      mensaje,
      persistente: true,
      ...opciones
    })
  }, [mostrarNotificacion])

  const mostrarAdvertencia = useCallback((titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => {
    mostrarNotificacion({
      tipo: 'warning',
      titulo,
      mensaje,
      ...opciones
    })
  }, [mostrarNotificacion])

  const mostrarInfo = useCallback((titulo: string, mensaje: string, opciones?: Partial<Notificacion>) => {
    mostrarNotificacion({
      tipo: 'info',
      titulo,
      mensaje,
      ...opciones
    })
  }, [mostrarNotificacion])

  const contextValue: NotificationContextType = {
    notificaciones: state.notificaciones,
    mostrarNotificacion,
    removerNotificacion,
    limpiarNotificaciones,
    mostrarExito,
    mostrarError,
    mostrarAdvertencia,
    mostrarInfo
  }

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  )
}

// Hook para notificaciones específicas del sistema
export const useSystemNotifications = () => {
  const { mostrarExito, mostrarError, mostrarAdvertencia, mostrarInfo } = useNotification()

  const notificarEvaluacionCompletada = useCallback((nombre: string) => {
    mostrarExito(
      'Evaluación completada',
      `La evaluación "${nombre}" se ha completado exitosamente.`
    )
  }, [mostrarExito])

  const notificarEvaluacionGuardada = useCallback((nombre: string) => {
    mostrarInfo(
      'Progreso guardado',
      `El progreso de "${nombre}" se ha guardado automáticamente.`
    )
  }, [mostrarInfo])

  const notificarErrorEvaluacion = useCallback((error: string) => {
    mostrarError(
      'Error en evaluación',
      `Ha ocurrido un error: ${error}`
    )
  }, [mostrarError])

  const notificarReporteGenerado = useCallback((tipo: string) => {
    mostrarExito(
      'Reporte generado',
      `El reporte ${tipo} se ha generado correctamente.`
    )
  }, [mostrarExito])

  const notificarErrorReporte = useCallback((error: string) => {
    mostrarError(
      'Error generando reporte',
      `No se pudo generar el reporte: ${error}`
    )
  }, [mostrarError])

  const notificarSuscripcionCambiada = useCallback((nivel: string) => {
    mostrarExito(
      'Suscripción actualizada',
      `Tu suscripción se ha cambiado a ${nivel}.`
    )
  }, [mostrarExito])

  const notificarErrorSuscripcion = useCallback((error: string) => {
    mostrarError(
      'Error en suscripción',
      `No se pudo procesar la suscripción: ${error}`
    )
  }, [mostrarError])

  const notificarUsuarioInvitado = useCallback((email: string) => {
    mostrarExito(
      'Usuario invitado',
      `Se ha enviado una invitación a ${email}.`
    )
  }, [mostrarExito])

  const notificarErrorUsuario = useCallback((error: string) => {
    mostrarError(
      'Error con usuario',
      `No se pudo procesar la solicitud: ${error}`
    )
  }, [mostrarError])

  return {
    notificarEvaluacionCompletada,
    notificarEvaluacionGuardada,
    notificarErrorEvaluacion,
    notificarReporteGenerado,
    notificarErrorReporte,
    notificarSuscripcionCambiada,
    notificarErrorSuscripcion,
    notificarUsuarioInvitado,
    notificarErrorUsuario
  }
}

