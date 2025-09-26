# app/api/v1/endpoints/reportes.py
"""
Endpoints de generación de reportes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.evaluacion import Evaluacion
from app.modelos.reporte import Reporte
from app.modelos.organizacion import Organizacion
from app.modelos.usuario import Usuario
from app.modelos.log_auditoria import LogAuditoria
from app.core.config import NivelSuscripcion
from app.core.excepciones import ExcepcionValidacion, ExcepcionRecursoNoEncontrado, ExcepcionNivelSuscripcion
from ..dependencias import (
    obtener_usuario_actual_dependencia,
    obtener_organizacion_usuario,
    verificar_nivel_suscripcion
)

router = APIRouter()


# Modelos Pydantic
class ReporteGenerateRequest(BaseModel):
    tipo_reporte: str = "completo"
    incluir_benchmarking: bool = False
    incluir_roadmap: bool = False


class ReporteResponse(BaseModel):
    id: str
    titulo: str
    tipo_reporte: str
    nivel_generado: str
    puntuacion_global: float
    total_fortalezas: int
    total_debilidades: int
    total_recomendaciones: int
    tiene_marca_agua: bool
    fecha_generacion: datetime
    url_pdf: Optional[str]


# Endpoints
@router.post("/evaluacion/{evaluacion_id}/generar", response_model=ReporteResponse)
async def generar_reporte_evaluacion(
    evaluacion_id: str,
    reporte_data: ReporteGenerateRequest,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Generar reporte de evaluación"""
    
    try:
        # Verificar que la evaluación existe y está completada
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        if not evaluacion.esta_completada:
            raise ExcepcionValidacion("La evaluación debe estar completada para generar el reporte")
        
        # Verificar permisos según nivel
        if reporte_data.incluir_benchmarking and organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            raise ExcepcionNivelSuscripcion("El benchmarking está disponible solo en planes Pro+")
        
        if reporte_data.incluir_roadmap and organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            raise ExcepcionNivelSuscripcion("El roadmap está disponible solo en planes Pro+")
        
        # Generar contenido del reporte
        from ...servicios.generador_reportes import GeneradorReportesPDF
        
        generador = GeneradorReportesPDF(organizacion.nivel_suscripcion)
        
        # Obtener recomendaciones según nivel
        recomendaciones = await generador.obtener_recomendaciones_por_nivel(
            evaluacion, organizacion.nivel_suscripcion
        )
        
        # Generar PDF
        contenido_pdf = await generador.generar_reporte_evaluacion(
            evaluacion, recomendaciones, reporte_data.tipo_reporte
        )
        
        # Guardar archivo PDF
        url_archivo = await generador.guardar_archivo_pdf(contenido_pdf, evaluacion_id)
        
        # Crear registro de reporte
        nuevo_reporte = Reporte(
            evaluacion_id=evaluacion.id,
            organizacion_id=organizacion.id,
            generado_por=usuario.id,
            tipo_reporte=reporte_data.tipo_reporte,
            nivel_generado=organizacion.nivel_suscripcion,
            titulo=f"Reporte de Evaluación - {evaluacion.nombre}",
            puntuacion_global=evaluacion.puntuacion_global,
            fortalezas=generador.obtener_fortalezas(evaluacion),
            debilidades=generador.obtener_debilidades(evaluacion),
            recomendaciones=recomendaciones,
            url_pdf=url_archivo,
            tiene_marca_agua=(organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO)
        )
        
        db.add(nuevo_reporte)
        db.commit()
        db.refresh(nuevo_reporte)
        
        # Log de generación
        LogAuditoria.crear_log(
            tipo_evento="reporte",
            accion="generar_reporte",
            exitoso=True,
            usuario_id=str(usuario.id),
            organizacion_id=str(organizacion.id),
            tipo_recurso="reporte",
            id_recurso=str(nuevo_reporte.id)
        )
        
        return ReporteResponse(
            id=str(nuevo_reporte.id),
            titulo=nuevo_reporte.titulo,
            tipo_reporte=nuevo_reporte.tipo_reporte,
            nivel_generado=nuevo_reporte.nivel_generado.value,
            puntuacion_global=float(nuevo_reporte.puntuacion_global),
            total_fortalezas=len(nuevo_reporte.fortalezas) if nuevo_reporte.fortalezas else 0,
            total_debilidades=len(nuevo_reporte.debilidades) if nuevo_reporte.debilidades else 0,
            total_recomendaciones=len(nuevo_reporte.recomendaciones) if nuevo_reporte.recomendaciones else 0,
            tiene_marca_agua=nuevo_reporte.tiene_marca_agua,
            fecha_generacion=nuevo_reporte.fecha_generacion,
            url_pdf=nuevo_reporte.url_pdf
        )
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado, ExcepcionNivelSuscripcion):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/evaluacion/{evaluacion_id}/puntuacion")
async def obtener_puntuacion_evaluacion(
    evaluacion_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener puntuación de la evaluación"""
    
    try:
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        if not evaluacion.esta_completada:
            raise ExcepcionValidacion("La evaluación debe estar completada")
        
        # Obtener puntuaciones según nivel
        puntuacion_global = float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else 0.0
        puntuaciones_dominio = evaluacion.puntuaciones_dominio or {}
        
        # Para nivel gratuito, limitar información
        if organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            return {
                "puntuacion_global": puntuacion_global,
                "nivel_suscripcion": organizacion.nivel_suscripcion.value,
                "mensaje": "Actualice a plan Pro para ver análisis detallado"
            }
        
        # Para niveles Pro+, incluir análisis detallado
        from ...servicios.analisis_evaluacion import AnalizadorEvaluacion
        
        analizador = AnalizadorEvaluacion()
        analisis = await analizador.analizar_evaluacion(evaluacion, organizacion.nivel_suscripcion)
        
        return {
            "puntuacion_global": puntuacion_global,
            "puntuaciones_dominio": puntuaciones_dominio,
            "nivel_suscripcion": organizacion.nivel_suscripcion.value,
            "analisis": analisis
        }
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/evaluacion/{evaluacion_id}/recomendaciones")
async def obtener_recomendaciones_evaluacion(
    evaluacion_id: str,
    limite: Optional[int] = None,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener recomendaciones de la evaluación"""
    
    try:
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        if not evaluacion.esta_completada:
            raise ExcepcionValidacion("La evaluación debe estar completada")
        
        # Obtener recomendaciones según nivel
        from ...servicios.generador_reportes import GeneradorReportesPDF
        
        generador = GeneradorReportesPDF(organizacion.nivel_suscripcion)
        recomendaciones = await generador.obtener_recomendaciones_por_nivel(
            evaluacion, organizacion.nivel_suscripcion
        )
        
        # Aplicar límite según nivel
        if organizacion.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            limite = min(limite or 3, 3)  # Máximo 3 para gratuito
        else:
            limite = limite or len(recomendaciones)
        
        recomendaciones_limitadas = recomendaciones[:limite]
        
        return {
            "recomendaciones": recomendaciones_limitadas,
            "total_disponibles": len(recomendaciones),
            "mostradas": len(recomendaciones_limitadas),
            "nivel_suscripcion": organizacion.nivel_suscripcion.value
        }
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/evaluacion/{evaluacion_id}/benchmarks")
async def obtener_benchmarks_evaluacion(
    evaluacion_id: str,
    organizacion: Organizacion = Depends(verificar_nivel_suscripcion(NivelSuscripcion.PRO)),
    db: Session = Depends(obtener_sesion)
):
    """Obtener benchmarks de la evaluación (solo Pro+)"""
    
    try:
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        if not evaluacion.esta_completada:
            raise ExcepcionValidacion("La evaluación debe estar completada")
        
        # Obtener benchmarks
        from ...servicios.benchmarking import ServicioBenchmarking
        
        servicio_benchmark = ServicioBenchmarking()
        benchmarks = await servicio_benchmark.obtener_benchmarks_organizacion(
            evaluacion, organizacion
        )
        
        return {
            "evaluacion_id": str(evaluacion.id),
            "benchmarks": benchmarks,
            "nivel_suscripcion": organizacion.nivel_suscripcion.value
        }
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/evaluacion/{evaluacion_id}/exportar/excel")
async def exportar_evaluacion_excel(
    evaluacion_id: str,
    organizacion: Organizacion = Depends(verificar_nivel_suscripcion(NivelSuscripcion.EMPRESARIAL)),
    db: Session = Depends(obtener_sesion)
):
    """Exportar evaluación a Excel (solo Empresarial)"""
    
    try:
        evaluacion = db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.organizacion_id == organizacion.id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ExcepcionRecursoNoEncontrado("Evaluación no encontrada")
        
        if not evaluacion.esta_completada:
            raise ExcepcionValidacion("La evaluación debe estar completada")
        
        # Generar archivo Excel
        from ...servicios.exportador_excel import ExportadorExcel
        
        exportador = ExportadorExcel()
        archivo_excel = await exportador.exportar_evaluacion_completa(evaluacion)
        
        # Log de exportación
        LogAuditoria.crear_log(
            tipo_evento="reporte",
            accion="exportar_excel",
            exitoso=True,
            organizacion_id=str(organizacion.id),
            tipo_recurso="evaluacion",
            id_recurso=str(evaluacion.id)
        )
        
        return {
            "mensaje": "Archivo Excel generado exitosamente",
            "url_descarga": archivo_excel["url"],
            "tamaño_archivo": archivo_excel["tamaño"],
            "fecha_generacion": datetime.utcnow()
        }
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )