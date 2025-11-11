import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Input } from '../../components/ui/input'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../../components/ui/alert-dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../../components/ui/dropdown-menu'
import { toast } from '../../components/ui/use-toast'
import { Loader2, MoreHorizontal, Filter, Plus, Search, Trash2 } from 'lucide-react'
import { api } from '../../utilidades/apiClient'
import { Evaluacion } from '../../tipos'
import { OnboardingEvaluaciones } from '../../components/onboarding/OnboardingEvaluaciones'
import { useAuth } from '../../hooks/useAuth'

export const EvaluacionesPage: React.FC = () => {
  const navigate = useNavigate()
  const { usuario } = useAuth()
  const [evaluaciones, setEvaluaciones] = useState<Evaluacion[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [mostrarConfirmacion, setMostrarConfirmacion] = useState(false)
  const [evaluacionSeleccionada, setEvaluacionSeleccionada] = useState<Evaluacion | null>(null)
  const [eliminando, setEliminando] = useState(false)
  const [creandoEvaluacion, setCreandoEvaluacion] = useState(false)

  useEffect(() => {
    cargarEvaluaciones()
  }, [])

  const cargarEvaluaciones = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/evaluaciones/?pagina=1&por_pagina=50')
      setEvaluaciones(response.evaluaciones)
    } catch (error) {
      } finally {
      setLoading(false)
    }
  }

  const manejarEliminarClick = (evaluacion: Evaluacion) => {
    setEvaluacionSeleccionada(evaluacion)
    setMostrarConfirmacion(true)
  }

  const manejarCambioDialogo = (open: boolean) => {
    if (!open && !eliminando) {
      setMostrarConfirmacion(false)
      setEvaluacionSeleccionada(null)
    } else {
      setMostrarConfirmacion(open)
    }
  }

  const eliminarEvaluacion = async () => {
    if (!evaluacionSeleccionada) {
      return
    }

    try {
      setEliminando(true)
      await api.delete(`/api/v1/evaluaciones/${evaluacionSeleccionada.id}`)
      setEvaluaciones((prev) => prev.filter((item) => item.id !== evaluacionSeleccionada.id))
      toast({
        title: 'Evaluación eliminada',
        description: 'El registro se eliminó correctamente.',
      })
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.mensaje ||
        error?.response?.data?.detail ||
        'No fue posible eliminar la evaluación. Inténtalo nuevamente.'
      toast({
        title: 'Error al eliminar',
        description: mensaje,
        variant: 'destructive',
      })
    } finally {
      setEliminando(false)
      setMostrarConfirmacion(false)
      setEvaluacionSeleccionada(null)
    }
  }

  const crearEvaluacionRapida = async () => {
    if (creandoEvaluacion) {
      return
    }

    try {
      setCreandoEvaluacion(true)
      const fecha = new Date().toLocaleDateString('es-CL', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      })
      const nombre = `Evaluación Plan Pro - ${fecha}`

      const response = await api.post('/api/v1/dashboard/evaluaciones', {
        nombre,
      })

      toast({
        title: 'Evaluación creada',
        description: 'Generamos el diagnóstico de 50 preguntas para tu Plan Pro. ¡Listo para comenzar!',
      })

      navigate(`/app/evaluaciones/${response.id}`)
    } catch (error: any) {
      const mensaje =
        error?.response?.data?.mensaje ||
        error?.response?.data?.detail ||
        'No fue posible crear la evaluación. Inténtalo nuevamente.'

      toast({
        title: 'Error al crear evaluación',
        description: mensaje,
        variant: 'destructive',
      })
    } finally {
      setCreandoEvaluacion(false)
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

  const evaluacionesFiltradas = evaluaciones.filter(evaluacion =>
    evaluacion.nombre.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="loading-skeleton h-8 w-64"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="loading-skeleton h-48"></div>
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
          <h1 className="text-3xl font-bold text-foreground">Evaluaciones</h1>
          <p className="text-muted-foreground">
            Gestiona tus evaluaciones de ciberseguridad
          </p>
        </div>
        <Button onClick={crearEvaluacionRapida} disabled={creandoEvaluacion}>
          {creandoEvaluacion ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Creando...
            </>
          ) : (
            <>
              <Plus className="w-4 h-4 mr-2" />
              Nueva Evaluación
            </>
          )}
        </Button>
      </div>

      {/* Filtros y búsqueda */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Buscar evaluaciones..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="w-4 h-4 mr-2" />
          Filtros
        </Button>
      </div>

      {/* Lista de evaluaciones */}
      {evaluacionesFiltradas.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <OnboardingEvaluaciones
              onCrearEvaluacion={crearEvaluacionRapida}
              creandoEvaluacion={creandoEvaluacion}
            />
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {evaluacionesFiltradas.map((evaluacion) => (
            <Card key={evaluacion.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{evaluacion.nombre}</CardTitle>
                    <CardDescription>
                      {evaluacion.framework?.nombre_mostrar || evaluacion.framework?.nombre || 'N/A'}
                    </CardDescription>
                  </div>
                  {usuario?.organizacion?.nivel_suscripcion === 'pro' && (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" aria-label="Acciones de evaluación">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => manejarEliminarClick(evaluacion)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Eliminar evaluación
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Estado y puntuación */}
                  <div className="flex items-center justify-between">
                    <Badge className={getEstadoBadgeColor(evaluacion.estado)}>
                      {evaluacion.estado.replace('_', ' ')}
                    </Badge>
                    {evaluacion.puntuacion_global && (
                      <span className="text-sm font-medium">
                        {evaluacion.puntuacion_global.toFixed(1)}/100
                      </span>
                    )}
                  </div>

                  {/* Progreso */}
                  {evaluacion.estado === 'en_progreso' && evaluacion.porcentaje_completado && (
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Progreso</span>
                        <span>{evaluacion.porcentaje_completado.toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-c4a-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${evaluacion.porcentaje_completado}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {/* Información adicional */}
                  <div className="text-sm text-muted-foreground">
                    <p>Preguntas: {evaluacion.preguntas_completadas}/{evaluacion.total_preguntas}</p>
                    <p>Creada: {new Date(evaluacion.fecha_creacion).toLocaleDateString('es-CL')}</p>
                    {evaluacion.fecha_completada && (
                      <p>Completada: {new Date(evaluacion.fecha_completada).toLocaleDateString('es-CL')}</p>
                    )}
                  </div>

                  {/* Acciones */}
                  <div className="flex space-x-2">
                    <Button asChild className="flex-1">
                      <Link to={`/app/evaluaciones/${evaluacion.id}`}>
                        {evaluacion.estado === 'completada' ? 'Ver Resultados' : 'Continuar'}
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <AlertDialog open={mostrarConfirmacion} onOpenChange={manejarCambioDialogo}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Eliminar evaluación?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta acción eliminará la evaluación seleccionada y sus datos asociados. No podrás deshacer este cambio.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={eliminando}>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={eliminarEvaluacion}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
              disabled={eliminando}
            >
              {eliminando && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Eliminar
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
