# app/api/v1/endpoints/evaluaciones.py
"""
Endpoints para gestionar evaluaciones completadas
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ....modelos import Evaluacion, Cuestionario, Usuario
from ....modelos.base import obtener_sesion
from ..dependencias import obtener_usuario_actual, obtener_usuario_opcional

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba"""
    return {"mensaje": "Endpoint funcionando correctamente"}

@router.get("/")
async def listar_evaluaciones(
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, ge=1, le=100)
):
    """Listar todas las evaluaciones del usuario"""
    try:
        # Si no hay usuario autenticado, devolver lista vacía
        if not usuario_actual:
            return {
                "evaluaciones": [],
                "total": 0,
                "pagina": pagina,
                "por_pagina": por_pagina,
                "total_paginas": 0
            }
        
        # Calcular offset para paginación
        offset = (pagina - 1) * por_pagina
        
        # Obtener total de evaluaciones
        total = db.query(Evaluacion).filter(
            Evaluacion.creado_por == usuario_actual.id
        ).count()
        
        # Obtener evaluaciones con paginación
        evaluaciones = db.query(Evaluacion).filter(
            Evaluacion.creado_por == usuario_actual.id
        ).offset(offset).limit(por_pagina).all()
        
        return {
            "evaluaciones": [
                {
            "id": str(evaluacion.id),
            "nombre": evaluacion.nombre,
                    "estado": evaluacion.estado,
                    "fecha_creacion": evaluacion.fecha_creacion,
                    "fecha_completada": evaluacion.fecha_completada,
                    "puntuacion_global": float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else None
                }
                for evaluacion in evaluaciones
            ],
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "total_paginas": (total + por_pagina - 1) // por_pagina
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evaluaciones: {str(e)}"
        )

@router.get("/completadas")
async def obtener_evaluaciones_completadas(
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion)
):
    """Obtener todas las evaluaciones completadas del usuario"""
    try:
        # Si no hay usuario autenticado, devolver lista vacía
        if not usuario_actual:
            return []
        
        # Buscar evaluaciones completadas del usuario
        evaluaciones = db.query(Evaluacion).filter(
            Evaluacion.creado_por == usuario_actual.id,
            Evaluacion.estado == "completada"
        ).all()
        
        return [
            {
                "id": str(evaluacion.id),
                "nombre": evaluacion.nombre,
                "cuestionario_id": str(evaluacion.cuestionario_id) if evaluacion.cuestionario_id else None,
                "puntuacion_global": float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else 0,
                "fecha_completada": evaluacion.fecha_completada.isoformat() if evaluacion.fecha_completada else None,
                "estado": evaluacion.estado
            }
            for evaluacion in evaluaciones
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evaluaciones completadas: {str(e)}"
        )

@router.get("/{evaluacion_id}")
async def obtener_evaluacion_por_id(
    evaluacion_id: str,
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion)
):
    """Obtener una evaluación específica por ID"""
    try:
        # Verificar que el usuario esté autenticado
        if not usuario_actual:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        # Buscar la evaluación solo del usuario autenticado
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.creado_por == usuario_actual.id
        ).first()
        
        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada"
            )
        
        return {
            "id": str(evaluacion.id),
            "nombre": evaluacion.nombre,
            "estado": evaluacion.estado,
            "fecha_creacion": evaluacion.fecha_creacion,
            "fecha_completada": evaluacion.fecha_completada,
            "puntuacion_global": float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else None,
            "puntuaciones_dominio": evaluacion.puntuaciones_dominio or {},
            "total_preguntas": evaluacion.total_preguntas,
            "preguntas_completadas": evaluacion.preguntas_completadas,
            "porcentaje_completado": evaluacion.porcentaje_completado,
            "framework_id": str(evaluacion.framework_id) if evaluacion.framework_id else None,
            "cuestionario_id": str(evaluacion.cuestionario_id) if evaluacion.cuestionario_id else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evaluación: {str(e)}"
        )

