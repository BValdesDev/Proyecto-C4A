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
  CheckCircle, 
  AlertCircle,
  Shield,
  Lock,
  Clock,
  Building,
  Mail,
  Phone,
  MapPin,
  User,
  Calendar,
  Receipt,
  Download,
  Eye,
  RefreshCw
} from 'lucide-react'
import { toast } from 'sonner'
import { api } from '../../utilidades/apiClient'

// Interfaces según prompt maestro
interface PropiedadesIntegracionStripe {
  organizacionId: string
  nivelActual: 'gratuito' | 'pro' | 'empresarial'
  onPagoExitoso: (resultado: ResultadoPago) => void
  onPagoFallido: (error: ErrorPago) => void
}

interface Plan {
  id: string
  nombre: string
  nivel: 'gratuito' | 'pro' | 'empresarial'
  precio_mensual: number
  moneda: string
  caracteristicas: string[]
  popular?: boolean
}

interface MetodoPago {
  id: string
  tipo: 'tarjeta' | 'transferencia' | 'paypal'
  ultimos_digitos?: string
  marca?: string
  fecha_vencimiento?: string
  es_principal: boolean
  estado: 'activo' | 'inactivo' | 'expirado'
}

interface ResultadoPago {
  id: string
  estado: 'exitoso' | 'pendiente' | 'fallido'
  monto: number
  moneda: string
  fecha: string
  metodo_pago: string
  referencia: string
}

interface ErrorPago {
  codigo: string
  mensaje: string
  detalles?: string
}

