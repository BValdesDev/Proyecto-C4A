# app/api/v1/endpoints/evaluaciones.py
"""
Endpoints de gestión de evaluaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.evaluacion import Evaluacion, EstadoEvaluacion
from app.modelos.pregunta import Pregunta
from app.modelos.framework import Framework
from app.modelos.respuesta import Respuesta
from app.modelos.organizacion import Organizacion
from app.modelos.usuario import Usuario
from app.modelos.log_auditoria import LogAuditoria
from app.core.config import NivelSuscripcion
from app.core.excepciones import ExcepcionValidacion, ExcepcionRecursoNoEncontrado, ExcepcionNivelSuscripcion
from ..dependencias import (
    obtener_usuario_actual_dependencia,
    obtener_organizacion_usuario,
    verificar_limite_evaluaciones,
    obtener_info_request
)

router = APIRouter()


# Modelos Pydantic
class EvaluacionCreateRequest(BaseModel):
    nombre: str
    framework_id: str


class RespuestaRequest(BaseModel):
    pregunta_id: str
    valor: int
    texto_evidencia: Optional[str] = None
    comentarios: Optional[str] = None
    nivel_confianza: Optional[int] = None


class RespuestasRequest(BaseModel):
    respuestas: List[RespuestaRequest]


class EvaluacionResponse(BaseModel):
    id: str
    nombre: str
    framework: dict
    nivel_usado: str
    estado: str
    total_preguntas: int
    preguntas_completadas: int
    porcentaje_completado: float
    puntuacion_global: Optional[float]
    fecha_inicio: Optional[datetime]
    fecha_completada: Optional[datetime]
    fecha_creacion: datetime


class PreguntaResponse(BaseModel):
    id: str
    codigo: str
    texto_pregunta: str
    texto_ayuda: Optional[str]
    categoria: Optional[str]
    peso: int
    tipo_respuesta: str
    orden: int


class EvaluacionListResponse(BaseModel):
    evaluaciones: List[EvaluacionResponse]
    total: int
    pagina: int
    por_pagina: int


# Endpoints
@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para verificar CORS"""
    return {"mensaje": "CORS funcionando correctamente", "timestamp": datetime.now().isoformat()}

