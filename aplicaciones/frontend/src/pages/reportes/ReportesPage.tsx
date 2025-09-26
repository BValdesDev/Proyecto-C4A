import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { FileText, Download, Eye, Calendar } from 'lucide-react'

export const ReportesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Reportes</h1>
          <p className="text-muted-foreground">
            Gestiona y descarga tus reportes de evaluación
          </p>
        </div>
        <Button>
          <FileText className="w-4 h-4 mr-2" />
          Generar Reporte
        </Button>
      </div>

      {/* Lista de reportes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">Evaluación de Seguridad {i}</CardTitle>
                  <CardDescription>
                    NIST CSF 2.0 - Evaluación Completa
                  </CardDescription>
                </div>
                <Badge variant="outline">PDF</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Puntuación</span>
                  <span className="font-medium">78.5/100</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Fecha</span>
                  <span>15/11/2024</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Estado</span>
                  <Badge className="bg-green-100 text-green-800">Completado</Badge>
                </div>
                
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    <Eye className="w-4 h-4 mr-2" />
                    Ver
                  </Button>
                  <Button size="sm" className="flex-1">
                    <Download className="w-4 h-4 mr-2" />
                    Descargar
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}