@router.get("/completadas/{cuestionario_id}")
async def verificar_evaluacion_completada(
    cuestionario_id: str,
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion)
):
    """Verificar si el usuario ya completó un cuestionario específico"""
    try:
        # Si no hay usuario autenticado, devolver que no está completada
        if not usuario_actual:
            return {
                "completada": False,
                "evaluacion_id": None,
                "puntuacion": None,
                "fecha_completada": None
            }
        
        # Buscar evaluación completada para este cuestionario y usuario
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.cuestionario_id == cuestionario_id,
            Evaluacion.creado_por == usuario_actual.id,
            Evaluacion.estado == "completada"
        ).first()
        
        return {
            "completada": evaluacion is not None,
            "evaluacion_id": str(evaluacion.id) if evaluacion else None,
            "puntuacion": float(evaluacion.puntuacion_global) if evaluacion and evaluacion.puntuacion_global else None,
            "fecha_completada": evaluacion.fecha_completada if evaluacion else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar evaluación: {str(e)}"
        )

@router.post("/completadas/{cuestionario_id}/guardar")
async def guardar_evaluacion_completada(
    cuestionario_id: str,
    resultado: dict = Body(...),
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional),
    db: Session = Depends(obtener_sesion)
):
    """Guardar una evaluación completada"""
    try:
        # Si no hay usuario autenticado, devolver error
        if not usuario_actual:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        # Verificar que el cuestionario existe
        cuestionario = db.query(Cuestionario).filter(
            Cuestionario.id == cuestionario_id
        ).first()
        
        if not cuestionario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuestionario no encontrado"
            )
        
        # Verificar si ya existe una evaluación completada
        evaluacion_existente = db.query(Evaluacion).filter(
            Evaluacion.cuestionario_id == cuestionario_id,
            Evaluacion.creado_por == usuario_actual.id,
            Evaluacion.estado == "completada"
        ).first()
        
        if evaluacion_existente:
            # Actualizar la evaluación existente
            evaluacion_existente.puntuacion_global = resultado.get("puntuacion_global", 0)
            evaluacion_existente.puntuaciones_dominio = resultado.get("puntuaciones_dominio", {})
            evaluacion_existente.fecha_completada = resultado.get("fecha_completada")
            evaluacion_existente.tiempo_real_minutos = resultado.get("tiempo_real_minutos", 0)
            
            db.commit()
            return {"mensaje": "Evaluación actualizada exitosamente", "evaluacion_id": str(evaluacion_existente.id)}
        else:
            # Crear nueva evaluación
            from datetime import datetime
            import uuid
            
            nueva_evaluacion = Evaluacion(
                id=uuid.uuid4(),
                nombre=f"Evaluación completada - {cuestionario.nombre}",
                organizacion_id=usuario_actual.organizacion_id,
                framework_id=cuestionario.framework_id,
                cuestionario_id=cuestionario_id,
                creado_por=usuario_actual.id,
                nivel_usado="gratuito",  # TODO: Obtener del usuario real
                total_preguntas=cuestionario.total_items,
                preguntas_completadas=cuestionario.total_items,
                estado="completada",
                puntuacion_global=resultado.get("puntuacion_global", 0),
                puntuaciones_dominio=resultado.get("puntuaciones_dominio", {}),
                fecha_inicio=resultado.get("fecha_inicio", datetime.now()),
                fecha_completada=resultado.get("fecha_completada", datetime.now()),
                tiempo_estimado_minutos=cuestionario.tiempo_estimado_minutos,
                tiempo_real_minutos=resultado.get("tiempo_real_minutos", 0)
            )
            
            db.add(nueva_evaluacion)
            db.commit()
            db.refresh(nueva_evaluacion)
            
            return {"mensaje": "Evaluación guardada exitosamente", "evaluacion_id": str(nueva_evaluacion.id)}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar evaluación: {str(e)}"
        )