interface SesionPago {
  id: string
  url_pago: string
  estado: 'activa' | 'expirada' | 'completada'
  fecha_expiracion: string
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

// Componente principal según prompt maestro
export const IntegracionStripe: React.FC<PropiedadesIntegracionStripe> = ({ 
  organizacionId, 
  nivelActual,
  onPagoExitoso,
  onPagoFallido
}) => {
  const [planes, setPlanes] = useState<Plan[]>([])
  const [metodosPago, setMetodosPago] = useState<MetodoPago[]>([])
  const [facturas, setFacturas] = useState<Factura[]>([])
  const [sesionPago, setSesionPago] = useState<SesionPago | null>(null)
  const [cargando, setCargando] = useState(true)
  const [procesando, setProcesando] = useState(false)
  const [mostrarFormularioPago, setMostrarFormularioPago] = useState(false)
  const [planSeleccionado, setPlanSeleccionado] = useState<Plan | null>(null)

  // Información de facturación
  const [infoFacturacion, setInfoFacturacion] = useState({
    nombre: '',
    email: '',
    telefono: '',
    direccion: '',
    ciudad: '',
    region: '',
    codigo_postal: '',
    rut: ''
  })

  useEffect(() => {
    cargarDatosStripe()
  }, [organizacionId])

  const cargarDatosStripe = async () => {
    try {
      setCargando(true)
      
      // Cargar planes disponibles
      const planesResponse = await api.get('/api/v1/suscripciones/niveles')
      setPlanes(planesResponse.data.planes)

      // Cargar métodos de pago
      const metodosResponse = await api.get(`/api/v1/facturacion/metodos-pago`)
      setMetodosPago(metodosResponse.data.metodos)

      // Cargar facturas
      const facturasResponse = await api.get(`/api/v1/facturacion/facturas`)
      setFacturas(facturasResponse.data.facturas)

      // Cargar información de facturación
      const infoResponse = await api.get(`/api/v1/organizaciones/${organizacionId}/facturacion`)
      setInfoFacturacion(infoResponse.data)

    } catch (error) {
      console.error('Error cargando datos de Stripe:', error)
      toast.error('Error al cargar los datos de pago')
    } finally {
      setCargando(false)
    }
  }

  const crearSesionPago = async (plan: Plan) => {
    try {
      setProcesando(true)
      
      const response = await api.post('/api/v1/stripe/crear-sesion-pago', {
        plan_id: plan.id,
        organizacion_id: organizacionId,
        info_facturacion: infoFacturacion,
        moneda: 'CLP'
      })

      const sesion: SesionPago = response.data
      setSesionPago(sesion)
      
      // Redirigir a Stripe Checkout
      window.location.href = sesion.url_pago
      
    } catch (error) {
      console.error('Error creando sesión de pago:', error)
      toast.error('Error al crear la sesión de pago')
      onPagoFallido({
        codigo: 'STRIPE_SESSION_ERROR',
        mensaje: 'Error al crear la sesión de pago',
        detalles: error instanceof Error ? error.message : 'Error desconocido'
      })
    } finally {
      setProcesando(false)
    }
  }

  const procesarPago = async (plan: Plan) => {
    try {
      setProcesando(true)
      
      const response = await api.post('/api/v1/stripe/procesar-pago', {
        plan_id: plan.id,
        organizacion_id: organizacionId,
        info_facturacion: infoFacturacion,
        moneda: 'CLP'
      })

      const resultado: ResultadoPago = response.data
      
      if (resultado.estado === 'exitoso') {
        toast.success('Pago procesado exitosamente')
        onPagoExitoso(resultado)
        await cargarDatosStripe()
      } else {
        toast.error('Error al procesar el pago')
        onPagoFallido({
          codigo: 'PAYMENT_FAILED',
          mensaje: 'El pago no pudo ser procesado',
          detalles: 'Verifique su método de pago e intente nuevamente'
        })
      }
      
    } catch (error) {
      console.error('Error procesando pago:', error)
      toast.error('Error al procesar el pago')
      onPagoFallido({
        codigo: 'PAYMENT_ERROR',
        mensaje: 'Error al procesar el pago',
        detalles: error instanceof Error ? error.message : 'Error desconocido'
      })
    } finally {
      setProcesando(false)
    }
  }

  const cancelarSuscripcion = async () => {
    try {
      setProcesando(true)
      
      await api.post('/api/v1/stripe/cancelar-suscripcion', {
        organizacion_id: organizacionId
      })

      toast.success('Suscripción cancelada exitosamente')
      await cargarDatosStripe()
      
    } catch (error) {
      console.error('Error cancelando suscripción:', error)
      toast.error('Error al cancelar la suscripción')
    } finally {
      setProcesando(false)
    }
  }

  const actualizarInfoFacturacion = async () => {
    try {
      setProcesando(true)
      
      await api.put(`/api/v1/organizaciones/${organizacionId}/facturacion`, infoFacturacion)
      
      toast.success('Información de facturación actualizada')
      
    } catch (error) {
      console.error('Error actualizando información:', error)
      toast.error('Error al actualizar la información')
    } finally {
      setProcesando(false)
    }
  }

  const formatearMoneda = (monto: number, moneda: string = 'CLP') => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: moneda
    }).format(monto)
  }

  const getColorPlan = (nivel: string) => {
    switch (nivel) {
      case 'gratuito': return 'border-gray-200'
      case 'pro': return 'border-blue-200 bg-blue-50'
      case 'empresarial': return 'border-purple-200 bg-purple-50'
      default: return 'border-gray-200'
    }
  }

  const getIconoPlan = (nivel: string) => {
    switch (nivel) {
      case 'gratuito': return <Shield className="w-5 h-5 text-gray-600" />
      case 'pro': return <Building className="w-5 h-5 text-blue-600" />
      case 'empresarial': return <Shield className="w-5 h-5 text-purple-600" />
      default: return <Shield className="w-5 h-5 text-gray-600" />
    }
  }

  if (cargando) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Cargando información de pago...</p>
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
            <span>Integración Stripe</span>
            <Badge className="bg-green-100 text-green-800">CLP</Badge>
          </CardTitle>
          <CardDescription>
            Gestione suscripciones y pagos en pesos chilenos
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Información de facturación */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Receipt className="w-5 h-5" />
            <span>Información de Facturación</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Nombre de la Empresa</Label>
              <Input
                value={infoFacturacion.nombre}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, nombre: e.target.value }))}
                placeholder="Mi Empresa S.A."
              />
            </div>
            <div className="space-y-2">
              <Label>RUT</Label>
              <Input
                value={infoFacturacion.rut}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, rut: e.target.value }))}
                placeholder="12.345.678-9"
              />
            </div>
            <div className="space-y-2">
              <Label>Email de Facturación</Label>
              <Input
                type="email"
                value={infoFacturacion.email}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, email: e.target.value }))}
                placeholder="facturacion@empresa.cl"
              />
            </div>
            <div className="space-y-2">
              <Label>Teléfono</Label>
              <Input
                value={infoFacturacion.telefono}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, telefono: e.target.value }))}
                placeholder="+56 9 1234 5678"
              />
            </div>
            <div className="space-y-2">
              <Label>Dirección</Label>
              <Input
                value={infoFacturacion.direccion}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, direccion: e.target.value }))}
                placeholder="Av. Principal 123"
              />
            </div>
            <div className="space-y-2">
              <Label>Ciudad</Label>
              <Input
                value={infoFacturacion.ciudad}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, ciudad: e.target.value }))}
                placeholder="Santiago"
              />
            </div>
            <div className="space-y-2">
              <Label>Región</Label>
              <Input
                value={infoFacturacion.region}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, region: e.target.value }))}
                placeholder="Metropolitana"
              />
            </div>
            <div className="space-y-2">
              <Label>Código Postal</Label>
              <Input
                value={infoFacturacion.codigo_postal}
                onChange={(e) => setInfoFacturacion(prev => ({ ...prev, codigo_postal: e.target.value }))}
                placeholder="7500000"
              />
            </div>
          </div>
          <div className="mt-4">
            <Button 
              onClick={actualizarInfoFacturacion}
              disabled={procesando}
            >
              {procesando ? 'Actualizando...' : 'Actualizar Información'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Planes disponibles */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="w-5 h-5" />
            <span>Planes de Suscripción</span>
          </CardTitle>
          <CardDescription>
            Seleccione un plan para su organización
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {planes.map((plan) => (
              <Card key={plan.id} className={`relative ${getColorPlan(plan.nivel)} ${plan.popular ? 'ring-2 ring-c4a-blue-200' : ''}`}>
                {plan.popular && (
                  <div className="absolute -top-2 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-c4a-blue-600">Más Popular</Badge>
                  </div>
                )}
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    {getIconoPlan(plan.nivel)}
                    <span>{plan.nombre}</span>
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
                    onClick={() => {
                      setPlanSeleccionado(plan)
                      setMostrarFormularioPago(true)
                    }}
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

      {/* Métodos de pago */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="w-5 h-5" />
            <span>Métodos de Pago</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {metodosPago.length > 0 ? (
            <div className="space-y-4">
              {metodosPago.map((metodo) => (
                <div key={metodo.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <CreditCard className="w-5 h-5 text-muted-foreground" />
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
                    <Badge 
                      variant={metodo.estado === 'activo' ? 'default' : 'secondary'}
                    >
                      {metodo.estado.toUpperCase()}
                    </Badge>
                    <Button variant="outline" size="sm">
                      Editar
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CreditCard className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
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
            <Receipt className="w-5 h-5" />
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
                      <Receipt className="w-5 h-5 text-muted-foreground" />
                      <div>
                        <h4 className="font-medium">Factura #{factura.numero}</h4>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <span>{new Date(factura.fecha_emision).toLocaleDateString('es-CL')}</span>
                          <span>•</span>
                          <span>{formatearMoneda(factura.monto, factura.moneda)}</span>
                          <span>•</span>
                          <Badge 
                            variant={factura.estado === 'pagada' ? 'default' : 'secondary'}
                          >
                            {factura.estado.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(factura.url_pdf, '_blank')}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        Ver
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          const link = document.createElement('a')
                          link.href = factura.url_pdf
                          link.download = `factura-${factura.numero}.pdf`
                          link.click()
                        }}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Descargar
                      </Button>
                      {factura.estado === 'pendiente' && factura.url_pago && (
                        <Button
                          size="sm"
                          onClick={() => window.location.href = factura.url_pago}
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
              <Receipt className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-semibold mb-2">No hay facturas</h3>
              <p className="text-muted-foreground">
                Las facturas aparecerán aquí una vez que se generen
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modal de confirmación de pago */}
      {mostrarFormularioPago && planSeleccionado && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirmar Pago</CardTitle>
              <CardDescription>
                Confirme los detalles de su suscripción
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-medium">Plan Seleccionado</h4>
                <div className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <span>{planSeleccionado.nombre}</span>
                    <span className="font-bold">
                      {formatearMoneda(planSeleccionado.precio_mensual, planSeleccionado.moneda)}/mes
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Información de Facturación</h4>
                <div className="p-3 border rounded-lg space-y-1 text-sm">
                  <p><strong>Empresa:</strong> {infoFacturacion.nombre}</p>
                  <p><strong>RUT:</strong> {infoFacturacion.rut}</p>
                  <p><strong>Email:</strong> {infoFacturacion.email}</p>
                </div>
              </div>

              <Alert>
                <Shield className="w-4 h-4" />
                <AlertDescription>
                  Los pagos se procesan de forma segura a través de Stripe. 
                  Su información de pago está protegida.
                </AlertDescription>
              </Alert>

              <div className="flex space-x-2">
                <Button 
                  variant="outline" 
                  onClick={() => setMostrarFormularioPago(false)}
                  className="flex-1"
                >
                  Cancelar
                </Button>
                <Button 
                  onClick={() => procesarPago(planSeleccionado)}
                  disabled={procesando}
                  className="flex-1"
                >
                  {procesando ? 'Procesando...' : 'Confirmar Pago'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Información de seguridad */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Lock className="w-5 h-5" />
            <span>Seguridad de Pagos</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-green-600" />
              <span>Encriptación SSL/TLS</span>
            </div>
            <div className="flex items-center space-x-2">
              <Lock className="w-4 h-4 text-green-600" />
              <span>PCI DSS Compliant</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Stripe Secure</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}