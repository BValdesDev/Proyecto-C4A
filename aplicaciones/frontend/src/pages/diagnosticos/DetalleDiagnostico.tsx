// src/pages/diagnosticos/DetalleDiagnostico.tsx
/**
 * Página de detalle del cuestionario antes de iniciarlo
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCuestionarios, CuestionarioDetalle } from '../../hooks/useCuestionarios';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Separator } from '../../components/ui/separator';
import {
  ArrowLeft,
  Clock,
  FileText,
  PlayCircle,
  ListChecks,
  Target,
  AlertCircle
} from 'lucide-react';

export default function DetalleDiagnostico() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { obtenerCuestionario } = useCuestionarios();
  const [cuestionario, setCuestionario] = useState<CuestionarioDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cargarCuestionario();
  }, [id]);

  const cargarCuestionario = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const cuest = await obtenerCuestionario(id);
      setCuestionario(cuest);
    } catch (err: any) {
      setError(err.response?.data?.mensaje || 'Error al cargar el cuestionario');
    } finally {
      setLoading(false);
    }
  };

  const handleIniciar = () => {
    navigate(`/app/diagnosticos/${id}/responder`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando información...</p>
        </div>
      </div>
    );
  }

  if (error || !cuestionario) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error || 'Cuestionario no encontrado'}</p>
          <Button onClick={() => navigate('/app/diagnosticos')} className="mt-4">
            Volver a diagnósticos
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <Button variant="ghost" onClick={() => navigate('/app/diagnosticos')} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver a diagnósticos
        </Button>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <h1 className="text-3xl font-bold text-gray-900">
                {cuestionario.nombre}
              </h1>
              <Badge variant="outline" className="text-sm">
                v{cuestionario.version}
              </Badge>
            </div>
            <p className="text-gray-600">
              Diagnóstico nivel {cuestionario.nivel}
            </p>
          </div>
        </div>
      </div>

      {/* Información del cuestionario */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Información del Diagnóstico</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Total de preguntas</p>
                <p className="text-lg font-semibold text-gray-900">{cuestionario.total_items} preguntas</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
                <Clock className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Tiempo estimado</p>
                <p className="text-lg font-semibold text-gray-900">{cuestionario.tiempo_estimado_minutos} minutos</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <ListChecks className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Secciones</p>
                <p className="text-lg font-semibold text-gray-900">{cuestionario.estructura_secciones.length} secciones</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-orange-100 flex items-center justify-center">
                <Target className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Nivel</p>
                <p className="text-lg font-semibold text-gray-900 capitalize">{cuestionario.nivel}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Instrucciones */}
      {cuestionario.texto_instrucciones && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Instrucciones</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-line text-gray-700">
                {cuestionario.texto_instrucciones}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Escala de Madurez */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Escala de Evaluación</CardTitle>
          <CardDescription>
            Para cada pregunta, seleccione el nivel que mejor describa la situación de su organización
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(cuestionario.escala_madurez).map(([nivel, descripcion]) => (
              <div key={nivel} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                <div className="h-10 w-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">
                  {nivel}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{descripcion}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Estructura de Secciones */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Estructura del Diagnóstico</CardTitle>
          <CardDescription>
            Secciones y temas que se evaluarán
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {cuestionario.estructura_secciones.map((seccion, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-500">
                    {idx + 1}.
                  </span>
                  <span className="text-gray-900">{seccion.nombre}</span>
                </div>
                <Badge variant="secondary">
                  {seccion.items} pregunta{seccion.items !== 1 ? 's' : ''}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Botón de inicio */}
      <div className="text-center">
        <Button 
          onClick={handleIniciar} 
          size="lg"
          className="px-8"
        >
          <PlayCircle className="h-5 w-5 mr-2" />
          Iniciar Diagnóstico
        </Button>
        <p className="mt-4 text-sm text-gray-600">
          Puede guardar su progreso en cualquier momento y continuar después
        </p>
      </div>
    </div>
  );
}

