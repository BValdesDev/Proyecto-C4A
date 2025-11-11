import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { FileText, Download, Eye, Calendar, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useCuestionarios } from '../../hooks/useCuestionarios';

interface EvaluacionCompletada {
  id: string;
  nombre: string;
  cuestionario_id: string;
  puntuacion_global: number;
  fecha_completada: string;
  estado: string;
}

export const ReportesPage: React.FC = () => {
  const [evaluaciones, setEvaluaciones] = useState<EvaluacionCompletada[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { obtenerEvaluacionesCompletadas } = useCuestionarios();

  useEffect(() => {
    cargarEvaluaciones();
  }, []);

  const cargarEvaluaciones = async () => {
    try {
      setLoading(true);
      const evaluacionesData = await obtenerEvaluacionesCompletadas();
      setEvaluaciones(evaluacionesData || []);
    } catch (err) {
      setError('Error al cargar las evaluaciones');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDescargarPDF = async (evaluacionId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/pdf/diagnostico/profesional/${evaluacionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error al generar PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reporte_diagnostico_${evaluacionId}.pdf`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error al descargar PDF:', error);
      alert('Error al generar el PDF. Por favor, inténtalo de nuevo.');
    }
  };

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-CL', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getNivelColor = (puntuacion: number) => {
    if (puntuacion >= 80) return 'bg-green-100 text-green-800 border-green-200';
    if (puntuacion >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const getNivelTexto = (puntuacion: number) => {
    if (puntuacion >= 80) return 'Excelente';
    if (puntuacion >= 60) return 'Bueno';
    return 'Requiere Mejoras';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando reportes...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={cargarEvaluaciones}>
            Reintentar
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Reportes</h1>
          <p className="text-muted-foreground">
            Gestiona y descarga tus reportes de evaluación completados
          </p>
        </div>
      </div>

      {/* Lista de reportes */}
      {evaluaciones.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay reportes disponibles
          </h3>
          <p className="text-gray-600 mb-4">
            Completa un diagnóstico para generar tu primer reporte
          </p>
          <Button onClick={() => window.location.href = '/app/diagnosticos'}>
            Ir a Diagnósticos
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {evaluaciones.map((evaluacion) => (
            <Card key={evaluacion.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{evaluacion.nombre}</CardTitle>
                    <CardDescription>
                      Diagnóstico de Ciberseguridad
                    </CardDescription>
                  </div>
                  <Badge variant="outline">PDF</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Puntuación</span>
                    <span className="font-medium">{evaluacion.puntuacion_global.toFixed(1)}/100</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Nivel</span>
                    <Badge className={getNivelColor(evaluacion.puntuacion_global)}>
                      {getNivelTexto(evaluacion.puntuacion_global)}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Fecha</span>
                    <span>{formatearFecha(evaluacion.fecha_completada)}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Estado</span>
                    <div className="flex items-center">
                      <CheckCircle2 className="h-4 w-4 text-green-500 mr-1" />
                      <span className="text-green-600 font-medium">Completado</span>
                    </div>
                  </div>
                </div>
              </CardContent>
              <div className="px-6 pb-6">
                <div className="flex gap-2">
                  <Button 
                    onClick={() => handleDescargarPDF(evaluacion.id)}
                    className="flex-1"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Descargar PDF
                  </Button>
                  <Button variant="outline" size="icon">
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};