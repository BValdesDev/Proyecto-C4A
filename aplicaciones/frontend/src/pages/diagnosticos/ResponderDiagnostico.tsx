// src/pages/diagnosticos/ResponderDiagnostico.tsx
/**
 * Página para responder un diagnóstico/cuestionario
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  useCuestionarios, 
  useResponderCuestionario,
  CuestionarioDetalle,
  PreguntaAsignada 
} from '../../hooks/useCuestionarios';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Textarea } from '../../components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '../../components/ui/radio-group';
import { Label } from '../../components/ui/label';
import { Alert, AlertDescription } from '../../components/ui/alert';
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Clock,
  FileText,
  HelpCircle,
  Save,
  BarChart3,
  TrendingUp
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

export default function ResponderDiagnostico() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { obtenerCuestionario, obtenerPreguntas, calcularMadurez, guardarEvaluacionCompletada } = useCuestionarios();
  const { 
    respuestas, 
    progreso,
    numRespuestasValidas,
    agregarRespuesta, 
    obtenerRespuesta, 
    calcularProgreso,
    exportarRespuestas 
  } = useResponderCuestionario(id || '');

  const [cuestionario, setCuestionario] = useState<CuestionarioDetalle | null>(null);
  const [preguntas, setPreguntas] = useState<PreguntaAsignada[]>([]);
  const [preguntaActual, setPreguntaActual] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, [id]);

  // Recalcular progreso cuando se cargan las preguntas
  useEffect(() => {
    if (preguntas.length > 0) {
      calcularProgreso(preguntas.length);
    }
  }, [preguntas.length]);

  const cargarDatos = async () => {
    if (!id) return;
    
    console.log('🔄 Cargando datos para cuestionario ID:', id);
    setLoading(true);
    setError(null);
    
    try {
      console.log('📡 Obteniendo cuestionario...');
      const cuest = await obtenerCuestionario(id);
      console.log('✅ Cuestionario obtenido:', cuest.nombre);
      
      console.log('📡 Obteniendo preguntas...');
      const pregs = await obtenerPreguntas(id);
      console.log('✅ Preguntas obtenidas:', pregs.length);
      
      setCuestionario(cuest);
      setPreguntas(pregs);
    } catch (err: any) {
      console.error('❌ Error al cargar datos:', err);
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.mensaje || 'Error al cargar el diagnóstico');
    } finally {
      setLoading(false);
    }
  };

  const handleRespuesta = (valor: number) => {
    if (!preguntas[preguntaActual]) return;

    const pregunta = preguntas[preguntaActual];
    const respuestaActual = obtenerRespuesta(pregunta.pregunta_id);

    // Actualizar respuesta inmediatamente
    agregarRespuesta(pregunta.pregunta_id, {
      pregunta_id: pregunta.pregunta_id,
      valor: valor,
      texto_evidencia: respuestaActual?.texto_evidencia || '',
      comentarios: respuestaActual?.comentarios || '',
      nivel_confianza: respuestaActual?.nivel_confianza || 3
    });

    // El progreso se recalcula automáticamente mediante useEffect cuando cambian las respuestas
    // Pero también lo forzamos aquí para asegurar actualización inmediata
    if (preguntas.length > 0) {
      calcularProgreso(preguntas.length);
    }
  };

  const handleEvidencia = (texto: string) => {
    if (!preguntas[preguntaActual]) return;

    const pregunta = preguntas[preguntaActual];
    const respuestaActual = obtenerRespuesta(pregunta.pregunta_id);

    if (respuestaActual) {
      agregarRespuesta(pregunta.pregunta_id, {
        ...respuestaActual,
        texto_evidencia: texto
      });
    }
  };

  const handleComentarios = (texto: string) => {
    if (!preguntas[preguntaActual]) return;

    const pregunta = preguntas[preguntaActual];
    const respuestaActual = obtenerRespuesta(pregunta.pregunta_id);

    if (respuestaActual) {
      agregarRespuesta(pregunta.pregunta_id, {
        ...respuestaActual,
        comentarios: texto
      });
    }
  };

  const handleSiguiente = () => {
    if (preguntaActual < preguntas.length - 1) {
      setPreguntaActual(prev => prev + 1);
    }
  };

  const handleAnterior = () => {
    if (preguntaActual > 0) {
      setPreguntaActual(prev => prev - 1);
    }
  };

  const handleFinalizar = async () => {
    if (!cuestionario || !id) return;

    setGuardando(true);
    try {
      // Calcular resultados
      const resultado = calcularMadurez(exportarRespuestas(), cuestionario);
      
      // Guardar evaluación completada en el backend
      let evaluacionId = null;
      let pdfGeneradoAuto = false;
      try {
        const response = await guardarEvaluacionCompletada(id, {
          ...resultado,
          fecha_inicio: new Date().toISOString(),
          fecha_completada: new Date().toISOString(),
          tiempo_real_minutos: 15 // TODO: Calcular tiempo real
        });
        evaluacionId = response?.evaluacion_id || null;
        
        // Verificar si es Plan Empresarial para indicar que el PDF se generó automáticamente
        const nivelUsuario = cuestionario.nivel; // 'avanzado' para empresarial
        pdfGeneradoAuto = nivelUsuario === 'avanzado' || cuestionario.total_items >= 100;
      } catch (saveError) {
        // Continuar aunque haya error al guardar
        console.error('Error guardando evaluación:', saveError);
      }
      
      // Navegar a resultados
      navigate(`/app/diagnosticos/${id}/resultados`, {
        state: { 
          resultado, 
          respuestas: exportarRespuestas(),
          evaluacionId,
          pdfGenerado: pdfGeneradoAuto
        }
      });
    } catch (err: any) {
      setError('Error al procesar los resultados');
    } finally {
      setGuardando(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando diagnóstico...</p>
        </div>
      </div>
    );
  }

  if (error || !cuestionario || preguntas.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600">{error || 'No se pudieron cargar las preguntas'}</p>
          <Button onClick={() => navigate('/app/diagnosticos')} className="mt-4">
            Volver a diagnósticos
          </Button>
        </div>
      </div>
    );
  }

  const pregunta = preguntas[preguntaActual];
  const respuestaActual = obtenerRespuesta(pregunta.pregunta_id);
  const config = getNivelConfig(cuestionario.nivel);
  const Icon = config.icon;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header con progreso */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <Button variant="ghost" onClick={() => navigate('/app/diagnosticos')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver
          </Button>
          <Badge variant="outline" className={config.color}>
            <Icon className="h-3 w-3 mr-1" />
            {config.label}
          </Badge>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {cuestionario.nombre}
        </h1>

        <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
          <div className="flex items-center">
            <FileText className="h-4 w-4 mr-1" />
            Pregunta {preguntaActual + 1} de {preguntas.length}
          </div>
          <div className="flex items-center">
            <Clock className="h-4 w-4 mr-1" />
            ~{cuestionario.tiempo_estimado_minutos} minutos
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">Progreso</span>
            <span className="font-medium text-gray-900">{Math.min(progreso, 100)}%</span>
          </div>
          <Progress value={Math.min(progreso, 100)} className="h-2" />
        </div>
      </div>

      {/* Pregunta Actual */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-lg mb-2">
                {pregunta.texto_pregunta}
              </CardTitle>
              {pregunta.texto_ayuda && (
                <CardDescription className="flex items-start gap-2">
                  <HelpCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>{pregunta.texto_ayuda}</span>
                </CardDescription>
              )}
            </div>
            <Badge variant="secondary" className="ml-2">
              {pregunta.seccion}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Escala de Madurez */}
          <div>
            <Label className="text-base font-medium mb-4 block">
              Seleccione el nivel de madurez:
            </Label>
            <RadioGroup
              value={respuestaActual?.valor?.toString() || ''}
              onValueChange={(val) => {
                // Ejecutar inmediatamente con un solo clic
                const valorNumerico = parseInt(val);
                if (!isNaN(valorNumerico) && valorNumerico !== respuestaActual?.valor) {
                  handleRespuesta(valorNumerico);
                }
              }}
              className="space-y-3"
            >
              {Object.entries(cuestionario.escala_madurez).map(([nivel, descripcion]) => {
                const valorNumerico = parseInt(nivel);
                const isSelected = respuestaActual?.valor === valorNumerico;
                
                return (
                  <div 
                    key={nivel}
                    className="flex items-center space-x-3 p-3 rounded-lg border-2 hover:bg-gray-50 transition-colors"
                    style={{
                      borderColor: isSelected ? '#3B82F6' : '#E5E7EB',
                      backgroundColor: isSelected ? '#EFF6FF' : 'transparent'
                    }}
                  >
                    <RadioGroupItem value={nivel} id={`nivel-${nivel}`} />
                    <Label 
                      htmlFor={`nivel-${nivel}`} 
                      className="flex-1 cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Nivel {nivel}</span>
                        <span className="text-sm text-gray-600">{descripcion}</span>
                      </div>
                    </Label>
                  </div>
                );
              })}
            </RadioGroup>
          </div>

          {/* Evidencia (opcional) */}
          <div>
            <Label htmlFor="evidencia" className="text-sm font-medium mb-2 block">
              Evidencia o justificación (opcional):
            </Label>
            <Textarea
              id="evidencia"
              placeholder="Describa evidencias que respalden su respuesta..."
              value={respuestaActual?.texto_evidencia || ''}
              onChange={(e) => handleEvidencia(e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>

          {/* Comentarios (opcional) */}
          <div>
            <Label htmlFor="comentarios" className="text-sm font-medium mb-2 block">
              Comentarios adicionales (opcional):
            </Label>
            <Textarea
              id="comentarios"
              placeholder="Agregue cualquier comentario relevante..."
              value={respuestaActual?.comentarios || ''}
              onChange={(e) => handleComentarios(e.target.value)}
              rows={2}
              className="resize-none"
            />
          </div>
        </CardContent>
      </Card>

      {/* Navegación */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handleAnterior}
          disabled={preguntaActual === 0}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Anterior
        </Button>

        <div className="text-sm text-gray-600">
          {numRespuestasValidas || respuestas.filter(r => r.valor !== undefined && r.valor !== null).length} de {preguntas.length} respondidas
        </div>

        {preguntaActual < preguntas.length - 1 ? (
          <Button
            onClick={handleSiguiente}
            disabled={!respuestaActual}
          >
            Siguiente
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button
            onClick={handleFinalizar}
            disabled={respuestas.length < preguntas.length || guardando}
            className="bg-green-600 hover:bg-green-700"
          >
            {guardando ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Procesando...
              </>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Finalizar Diagnóstico
              </>
            )}
          </Button>
        )}
      </div>

      {/* Alerta si falta responder */}
      {preguntaActual === preguntas.length - 1 && respuestas.length < preguntas.length && (
        <Alert className="mt-6">
          <AlertDescription>
            Complete todas las preguntas para finalizar el diagnóstico y ver sus resultados.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

