# app/api/v1/endpoints/dashboard.py
"""
Endpoints del Dashboard para C4A SaaS
Proporciona estadísticas y acciones rápidas para el usuario
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.evaluacion import Evaluacion, EstadoEvaluacion
from app.modelos.organizacion import Organizacion
from app.modelos.framework import Framework
from app.core.config import NivelSuscripcion
from app.core.excepciones import ExcepcionC4A, ExcepcionValidacion
from ..dependencias import obtener_usuario_actual_dependencia

router = APIRouter()


# Modelos Pydantic para respuestas
class DashboardSummary(BaseModel):
    """Resumen del dashboard"""
    total_evaluaciones: int
    promedio_puntuacion: float
    en_progreso: int
    uso_mensual: int
    nivel_suscripcion: str
    limite_mensual: int
    porcentaje_uso: float


class EvaluacionReciente(BaseModel):
    """Evaluación reciente"""
    id: str
    nombre: str
    fecha_creacion: datetime
    estado: str
    puntuacion: Optional[float]
    porcentaje_completado: float


class AccionRapida(BaseModel):
    """Acción rápida disponible"""
    id: str
    nombre: str
    descripcion: str
    disponible: bool
    icono: str
    ruta: str


class CrearEvaluacionRequest(BaseModel):
    """Request para crear nueva evaluación"""
    nombre: str
    framework_id: Optional[str] = None


class CrearEvaluacionResponse(BaseModel):
    """Response de creación de evaluación"""
    id: str
    nombre: str
    estado: str
    fecha_creacion: datetime
    mensaje: str


@router.get("/summary", response_model=DashboardSummary)
async def obtener_resumen_dashboard(
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Obtener resumen del dashboard
    
    Returns:
        - total_evaluaciones: Número total de evaluaciones
        - promedio_puntuacion: Puntuación promedio de evaluaciones completadas
        - en_progreso: Cantidad de evaluaciones activas
        - uso_mensual: Evaluaciones realizadas en el mes actual
        - nivel_suscripcion: Nivel de suscripción actual
        - limite_mensual: Límite de evaluaciones por mes
        - porcentaje_uso: Porcentaje de uso del límite mensual
    """
    try:
        # Obtener organización del usuario
        organizacion = usuario_actual.organizacion
        
        # Obtener todas las evaluaciones de la organización
        evaluaciones = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).all()
        
        # Calcular estadísticas básicas
        total_evaluaciones = len(evaluaciones)
        en_progreso = len([e for e in evaluaciones if e.estado in [
            EstadoEvaluacion.BORRADOR, EstadoEvaluacion.EN_PROGRESO
        ]])
        
        # Calcular uso mensual
        inicio_mes = datetime.utcnow().replace(tzinfo=None, day=1, hour=0, minute=0, second=0, microsecond=0)
        uso_mensual = len([e for e in evaluaciones if e.fecha_creacion.replace(tzinfo=None) >= inicio_mes])
        
        # Calcular promedio de puntuación
        evaluaciones_completadas = [e for e in evaluaciones if e.estado == EstadoEvaluacion.COMPLETADA and e.puntuacion_global]
        if evaluaciones_completadas:
            promedio_puntuacion = sum(float(e.puntuacion_global) for e in evaluaciones_completadas) / len(evaluaciones_completadas)
        else:
            promedio_puntuacion = 0.0
        
        # Calcular porcentaje de uso
        limite_mensual = organizacion.maximo_evaluaciones_por_mes
        porcentaje_uso = (uso_mensual / limite_mensual) * 100 if limite_mensual > 0 else 0
        
        return DashboardSummary(
            total_evaluaciones=total_evaluaciones,
            promedio_puntuacion=round(promedio_puntuacion, 2),
            en_progreso=en_progreso,
            uso_mensual=uso_mensual,
            nivel_suscripcion=organizacion.nivel_suscripcion.value,
            limite_mensual=limite_mensual,
            porcentaje_uso=round(porcentaje_uso, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen del dashboard: {str(e)}"
        )


@router.get("/evaluaciones-recientes", response_model=List[EvaluacionReciente])
async def obtener_evaluaciones_recientes(
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Obtener las últimas 5 evaluaciones del usuario
    
    Returns:
        Lista de evaluaciones recientes con:
        - id, nombre, fecha_creacion, estado, puntuacion, porcentaje_completado
    """
    try:
        # Obtener organización del usuario
        organizacion = usuario_actual.organizacion
        
        # Obtener las últimas 5 evaluaciones ordenadas por fecha de creación
        evaluaciones = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).order_by(Evaluacion.fecha_creacion.desc()).limit(5).all()
        
        evaluaciones_recientes = []
        for evaluacion in evaluaciones:
            evaluaciones_recientes.append(EvaluacionReciente(
                id=str(evaluacion.id),
                nombre=evaluacion.nombre,
                fecha_creacion=evaluacion.fecha_creacion,
                estado=evaluacion.estado.value,
                puntuacion=float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else None,
                porcentaje_completado=round(evaluacion.porcentaje_completado, 2)
            ))
        
        return evaluaciones_recientes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evaluaciones recientes: {str(e)}"
        )


@router.post("/evaluaciones", response_model=CrearEvaluacionResponse)
async def crear_nueva_evaluacion(
    request: CrearEvaluacionRequest,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Crear una nueva evaluación
    
    Verifica límites del plan y crea una evaluación inicial con estado "en progreso"
    
    Args:
        - nombre: Nombre de la evaluación
        - framework_id: ID del framework a usar (opcional, usa el por defecto)
    
    Returns:
        Información de la evaluación creada
    """
    try:
        # Verificar si el usuario puede crear evaluaciones
        if not usuario_actual.puede_crear_evaluacion():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para crear evaluaciones o has alcanzado el límite mensual"
            )
        
        # Verificar límites de la organización
        organizacion = usuario_actual.organizacion
        if not organizacion.puede_crear_evaluacion:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Has alcanzado el límite de {organizacion.maximo_evaluaciones_por_mes} evaluaciones por mes"
            )
        
        # Obtener framework (usar el por defecto si no se especifica)
        if request.framework_id:
            framework = db.query(Framework).filter(
                Framework.id == uuid.UUID(request.framework_id),
                Framework.esta_activo == True
            ).first()
            if not framework:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Framework no encontrado"
                )
        else:
            # Usar el framework por defecto (primer framework activo)
            framework = db.query(Framework).filter(
                Framework.esta_activo == True
            ).first()
            if not framework:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No hay frameworks disponibles"
                )
        
        # Crear nueva evaluación
        nueva_evaluacion = Evaluacion(
            nombre=request.nombre,
            organizacion_id=organizacion.id,
            framework_id=framework.id,
            creado_por=usuario_actual.id,
            nivel_usado=organizacion.nivel_suscripcion,
            total_preguntas=framework.contar_preguntas_activas_para_nivel(organizacion.nivel_suscripcion),
            estado=EstadoEvaluacion.EN_PROGRESO
        )
        
        # Iniciar la evaluación
        nueva_evaluacion.iniciar_evaluacion()
        
        db.add(nueva_evaluacion)
        db.commit()
        db.refresh(nueva_evaluacion)
        
        return CrearEvaluacionResponse(
            id=str(nueva_evaluacion.id),
            nombre=nueva_evaluacion.nombre,
            estado=nueva_evaluacion.estado.value,
            fecha_creacion=nueva_evaluacion.fecha_creacion,
            mensaje="Evaluación creada exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear evaluación: {str(e)}"
        )


