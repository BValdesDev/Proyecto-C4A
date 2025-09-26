# app/api/v1/endpoints/organizaciones.py
"""
Endpoints de gestión de organizaciones
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.organizacion import Organizacion, TamañoEmpresa, Sector
from app.modelos.usuario import Usuario
from app.modelos.log_auditoria import LogAuditoria
from app.core.config import NivelSuscripcion
from app.core.excepciones import ExcepcionValidacion, ExcepcionRecursoNoEncontrado
from ..dependencias import (
    obtener_usuario_actual_dependencia,
    obtener_organizacion_usuario,
    verificar_permiso
)

router = APIRouter()


# Modelos Pydantic
class OrganizacionCreateRequest(BaseModel):
    nombre: str
    rut: Optional[str] = None
    sector: Sector
    tamaño: TamañoEmpresa
    region: Optional[str] = None
    comuna: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None
    telefono: Optional[str] = None


class OrganizacionUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    rut: Optional[str] = None
    sector: Optional[Sector] = None
    tamaño: Optional[TamañoEmpresa] = None
    region: Optional[str] = None
    comuna: Optional[str] = None
    descripcion: Optional[str] = None
    sitio_web: Optional[str] = None
    telefono: Optional[str] = None
    email_facturacion: Optional[str] = None


class OrganizacionResponse(BaseModel):
    id: str
    nombre: str
    rut: Optional[str]
    sector: str
    tamaño: str
    region: Optional[str]
    comuna: Optional[str]
    nivel_suscripcion: str
    fecha_inicio_suscripcion: Optional[datetime]
    fecha_vencimiento_suscripcion: Optional[datetime]
    maximo_usuarios: int
    maximo_evaluaciones_por_mes: int
    maximo_dias_retencion_datos: int
    descripcion: Optional[str]
    sitio_web: Optional[str]
    telefono: Optional[str]
    email_facturacion: Optional[str]
    fecha_creacion: datetime


class UsoOrganizacionResponse(BaseModel):
    evaluaciones_usadas: int
    evaluaciones_limite: int
    usuarios_activos: int
    usuarios_limite: int
    porcentaje_uso_evaluaciones: float
    porcentaje_uso_usuarios: float


# Endpoints
@router.post("/", response_model=OrganizacionResponse)
async def crear_organizacion(
    org_data: OrganizacionCreateRequest,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Crear nueva organización"""
    
    try:
        # Verificar que el usuario no tenga ya una organización
        if usuario.organizacion_id:
            raise ExcepcionValidacion("El usuario ya pertenece a una organización")
        
        # Verificar RUT único si se proporciona
        if org_data.rut:
            org_existente = db.query(Organizacion).filter(
                Organizacion.rut == org_data.rut,
                Organizacion.fecha_eliminacion.is_(None)
            ).first()
            
            if org_existente:
                raise ExcepcionValidacion("El RUT ya está registrado")
        
        # Crear organización
        nueva_organizacion = Organizacion(
            nombre=org_data.nombre,
            rut=org_data.rut,
            sector=org_data.sector,
            tamaño=org_data.tamaño,
            region=org_data.region,
            comuna=org_data.comuna,
            descripcion=org_data.descripcion,
            sitio_web=org_data.sitio_web,
            telefono=org_data.telefono,
            nivel_suscripcion=NivelSuscripcion.GRATUITO,
            consentimiento_otorgado=True,
            fecha_consentimiento=datetime.utcnow(),
            politica_privacidad_aceptada=True,
            fecha_aceptacion_politica=datetime.utcnow()
        )
        
        # Configurar límites según nivel
        nueva_organizacion.actualizar_limites_nivel()
        
        db.add(nueva_organizacion)
        db.commit()
        db.refresh(nueva_organizacion)
        
        # Asignar usuario a la organización
        usuario.organizacion_id = nueva_organizacion.id
        db.commit()
        
        # Log de creación
        LogAuditoria.crear_log(
            tipo_evento="organizacion",
            accion="crear_organizacion",
            exitoso=True,
            usuario_id=str(usuario.id),
            organizacion_id=str(nueva_organizacion.id),
            tipo_recurso="organizacion",
            id_recurso=str(nueva_organizacion.id)
        )
        
        return OrganizacionResponse(
            id=str(nueva_organizacion.id),
            nombre=nueva_organizacion.nombre,
            rut=nueva_organizacion.rut,
            sector=nueva_organizacion.sector.value,
            tamaño=nueva_organizacion.tamaño.value,
            region=nueva_organizacion.region,
            comuna=nueva_organizacion.comuna,
            nivel_suscripcion=nueva_organizacion.nivel_suscripcion.value,
            fecha_inicio_suscripcion=nueva_organizacion.fecha_inicio_suscripcion,
            fecha_vencimiento_suscripcion=nueva_organizacion.fecha_vencimiento_suscripcion,
            maximo_usuarios=nueva_organizacion.maximo_usuarios,
            maximo_evaluaciones_por_mes=nueva_organizacion.maximo_evaluaciones_por_mes,
            maximo_dias_retencion_datos=nueva_organizacion.maximo_dias_retencion_datos,
            descripcion=nueva_organizacion.descripcion,
            sitio_web=nueva_organizacion.sitio_web,
            telefono=nueva_organizacion.telefono,
            email_facturacion=nueva_organizacion.email_facturacion,
            fecha_creacion=nueva_organizacion.fecha_creacion
        )
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{org_id}", response_model=OrganizacionResponse)
async def obtener_organizacion(
    org_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener información de la organización"""
    
    try:
        return OrganizacionResponse(
            id=str(organizacion.id),
            nombre=organizacion.nombre,
            rut=organizacion.rut,
            sector=organizacion.sector.value,
            tamaño=organizacion.tamaño.value,
            region=organizacion.region,
            comuna=organizacion.comuna,
            nivel_suscripcion=organizacion.nivel_suscripcion.value,
            fecha_inicio_suscripcion=organizacion.fecha_inicio_suscripcion,
            fecha_vencimiento_suscripcion=organizacion.fecha_vencimiento_suscripcion,
            maximo_usuarios=organizacion.maximo_usuarios,
            maximo_evaluaciones_por_mes=organizacion.maximo_evaluaciones_por_mes,
            maximo_dias_retencion_datos=organizacion.maximo_dias_retencion_datos,
            descripcion=organizacion.descripcion,
            sitio_web=organizacion.sitio_web,
            telefono=organizacion.telefono,
            email_facturacion=organizacion.email_facturacion,
            fecha_creacion=organizacion.fecha_creacion
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put("/{org_id}", response_model=OrganizacionResponse)
async def actualizar_organizacion(
    org_id: str,
    org_data: OrganizacionUpdateRequest,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Actualizar información de la organización"""
    
    try:
        # Verificar RUT único si se proporciona
        if org_data.rut and org_data.rut != organizacion.rut:
            org_existente = db.query(Organizacion).filter(
                Organizacion.rut == org_data.rut,
                Organizacion.fecha_eliminacion.is_(None),
                Organizacion.id != organizacion.id
            ).first()
            
            if org_existente:
                raise ExcepcionValidacion("El RUT ya está registrado")
        
        # Actualizar campos
        if org_data.nombre is not None:
            organizacion.nombre = org_data.nombre
        if org_data.rut is not None:
            organizacion.rut = org_data.rut
        if org_data.sector is not None:
            organizacion.sector = org_data.sector
        if org_data.tamaño is not None:
            organizacion.tamaño = org_data.tamaño
        if org_data.region is not None:
            organizacion.region = org_data.region
        if org_data.comuna is not None:
            organizacion.comuna = org_data.comuna
        if org_data.descripcion is not None:
            organizacion.descripcion = org_data.descripcion
        if org_data.sitio_web is not None:
            organizacion.sitio_web = org_data.sitio_web
        if org_data.telefono is not None:
            organizacion.telefono = org_data.telefono
        if org_data.email_facturacion is not None:
            organizacion.email_facturacion = org_data.email_facturacion
        
        db.commit()
        db.refresh(organizacion)
        
        # Log de actualización
        LogAuditoria.crear_log(
            tipo_evento="organizacion",
            accion="actualizar_organizacion",
            exitoso=True,
            organizacion_id=str(organizacion.id),
            tipo_recurso="organizacion",
            id_recurso=str(organizacion.id)
        )
        
        return OrganizacionResponse(
            id=str(organizacion.id),
            nombre=organizacion.nombre,
            rut=organizacion.rut,
            sector=organizacion.sector.value,
            tamaño=organizacion.tamaño.value,
            region=organizacion.region,
            comuna=organizacion.comuna,
            nivel_suscripcion=organizacion.nivel_suscripcion.value,
            fecha_inicio_suscripcion=organizacion.fecha_inicio_suscripcion,
            fecha_vencimiento_suscripcion=organizacion.fecha_vencimiento_suscripcion,
            maximo_usuarios=organizacion.maximo_usuarios,
            maximo_evaluaciones_por_mes=organizacion.maximo_evaluaciones_por_mes,
            maximo_dias_retencion_datos=organizacion.maximo_dias_retencion_datos,
            descripcion=organizacion.descripcion,
            sitio_web=organizacion.sitio_web,
            telefono=organizacion.telefono,
            email_facturacion=organizacion.email_facturacion,
            fecha_creacion=organizacion.fecha_creacion
        )
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{org_id}/usuarios")
async def listar_usuarios_organizacion(
    org_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Listar usuarios de la organización"""
    
    try:
        from ...modelos.usuario import Usuario
        
        usuarios = db.query(Usuario).filter(
            Usuario.organizacion_id == organizacion.id,
            Usuario.fecha_eliminacion.is_(None)
        ).all()
        
        usuarios_response = []
        for usuario in usuarios:
            usuarios_response.append({
                "id": str(usuario.id),
                "email": usuario.email,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "estado_cuenta": usuario.estado_cuenta.value,
                "rol": {
                    "id": str(usuario.rol.id),
                    "nombre": usuario.rol.nombre.value,
                    "nombre_mostrar": usuario.rol.nombre_mostrar
                },
                "fecha_ultimo_acceso": usuario.fecha_ultimo_acceso,
                "fecha_creacion": usuario.fecha_creacion
            })
        
        return {
            "usuarios": usuarios_response,
            "total": len(usuarios_response)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{org_id}/uso", response_model=UsoOrganizacionResponse)
async def obtener_uso_organizacion(
    org_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener uso actual de la organización"""
    
    try:
        uso = organizacion.obtener_uso_mensual()
        
        return UsoOrganizacionResponse(
            evaluaciones_usadas=uso["evaluaciones_usadas"],
            evaluaciones_limite=uso["evaluaciones_limite"],
            usuarios_activos=uso["usuarios_activos"],
            usuarios_limite=uso["usuarios_limite"],
            porcentaje_uso_evaluaciones=uso["porcentaje_uso_evaluaciones"],
            porcentaje_uso_usuarios=uso["porcentaje_uso_usuarios"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{org_id}/estadisticas")
async def obtener_estadisticas_organizacion(
    org_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Obtener estadísticas de la organización"""
    
    try:
        # Obtener estadísticas reales de la organización
        from app.modelos.evaluacion import Evaluacion, EstadoEvaluacion
        from app.modelos.usuario import Usuario
        
        # Estadísticas de evaluaciones
        total_evaluaciones = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).count()
        
        evaluaciones_completadas = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.estado == EstadoEvaluacion.COMPLETADA,
            Evaluacion.fecha_eliminacion.is_(None)
        ).count()
        
        evaluaciones_en_progreso = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.estado == EstadoEvaluacion.EN_PROGRESO,
            Evaluacion.fecha_eliminacion.is_(None)
        ).count()
        
        # Puntuación promedio
        evaluaciones_con_puntuacion = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.puntuacion_global.isnot(None),
            Evaluacion.fecha_eliminacion.is_(None)
        ).all()
        
        puntuacion_promedio = 0.0
        if evaluaciones_con_puntuacion:
            puntuacion_promedio = sum(eval.puntuacion_global for eval in evaluaciones_con_puntuacion) / len(evaluaciones_con_puntuacion)
        
        # Estadísticas de usuarios
        total_usuarios = db.query(Usuario).filter(
            Usuario.organizacion_id == usuario.organizacion_id,
            Usuario.fecha_eliminacion.is_(None)
        ).count()
        
        usuarios_activos = db.query(Usuario).filter(
            Usuario.organizacion_id == usuario.organizacion_id,
            Usuario.estado_cuenta == "activo",
            Usuario.fecha_eliminacion.is_(None)
        ).count()
        
        # Uso mensual (evaluaciones creadas este mes)
        from datetime import datetime, timedelta
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        uso_mensual = db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == usuario.organizacion_id,
            Evaluacion.fecha_creacion >= inicio_mes,
            Evaluacion.fecha_eliminacion.is_(None)
        ).count()
        
        # Límites según nivel de suscripción
        limite_mensual = usuario.organizacion.maximo_evaluaciones_por_mes
        limite_usuarios = usuario.organizacion.maximo_usuarios
        
        # Porcentajes de uso
        porcentaje_uso_evaluaciones = (uso_mensual / limite_mensual * 100) if limite_mensual > 0 else 0
        porcentaje_uso_usuarios = (total_usuarios / limite_usuarios * 100) if limite_usuarios > 0 else 0
        
        return {
            "total_evaluaciones": total_evaluaciones,
            "evaluaciones_completadas": evaluaciones_completadas,
            "puntuacion_promedio": round(puntuacion_promedio, 2),
            "evaluaciones_en_progreso": evaluaciones_en_progreso,
            "total_usuarios": total_usuarios,
            "usuarios_activos": usuarios_activos,
            "uso_mensual": uso_mensual,
            "limite_mensual": limite_mensual,
            "porcentaje_uso_evaluaciones": round(porcentaje_uso_evaluaciones, 1),
            "porcentaje_uso_usuarios": round(porcentaje_uso_usuarios, 1)
        }
        
    except Exception as e:
        print(f"Error en obtener_estadisticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )