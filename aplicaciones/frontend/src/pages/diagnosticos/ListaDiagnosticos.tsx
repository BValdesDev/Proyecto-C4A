// src/pages/diagnosticos/ListaDiagnosticos.tsx
/**
 * Página principal para listar y seleccionar diagnósticos
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCuestionarios, Cuestionario } from '../../hooks/useCuestionarios';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { 
  ClipboardList, 
  Clock, 
  FileText, 
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  BarChart3
} from 'lucide-react';

const getNivelConfig = (nivel: string) => {
  switch (nivel) {
    case 'basico':
      return {
        label: 'Básico',
        color: 'bg-green-100 text-green-800 border-green-200',
        icon: CheckCircle2,
        descripcion: 'Evaluación rápida e introductoria'
      };
    case 'intermedio':
      return {
        label: 'Intermedio',
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        icon: BarChart3,
        descripcion: 'Evaluación completa basada en NIST CSF'
      };
    case 'avanzado':
      return {
        label: 'Avanzado',
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        icon: TrendingUp,
        descripcion: 'Diagnóstico organizacional exhaustivo'
      };
    default:
      return {
        label: nivel,
        color: 'bg-gray-100 text-gray-800 border-gray-200',
        icon: FileText,
        descripcion: 'Diagnóstico personalizado'
      };
  }
};

export default function ListaDiagnosticos() {
  const navigate = useNavigate();
  const { cuestionarios, loading, error, listarCuestionarios, evaluacionesCompletadas, obtenerEvaluacionesCompletadas } = useCuestionarios();

  useEffect(() => {
    listarCuestionarios();
    obtenerEvaluacionesCompletadas();
  }, []);

  const handleIniciarDiagnostico = (cuestionarioId: string) => {
    // Verificar si ya está completado
    if (evaluacionesCompletadas.includes(cuestionarioId)) {
      alert('Ya has completado este diagnóstico. Ve a la sección de reportes para ver tus resultados.');
      return;
    }
    
    navigate(`/app/diagnosticos/${cuestionarioId}/responder`);
  };

  const handleVerDetalle = (cuestionarioId: string) => {
    navigate(`/app/diagnosticos/${cuestionarioId}`);
  };

  if (loading && cuestionarios.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando diagnósticos...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error al cargar diagnósticos</h2>
          <p className="text-gray-600">{error}</p>
          <Button onClick={() => listarCuestionarios()} className="mt-4">
            Reintentar
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">

      {/* Lista de Cuestionarios */}
      {cuestionarios.length === 0 ? (
        <div className="text-center py-12">
          <ClipboardList className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No hay diagnósticos disponibles
          </h3>
          <p className="text-gray-600">
            No se encontraron diagnósticos en el sistema
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cuestionarios.map(cuestionario => {
            const config = getNivelConfig(cuestionario.nivel);
            const Icon = config.icon;

            return (
              <Card key={cuestionario.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between mb-2">
                    <Badge variant="outline" className={config.color}>
                      <Icon className="h-3 w-3 mr-1" />
                      {config.label}
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      v{cuestionario.version}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl">{cuestionario.nombre}</CardTitle>
                  <CardDescription>{config.descripcion}</CardDescription>
                </CardHeader>

                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <FileText className="h-4 w-4 mr-2 text-gray-400" />
                      <span>{cuestionario.total_items} preguntas</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock className="h-4 w-4 mr-2 text-gray-400" />
                      <span>~{cuestionario.tiempo_estimado_minutos} minutos</span>
                    </div>
                    {cuestionario.total_evaluaciones > 0 && (
                      <div className="flex items-center text-sm text-gray-600">
                        <TrendingUp className="h-4 w-4 mr-2 text-gray-400" />
                        <span>{cuestionario.total_evaluaciones} evaluaciones completadas</span>
                      </div>
                    )}
                  </div>

                  {cuestionario.descripcion && (
                    <p className="mt-4 text-sm text-gray-600 line-clamp-2">
                      {cuestionario.descripcion}
                    </p>
                  )}
                </CardContent>

                <CardFooter className="flex gap-2">
                  {evaluacionesCompletadas.includes(cuestionario.id) ? (
                    <>
                      <Button 
                        onClick={() => handleIniciarDiagnostico(cuestionario.id)}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                        disabled
                      >
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Completado
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => navigate('/app/reportes')}
                      >
                        Ver Reportes
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button 
                        onClick={() => handleIniciarDiagnostico(cuestionario.id)}
                        className="flex-1"
                      >
                        Iniciar Diagnóstico
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => handleVerDetalle(cuestionario.id)}
                      >
                        Ver Detalle
                      </Button>
                    </>
                  )}
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}

    </div>
  );
}

