import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Download, Eye, Calendar, CreditCard, AlertCircle } from 'lucide-react'

interface InvoiceCardProps {
  id: string
  invoiceNumber: string
  amount: number
  currency: string
  status: 'paid' | 'pending' | 'overdue' | 'cancelled'
  dueDate: string
  paidDate?: string
  description: string
  onView?: () => void
  onDownload?: () => void
  onPay?: () => void
}

export const InvoiceCard: React.FC<InvoiceCardProps> = ({
  id,
  invoiceNumber,
  amount,
  currency,
  status,
  dueDate,
  paidDate,
  description,
  onView,
  onDownload,
  onPay
}) => {
  const getStatusBadge = () => {
    switch (status) {
      case 'paid':
        return <Badge className="bg-green-100 text-green-800">Pagada</Badge>
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pendiente</Badge>
      case 'overdue':
        return <Badge className="bg-red-100 text-red-800">Vencida</Badge>
      case 'cancelled':
        return <Badge className="bg-gray-100 text-gray-800">Cancelada</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800">Desconocido</Badge>
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'paid':
        return <CreditCard className="w-5 h-5 text-green-600" />
      case 'pending':
        return <Calendar className="w-5 h-5 text-yellow-600" />
      case 'overdue':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'cancelled':
        return <CreditCard className="w-5 h-5 text-gray-600" />
      default:
        return <CreditCard className="w-5 h-5 text-gray-600" />
    }
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('es-CL', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  const isOverdue = status === 'overdue'
  const isPending = status === 'pending'

  return (
    <Card className={`hover:shadow-md transition-shadow ${isOverdue ? 'border-red-200' : ''}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon()}
            <div>
              <CardTitle className="text-lg">
                Factura #{invoiceNumber}
              </CardTitle>
              <CardDescription className="mt-1">{description}</CardDescription>
            </div>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Información de la factura */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Monto:</span>
              <span className={`ml-2 font-bold text-lg ${isOverdue ? 'text-red-600' : ''}`}>
                {formatCurrency(amount, currency)}
              </span>
            </div>
            <div>
              <span className="text-muted-foreground">Vencimiento:</span>
              <span className={`ml-2 font-medium ${isOverdue ? 'text-red-600' : ''}`}>
                {new Date(dueDate).toLocaleDateString('es-CL')}
              </span>
            </div>
            {paidDate && (
              <div>
                <span className="text-muted-foreground">Pagada:</span>
                <span className="ml-2 font-medium text-green-600">
                  {new Date(paidDate).toLocaleDateString('es-CL')}
                </span>
              </div>
            )}
            <div>
              <span className="text-muted-foreground">ID:</span>
              <span className="ml-2 font-mono text-xs">{id.slice(0, 8)}...</span>
            </div>
          </div>

          {/* Alertas */}
          {isOverdue && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center space-x-2 text-red-800">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Factura vencida</span>
              </div>
              <p className="text-sm text-red-700 mt-1">
                Esta factura está vencida. Por favor, contáctanos para resolver el pago.
              </p>
            </div>
          )}

          {/* Acciones */}
          <div className="flex space-x-2">
            {onView && (
              <Button variant="outline" size="sm" onClick={onView}>
                <Eye className="w-4 h-4 mr-2" />
                Ver
              </Button>
            )}
            
            {onDownload && (
              <Button variant="outline" size="sm" onClick={onDownload}>
                <Download className="w-4 h-4 mr-2" />
                Descargar
              </Button>
            )}
            
            {isPending && onPay && (
              <Button size="sm" onClick={onPay} className="bg-c4a-blue-600 hover:bg-c4a-blue-700">
                <CreditCard className="w-4 h-4 mr-2" />
                Pagar Ahora
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

