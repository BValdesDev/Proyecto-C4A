import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select'
import { Textarea } from '../../components/ui/textarea'
import { Badge } from '../../components/ui/badge'
import { ArrowLeft, Shield, FileText, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

interface Framework {
  id: string
  nombre: string
  nombre_mostrar: string
  version: string
  descripcion?: string
  niveles_disponibles: string[]
}

const CrearEvaluacionPage: React.FC = () => {
  const navigate = useNavigate()
  const [frameworks, setFrameworks] = useState<Framework[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [formData, setFormData] = useState({
    nombre: '',
    framework_id: '',
    descripcion: ''
  })

  useEffect(() => {
    cargarFrameworks()
  }, [])

  const cargarFrameworks = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/evaluaciones/frameworks')
      setFrameworks(response.frameworks)
    } catch (error) {
      console.error('Error cargando frameworks:', error)
      toast.error('Error al cargar los frameworks disponibles')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.nombre.trim()) {
      toast.error('El nombre de la evaluación es requerido')
      return
    }
    
    if (!formData.framework_id) {
      toast.error('Debe seleccionar un framework')
      return
    }

    try {
      setCreating(true)
      const response = await api.post('/api/v1/evaluaciones/', {
        nombre: formData.nombre,
        framework_id: formData.framework_id
      })
      
      toast.success('Evaluación creada exitosamente')
      navigate(`/evaluaciones/${response.id}`)
    } catch (error) {
      console.error('Error creando evaluación:', error)
      toast.error('Error al crear la evaluación')
    } finally {
      setCreating(false)
    }
  }

  const getFrameworkBadgeColor = (niveles: string[]) => {
    if (niveles.includes('empresarial')) return 'bg-purple-100 text-purple-800'
    if (niveles.includes('pro')) return 'bg-blue-100 text-blue-800'
    return 'bg-green-100 text-green-800'
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-c4a-blue-600 mx-auto mb-4"></div>
            <p className="text-muted-foreground">Cargando frameworks...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="ghost"
          onClick={() => navigate('/evaluaciones')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver a Evaluaciones
        </Button>
        
        <div className="flex items-center space-x-3 mb-2">
          <Shield className="w-8 h-8 text-c4a-blue-600" />
          <h1 className="text-3xl font-bold">Crear Nueva Evaluación</h1>
        </div>
        <p className="text-muted-foreground">
          Crea una nueva evaluación de ciberseguridad para tu organización
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Información de la Evaluación</CardTitle>
              <CardDescription>
                Completa los datos básicos para crear tu evaluación
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Nombre */}
                <div className="space-y-2">
                  <Label htmlFor="nombre">Nombre de la Evaluación *</Label>
                  <Input
                    id="nombre"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Ej: Evaluación de Ciberseguridad Q1 2024"
                    required
                  />
                </div>

                {/* Framework */}
                <div className="space-y-2">
                  <Label htmlFor="framework">Framework de Evaluación *</Label>
                  <Select
                    value={formData.framework_id}
                    onValueChange={(value) => setFormData({ ...formData, framework_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona un framework" />
                    </SelectTrigger>
                    <SelectContent>
                      {frameworks.map((framework) => (
                        <SelectItem key={framework.id} value={framework.id}>
                          <div className="flex items-center space-x-2">
                            <span>{framework.nombre_mostrar}</span>
                            <Badge variant="secondary" className="text-xs">
                              v{framework.version}
                            </Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Descripción */}
                <div className="space-y-2">
                  <Label htmlFor="descripcion">Descripción (Opcional)</Label>
                  <Textarea
                    id="descripcion"
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    placeholder="Describe el propósito y alcance de esta evaluación..."
                    rows={4}
                  />
                </div>

                {/* Botones */}
                <div className="flex space-x-4 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => navigate('/evaluaciones')}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={creating}
                    className="bg-c4a-blue-600 hover:bg-c4a-blue-700"
                  >
                    {creating ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Creando...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4 mr-2" />
                        Crear Evaluación
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Información de Frameworks */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Frameworks Disponibles</CardTitle>
              <CardDescription>
                Selecciona el framework que mejor se adapte a tu organización
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {frameworks.map((framework) => (
                <div
                  key={framework.id}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    formData.framework_id === framework.id
                      ? 'border-c4a-blue-500 bg-c4a-blue-50'
                      : 'border-border hover:border-c4a-blue-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold">{framework.nombre_mostrar}</h4>
                    <Badge variant="secondary" className="text-xs">
                      v{framework.version}
                    </Badge>
                  </div>
                  
                  {framework.descripcion && (
                    <p className="text-sm text-muted-foreground mb-3">
                      {framework.descripcion}
                    </p>
                  )}
                  
                  <div className="flex flex-wrap gap-1">
                    {framework.niveles_disponibles.map((nivel) => (
                      <Badge
                        key={nivel}
                        className={`text-xs ${getFrameworkBadgeColor(framework.niveles_disponibles)}`}
                      >
                        {nivel}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Información adicional */}
          <Card>
            <CardHeader>
              <CardTitle>¿Qué sigue?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">Preguntas Personalizadas</p>
                  <p className="text-sm text-muted-foreground">
                    Adaptadas a tu nivel de suscripción
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">Reportes Detallados</p>
                  <p className="text-sm text-muted-foreground">
                    Análisis completo de tu postura de seguridad
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium">Recomendaciones</p>
                  <p className="text-sm text-muted-foreground">
                    Acciones específicas para mejorar
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default CrearEvaluacionPage
















