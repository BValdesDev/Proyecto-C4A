// src/pages/diagnosticos/ResultadosDiagnostico.tsx
/**
 * Página para mostrar resultados del diagnóstico completado
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ResultadoMadurez, RespuestaCuestionario } from '../../hooks/useCuestionarios';
import apiClient from '../../utilidades/apiClient';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import {
  ArrowLeft,
  Download,
  Share2,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  FileText
} from 'lucide-react';

// Escala de madurez por defecto
const getEscalaMadurez = (nivel: number): string => {
  const escalas = {
    1: "No implementado",
    2: "Parcialmente implementado", 
    3: "En desarrollo",
    4: "Implementado",
    5: "Optimizado/Mejorado continuamente"
  };
  return escalas[nivel as keyof typeof escalas] || `Nivel ${nivel}`;
};

export default function ResultadosDiagnostico() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [resultado, setResultado] = useState<ResultadoMadurez | null>(null);
  const [respuestas, setRespuestas] = useState<RespuestaCuestionario[]>([]);
  const [evaluacionId, setEvaluacionId] = useState<string | null>(null);
  const [pdfGenerado, setPdfGenerado] = useState(false);

  useEffect(() => {
    // Obtener resultados del state de navegación
    const state = location.state as { 
      resultado: ResultadoMadurez; 
      respuestas: RespuestaCuestionario[];
      evaluacionId?: string;
      pdfGenerado?: boolean;
    } | null;
    
    if (state?.resultado) {
      setResultado(state.resultado);
      setRespuestas(state.respuestas || []);
      setEvaluacionId(state.evaluacionId || null);
      setPdfGenerado(state.pdfGenerado || false);
    } else {
      // Si no hay state, volver a diagnósticos
      navigate('/app/diagnosticos');
    }
  }, [location, navigate]);

  const handleDescargarPDF = async () => {
    try {
      const baseURL = apiClient.defaults.baseURL || 'http://localhost:9000'

      // Preparar datos del resultado para el PDF
      const datosPDF = {
        nombre: `Diagnóstico de Ciberseguridad - ${resultado?.nivel_madurez || 'Completado'}`,
        puntuacion_global: resultado?.puntuacion_global || 0,
        puntuaciones_dominio: resultado?.puntuaciones_dominio || {},
        tiempo_real_minutos: resultado?.tiempo_real_minutos || 0,
        total_preguntas: respuestas.length,
        preguntas_completadas: respuestas.length,
        cuestionario_nombre: 'Diagnóstico de Ciberseguridad',
        nivel: 'básico',
        descripcion: 'Evaluación de madurez en ciberseguridad'
      };

      console.log('Datos enviados al PDF:', datosPDF);

      // Llamar al endpoint para generar PDF profesional
      const response = await fetch(`${baseURL}/api/v1/pdf/profesional/diagnostico/profesional`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('c4a_token')}`
        },
        body: JSON.stringify(datosPDF)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error del servidor:', errorText);
        throw new Error(`Error al generar PDF: ${response.status} - ${errorText}`);
      }

      // Crear blob y descargar
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const fecha = new Date().toISOString().split('T')[0];
      link.download = `diagnostico_ciberseguridad_${fecha}.pdf`;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Error al descargar PDF:', error);
      alert('Error al generar el PDF. Por favor, inténtalo de nuevo.');
    }
  };

  const handleCompartir = () => {
    // TODO: Implementar compartir resultados
    };

  const handleNuevoDiagnostico = () => {
    navigate('/app/diagnosticos');
  };

  if (!resultado) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando resultados...</p>
        </div>
      </div>
    );
  }

  const nivelMadurez = resultado.nivel_madurez;

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <Button variant="ghost" onClick={() => navigate('/app/diagnosticos')} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver a diagnósticos
        </Button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Resultados del Diagnóstico
            </h1>
            <p className="text-gray-600">
              Evaluación completada exitosamente
            </p>
          </div>
          <CheckCircle2 className="h-12 w-12 text-green-500" />
        </div>
      </div>

      {/* Resultado Principal */}
      <Card className="mb-8 border-2" style={{ borderColor: nivelMadurez.color }}>
        <CardHeader className="text-center pb-4">
          <div className="mb-4">
            <div 
              className="w-32 h-32 rounded-full mx-auto flex items-center justify-center text-4xl font-bold text-white"
              style={{ backgroundColor: nivelMadurez.color }}
            >
              {resultado.puntuacion_global}%
            </div>
          </div>
          <CardTitle className="text-2xl mb-2">
            Nivel de Madurez: {nivelMadurez.nombre}
          </CardTitle>
          <CardDescription className="text-base">
            {nivelMadurez.descripcion}
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Puntuación Global</span>
                <span className="font-medium">{resultado.puntuacion_global}%</span>
              </div>
              <Progress 
                value={resultado.puntuacion_global} 
                className="h-3"
                style={{ 
                  backgroundColor: '#E5E7EB'
                }}
              />
            </div>

            <div className="flex items-center justify-between text-sm p-4 bg-gray-50 rounded-lg">
              <span className="text-gray-700">Rango de puntuación</span>
              <span className="font-medium" style={{ color: nivelMadurez.color }}>
                {nivelMadurez.rango}%
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Estadísticas */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Preguntas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {respuestas.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Puntuación Promedio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-900">
              {(respuestas.reduce((sum, r) => sum + r.valor, 0) / respuestas.length).toFixed(1)} / 5
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Nivel Alcanzado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold" style={{ color: nivelMadurez.color }}>
              {nivelMadurez.nombre}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recomendaciones */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Recomendaciones de Mejora
          </CardTitle>
          <CardDescription>
            Acciones sugeridas para mejorar su nivel de madurez en ciberseguridad
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {resultado.recomendaciones.map((recomendacion, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <div className="mt-0.5">
                  <div className="h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-sm font-medium">
                    {idx + 1}
                  </div>
                </div>
                <p className="text-gray-700 flex-1">{recomendacion}</p>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Distribución de Respuestas */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Distribución de Respuestas
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map(nivel => {
              const cantidad = respuestas.filter(r => r.valor === nivel).length;
              const porcentaje = (cantidad / respuestas.length) * 100;
              
              return (
                <div key={nivel}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">
                      Nivel {nivel}: {getEscalaMadurez(nivel)}
                    </span>
                    <span className="font-medium text-gray-900">
                      {cantidad} ({porcentaje.toFixed(0)}%)
                    </span>
                  </div>
                  <Progress value={porcentaje} className="h-2" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Notificación de PDF generado automáticamente (Plan Empresarial) */}
      {pdfGenerado && (
        <Card className="mb-8 border-green-200 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 mb-1">
                  Reporte PDF Generado Automáticamente
                </h3>
                <p className="text-sm text-green-700 mb-3">
                  Su reporte PDF profesional ha sido generado automáticamente. Puede descargarlo ahora o acceder a él desde su historial de evaluaciones.
                </p>
                {evaluacionId && (
                  <Button 
                    onClick={async () => {
                      try {
                        const baseURL = apiClient.defaults.baseURL || 'http://localhost:9000'
                        const response = await fetch(`${baseURL}/api/v1/pdf/profesional/diagnostico/profesional/${evaluacionId}`, {
                          headers: {
                            'Authorization': `Bearer ${localStorage.getItem('c4a_token')}`
                          }
                        });
                        if (response.ok) {
                          const blob = await response.blob();
                          const url = window.URL.createObjectURL(blob);
                          const link = document.createElement('a');
                          link.href = url;
                          link.download = `reporte_ciberseguridad_${evaluacionId}.pdf`;
                          document.body.appendChild(link);
                          link.click();
                          document.body.removeChild(link);
                          window.URL.revokeObjectURL(url);
                        }
                      } catch (error) {
                        console.error('Error descargando PDF:', error);
                        handleDescargarPDF(); // Fallback al método manual
                      }
                    }}
                    className="bg-green-600 hover:bg-green-700 text-white"
                    size="sm"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Descargar PDF Generado
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Acciones */}
      <div className="flex flex-wrap gap-4 justify-center">
        <Button onClick={handleDescargarPDF} variant="outline" size="lg">
          <Download className="h-4 w-4 mr-2" />
          {pdfGenerado ? 'Regenerar PDF' : 'Descargar PDF'}
        </Button>
        <Button onClick={handleCompartir} variant="outline" size="lg">
          <Share2 className="h-4 w-4 mr-2" />
          Compartir Resultados
        </Button>
        <Button onClick={handleNuevoDiagnostico} size="lg">
          <FileText className="h-4 w-4 mr-2" />
          Nuevo Diagnóstico
        </Button>
      </div>

      {/* Información adicional */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-600 text-center">
          Los resultados se guardarán automáticamente en su historial. 
          Puede descargar un informe en PDF o compartir los resultados con su equipo.
        </p>
      </div>
    </div>
  );
}

