# app/api/v1/endpoints/evaluaciones.py
"""
Endpoints para gestionar evaluaciones completadas
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ....core.config import NivelSuscripcion
from ....modelos import Evaluacion, Cuestionario, Usuario
from ....modelos.organizacion import Organizacion
from ....modelos.base import obtener_sesion
from ..dependencias import obtener_usuario_actual_dependencia, obtener_usuario_opcional
from app.core.rate_limiting import get_rate_limiter

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
            Evaluacion.creado_por == usuario_actual.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).count()
        
        # Obtener evaluaciones con paginación
        evaluaciones = db.query(Evaluacion).filter(
            Evaluacion.creado_por == usuario_actual.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).offset(offset).limit(por_pagina).all()
        
        return {
            "evaluaciones": [
                {
                    "id": str(evaluacion.id),
                    "nombre": evaluacion.nombre,
                    "estado": evaluacion.estado.value if hasattr(evaluacion.estado, "value") else evaluacion.estado,
                    "fecha_creacion": evaluacion.fecha_creacion.isoformat() if evaluacion.fecha_creacion else None,
                    "fecha_completada": evaluacion.fecha_completada.isoformat() if evaluacion.fecha_completada else None,
                    "puntuacion_global": float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else None,
                    "total_preguntas": evaluacion.total_preguntas,
                    "preguntas_completadas": evaluacion.preguntas_completadas,
                    "porcentaje_completado": evaluacion.porcentaje_completado,
                    "nivel_usado": evaluacion.nivel_usado.value if evaluacion.nivel_usado else None,
                    "framework": {
                        "id": str(evaluacion.framework.id),
                        "nombre": evaluacion.framework.nombre,
                        "nombre_mostrar": evaluacion.framework.nombre_mostrar,
                        "version": evaluacion.framework.version
                    } if evaluacion.framework else None
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

@router.delete("/{evaluacion_id}")
async def eliminar_evaluacion(
    evaluacion_id: UUID,
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Eliminar una evaluación del Plan Pro mediante eliminación lógica"""
    try:
        # Verificar que la organización exista y tenga Plan Pro
        organizacion = db.query(Organizacion).filter(
            Organizacion.id == usuario_actual.organizacion_id,
            Organizacion.fecha_eliminacion.is_(None)
        ).first()

        if not organizacion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organización no encontrada o inactiva"
            )

        if organizacion.nivel_suscripcion != NivelSuscripcion.PRO:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La eliminación de evaluaciones está disponible solo para el Plan Pro"
            )

        # Buscar evaluación del usuario
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.creado_por == usuario_actual.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()

        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluación no encontrada"
            )

        evaluacion.fecha_eliminacion = datetime.utcnow()
        db.commit()

        return {
            "mensaje": "Evaluación eliminada correctamente",
            "evaluacion_id": str(evaluacion_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar evaluación: {str(e)}"
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
    """Guardar una evaluación completada y generar PDF automáticamente para Plan Empresarial"""
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
        
        # Obtener nivel de suscripción del usuario
        from ....modelos.organizacion import Organizacion
        organizacion = db.query(Organizacion).filter(
            Organizacion.id == usuario_actual.organizacion_id
        ).first()
        
        nivel_suscripcion = organizacion.nivel_suscripcion.value if organizacion else "gratuito"
        
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
            
            # Generar PDF automáticamente para Plan Empresarial
            evaluacion_id = str(evaluacion_existente.id)
            if nivel_suscripcion == "empresarial":
                try:
                    from ....servicios.pdf_profesional_service import PDFProfesionalService
                    from datetime import datetime
                    
                    pdf_service = PDFProfesionalService()
                    usuario_data = {
                        'nombre': f"{usuario_actual.nombres} {usuario_actual.apellidos}",
                        'email': usuario_actual.email,
                        'organizacion': organizacion.nombre if organizacion else 'Organización no encontrada'
                    }
                    
                    datos_pdf = {
                        'nombre': evaluacion_existente.nombre,
                        'puntuacion_global': float(evaluacion_existente.puntuacion_global) if evaluacion_existente.puntuacion_global else 0,
                        'puntuaciones_dominio': evaluacion_existente.puntuaciones_dominio or {},
                        'tiempo_real_minutos': evaluacion_existente.tiempo_real_minutos or 0,
                        'total_preguntas': evaluacion_existente.total_preguntas,
                        'preguntas_completadas': evaluacion_existente.preguntas_completadas,
                        'cuestionario_nombre': cuestionario.nombre,
                        'nivel': nivel_suscripcion,
                        'descripcion': 'Evaluación de madurez en ciberseguridad - Plan Empresarial',
                        'fecha_inicio': evaluacion_existente.fecha_inicio.isoformat() if evaluacion_existente.fecha_inicio else datetime.now().isoformat(),
                        'fecha_completada': evaluacion_existente.fecha_completada.isoformat() if evaluacion_existente.fecha_completada else datetime.now().isoformat()
                    }
                    
                    pdf_content = pdf_service.generar_informe_profesional(datos_pdf, usuario_data)
                    
                    # Guardar PDF en el sistema de reportes (opcional)
                    # Por ahora solo se genera, se puede descargar después desde el endpoint específico
                    
                except Exception as pdf_error:
                    # No fallar la operación si hay error en PDF, solo loguear
                    print(f"Error generando PDF automático: {pdf_error}")
            
            return {"mensaje": "Evaluación actualizada exitosamente", "evaluacion_id": evaluacion_id}
        else:
            rate_limiter = get_rate_limiter()
            limite_evaluaciones = rate_limiter.check_evaluation_limit(
                str(usuario_actual.organizacion_id),
                nivel_suscripcion
            )

            if not limite_evaluaciones["allowed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Límite mensual de evaluaciones alcanzado para tu suscripción",
                    headers={
                        "Retry-After": "2592000",
                        "X-RateLimit-Limit-Month": str(limite_evaluaciones["limit"]),
                        "X-RateLimit-Remaining-Month": str(
                            max(limite_evaluaciones["limit"] - limite_evaluaciones["current_evaluations"], 0)
                        ),
                        "X-RateLimit-Period": limite_evaluaciones["period"]
                    }
                )

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
                nivel_usado=nivel_suscripcion,
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
            
            evaluacion_id = str(nueva_evaluacion.id)
            
            # Generar PDF automáticamente para Plan Empresarial
            if nivel_suscripcion == "empresarial":
                try:
                    from ....servicios.pdf_profesional_service import PDFProfesionalService
                    
                    pdf_service = PDFProfesionalService()
                    usuario_data = {
                        'nombre': f"{usuario_actual.nombres} {usuario_actual.apellidos}",
                        'email': usuario_actual.email,
                        'organizacion': organizacion.nombre if organizacion else 'Organización no encontrada'
                    }
                    
                    datos_pdf = {
                        'nombre': nueva_evaluacion.nombre,
                        'puntuacion_global': float(nueva_evaluacion.puntuacion_global) if nueva_evaluacion.puntuacion_global else 0,
                        'puntuaciones_dominio': nueva_evaluacion.puntuaciones_dominio or {},
                        'tiempo_real_minutos': nueva_evaluacion.tiempo_real_minutos or 0,
                        'total_preguntas': nueva_evaluacion.total_preguntas,
                        'preguntas_completadas': nueva_evaluacion.preguntas_completadas,
                        'cuestionario_nombre': cuestionario.nombre,
                        'nivel': nivel_suscripcion,
                        'descripcion': 'Evaluación de madurez en ciberseguridad - Plan Empresarial',
                        'fecha_inicio': nueva_evaluacion.fecha_inicio.isoformat() if nueva_evaluacion.fecha_inicio else datetime.now().isoformat(),
                        'fecha_completada': nueva_evaluacion.fecha_completada.isoformat() if nueva_evaluacion.fecha_completada else datetime.now().isoformat()
                    }
                    
                    pdf_content = pdf_service.generar_informe_profesional(datos_pdf, usuario_data)
                    
                    # Guardar PDF en el sistema de reportes (opcional)
                    # Por ahora solo se genera, se puede descargar después desde el endpoint específico
                    
                except Exception as pdf_error:
                    # No fallar la operación si hay error en PDF, solo loguear
                    print(f"Error generando PDF automático: {pdf_error}")
            
            return {"mensaje": "Evaluación guardada exitosamente", "evaluacion_id": evaluacion_id}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar evaluación: {str(e)}"
        )