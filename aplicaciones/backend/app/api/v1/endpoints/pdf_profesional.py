#!/usr/bin/env python3
"""
Endpoint para generación de PDFs profesionales
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import io
from datetime import datetime

from ....modelos import Evaluacion, Usuario, Organizacion, Cuestionario
from ....modelos.base import obtener_sesion
from ..dependencias import obtener_usuario_actual, obtener_usuario_opcional
from ....servicios.pdf_profesional_service import PDFProfesionalService

router = APIRouter()

@router.post("/diagnostico/profesional")
async def generar_pdf_profesional(
    datos_resultado: Dict[str, Any] = Body(...),
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion)
):
    """Generar PDF profesional con análisis detallado y recomendaciones"""
    try:
        # Si no hay usuario autenticado, usar datos por defecto
        if not usuario_actual:
            usuario_data = {
                'nombre': 'Usuario',
                'email': 'usuario@ejemplo.com',
                'organizacion': 'Organización de Prueba'
            }
        else:
            # Obtener información de la organización
            organizacion = db.query(Organizacion).filter(
                Organizacion.id == usuario_actual.organizacion_id
            ).first()
            
            usuario_data = {
                'nombre': f"{usuario_actual.nombres} {usuario_actual.apellidos}",
                'email': usuario_actual.email,
                'organizacion': organizacion.nombre if organizacion else 'Organización no encontrada',
                'sector': organizacion.sector.value if organizacion and organizacion.sector else None,
                'tamaño': organizacion.tamaño.value if organizacion and organizacion.tamaño else None
            }
        
        # Calcular puntuación promedio desde los datos proporcionados
        # Si viene puntuacion_promedio en los datos, usarlo; si no, calcularlo
        puntuacion_promedio = datos_resultado.get('puntuacion_promedio')
        puntos_obtenidos = datos_resultado.get('puntos_obtenidos')
        puntos_maximos = datos_resultado.get('puntos_maximos')
        
        total_preguntas = datos_resultado.get('total_preguntas', 0)
        preguntas_completadas = datos_resultado.get('preguntas_completadas', total_preguntas)
        
        # FORZAR CÁLCULO DE DATOS REALES - Sin valores por defecto inventados
        # Si no viene el promedio, calcularlo desde los datos disponibles
        if puntuacion_promedio is None:
            if puntos_obtenidos is not None and preguntas_completadas > 0:
                # Calcular desde puntos obtenidos: promedio = puntos_obtenidos / preguntas_completadas
                puntuacion_promedio = puntos_obtenidos / preguntas_completadas
            else:
                # Calcular desde porcentaje si está disponible
                puntuacion_global = datos_resultado.get('puntuacion_global', 0)
                if puntuacion_global > 0:
                    puntuacion_promedio = (puntuacion_global / 100) * 5
                else:
                    puntuacion_promedio = 0.0
        
        # Calcular puntos si no están disponibles (SIN valores por defecto inventados)
        if puntos_obtenidos is None:
            if puntuacion_promedio is not None and preguntas_completadas > 0:
                puntos_obtenidos = puntuacion_promedio * preguntas_completadas
            else:
                puntos_obtenidos = 0.0
        
        if puntos_maximos is None:
            puntos_maximos = preguntas_completadas * 5 if preguntas_completadas > 0 else 0.0
        
        # Asegurar que los valores sean float (no None)
        puntuacion_promedio = float(puntuacion_promedio) if puntuacion_promedio is not None else 0.0
        puntos_obtenidos = float(puntos_obtenidos) if puntos_obtenidos is not None else 0.0
        puntos_maximos = float(puntos_maximos) if puntos_maximos is not None else 0.0
        
        # Preparar datos para el PDF
        datos_pdf = {
            'nombre': datos_resultado.get('nombre', 'Diagnóstico de Ciberseguridad'),
            'puntuacion_global': datos_resultado.get('puntuacion_global', 0),
            'puntuaciones_dominio': datos_resultado.get('puntuaciones_dominio', {}),
            'tiempo_real_minutos': datos_resultado.get('tiempo_real_minutos', 0),
            'total_preguntas': total_preguntas,
            'preguntas_completadas': preguntas_completadas,
            'cuestionario_nombre': datos_resultado.get('cuestionario_nombre', 'Diagnóstico de Ciberseguridad'),
            'nivel': datos_resultado.get('nivel', 'básico'),
            'descripcion': datos_resultado.get('descripcion', 'Evaluación de madurez en ciberseguridad'),
            'fecha_inicio': datos_resultado.get('fecha_inicio', datetime.now().isoformat()),
            'fecha_completada': datos_resultado.get('fecha_completada', datetime.now().isoformat()),
            'puntuacion_promedio': puntuacion_promedio,  # Promedio calculado desde respuestas
            'puntos_obtenidos': puntos_obtenidos,  # Puntos totales obtenidos
            'puntos_maximos': puntos_maximos,  # Puntos máximos posibles
            'client_info': datos_resultado.get('client_info', {
                'industria': usuario_data.get('sector', 'No especificado'),
                'tamaño': usuario_data.get('tamaño', 'No especificado'),
                'amenazas_comunes': None  # Se calculará automáticamente
            }),
            'sector': usuario_data.get('sector'),
            'tamaño': usuario_data.get('tamaño'),
            'hallazgos': datos_resultado.get('hallazgos', None)  # Opcional: se generará automáticamente si no se proporciona
        }
        
        # Generar PDF profesional
        pdf_service = PDFProfesionalService()
        pdf_content = pdf_service.generar_informe_profesional(datos_pdf, usuario_data)
        
        # Crear respuesta con el PDF
        pdf_buffer = io.BytesIO(pdf_content)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=informe_ciberseguridad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
        
    except Exception as e:
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error al generar PDF profesional: {error_detail}")
        print(f"Traceback completo:\n{traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar PDF profesional: {error_detail}"
        )

@router.get("/diagnostico/profesional/{evaluacion_id}")
async def descargar_pdf_profesional(
    evaluacion_id: str,
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion)
):
    """Descargar PDF profesional de una evaluación específica"""
    try:
        # Buscar la evaluación con respuestas cargadas
        from sqlalchemy.orm import joinedload
        evaluacion = db.query(Evaluacion).options(
            joinedload(Evaluacion.respuestas)
        ).filter(
            Evaluacion.id == evaluacion_id
        ).first()
        
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada"
            )
        
        # Obtener información del usuario
        if not usuario_actual:
            usuario_data = {
                'nombre': 'Usuario',
                'email': 'usuario@ejemplo.com',
                'organizacion': 'Organización de Prueba'
            }
        else:
            # Obtener información de la organización
            organizacion = db.query(Organizacion).filter(
                Organizacion.id == usuario_actual.organizacion_id
            ).first()
            
            usuario_data = {
                'nombre': f"{usuario_actual.nombres} {usuario_actual.apellidos}",
                'email': usuario_actual.email,
                'organizacion': organizacion.nombre if organizacion else 'Organización no encontrada',
                'sector': organizacion.sector.value if organizacion and organizacion.sector else None,
                'tamaño': organizacion.tamaño.value if organizacion and organizacion.tamaño else None
            }
        
        # Obtener organización de la evaluación si está disponible
        organizacion_eval = evaluacion.organizacion if evaluacion.organizacion else None
        
        # Calcular puntuación promedio desde las respuestas reales
        puntuacion_promedio = 0.0
        if evaluacion.respuestas:
            valores_respuestas = [r.valor for r in evaluacion.respuestas]
            if valores_respuestas:
                puntuacion_promedio = sum(valores_respuestas) / len(valores_respuestas)
        
        # Calcular puntos obtenidos y máximos desde respuestas reales
        puntos_obtenidos = 0.0
        puntos_maximos = 0.0
        if evaluacion.respuestas:
            valores_respuestas = [r.valor for r in evaluacion.respuestas]
            puntos_obtenidos = sum(valores_respuestas)
            puntos_maximos = len(valores_respuestas) * 5
        
        # Preparar datos para el PDF
        datos_pdf = {
            'nombre': evaluacion.nombre,
            'puntuacion_global': float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else 0,
            'puntuaciones_dominio': evaluacion.puntuaciones_dominio or {},
            'tiempo_real_minutos': evaluacion.tiempo_real_minutos or 0,
            'total_preguntas': evaluacion.total_preguntas,
            'preguntas_completadas': evaluacion.preguntas_completadas,
            'cuestionario_nombre': evaluacion.nombre,
            'nivel': evaluacion.nivel_usado.value if evaluacion.nivel_usado else 'básico',
            'descripcion': 'Evaluación de madurez en ciberseguridad',
            'fecha_inicio': evaluacion.fecha_inicio.isoformat() if evaluacion.fecha_inicio else datetime.now().isoformat(),
            'fecha_completada': evaluacion.fecha_completada.isoformat() if evaluacion.fecha_completada else datetime.now().isoformat(),
            'puntuacion_promedio': puntuacion_promedio,  # Promedio calculado desde respuestas
            'puntos_obtenidos': puntos_obtenidos,  # Puntos totales obtenidos
            'puntos_maximos': puntos_maximos,  # Puntos máximos posibles
            'client_info': {
                'industria': organizacion_eval.sector.value if organizacion_eval and organizacion_eval.sector else usuario_data.get('sector', 'No especificado'),
                'tamaño': organizacion_eval.tamaño.value if organizacion_eval and organizacion_eval.tamaño else usuario_data.get('tamaño', 'No especificado'),
                'amenazas_comunes': None  # Se calculará automáticamente
            },
            'sector': organizacion_eval.sector.value if organizacion_eval and organizacion_eval.sector else usuario_data.get('sector'),
            'tamaño': organizacion_eval.tamaño.value if organizacion_eval and organizacion_eval.tamaño else usuario_data.get('tamaño'),
            'hallazgos': None  # Se generará automáticamente desde puntuaciones
        }
        
        # Generar PDF profesional
        pdf_service = PDFProfesionalService()
        pdf_content = pdf_service.generar_informe_profesional(datos_pdf, usuario_data)
        
        # Crear respuesta con el PDF
        pdf_buffer = io.BytesIO(pdf_content)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=informe_ciberseguridad_{evaluacion_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar PDF profesional: {str(e)}"
        )

