#!/usr/bin/env python3
"""
Endpoints de generación de reportes de ciberseguridad
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import io
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.evaluacion import Evaluacion
from app.modelos.usuario import Usuario
from app.servicios.reporte_service import ReporteCiberseguridadService
from ..dependencias import obtener_usuario_actual_dependencia

router = APIRouter()

# Modelos Pydantic
class ReporteResponse(BaseModel):
    evaluacion: dict
    organizacion: dict
    metricas: dict
    analisis_categorias: dict
    recomendaciones: List[dict]
    plan_accion: dict
    fecha_generacion: str

# Endpoints
@router.get("/evaluacion/{evaluacion_id}")
async def obtener_reporte_evaluacion(
    evaluacion_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtener reporte de evaluación en formato JSON
    
    Genera un reporte completo con análisis de ciberseguridad, recomendaciones
    y plan de acción basado en las respuestas de la evaluación.
    """
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
        
        if evaluacion.estado.value != "completada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La evaluación debe estar completada para generar el reporte"
            )
        
        # Generar reporte
        reporte_service = ReporteCiberseguridadService(db)
        reporte = reporte_service.generar_reporte_evaluacion(evaluacion_id)
        
        return {
            "success": True,
            "data": reporte,
            "mensaje": "Reporte generado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generando reporte: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/evaluacion/{evaluacion_id}/pdf")
async def generar_pdf_reporte(
    evaluacion_id: str,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """
    Generar y descargar reporte en formato PDF
    
    Genera un reporte completo en formato PDF con análisis de ciberseguridad,
    recomendaciones y plan de acción.
    """
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
        
        if evaluacion.estado.value != "completada":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La evaluación debe estar completada para generar el PDF"
            )
        
        # Generar reporte
        reporte_service = ReporteCiberseguridadService(db)
        reporte = reporte_service.generar_reporte_evaluacion(evaluacion_id)
        
        # Generar PDF
        pdf_content = generar_pdf_reporte(reporte)
        
        # Preparar respuesta
        filename = f"Reporte_Ciberseguridad_{evaluacion.nombre.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

