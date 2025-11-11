import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { 
  CreditCard, 
  DollarSign, 
  Calendar, 
  Download, 
  Eye, 
  CheckCircle, 
  AlertCircle,
  Shield,
  Users,
  FileText,
  BarChart3,
  Clock,
  TrendingUp,
  CreditCard as CardIcon,
  Building,
  Mail,
  Phone
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesPortalFacturacion {
  organizacionId: string
  nivelActual: 'gratuito' | 'pro' | 'empresarial'
}

interface Suscripcion {
  id: string
  nivel: 'gratuito' | 'pro' | 'empresarial'
  estado: 'activa' | 'cancelada' | 'suspendida'
  fecha_inicio: string
  fecha_vencimiento: string
  monto_mensual: number
  moneda: string
  metodo_pago: string
  ultimo_pago: string
  proximo_pago: string
}

interface Factura {
  id: string
  numero: string
  fecha_emision: string
  fecha_vencimiento: string
  monto: number
  moneda: string
  estado: 'pagada' | 'pendiente' | 'vencida'
  descripcion: string
  url_pdf: string
  url_pago?: string
}

interface Plan {
  id: string
  nombre: string
  nivel: 'gratuito' | 'pro' | 'empresarial'
  precio_mensual: number
  moneda: string
  caracteristicas: string[]
  limite_evaluaciones: number
  limite_usuarios: number
  limite_reportes: number
  incluye_benchmarking: boolean
  incluye_analytics: boolean
  incluye_soporte: string
  popular?: boolean
}

interface MetodoPago {
  id: string
  tipo: 'tarjeta' | 'transferencia' | 'paypal'
  ultimos_digitos?: string
  marca?: string
  fecha_vencimiento?: string
  es_principal: boolean
}

// Componente principal según prompt maestro
export const PortalFacturacion: React.FC<PropiedadesPortalFacturacion> = ({ 
  organizacionId, 
  nivelActual 
}) => {
  const [suscripcion, setSuscripcion] = useState<Suscripcion | null>(null)
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [planes, setPlanes] = useState<Plan[]>([])
  const [metodosPago, setMetodosPago] = useState<MetodoPago[]>([])
  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [mostrarCambiarPlan, setMostrarCambiarPlan] = useState(false)

  useEffect(() => {
    cargarDatosFacturacion()
  }, [organizacionId])

  const cargarDatosFacturacion = async () => {
    try {
      setCargando(true)
      
      // Cargar suscripción actual
      const suscripcionResponse = await api.get(`/api/v1/suscripciones/organizacion/${organizacionId}`)
      setSuscripcion(suscripcionResponse.data)

      // Cargar facturas
      const facturasResponse = await api.get(`/api/v1/facturacion/facturas`)
      setFacturas(facturasResponse.data.facturas)

      // Cargar planes disponibles
      const planesResponse = await api.get('/api/v1/suscripciones/niveles')
      setPlanes(planesResponse.data.planes)

      // Cargar métodos de pago
      const metodosResponse = await api.get(`/api/v1/facturacion/metodos-pago`)
      setMetodosPago(metodosResponse.data.metodos)

    } catch (error) {
      toast.error('Error al cargar los datos de facturación')
    } finally {
      setCargando(false)
    }
  }

  const cambiarPlan = async (nuevoPlan: Plan) => {
    try {
      setProcesando(true)
      
      const response = await api.post('/api/v1/suscripciones/cambiar-plan', {
        plan_id: nuevoPlan.id,
        organizacion_id: organizacionId
      })

      if (response.data.url_pago) {
        // Redirigir a Stripe para completar el pago
        window.location.href = response.data.url_pago
      } else {
        toast.success('Plan actualizado exitosamente')
        await cargarDatosFacturacion()
        setMostrarCambiarPlan(false)
      }
      
    } catch (error) {
      console.error('Error cambiando plan:', error)
      toast.error('Error al cambiar el plan')
    } finally {
      setProcesando(false)
    }
  }

  const cancelarSuscripcion = async () => {
    try {
      setProcesando(true)
      
      await api.post('/api/v1/suscripciones/cancelar', {
        organizacion_id: organizacionId
      })

      toast.success('Suscripción cancelada exitosamente')
      await cargarDatosFacturacion()
      
    } catch (error) {
      console.error('Error cancelando suscripción:', error)
      toast.error('Error al cancelar la suscripción')
    } finally {
      setProcesando(false)
    }
  }

  const descargarFactura = async (factura: Factura) => {
    try {
      const response = await api.get(factura.url_pdf, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `factura-${factura.numero}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error descargando factura:', error)
      toast.error('Error al descargar la factura')
    }
  }

  const pagarFactura = async (factura: Factura) => {
    try {
      if (factura.url_pago) {
        window.location.href = factura.url_pago
      } else {
        toast.error('No hay método de pago disponible para esta factura')
      }
    } catch (error) {
      console.error('Error pagando factura:', error)
      toast.error('Error al procesar el pago')
    }
  }

  const formatearMoneda = (monto: number, moneda: string = 'CLP') => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: moneda
    }).format(monto)
  }

  const getColorEstado = (estado: string) => {
    switch (estado) {
      case 'pagada': return 'bg-green-100 text-green-800'
      case 'pendiente': return 'bg-yellow-100 text-yellow-800'
      case 'vencida': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getIconoEstado = (estado: string) => {
    switch (estado) {
      case 'pagada': return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'pendiente': return <Clock className="w-4 h-4 text-yellow-600" />
      case 'vencida': return <AlertCircle className="w-4 h-4 text-red-600" />
      default: return <AlertCircle className="w-4 h-4 text-gray-600" />
    }
  }

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando portal de facturación...</p>
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
            <CreditCard className="w-6 h-6 text-c4a-blue-600" />
            <span>Portal de Facturación</span>
          </CardTitle>
          <CardDescription>
            Gestione su suscripción, facturas y métodos de pago
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Resumen de suscripción actual */}
      {suscripcion && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span>Suscripción Actual</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 border rounded-lg">
                <h4 className="font-medium text-lg">{suscripcion.nivel.toUpperCase()}</h4>
                <p className="text-sm text-muted-foreground">Plan Actual</p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <h4 className="font-medium text-lg">
                  {formatearMoneda(suscripcion.monto_mensual, suscripcion.moneda)}
                </h4>
                <p className="text-sm text-muted-foreground">Mensual</p>
              </div>
              <div className="text-center p-4 border rounded-lg">
                <h4 className="font-medium text-lg">
                  {new Date(suscripcion.fecha_vencimiento).toLocaleDateString('es-CL')}
                </h4>
                <p className="text-sm text-muted-foreground">Próximo Pago</p>
              </div>
            </div>
            <div className="mt-4 flex justify-center space-x-2">
              <Button 
                variant="outline" 
                onClick={() => setMostrarCambiarPlan(true)}
                disabled={procesando}
              >
                Cambiar Plan
              </Button>
              {suscripcion.nivel !== 'gratuito' && (
                <Button 
                  variant="outline" 
                  onClick={cancelarSuscripcion}
                  disabled={procesando}
                  className="text-red-600 hover:text-red-700"
                >
                  Cancelar Suscripción
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Métodos de pago */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CardIcon className="w-5 h-5" />
            <span>Métodos de Pago</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {metodosPago.length > 0 ? (
            <div className="space-y-4">
              {metodosPago.map((metodo) => (
                <div key={metodo.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CardIcon className="w-5 h-5 text-muted-foreground" />
                    <div>
                      <h4 className="font-medium">
                        {metodo.tipo === 'tarjeta' ? 'Tarjeta de Crédito' : 
                         metodo.tipo === 'transferencia' ? 'Transferencia Bancaria' : 
                         'PayPal'}
                      </h4>
                      {metodo.ultimos_digitos && (
                        <p className="text-sm text-muted-foreground">
                          **** **** **** {metodo.ultimos_digitos}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {metodo.es_principal && (
                      <Badge variant="outline">Principal</Badge>
                    )}
                    <Button variant="outline" size="sm">
                      Editar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CardIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No hay métodos de pago</h3>
              <p className="text-muted-foreground mb-4">
                Agregue un método de pago para gestionar su suscripción
              </p>
              <Button>
                Agregar Método de Pago
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Facturas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Historial de Facturas</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {facturas.length > 0 ? (
            <div className="space-y-4">
              {facturas.map((factura) => (
                <div key={factura.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getIconoEstado(factura.estado)}
                      <div>
                        <h4 className="font-medium">Factura #{factura.numero}</h4>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <span>{new Date(factura.fecha_emision).toLocaleDateString('es-CL')}</span>
                          <span>•</span>
                          <span>{formatearMoneda(factura.monto, factura.moneda)}</span>
                          <span>•</span>
                          <Badge className={getColorEstado(factura.estado)}>
                            {factura.estado.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => descargarFactura(factura)}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Descargar
                      </Button>
                      {factura.estado === 'pendiente' && factura.url_pago && (
                        <Button
                          size="sm"
                          onClick={() => pagarFactura(factura)}
                        >
                          <CreditCard className="w-4 h-4 mr-1" />
                          Pagar
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No hay facturas</h3>
              <p className="text-muted-foreground">
                Las facturas aparecerán aquí una vez que se generen
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal para cambiar plan */}
      {mostrarCambiarPlan && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>Cambiar Plan de Suscripción</CardTitle>
              <CardDescription>
                Seleccione un nuevo plan para su organización
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {planes.map((plan) => (
                  <Card key={plan.id} className={`relative ${plan.popular ? 'border-c4a-blue-200 bg-c4a-blue-50' : ''}`}>
                    {plan.popular && (
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                        <Badge className="bg-c4a-blue-600">Más Popular</Badge>
                      </div>
                    )}
                    <CardHeader>
                      <CardTitle className="text-center">
                        {plan.nombre}
                      </CardTitle>
                      <div className="text-center">
                        <span className="text-3xl font-bold">
                          {formatearMoneda(plan.precio_mensual, plan.moneda)}
                        </span>
                        <span className="text-muted-foreground">/mes</span>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        {plan.caracteristicas.map((caracteristica, index) => (
                          <div key={index} className="flex items-center space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-600" />
                            <span className="text-sm">{caracteristica}</span>
                          </div>
                        ))}
                      </div>
                      <Button 
                        className="w-full"
                        onClick={() => cambiarPlan(plan)}
                        disabled={procesando || plan.nivel === nivelActual}
                        variant={plan.nivel === nivelActual ? "outline" : "default"}
                      >
                        {plan.nivel === nivelActual ? 'Plan Actual' : 
                         procesando ? 'Procesando...' : 'Seleccionar Plan'}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Información de facturación */}
      <Card>
        <CardHeader>
          <CardTitle>Información de Facturación</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Email de Facturación</Label>
              <Input placeholder="facturacion@empresa.cl" />
            </div>
            <div className="space-y-2">
              <Label>RUT de la Empresa</Label>
              <Input placeholder="12.345.678-9" />
            </div>
            <div className="space-y-2">
              <Label>Dirección</Label>
              <Input placeholder="Av. Principal 123, Santiago" />
            </div>
            <div className="space-y-2">
              <Label>Teléfono</Label>
              <Input placeholder="+56 9 1234 5678" />
            </div>
          </div>
          <div className="mt-4">
            <Button>
              Actualizar Información
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}