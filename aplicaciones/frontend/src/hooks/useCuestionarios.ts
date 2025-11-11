// src/hooks/useCuestionarios.ts
/**
 * Hook personalizado para gestionar cuestionarios/diagnósticos
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../utilidades/apiClient';

export interface Cuestionario {
  id: string;
  nombre: string;
  codigo: string;
  descripcion: string | null;
  nivel: 'basico' | 'intermedio' | 'avanzado';
  total_items: number;
  tiempo_estimado_minutos: number;
  version: string;
  esta_activo: boolean;
  es_editable_por_admin: boolean;
  framework_id: string;
  total_evaluaciones: number;
}

export interface CuestionarioDetalle extends Cuestionario {
  texto_instrucciones: string | null;
  configuracion_formato: {
    color_institucional: string;
    color_secundario: string;
    tipografia: string;
    incluir_logo: boolean;
    incluir_portada: boolean;
    incluir_instrucciones: boolean;
  };
  escala_madurez: {
    [key: string]: string;
  };
  niveles_resultado: {
    [key: string]: {
      nombre: string;
      descripcion: string;
      color: string;
    };
  };
  estructura_secciones: Array<{
    nombre: string;
    tipo: string;
    items: number;
  }>;
  total_preguntas_asignadas: number;
}

export interface PreguntaAsignada {
  id: string;
  pregunta_id: string;
  codigo_pregunta: string;
  texto_pregunta: string;
  texto_ayuda: string | null;
  seccion: string;
  tipo_seccion: string;
  orden_seccion: number;
  orden_pregunta: number;
  es_obligatoria: boolean;
  peso: number;
}

export interface RespuestaCuestionario {
  pregunta_id: string;
  valor: number;
  texto_evidencia?: string;
  comentarios?: string;
  nivel_confianza?: number;
}

export interface ResultadoMadurez {
  puntuacion_global: number;
  nivel_madurez: {
    nombre: string;
    descripcion: string;
    color: string;
    rango: string;
  };
  puntuaciones_por_seccion: {
    [seccion: string]: number;
  };
  recomendaciones: string[];
}

export function useCuestionarios() {
  const [cuestionarios, setCuestionarios] = useState<Cuestionario[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluacionesCompletadas, setEvaluacionesCompletadas] = useState<string[]>([]);

  // Listar todos los cuestionarios
  const listarCuestionarios = async (nivel?: string, activosSolo: boolean = true) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (nivel) params.append('nivel', nivel);
      if (!activosSolo) params.append('activos_solo', 'false');

      const response = await apiClient.get(`/api/v1/cuestionarios?${params.toString()}`);
      setCuestionarios(response.data);
      return response.data;
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al cargar cuestionarios';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Obtener detalle de un cuestionario
  const obtenerCuestionario = async (id: string): Promise<CuestionarioDetalle> => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get(`/api/v1/cuestionarios/${id}`);
      return response.data;
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al cargar cuestionario';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Obtener preguntas de un cuestionario
  const obtenerPreguntas = async (
    cuestionarioId: string,
    seccion?: string
  ): Promise<PreguntaAsignada[]> => {
    setLoading(true);
    setError(null);
    try {
      const params = seccion ? `?seccion=${encodeURIComponent(seccion)}` : '';
      const response = await apiClient.get(`/api/v1/cuestionarios/${cuestionarioId}/preguntas${params}`);
      return response.data;
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al cargar preguntas';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Calcular nivel de madurez basado en respuestas
  const calcularMadurez = (
    respuestas: RespuestaCuestionario[],
    cuestionario: CuestionarioDetalle
  ): ResultadoMadurez => {
    // Calcular puntuación global (promedio de todas las respuestas)
    const totalValores = respuestas.reduce((sum, r) => sum + r.valor, 0);
    const puntuacionGlobal = (totalValores / (respuestas.length * 5)) * 100;

    // Determinar nivel de madurez según los rangos configurados
    let nivelMadurez = {
      nombre: 'Inicial',
      descripcion: 'Evaluación incompleta',
      color: '#6B7280',
      rango: '0-20'
    };

    for (const [rango, datos] of Object.entries(cuestionario.niveles_resultado)) {
      const [min, max] = rango.split('-').map(Number);
      if (puntuacionGlobal >= min && puntuacionGlobal <= max) {
        nivelMadurez = {
          ...datos,
          rango
        };
        break;
      }
    }

    // Calcular puntuaciones por sección (simplificado)
    const puntuacionesPorSeccion: { [seccion: string]: number } = {};
    // Aquí se implementaría la lógica real de cálculo por sección

    // Generar recomendaciones basadas en el nivel
    const recomendaciones: string[] = [];
    if (puntuacionGlobal < 40) {
      recomendaciones.push('Establecer políticas básicas de seguridad');
      recomendaciones.push('Capacitar al personal en concientización de ciberseguridad');
      recomendaciones.push('Implementar respaldos regulares de información crítica');
    } else if (puntuacionGlobal < 60) {
      recomendaciones.push('Documentar procesos de seguridad existentes');
      recomendaciones.push('Implementar controles de acceso más robustos');
      recomendaciones.push('Establecer procedimientos de respuesta a incidentes');
    } else if (puntuacionGlobal < 80) {
      recomendaciones.push('Implementar monitoreo continuo de seguridad');
      recomendaciones.push('Realizar evaluaciones de vulnerabilidades periódicas');
      recomendaciones.push('Mejorar la integración de controles de seguridad');
    } else {
      recomendaciones.push('Mantener la mejora continua de procesos');
      recomendaciones.push('Implementar métricas avanzadas de seguridad');
      recomendaciones.push('Compartir mejores prácticas con la industria');
    }

    return {
      puntuacion_global: Math.round(puntuacionGlobal * 10) / 10,
      nivel_madurez: nivelMadurez,
      puntuaciones_por_seccion: puntuacionesPorSeccion,
      recomendaciones
    };
  };

  // Crear cuestionario (solo admins)
  const crearCuestionario = async (data: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post('/api/v1/cuestionarios', data);
      await listarCuestionarios(); // Recargar lista
      return response.data;
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al crear cuestionario';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Actualizar cuestionario (solo admins)
  const actualizarCuestionario = async (id: string, data: any) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.put(`/api/v1/cuestionarios/${id}`, data);
      await listarCuestionarios(); // Recargar lista
      return response.data;
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al actualizar cuestionario';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Eliminar cuestionario (solo admins)
  const eliminarCuestionario = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.delete(`/api/v1/cuestionarios/${id}`);
      await listarCuestionarios(); // Recargar lista
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al eliminar cuestionario';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Clonar cuestionario (solo admins)
  const clonarCuestionario = async (id: string, nuevoNombre: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post(
        `/api/v1/cuestionarios/${id}/clonar?nuevo_nombre=${encodeURIComponent(nuevoNombre)}`
      );
      await listarCuestionarios(); // Recargar lista
      return response.data;
    } catch (err: any) {
      const mensaje = err.response?.data?.mensaje || 'Error al clonar cuestionario';
      setError(mensaje);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Cargar cuestionarios al montar el componente
  useEffect(() => {
    listarCuestionarios();
  }, []);

  // Verificar si el usuario ya completó un cuestionario
  const verificarEvaluacionCompletada = async (cuestionarioId: string): Promise<boolean> => {
    try {
      const response = await apiClient.get(`/api/v1/evaluaciones/completadas/${cuestionarioId}`);
      return response.data.completada || false;
    } catch (error) {
      return false;
    }
  };

  // Obtener evaluaciones completadas del usuario
  const obtenerEvaluacionesCompletadas = async () => {
    try {
      const response = await apiClient.get('/api/v1/evaluaciones/completadas');
      const evaluaciones = response.data || [];
      const ids = evaluaciones.map((evaluacion: any) => evaluacion.cuestionario_id);
      setEvaluacionesCompletadas(ids);
      return evaluaciones;
    } catch (error) {
      return [];
    }
  };

  // Guardar evaluación completada
  const guardarEvaluacionCompletada = async (cuestionarioId: string, resultado: any) => {
    try {
      const response = await apiClient.post(`/api/v1/evaluaciones/completadas/${cuestionarioId}/guardar`, {
        puntuacion_global: resultado.puntuacion_global || 0,
        puntuaciones_dominio: resultado.puntuaciones_dominio || {},
        tiempo_real_minutos: resultado.tiempo_real_minutos || 0,
        fecha_inicio: resultado.fecha_inicio || new Date().toISOString(),
        fecha_completada: resultado.fecha_completada || new Date().toISOString()
      });
      
      // Actualizar la lista de evaluaciones completadas
      setEvaluacionesCompletadas(prev => [...prev, cuestionarioId]);
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  return {
    cuestionarios,
    loading,
    error,
    evaluacionesCompletadas,
    listarCuestionarios,
    obtenerCuestionario,
    obtenerPreguntas,
    calcularMadurez,
    crearCuestionario,
    actualizarCuestionario,
    eliminarCuestionario,
    clonarCuestionario,
    verificarEvaluacionCompletada,
    obtenerEvaluacionesCompletadas,
    guardarEvaluacionCompletada
  };
}

// Hook específico para responder un cuestionario
export function useResponderCuestionario(cuestionarioId: string) {
  const [respuestas, setRespuestas] = useState<Map<string, RespuestaCuestionario>>(new Map());
  const [progreso, setProgreso] = useState(0);
  const [totalPreguntas, setTotalPreguntas] = useState(0);
  const [contadorRespuestas, setContadorRespuestas] = useState(0);

  const agregarRespuesta = (preguntaId: string, respuesta: RespuestaCuestionario) => {
    setRespuestas(prev => {
      const nuevas = new Map(prev);
      nuevas.set(preguntaId, respuesta);
      // Actualizar contador inmediatamente con el nuevo tamaño
      const nuevoSize = nuevas.size;
      setContadorRespuestas(nuevoSize);
      return nuevas;
    });
  };

  const obtenerRespuesta = (preguntaId: string): RespuestaCuestionario | undefined => {
    return respuestas.get(preguntaId);
  };

  const calcularProgreso = useCallback((total: number): number => {
    if (total > 0) {
      setTotalPreguntas(total);
      // Sincronizar contador con el tamaño actual del Map
      setRespuestas(prev => {
        setContadorRespuestas(prev.size);
        return prev;
      });
    }
    return 0;
  }, []);

  // Recalcular progreso automáticamente cuando cambian las respuestas o el total
  useEffect(() => {
    if (totalPreguntas > 0) {
      const prog = (contadorRespuestas / totalPreguntas) * 100;
      const progresoRedondeado = Math.min(Math.round(prog), 100);
      setProgreso(progresoRedondeado);
    } else {
      setProgreso(0);
    }
  }, [contadorRespuestas, totalPreguntas]);

  const limpiarRespuestas = () => {
    setRespuestas(new Map());
    setProgreso(0);
    setTotalPreguntas(0);
    setContadorRespuestas(0);
  };

  const exportarRespuestas = (): RespuestaCuestionario[] => {
    return Array.from(respuestas.values());
  };

  // Calcular número de respuestas válidas (con valor definido)
  const respuestasArray = Array.from(respuestas.entries()).map(([id, resp]) => ({ ...resp, id }));
  const numRespuestasValidas = respuestasArray.filter(r => r.valor !== undefined && r.valor !== null).length;

  return {
    respuestas: respuestasArray,
    progreso,
    numRespuestasValidas, // Agregar contador explícito
    agregarRespuesta,
    obtenerRespuesta,
    calcularProgreso,
    limpiarRespuestas,
    exportarRespuestas
  };
}