def generar_pdf_reporte(reporte: dict) -> bytes:
    """Generar PDF del reporte"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=8,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Contenido del PDF
    story = []
    
    # Portada
    story.append(Paragraph("REPORTE DE EVALUACIÓN DE CIBERSEGURIDAD", title_style))
    story.append(Spacer(1, 20))
    
    # Información de la evaluación
    eval_info = reporte["evaluacion"]
    org_info = reporte["organizacion"]
    
    info_data = [
        ["Organización:", org_info["nombre"]],
        ["Evaluación:", eval_info["nombre"]],
        ["Framework:", eval_info["framework"]],
        ["Nivel:", eval_info["nivel_usado"].upper()],
        ["Fecha de Evaluación:", datetime.fromisoformat(eval_info["fecha_completada"]).strftime("%d/%m/%Y")],
        ["Fecha de Reporte:", datetime.fromisoformat(reporte["fecha_generacion"]).strftime("%d/%m/%Y %H:%M")]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
    ]))
    
    story.append(info_table)
    story.append(PageBreak())
    
    # Resumen Ejecutivo
    story.append(Paragraph("RESUMEN EJECUTIVO", heading_style))
    
    metricas = reporte["metricas"]
    nivel_madurez = metricas["nivel_madurez"]
    porcentaje = metricas["porcentaje_logrado"]
    
    resumen_text = f"""
    Su organización ha alcanzado un nivel de madurez en ciberseguridad de <b>{nivel_madurez}</b> 
    con una puntuación general de <b>{porcentaje:.1f}%</b>.
    
    Este reporte proporciona un análisis detallado de su postura de seguridad, identificando 
    fortalezas, áreas de mejora y recomendaciones específicas para fortalecer su programa 
    de ciberseguridad.
    """
    
    story.append(Paragraph(resumen_text, normal_style))
    story.append(Spacer(1, 12))
    
    # Métricas principales
    story.append(Paragraph("MÉTRICAS PRINCIPALES", subheading_style))
    
    metricas_data = [
        ["Métrica", "Valor"],
        ["Puntuación Promedio", f"{metricas['puntuacion_promedio']}/5.0"],
        ["Porcentaje Logrado", f"{metricas['porcentaje_logrado']:.1f}%"],
        ["Nivel de Madurez", nivel_madurez],
        ["Total de Preguntas", str(metricas['total_respuestas'])],
        ["Puntuación Total", f"{metricas['puntuacion_total']}/{metricas['puntuacion_maxima']}"]
    ]
    
    metricas_table = Table(metricas_data, colWidths=[3*inch, 2*inch])
    metricas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 1), (1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metricas_table)
    story.append(PageBreak())
    
    # Análisis por Categorías
    story.append(Paragraph("ANÁLISIS POR CATEGORÍAS", heading_style))
    
    categorias = reporte["analisis_categorias"]
    for categoria, datos in categorias.items():
        story.append(Paragraph(f"{categoria.upper()}", subheading_style))
        
        categoria_text = f"""
        <b>Puntuación:</b> {datos['puntuacion_total']}/{datos['puntuacion_maxima']} 
        ({datos['porcentaje']:.1f}%)
        
        <b>Fortalezas:</b> {len(datos['fortalezas'])} áreas bien implementadas
        <b>Debilidades:</b> {len(datos['debilidades'])} áreas que requieren atención
        """
        
        story.append(Paragraph(categoria_text, normal_style))
        story.append(Spacer(1, 8))
    
    story.append(PageBreak())
    
    # Recomendaciones Prioritarias
    story.append(Paragraph("RECOMENDACIONES PRIORITARIAS", heading_style))
    
    recomendaciones = reporte["recomendaciones"][:5]  # Top 5
    
    for i, rec in enumerate(recomendaciones, 1):
        story.append(Paragraph(f"{i}. {rec['accion']}", subheading_style))
        
        rec_text = f"""
        <b>Categoría:</b> {rec['categoria']}
        <b>Nivel de Criticidad:</b> {rec['nivel_criticidad']}
        <b>Tiempo Estimado:</b> {rec['tiempo_estimado']}
        <b>Costo:</b> {rec['costo']}
        <b>Prioridad:</b> {rec['prioridad']}/10
        
        <b>Descripción:</b> {rec['descripcion']}
        
        <b>Beneficio:</b> {rec['beneficio']}
        """
        
        story.append(Paragraph(rec_text, normal_style))
        
        # Pasos concretos
        if rec.get('pasos_concretos'):
            story.append(Paragraph("<b>Pasos Concretos:</b>", normal_style))
            for paso in rec['pasos_concretos']:
                story.append(Paragraph(f"• {paso}", normal_style))
        
        story.append(Spacer(1, 12))
    
    story.append(PageBreak())
    
    # Plan de Acción
    story.append(Paragraph("PLAN DE ACCIÓN", heading_style))
    
    plan = reporte["plan_accion"]
    
    # Resumen del plan
    resumen_plan = f"""
    <b>Total de Recomendaciones:</b> {plan['resumen']['total_recomendaciones']}
    <b>Críticas:</b> {plan['resumen']['criticas']}
    <b>Importantes:</b> {plan['resumen']['importantes']}
    <b>Mejoras:</b> {plan['resumen']['mejoras']}
    """
    
    story.append(Paragraph(resumen_plan, normal_style))
    story.append(Spacer(1, 12))
    
    # Cronograma
    story.append(Paragraph("CRONOGRAMA DE IMPLEMENTACIÓN", subheading_style))
    
    for fase in plan['cronograma']:
        story.append(Paragraph(fase['fase'], subheading_style))
        story.append(Paragraph(fase['descripcion'], normal_style))
        story.append(Paragraph(f"<b>Inversión:</b> {fase['inversion']}", normal_style))
        story.append(Spacer(1, 8))
    
    # Inversión estimada
    if 'inversion_estimada' in plan:
        inv = plan['inversion_estimada']
        story.append(Paragraph("INVERSIÓN ESTIMADA", subheading_style))
        
        inv_text = f"""
        <b>Inversión Total:</b> ${inv['total_clp']:,.0f} CLP (${inv['total_usd']:,.0f} USD)
        <b>Período:</b> {inv['periodo']}
        """
        
        story.append(Paragraph(inv_text, normal_style))
    
    # ROI proyectado
    if 'roi_proyectado' in plan:
        roi = plan['roi_proyectado']
        story.append(Paragraph("ROI PROYECTADO", subheading_style))
        
        roi_text = f"""
        <b>Reducción de Riesgo:</b> {roi['reduccion_riesgo']:.0f}%
        <b>Beneficio Anual Proyectado:</b> ${roi['beneficio_anual_clp']:,.0f} CLP
        <b>ROI:</b> {roi['roi_porcentaje']:.1f}%
        <b>Período de Recuperación:</b> {roi['periodo_recuperacion']:.1f} meses
        """
        
        story.append(Paragraph(roi_text, normal_style))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()