@router.get("/acciones", response_model=List[AccionRapida])
async def obtener_acciones_rapidas(
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Obtener acciones rápidas disponibles
    
    Returns:
        Lista de acciones disponibles basadas en permisos del usuario:
        - crearNuevaEvaluacion
        - verReportes
        - gestionarUsuarios
        - actualizarPlan
    """
    try:
        organizacion = usuario_actual.organizacion
        acciones = []
        
        # Acción: Crear Nueva Evaluación
        puede_crear_evaluacion = (
            usuario_actual.puede_crear_evaluacion() and 
            organizacion.puede_crear_evaluacion
        )
        acciones.append(AccionRapida(
            id="crear_nueva_evaluacion",
            nombre="Crear Nueva Evaluación",
            descripcion="Iniciar una nueva evaluación de ciberseguridad",
            disponible=puede_crear_evaluacion,
            icono="plus-circle",
            ruta="/evaluaciones/nueva"
        ))
        
        # Acción: Ver Reportes
        puede_ver_reportes = usuario_actual.puede_acceder_recurso("reportes", "leer")
        acciones.append(AccionRapida(
            id="ver_reportes",
            nombre="Ver Reportes",
            descripcion="Acceder a reportes y análisis de evaluaciones",
            disponible=puede_ver_reportes,
            icono="bar-chart",
            ruta="/reportes"
        ))
        
        # Acción: Gestionar Usuarios (solo para administradores)
        puede_gestionar_usuarios = (
            usuario_actual.puede_acceder_recurso("usuarios", "gestionar") and
            organizacion.nivel_suscripcion in [NivelSuscripcion.PRO, NivelSuscripcion.EMPRESARIAL]
        )
        acciones.append(AccionRapida(
            id="gestionar_usuarios",
            nombre="Gestionar Usuarios",
            descripcion="Administrar usuarios de la organización",
            disponible=puede_gestionar_usuarios,
            icono="users",
            ruta="/usuarios"
        ))
        
        # Acción: Actualizar Plan
        puede_actualizar_plan = (
            usuario_actual.puede_acceder_recurso("suscripciones", "gestionar") and
            organizacion.nivel_suscripcion != NivelSuscripcion.EMPRESARIAL
        )
        acciones.append(AccionRapida(
            id="actualizar_plan",
            nombre="Actualizar Plan",
            descripcion="Mejorar tu plan de suscripción",
            disponible=puede_actualizar_plan,
            icono="credit-card",
            ruta="/suscripciones"
        ))
        
        # Acción: Ver Dashboard (siempre disponible)
        acciones.append(AccionRapida(
            id="ver_dashboard",
            nombre="Ver Dashboard",
            descripcion="Acceder al panel principal",
            disponible=True,
            icono="home",
            ruta="/dashboard"
        ))
        
        return acciones
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener acciones rápidas: {str(e)}"
        )


@router.get("/estadisticas-uso")
async def obtener_estadisticas_uso(
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Obtener estadísticas detalladas de uso
    
    Returns:
        Estadísticas de uso de la organización
    """
    try:
        organizacion = usuario_actual.organizacion
        
        # Obtener estadísticas de uso de la organización
        uso_mensual = organizacion.obtener_uso_mensual()
        
        # Obtener estadísticas del usuario
        estadisticas_usuario = usuario_actual.obtener_estadisticas_uso()
        
        return {
            "organizacion": {
                "nombre": organizacion.nombre,
                "nivel_suscripcion": organizacion.nivel_suscripcion.value,
                "uso_mensual": uso_mensual
            },
            "usuario": estadisticas_usuario,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas de uso: {str(e)}"
        )