@router.get("/frameworks")
async def obtener_frameworks_disponibles(
    db: Session = Depends(obtener_sesion)
):
    """Obtener frameworks disponibles para crear evaluaciones"""
    
    try:
        frameworks = db.query(Framework).filter(
            Framework.esta_activo == True
        ).all()
        
        frameworks_response = []
        for framework in frameworks:
            frameworks_response.append({
                "id": str(framework.id),
                "nombre": framework.nombre,
                "nombre_mostrar": framework.nombre_mostrar,
                "version": framework.version,
                "descripcion": framework.descripcion,
                "niveles_disponibles": framework.niveles_disponibles
            })
        
        return {
            "frameworks": frameworks_response,
            "total": len(frameworks_response)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/")
async def crear_evaluacion(
    eval_data: dict,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Crear nueva evaluación"""
    
    try:
        # Obtener datos del request
        nombre = eval_data.get("nombre", "Evaluación sin nombre")
        framework_id = eval_data.get("framework_id")
        nivel_usado = eval_data.get("nivel_usado", "basico")
        
        if not framework_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="framework_id es requerido"
            )
        
        # Verificar que el framework existe
        framework = db.query(Framework).filter(
            Framework.id == framework_id,
            Framework.esta_activo == True
        ).first()
        
        if not framework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Framework no encontrado"
            )
        
        # Mapear nivel_usado a enum correcto
        from app.core.config import NivelSuscripcion
        nivel_enum = NivelSuscripcion.GRATUITO  # Por defecto
        
        if nivel_usado == "basico":
            nivel_enum = NivelSuscripcion.GRATUITO
        elif nivel_usado == "intermedio":
            nivel_enum = NivelSuscripcion.PROFESIONAL
        elif nivel_usado == "avanzado":
            nivel_enum = NivelSuscripcion.EMPRESARIAL
        
        # Crear evaluación real en la base de datos
        evaluacion = Evaluacion(
            nombre=nombre,
            framework_id=framework_id,
            nivel_usado=nivel_enum,
            estado=EstadoEvaluacion.EN_PROGRESO,
            total_preguntas=0,  # Se calculará después
            preguntas_completadas=0,
            organizacion_id=usuario.organizacion_id,
            creado_por=usuario.id
        )
        
        db.add(evaluacion)
        db.commit()
        db.refresh(evaluacion)
        
        # Calcular total de preguntas para este framework y nivel
        # Mapear nivel_usado a la clave en disponibilidad_por_nivel
        nivel_key = "gratuito"  # Por defecto
        if nivel_usado == "basico":
            nivel_key = "gratuito"
        elif nivel_usado == "intermedio":
            nivel_key = "pro"
        elif nivel_usado == "avanzado":
            nivel_key = "empresarial"
        
        total_preguntas = db.query(Pregunta).filter(
            Pregunta.framework_id == framework_id,
            Pregunta.disponibilidad_por_nivel[nivel_key].astext == "true",
            Pregunta.esta_activa == True
        ).count()
        
        # Actualizar el total de preguntas
        evaluacion.total_preguntas = total_preguntas
        db.commit()
        
        return {
            "id": str(evaluacion.id),
            "nombre": evaluacion.nombre,
            "framework": {
                "id": str(framework.id),
                "nombre": framework.nombre,
                "nombre_mostrar": framework.nombre_mostrar,
                "version": framework.version
            },
            "nivel_usado": nivel_usado,
            "estado": evaluacion.estado.value,
            "total_preguntas": evaluacion.total_preguntas,
            "preguntas_completadas": evaluacion.preguntas_completadas,
            "porcentaje_completado": evaluacion.porcentaje_completado,
            "puntuacion_global": float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else None,
            "fecha_inicio": evaluacion.fecha_inicio.isoformat() if evaluacion.fecha_inicio else None,
            "fecha_completada": evaluacion.fecha_completada.isoformat() if evaluacion.fecha_completada else None,
            "fecha_creacion": evaluacion.fecha_creacion.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en crear_evaluacion: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/")
async def listar_evaluaciones(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    estado: Optional[EstadoEvaluacion] = None,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Listar evaluaciones de la organización"""
    
    try:
        # Filtrar evaluaciones por organización del usuario
        query = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        )
        
        # Filtrar por estado si se especifica
        if estado:
            query = query.filter(Evaluacion.estado == estado)
        
        # Obtener total para paginación
        total = query.count()
        
        # Aplicar paginación
        offset = (pagina - 1) * por_pagina
        evaluaciones = query.offset(offset).limit(por_pagina).all()
        
        # Formatear respuesta
        evaluaciones_response = []
        for eval in evaluaciones:
            evaluaciones_response.append({
                "id": str(eval.id),
                "nombre": eval.nombre,
                "framework": {
                    "id": str(eval.framework.id),
                    "nombre": eval.framework.nombre,
                    "nombre_mostrar": eval.framework.nombre_mostrar,
                    "version": eval.framework.version
                },
                "nivel_usado": eval.nivel_usado.value,
                "estado": eval.estado.value,
                "total_preguntas": eval.total_preguntas,
                "preguntas_completadas": eval.preguntas_completadas,
                "porcentaje_completado": eval.porcentaje_completado,
                "puntuacion_global": eval.puntuacion_global,
                "fecha_inicio": eval.fecha_inicio.isoformat() if eval.fecha_inicio else None,
                "fecha_completada": eval.fecha_completada.isoformat() if eval.fecha_completada else None,
                "fecha_creacion": eval.fecha_creacion.isoformat()
            })
        
        total_paginas = (total + por_pagina - 1) // por_pagina
        
        return {
            "evaluaciones": evaluaciones_response,
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": total_paginas
        }
        
    except Exception as e:
        print(f"Error en listar_evaluaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{evaluacion_id}")
async def obtener_evaluacion(
    evaluacion_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Obtener evaluación específica"""
    
    try:
        # Buscar evaluación de la organización del usuario
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada"
            )
        
        return {
            "id": str(evaluacion.id),
            "nombre": evaluacion.nombre,
            "framework": {
                "id": str(evaluacion.framework.id),
                "nombre": evaluacion.framework.nombre,
                "nombre_mostrar": evaluacion.framework.nombre_mostrar,
                "version": evaluacion.framework.version
            },
            "nivel_usado": evaluacion.nivel_usado.value,
            "estado": evaluacion.estado.value,
            "total_preguntas": evaluacion.total_preguntas,
            "preguntas_completadas": evaluacion.preguntas_completadas,
            "porcentaje_completado": evaluacion.porcentaje_completado,
            "puntuacion_global": evaluacion.puntuacion_global,
            "fecha_inicio": evaluacion.fecha_inicio.isoformat() if evaluacion.fecha_inicio else None,
            "fecha_completada": evaluacion.fecha_completada.isoformat() if evaluacion.fecha_completada else None,
            "fecha_creacion": evaluacion.fecha_creacion.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en obtener_evaluacion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{evaluacion_id}/preguntas")
async def obtener_preguntas_evaluacion(
    evaluacion_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Obtener preguntas de la evaluación"""
    
    try:
        # Verificar que la evaluación existe y pertenece a la organización
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada"
            )
        
        # Obtener preguntas del framework según el nivel de suscripción
        # Para nivel empresarial: incluir todas las preguntas (gratuito + pro + empresarial)
        # Para nivel pro: incluir preguntas gratuito + pro
        # Para nivel gratuito: solo preguntas gratuito
        
        if evaluacion.nivel_usado.value == "EMPRESARIAL":
            # Nivel empresarial: incluir TODAS las preguntas
            preguntas = db.query(Pregunta).filter(
                Pregunta.framework_id == evaluacion.framework_id,
                Pregunta.esta_activa == True
            ).order_by(Pregunta.orden).all()
        elif evaluacion.nivel_usado.value == "PROFESIONAL":
            # Nivel pro: incluir preguntas gratuito + pro
            from sqlalchemy import or_
            preguntas = db.query(Pregunta).filter(
                Pregunta.framework_id == evaluacion.framework_id,
                or_(
                    Pregunta.disponibilidad_por_nivel["gratuito"].astext == "true",
                    Pregunta.disponibilidad_por_nivel["pro"].astext == "true"
                ),
                Pregunta.esta_activa == True
            ).order_by(Pregunta.orden).all()
        else:
            # Nivel gratuito: solo preguntas gratuito
            preguntas = db.query(Pregunta).filter(
                Pregunta.framework_id == evaluacion.framework_id,
                Pregunta.disponibilidad_por_nivel["gratuito"].astext == "true",
                Pregunta.esta_activa == True
            ).order_by(Pregunta.orden).all()
        
        # Formatear respuesta
        preguntas_response = []
        for pregunta in preguntas:
            preguntas_response.append({
                "id": str(pregunta.id),
                "codigo": pregunta.codigo,
                "texto_pregunta": pregunta.texto_pregunta,
                "texto_ayuda": pregunta.texto_ayuda,
                "categoria": pregunta.categoria,
                "nivel": evaluacion.nivel_usado.value.lower(),
                "tipo": pregunta.tipo_respuesta,
                "opciones": []  # Las opciones se generan dinámicamente según tipo_respuesta
            })
        
        return preguntas_response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en obtener_preguntas_evaluacion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/{evaluacion_id}/respuestas")
async def guardar_respuestas(
    evaluacion_id: str,
    request: Request,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Guardar respuestas de la evaluación"""
    
    try:
        # Obtener datos del request
        respuestas_data = await request.json()
        
        # Verificar que la evaluación existe y pertenece a la organización
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluacion no encontrada"
            )
        
        respuestas_recibidas = respuestas_data.get('respuestas', [])
        
        # Guardar cada respuesta
        respuestas_guardadas = 0
        for respuesta_data in respuestas_recibidas:
            # Verificar que la pregunta existe
            pregunta = db.query(Pregunta).filter(
                Pregunta.id == respuesta_data.get('pregunta_id'),
                Pregunta.framework_id == evaluacion.framework_id
            ).first()
            
            if pregunta:
                # Crear o actualizar respuesta
                respuesta_existente = db.query(Respuesta).filter(
                    Respuesta.evaluacion_id == evaluacion.id,
                    Respuesta.pregunta_id == pregunta.id,
                    Respuesta.respondido_por == usuario.id
                ).first()
                
                if respuesta_existente:
                    # Actualizar respuesta existente
                    respuesta_existente.valor = respuesta_data.get('valor')
                    respuesta_existente.texto_evidencia = respuesta_data.get('texto_evidencia', '')
                    respuesta_existente.comentarios = respuesta_data.get('comentarios', '')
                    respuesta_existente.nivel_confianza = respuesta_data.get('nivel_confianza', 3)
                else:
                    # Crear nueva respuesta
                    nueva_respuesta = Respuesta(
                        evaluacion_id=evaluacion.id,
                        pregunta_id=pregunta.id,
                        respondido_por=usuario.id,
                        valor=respuesta_data.get('valor'),
                        texto_evidencia=respuesta_data.get('texto_evidencia', ''),
                        comentarios=respuesta_data.get('comentarios', ''),
                        nivel_confianza=respuesta_data.get('nivel_confianza', 3)
                    )
                    db.add(nueva_respuesta)
                
                respuestas_guardadas += 1
        
        # Actualizar progreso de la evaluación según el nivel
        if evaluacion.nivel_usado.value == "EMPRESARIAL":
            # Nivel empresarial: contar TODAS las preguntas
            total_preguntas = db.query(Pregunta).filter(
                Pregunta.framework_id == evaluacion.framework_id,
                Pregunta.esta_activa == True
            ).count()
        elif evaluacion.nivel_usado.value == "PROFESIONAL":
            # Nivel pro: contar preguntas gratuito + pro
            from sqlalchemy import or_
            total_preguntas = db.query(Pregunta).filter(
                Pregunta.framework_id == evaluacion.framework_id,
                or_(
                    Pregunta.disponibilidad_por_nivel["gratuito"].astext == "true",
                    Pregunta.disponibilidad_por_nivel["pro"].astext == "true"
                ),
                Pregunta.esta_activa == True
            ).count()
        else:
            # Nivel gratuito: contar solo preguntas gratuito
            total_preguntas = db.query(Pregunta).filter(
                Pregunta.framework_id == evaluacion.framework_id,
                Pregunta.disponibilidad_por_nivel["gratuito"].astext == "true",
                Pregunta.esta_activa == True
            ).count()
        
        evaluacion.preguntas_completadas = respuestas_guardadas
        porcentaje_completado = (respuestas_guardadas / total_preguntas * 100) if total_preguntas > 0 else 0
        
        # Si se completaron todas las preguntas, marcar como completada
        if respuestas_guardadas >= total_preguntas:
            evaluacion.estado = EstadoEvaluacion.COMPLETADA
            evaluacion.fecha_completada = datetime.now()
        
        db.commit()
        
        return {
            "mensaje": "Respuestas guardadas exitosamente",
            "evaluacion_id": evaluacion_id,
            "respuestas_guardadas": respuestas_guardadas,
            "total_preguntas": total_preguntas,
            "porcentaje_completado": porcentaje_completado,
            "fecha_guardado": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en guardar_respuestas: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/{evaluacion_id}/finalizar")
async def finalizar_evaluacion(
    evaluacion_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Finalizar evaluación manualmente y generar resumen"""
    
    try:
        # Verificar que la evaluación existe y pertenece a la organización
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluacion no encontrada"
            )
        
        # Marcar como completada
        evaluacion.estado = EstadoEvaluacion.COMPLETADA
        evaluacion.fecha_completada = datetime.now()
        
        # Calcular puntuación global si no existe
        if not evaluacion.puntuacion_global:
            # Obtener respuestas para calcular puntuación
            respuestas = db.query(Respuesta).filter(
                Respuesta.evaluacion_id == evaluacion_id
            ).all()
            
            if respuestas:
                puntuacion_total = sum(r.valor for r in respuestas)
                puntuacion_maxima = len(respuestas) * 5
                evaluacion.puntuacion_global = (puntuacion_total / puntuacion_maxima) * 100 if puntuacion_maxima > 0 else 0
        
        db.commit()
        
        # Generar resumen rápido del reporte
        from app.servicios.reporte_service import ReporteCiberseguridadService
        reporte_service = ReporteCiberseguridadService(db)
        
        try:
            reporte = reporte_service.generar_reporte_evaluacion(evaluacion_id)
            resumen = {
                "puntuacion_general": reporte["metricas"]["porcentaje_logrado"],
                "nivel_madurez": reporte["metricas"]["nivel_madurez"],
                "recomendaciones_criticas": len([r for r in reporte["recomendaciones"] if r["prioridad"] >= 8]),
                "total_recomendaciones": len(reporte["recomendaciones"])
            }
        except Exception as e:
            print(f"Error generando resumen del reporte: {e}")
            resumen = {
                "puntuacion_general": evaluacion.puntuacion_global or 0,
                "nivel_madurez": "BÁSICO",
                "recomendaciones_criticas": 0,
                "total_recomendaciones": 0
            }
        
        return {
            "success": True,
            "mensaje": "Evaluacion finalizada exitosamente",
            "evaluacion_id": evaluacion_id,
            "estado": evaluacion.estado.value,
            "fecha_completada": evaluacion.fecha_completada.isoformat(),
            "puntuacion_global": evaluacion.puntuacion_global,
            "resumen": resumen,
            "redireccion": "/app/dashboard"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en finalizar_evaluacion: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{evaluacion_id}/progreso")
async def obtener_progreso_evaluacion(
    evaluacion_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener progreso detallado de la evaluación"""
    
    try:
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        progreso_detallado = evaluacion.obtener_progreso_detallado()
        estadisticas = evaluacion.obtener_estadisticas()
        
        return {
            "evaluacion_id": str(evaluacion.id),
            "nombre": evaluacion.nombre,
            "estadisticas": estadisticas,
            "progreso_por_categoria": progreso_detallado
        }
        
    except ExcepcionRecursoNoEncontrado:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete("/{evaluacion_id}")
async def eliminar_evaluacion(
    evaluacion_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Eliminar evaluación (eliminación lógica)"""
    
    try:
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        # Eliminación lógica
        evaluacion.fecha_eliminacion = datetime.utcnow()
        db.commit()
        
        # Log de eliminación
        LogAuditoria.crear_log(
            tipo_evento="evaluacion",
            accion="eliminar_evaluacion",
            exitoso=True,
            usuario_id=str(usuario.id),
            organizacion_id=str(organizacion.id),
            tipo_recurso="evaluacion",
            id_recurso=str(evaluacion.id)
        )
        
        return {"mensaje": "Evaluación eliminada exitosamente"}
        
    except ExcepcionRecursoNoEncontrado:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )