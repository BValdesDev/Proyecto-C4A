# app/servicios/pdf_service.py
"""
Servicio para generación de PDFs de diagnósticos
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
from typing import Dict, List, Optional
import io

from ..modelos.cuestionario import Cuestionario
from ..modelos.evaluacion import Evaluacion
from .calculo_madurez_service import CalculoMadurezService

class PDFService:
    """Servicio para generación de PDFs de diagnósticos"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        """Configurar estilos personalizados"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='TituloC4A',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='SubtituloC4A',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='NormalC4A',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para destacados
        self.styles.add(ParagraphStyle(
            name='DestacadoC4A',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1E3A8A'),
            fontName='Helvetica-Bold',
            spaceAfter=6
        ))
    
    def _crear_portada(
        self, 
        elementos: List,
        cuestionario: Cuestionario,
        organizacion_nombre: str,
        fecha: datetime
    ):
        """Crear portada del PDF"""
        # Logo o título principal
        elementos.append(Spacer(1, 1.5*inch))
        
        # Título del diagnóstico
        titulo = Paragraph(
            f"<b>DIAGNÓSTICO DE MADUREZ EN CIBERSEGURIDAD</b>",
            self.styles['TituloC4A']
        )
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.3*inch))
        
        # Nombre del cuestionario
        elementos.append(Paragraph(
            cuestionario.nombre,
            self.styles['SubtituloC4A']
        ))
        elementos.append(Spacer(1, 0.5*inch))
        
        # Información de la evaluación
        info_data = [
            ['Organización:', organizacion_nombre],
            ['Nivel de Diagnóstico:', cuestionario.nivel.value.capitalize()],
            ['Total de Preguntas:', str(cuestionario.total_items)],
            ['Fecha de Evaluación:', fecha.strftime('%d de %B de %Y')],
            ['Versión:', cuestionario.version]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6B7280')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111827')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(info_table)
        elementos.append(Spacer(1, 1*inch))
        
        # Pie de portada
        elementos.append(Paragraph(
            f"<i>Basado en NIST Cybersecurity Framework 2.0 y COBIT 2019</i>",
            self.styles['Normal']
        ))
        
        elementos.append(PageBreak())
    
    def _crear_instrucciones(
        self,
        elementos: List,
        cuestionario: Cuestionario
    ):
        """Crear sección de instrucciones"""
        elementos.append(Paragraph(
            "Instrucciones y Metodología",
            self.styles['SubtituloC4A']
        ))
        elementos.append(Spacer(1, 0.2*inch))
        
        if cuestionario.texto_instrucciones:
            # Limpiar y formatear instrucciones
            instrucciones = cuestionario.texto_instrucciones.replace('#', '').strip()
            elementos.append(Paragraph(instrucciones, self.styles['NormalC4A']))
            elementos.append(Spacer(1, 0.3*inch))
        
        # Tabla de escala de madurez
        elementos.append(Paragraph(
            "Escala de Evaluación",
            self.styles['DestacadoC4A']
        ))
        
        escala_data = [['Nivel', 'Descripción']]
        for nivel, descripcion in cuestionario.escala_madurez.items():
            escala_data.append([nivel, descripcion])
        
        escala_table = Table(escala_data, colWidths=[0.8*inch, 5.5*inch])
        escala_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elementos.append(escala_table)
        elementos.append(PageBreak())
    
    def _crear_resultados(
        self,
        elementos: List,
        analisis: Dict[str, any],
        cuestionario: Cuestionario
    ):
        """Crear sección de resultados"""
        elementos.append(Paragraph(
            "Resultados del Diagnóstico",
            self.styles['SubtituloC4A']
        ))
        elementos.append(Spacer(1, 0.3*inch))
        
        # Resultado principal
        nivel_madurez = analisis['nivel_madurez']
        
        resultado_data = [
            ['', ''],
            ['NIVEL DE MADUREZ', nivel_madurez['nombre'].upper()],
            ['Puntuación Global', f"{analisis['puntuacion_global']:.1f}%"],
            ['Rango', f"{nivel_madurez['rango']}%"],
            ['', '']
        ]
        
        resultado_table = Table(resultado_data, colWidths=[3*inch, 3*inch])
        resultado_table.setStyle(TableStyle([
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 18),
            ('FONTSIZE', (0, 2), (-1, -1), 14),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor(nivel_madurez['color'])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elementos.append(resultado_table)
        elementos.append(Spacer(1, 0.3*inch))
        
        # Descripción del nivel
        elementos.append(Paragraph(
            nivel_madurez['descripcion'],
            self.styles['NormalC4A']
        ))
        elementos.append(Spacer(1, 0.5*inch))
        
        # Distribución de respuestas
        if 'distribucion_respuestas' in analisis:
            elementos.append(Paragraph(
                "Distribución de Respuestas",
                self.styles['DestacadoC4A']
            ))
            
            dist_data = [['Nivel', 'Cantidad', 'Porcentaje']]
            total_respuestas = sum(analisis['distribucion_respuestas'].values())
            
            for nivel in range(1, 6):
                cantidad = analisis['distribucion_respuestas'].get(nivel, 0)
                porcentaje = (cantidad / total_respuestas * 100) if total_respuestas > 0 else 0
                dist_data.append([
                    f"Nivel {nivel}",
                    str(cantidad),
                    f"{porcentaje:.1f}%"
                ])
            
            dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            dist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            elementos.append(dist_table)
            elementos.append(Spacer(1, 0.3*inch))
        
        elementos.append(PageBreak())
    
    def _crear_recomendaciones(
        self,
        elementos: List,
        recomendaciones: List[str]
    ):
        """Crear sección de recomendaciones"""
        elementos.append(Paragraph(
            "Recomendaciones de Mejora",
            self.styles['SubtituloC4A']
        ))
        elementos.append(Spacer(1, 0.2*inch))
        
        elementos.append(Paragraph(
            "A continuación se presentan recomendaciones específicas para mejorar el nivel de madurez en ciberseguridad de su organización:",
            self.styles['NormalC4A']
        ))
        elementos.append(Spacer(1, 0.2*inch))
        
        for idx, recomendacion in enumerate(recomendaciones, 1):
            elementos.append(Paragraph(
                f"<b>{idx}.</b> {recomendacion}",
                self.styles['NormalC4A']
            ))
            elementos.append(Spacer(1, 0.1*inch))
    
    def generar_pdf_diagnostico(
        self,
        evaluacion: Evaluacion,
        cuestionario: Cuestionario,
        analisis: Dict[str, any],
        db
    ) -> bytes:
        """
        Generar PDF completo del diagnóstico.
        
        Returns:
            bytes: Contenido del PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        elementos = []
        
        # 1. Portada
        organizacion_nombre = evaluacion.organizacion.nombre if evaluacion.organizacion else "Organización"
        self._crear_portada(
            elementos,
            cuestionario,
            organizacion_nombre,
            evaluacion.fecha_completada or datetime.utcnow()
        )
        
        # 2. Instrucciones
        if cuestionario.configuracion_formato.get('incluir_instrucciones', True):
            self._crear_instrucciones(elementos, cuestionario)
        
        # 3. Resultados
        self._crear_resultados(elementos, analisis, cuestionario)
        
        # 4. Recomendaciones
        if analisis.get('recomendaciones'):
            self._crear_recomendaciones(elementos, analisis['recomendaciones'])
        
        # 5. Pie de página con metadata
        elementos.append(PageBreak())
        elementos.append(Spacer(1, 2*inch))
        elementos.append(Paragraph(
            f"<i>Documento generado el {datetime.utcnow().strftime('%d de %B de %Y a las %H:%M')} hrs</i>",
            self.styles['Normal']
        ))
        elementos.append(Paragraph(
            f"<i>C4A SaaS - Plataforma de Evaluación de Ciberseguridad</i>",
            self.styles['Normal']
        ))
        elementos.append(Paragraph(
            f"<i>Código de evaluación: {str(evaluacion.id)[:8]}</i>",
            self.styles['Normal']
        ))
        
        # Construir PDF
        doc.build(elementos)
        
        # Obtener bytes del buffer
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generar_pdf_basico(
        self,
        evaluacion: Evaluacion,
        cuestionario: Cuestionario,
        analisis: Dict[str, any],
        db
    ) -> bytes:
        """Generar PDF simplificado para diagnóstico básico"""
        # Por ahora, usar el mismo generador
        # En el futuro se puede personalizar para cada nivel
        return self.generar_pdf_diagnostico(evaluacion, cuestionario, analisis, db)
    
    def generar_pdf_intermedio(
        self,
        evaluacion: Evaluacion,
        cuestionario: Cuestionario,
        analisis: Dict[str, any],
        db
    ) -> bytes:
        """Generar PDF con gráficos para diagnóstico intermedio"""
        # Por ahora, usar el mismo generador
        # En el futuro se pueden agregar gráficos de barras por función NIST
        return self.generar_pdf_diagnostico(evaluacion, cuestionario, analisis, db)
    
    def generar_pdf_avanzado(
        self,
        evaluacion: Evaluacion,
        cuestionario: Cuestionario,
        analisis: Dict[str, any],
        db
    ) -> bytes:
        """Generar PDF completo con análisis detallado para diagnóstico avanzado"""
        # Por ahora, usar el mismo generador
        # En el futuro se pueden agregar análisis más profundos y visualizaciones
        return self.generar_pdf_diagnostico(evaluacion, cuestionario, analisis, db)

