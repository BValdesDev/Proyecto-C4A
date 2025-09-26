
# app/api/v1/endpoints/suscripciones.py
"""
Endpoints de gestión de suscripciones
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.organizacion import Organizacion
from app.modelos.suscripcion import Suscripcion
from app.modelos.usuario import Usuario
from app.modelos.log_auditoria import LogAuditoria
from app.core.config import NivelSuscripcion, PRECIOS_CLP, CARACTERISTICAS_POR_NIVEL
from app.core.excepciones import ExcepcionValidacion, ExcepcionRecursoNoEncontrado
from ..dependencias import (
    obtener_usuario_actual_dependencia,
    obtener_organizacion_usuario
)

router = APIRouter()


# Modelos Pydantic
class NivelSuscripcionResponse(BaseModel):
    nivel: str
    nombre_mostrar: str
    precio_mensual_clp: int
    precio_anual_clp: int
    caracteristicas: List[str]
    limites: Dict[str, Any]


class SuscripcionResponse(BaseModel):
    id: str
    nivel: str
    estado: str
    monto_clp: float
    ciclo_facturacion: str
    inicio_periodo_actual: datetime
    fin_periodo_actual: datetime
    uso_evaluaciones: int
    uso_usuarios: int
    fecha_creacion: datetime


class CambioSuscripcionRequest(BaseModel):
    nuevo_nivel: NivelSuscripcion
    metodo_pago_id: Optional[str] = None


# Endpoints
@router.get("/niveles", response_model=List[NivelSuscripcionResponse])
async def obtener_niveles_suscripcion():
    """Obtener niveles de suscripción disponibles"""
    
    try:
        niveles = []
        
        for nivel in NivelSuscripcion:
            precio_mensual = PRECIOS_CLP[nivel]
            precio_anual = int(precio_mensual * 12 * 0.8)  # 20% descuento anual
            
            # Obtener límites
            from ...core.config import LIMITES_POR_NIVEL
            limites = LIMITES_POR_NIVEL[nivel]
            
            niveles.append(NivelSuscripcionResponse(
                nivel=nivel.value,
                nombre_mostrar=nivel.value.title(),
                precio_mensual_clp=precio_mensual,
                precio_anual_clp=precio_anual,
                caracteristicas=CARACTERISTICAS_POR_NIVEL[nivel],
                limites=limites
            ))
        
        return niveles
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/actual", response_model=SuscripcionResponse)
async def obtener_suscripcion_actual(
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener suscripción actual de la organización"""
    
    try:
        # Buscar suscripción activa
        suscripcion = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        if not suscripcion:
            # Si no hay suscripción activa, crear una gratuita
            suscripcion = Suscripcion(
                organizacion_id=organizacion.id,
                id_cliente_stripe="gratuito",
                nivel=NivelSuscripcion.GRATUITO,
                estado="active",
                monto_centavos=0,
                inicio_periodo_actual=datetime.utcnow(),
                fin_periodo_actual=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            )
            db.add(suscripcion)
            db.commit()
            db.refresh(suscripcion)
        
        return SuscripcionResponse(
            id=str(suscripcion.id),
            nivel=suscripcion.nivel.value,
            estado=suscripcion.estado,
            monto_clp=suscripcion.monto_clp,
            ciclo_facturacion=suscripcion.ciclo_facturacion,
            inicio_periodo_actual=suscripcion.inicio_periodo_actual,
            fin_periodo_actual=suscripcion.fin_periodo_actual,
            uso_evaluaciones=suscripcion.uso_evaluaciones_periodo_actual,
            uso_usuarios=suscripcion.uso_usuarios_periodo_actual,
            fecha_creacion=suscripcion.fecha_creacion
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/suscribirse")
async def suscribirse_nivel(
    suscripcion_data: CambioSuscripcionRequest,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Suscribirse a un nivel de suscripción"""
    
    try:
        # Verificar que no es downgrade
        if organizacion.nivel_suscripcion != NivelSuscripcion.GRATUITO:
            niveles = [NivelSuscripcion.GRATUITO, NivelSuscripcion.PRO, NivelSuscripcion.EMPRESARIAL]
            nivel_actual_idx = niveles.index(organizacion.nivel_suscripcion)
            nuevo_nivel_idx = niveles.index(suscripcion_data.nuevo_nivel)
            
            if nuevo_nivel_idx < nivel_actual_idx:
                raise ExcepcionValidacion("No se permite downgrade directo. Use el endpoint de cancelación.")
        
        # Si es nivel gratuito, no requiere pago
        if suscripcion_data.nuevo_nivel == NivelSuscripcion.GRATUITO:
            organizacion.nivel_suscripcion = NivelSuscripcion.GRATUITO
            organizacion.actualizar_limites_nivel()
            db.commit()
            
            return {
                "mensaje": "Suscripción actualizada a nivel gratuito",
                "nuevo_nivel": NivelSuscripcion.GRATUITO.value
            }
        
        # Para niveles de pago, integrar con Stripe
        from ...servicios.stripe_service import ServicioStripe
        
        stripe_service = ServicioStripe()
        
        # Crear o actualizar suscripción en Stripe
        if organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            # Crear nueva suscripción
            suscripcion_stripe = await stripe_service.crear_suscripcion(
                organizacion, suscripcion_data.nuevo_nivel, suscripcion_data.metodo_pago_id
            )
        else:
            # Actualizar suscripción existente
            suscripcion_stripe = await stripe_service.actualizar_suscripcion(
                organizacion, suscripcion_data.nuevo_nivel
            )
        
        # Actualizar organización
        organizacion.nivel_suscripcion = suscripcion_data.nuevo_nivel
        organizacion.actualizar_limites_nivel()
        organizacion.fecha_inicio_suscripcion = datetime.utcnow()
        organizacion.fecha_vencimiento_suscripcion = suscripcion_stripe["fecha_vencimiento"]
        
        # Crear o actualizar registro de suscripción
        suscripcion_existente = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        if suscripcion_existente:
            suscripcion_existente.nivel = suscripcion_data.nuevo_nivel
            suscripcion_existente.monto_centavos = suscripcion_stripe["monto_centavos"]
            suscripcion_existente.inicio_periodo_actual = suscripcion_stripe["inicio_periodo"]
            suscripcion_existente.fin_periodo_actual = suscripcion_stripe["fin_periodo"]
        else:
            nueva_suscripcion = Suscripcion(
                organizacion_id=organizacion.id,
                id_suscripcion_stripe=suscripcion_stripe["id"],
                id_cliente_stripe=suscripcion_stripe["cliente_id"],
                nivel=suscripcion_data.nuevo_nivel,
                estado="active",
                monto_centavos=suscripcion_stripe["monto_centavos"],
                inicio_periodo_actual=suscripcion_stripe["inicio_periodo"],
                fin_periodo_actual=suscripcion_stripe["fin_periodo"]
            )
            db.add(nueva_suscripcion)
        
        db.commit()
        
        # Log de suscripción
        LogAuditoria.crear_log(
            tipo_evento="suscripcion",
            accion="suscribirse",
            exitoso=True,
            usuario_id=str(usuario.id),
            organizacion_id=str(organizacion.id),
            tipo_recurso="suscripcion"
        )
        
        return {
            "mensaje": f"Suscripción actualizada a nivel {suscripcion_data.nuevo_nivel.value}",
            "nuevo_nivel": suscripcion_data.nuevo_nivel.value,
            "fecha_vencimiento": organizacion.fecha_vencimiento_suscripcion,
            "limites": organizacion.obtener_uso_mensual()
        }
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/cancelar")
async def cancelar_suscripcion(
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Cancelar suscripción actual"""
    
    try:
        if organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            raise ExcepcionValidacion("No se puede cancelar una suscripción gratuita")
        
        # Cancelar en Stripe
        from ...servicios.stripe_service import ServicioStripe
        
        stripe_service = ServicioStripe()
        await stripe_service.cancelar_suscripcion(organizacion)
        
        # Actualizar organización
        organizacion.nivel_suscripcion = NivelSuscripcion.GRATUITO
        organizacion.actualizar_limites_nivel()
        organizacion.fecha_vencimiento_suscripcion = None
        
        # Actualizar suscripción
        suscripcion = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        if suscripcion:
            suscripcion.estado = "canceled"
        
        db.commit()
        
        # Log de cancelación
        LogAuditoria.crear_log(
            tipo_evento="suscripcion",
            accion="cancelar_suscripcion",
            exitoso=True,
            usuario_id=str(usuario.id),
            organizacion_id=str(organizacion.id),
            tipo_recurso="suscripcion"
        )
        
        return {
            "mensaje": "Suscripción cancelada exitosamente",
            "nuevo_nivel": NivelSuscripcion.GRATUITO.value,
            "fecha_efectiva": datetime.utcnow()
        }
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/uso")
async def obtener_uso_suscripcion(
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener uso actual de la suscripción"""
    
    try:
        suscripcion = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        if not suscripcion:
            # Crear suscripción gratuita si no existe
            suscripcion = Suscripcion(
                organizacion_id=organizacion.id,
                id_cliente_stripe="gratuito",
                nivel=NivelSuscripcion.GRATUITO,
                estado="active",
                monto_centavos=0,
                inicio_periodo_actual=datetime.utcnow(),
                fin_periodo_actual=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            )
            db.add(suscripcion)
            db.commit()
            db.refresh(suscripcion)
        
        estadisticas = suscripcion.obtener_estadisticas_uso()
        
        return {
            "suscripcion": {
                "nivel": suscripcion.nivel.value,
                "estado": suscripcion.estado,
                "monto_clp": suscripcion.monto_clp
            },
            "uso": estadisticas,
            "organizacion": {
                "nombre": organizacion.nombre,
                "nivel_suscripcion": organizacion.nivel_suscripcion.value
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/facturas")
async def obtener_facturas(
    pagina: int = 1,
    por_pagina: int = 20,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener historial de facturas"""
    
    try:
        if organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            return {
                "facturas": [],
                "total": 0,
                "mensaje": "No hay facturas para el plan gratuito"
            }
        
        # Obtener facturas de Stripe
        from ...servicios.stripe_service import ServicioStripe
        
        stripe_service = ServicioStripe()
        facturas = await stripe_service.obtener_facturas_organizacion(organizacion)
        
        return {
            "facturas": facturas,
            "total": len(facturas),
            "pagina": pagina,
            "por_pagina": por_pagina
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )