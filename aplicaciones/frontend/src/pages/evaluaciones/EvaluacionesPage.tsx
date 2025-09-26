import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Input } from '../../components/ui/input'
import { Plus, Search, Filter, MoreHorizontal } from 'lucide-react'
import { api } from '../../utilidades/apiClient'
import { Evaluacion } from '../../tipos'

export const EvaluacionesPage: React.FC = () => {
  const navigate = useNavigate()
  const [evaluaciones, setEvaluaciones] = useState<Evaluacion[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    cargarEvaluaciones()
  }, [])

  const cargarEvaluaciones = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/evaluaciones/?pagina=1&por_pagina=50')
      setEvaluaciones(response.evaluaciones)
    } catch (error) {
      console.error('Error cargando evaluaciones:', error)
    } finally {
      setLoading(false)
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
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Nueva Evaluación
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
          <CardContent className="text-center py-12">
            <div className="text-muted-foreground">
              <Plus className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">No hay evaluaciones</h3>
              <p className="mb-4">Crea tu primera evaluación de ciberseguridad</p>
              <Button onClick={() => navigate('/evaluaciones/crear')}>
                <Plus className="w-4 h-4 mr-2" />
                Crear Evaluación
              </Button>
            </div>
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
                      {evaluacion.framework.nombre_mostrar}
                    </CardDescription>
                  </div>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
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
                  {evaluacion.estado === 'en_progreso' && (
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
                      <Link to={`/evaluaciones/${evaluacion.id}`}>
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
    </div>
  )
}
