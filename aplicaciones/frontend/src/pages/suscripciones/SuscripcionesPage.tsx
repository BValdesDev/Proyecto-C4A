import React from 'react'
import { useAuth } from '../../hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Check, X, CreditCard, Users, FileText, BarChart3 } from 'lucide-react'

export const SuscripcionesPage: React.FC = () => {
  const { usuario } = useAuth()

  const planes = [
    {
      id: 'gratuito',
      nombre: 'Gratuito',
      precio: 0,
      descripcion: 'Perfecto para empezar',
      caracteristicas: [
        '10 preguntas básicas',
        '3 recomendaciones',
        '1 evaluación por mes',
        'Reporte con marca de agua',
        'Soporte por email'
      ],
      limitaciones: [
        'Sin benchmarking',
        'Sin análisis avanzado',
        'Limitado a 1 usuario'
      ]
    },
    {
      id: 'pro',
      nombre: 'Pro',
      precio: 32000,
      descripcion: 'Para PyMEs establecidas',
      caracteristicas: [
        '50 preguntas detalladas',
        '15 recomendaciones',
        '50 evaluaciones por mes',
        'Benchmarking sectorial',
        'Dashboard interactivo',
        'Reportes sin marca de agua',
        'Soporte prioritario'
      ],
      limitaciones: [
        'Máximo 10 usuarios',
        'Sin SSO'
      ]
    },
    {
      id: 'empresarial',
      nombre: 'Empresarial',
      precio: 240000,
      descripcion: 'Para grandes organizaciones',
      caracteristicas: [
        '100 preguntas completas',
        '50+ recomendaciones',
        '1000 evaluaciones por mes',
        'SSO y gestión multi-usuario',
        'API completa',
        'Marca blanca',
        'Soporte dedicado',
        'Consultoría personalizada'
      ],
      limitaciones: []
    }
  ]

  const getNivelBadgeColor = (nivel: string) => {
    switch (nivel) {
      case 'gratuito':
        return 'bg-gray-100 text-gray-800'
      case 'pro':
        return 'bg-c4a-blue-100 text-c4a-blue-800'
      case 'empresarial':
        return 'bg-c4a-purple-100 text-c4a-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Suscripciones</h1>
          <p className="text-muted-foreground">
            Elige el plan que mejor se adapte a tu organización
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Badge className={getNivelBadgeColor(usuario?.organizacion?.nivel_suscripcion || 'gratuito')}>
            Plan Actual: {usuario?.organizacion?.nivel_suscripcion?.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* Planes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {planes.map((plan) => (
          <Card 
            key={plan.id} 
            className={`relative flex flex-col h-full ${
              plan.id === usuario?.organizacion?.nivel_suscripcion 
                ? 'ring-2 ring-c4a-blue-500' 
                : ''
            } ${
              plan.id === 'pro' 
                ? 'border-c4a-blue-200' 
                : ''
            }`}
          >
            {plan.id === 'pro' && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <Badge className="bg-c4a-blue-600 text-white">
                  Más Popular
                </Badge>
              </div>
            )}
            
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">{plan.nombre}</CardTitle>
              <CardDescription>{plan.descripcion}</CardDescription>
              <div className="mt-4">
                <span className="text-4xl font-bold">
                  ${plan.precio.toLocaleString('es-CL')}
                </span>
                <span className="text-muted-foreground">/mes</span>
              </div>
            </CardHeader>
            
            <CardContent className="flex flex-col h-full">
              <div className="flex-1 space-y-4">
                {/* Características */}
                <div>
                  <h4 className="font-medium mb-2">Incluye:</h4>
                  <ul className="space-y-2">
                    {plan.caracteristicas.map((caracteristica, index) => (
                      <li key={index} className="flex items-center space-x-2">
                        <Check className="w-4 h-4 text-green-600" />
                        <span className="text-sm">{caracteristica}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Limitaciones */}
                {plan.limitaciones.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Limitaciones:</h4>
                    <ul className="space-y-2">
                      {plan.limitaciones.map((limitacion, index) => (
                        <li key={index} className="flex items-center space-x-2">
                          <X className="w-4 h-4 text-red-500" />
                          <span className="text-sm text-muted-foreground">{limitacion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Botón de acción - siempre en la parte inferior */}
              <div className="pt-4 mt-auto">
                {plan.id === usuario?.organizacion?.nivel_suscripcion ? (
                  <Button className="w-full" disabled>
                    Plan Actual
                  </Button>
                ) : (
                  <Button 
                    className={`w-full ${
                      plan.id === 'pro' 
                        ? 'bg-c4a-blue-600 hover:bg-c4a-blue-700' 
                        : ''
                    }`}
                  >
                    {plan.id === 'gratuito' ? 'Actual Plan' : 'Actualizar Plan'}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Información adicional */}
      <Card>
        <CardHeader>
          <CardTitle>¿Necesitas ayuda para elegir?</CardTitle>
          <CardDescription>
            Nuestro equipo está aquí para ayudarte a encontrar el plan perfecto
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <CreditCard className="w-8 h-8 mx-auto mb-2 text-c4a-blue-600" />
              <h4 className="font-medium">Facturación Flexible</h4>
              <p className="text-sm text-muted-foreground">
                Paga mensual o anual con descuento
              </p>
            </div>
            <div className="text-center">
              <Users className="w-8 h-8 mx-auto mb-2 text-c4a-blue-600" />
              <h4 className="font-medium">Escalable</h4>
              <p className="text-sm text-muted-foreground">
                Cambia de plan en cualquier momento
              </p>
            </div>
            <div className="text-center">
              <FileText className="w-8 h-8 mx-auto mb-2 text-c4a-blue-600" />
              <h4 className="font-medium">Sin Compromiso</h4>
              <p className="text-sm text-muted-foreground">
                Cancela cuando quieras
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
