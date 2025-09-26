import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Download, Eye, Calendar, FileText } from 'lucide-react'

interface ReportCardProps {
  id: string
  title: string
  description: string
  type: 'pdf' | 'excel' | 'dashboard'
  status: 'generado' | 'generando' | 'error'
  createdAt: string
  size?: string
  downloadUrl?: string
  onView?: () => void
  onDownload?: () => void
  onRegenerate?: () => void
}

export const ReportCard: React.FC<ReportCardProps> = ({
  id,
  title,
  description,
  type,
  status,
  createdAt,
  size,
  downloadUrl,
  onView,
  onDownload,
  onRegenerate
}) => {
  const getStatusBadge = () => {
    switch (status) {
      case 'generado':
        return <Badge className="bg-green-100 text-green-800">Generado</Badge>
      case 'generando':
        return <Badge className="bg-yellow-100 text-yellow-800">Generando...</Badge>
      case 'error':
        return <Badge className="bg-red-100 text-red-800">Error</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800">Desconocido</Badge>
    }
  }

  const getTypeIcon = () => {
    switch (type) {
      case 'pdf':
        return <FileText className="w-5 h-5 text-red-600" />
      case 'excel':
        return <FileText className="w-5 h-5 text-green-600" />
      case 'dashboard':
        return <Eye className="w-5 h-5 text-c4a-blue-600" />
      default:
        return <FileText className="w-5 h-5 text-gray-600" />
    }
  }

  const getTypeLabel = () => {
    switch (type) {
      case 'pdf':
        return 'PDF'
      case 'excel':
        return 'Excel'
      case 'dashboard':
        return 'Dashboard'
      default:
        return 'Archivo'
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            {getTypeIcon()}
            <div>
              <CardTitle className="text-lg">{title}</CardTitle>
              <CardDescription className="mt-1">{description}</CardDescription>
            </div>
          </div>
          {getStatusBadge()}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {/* Información del reporte */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Tipo:</span>
              <span className="ml-2 font-medium">{getTypeLabel()}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Creado:</span>
              <span className="ml-2 font-medium">
                {new Date(createdAt).toLocaleDateString('es-CL')}
              </span>
            </div>
            {size && (
              <div>
                <span className="text-muted-foreground">Tamaño:</span>
                <span className="ml-2 font-medium">{size}</span>
              </div>
            )}
            <div>
              <span className="text-muted-foreground">ID:</span>
              <span className="ml-2 font-mono text-xs">{id.slice(0, 8)}...</span>
            </div>
          </div>

          {/* Acciones */}
          <div className="flex space-x-2">
            {status === 'generado' && (
              <>
                {onView && (
                  <Button variant="outline" size="sm" onClick={onView}>
                    <Eye className="w-4 h-4 mr-2" />
                    Ver
                  </Button>
                )}
                {onDownload && (
                  <Button size="sm" onClick={onDownload}>
                    <Download className="w-4 h-4 mr-2" />
                    Descargar
                  </Button>
                )}
              </>
            )}
            
            {status === 'error' && onRegenerate && (
              <Button variant="outline" size="sm" onClick={onRegenerate}>
                Regenerar
              </Button>
            )}
            
            {status === 'generando' && (
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-c4a-blue-600"></div>
                <span>Generando reporte...</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}


