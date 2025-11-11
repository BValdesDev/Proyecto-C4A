#!/usr/bin/env python3
"""
Servicio profesional para generación de PDFs con análisis detallado y recomendaciones
-- MODIFICADO para replicar la estructura del "Reporte resultado deseado.docx" --
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Rect, Group, String, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime
import io
import os
from typing import Dict, Any, List
import pytz

class PDFProfesionalService:
    """Servicio para generar PDFs profesionales con análisis y recomendaciones"""
    
    @staticmethod
    def _obtener_fecha_santiago() -> datetime:
        """
        Obtener fecha y hora actual en zona horaria de Santiago, Chile (America/Santiago).
        Convierte la hora UTC del servidor a la zona horaria de Chile.
        """
        try:
            # Obtener hora actual en UTC
            ahora_utc = datetime.now(pytz.UTC)
            # Convertir a zona horaria de Santiago, Chile (UTC-3 en invierno, UTC-4 en verano)
            zona_santiago = pytz.timezone('America/Santiago')
            ahora_santiago = ahora_utc.astimezone(zona_santiago)
            return ahora_santiago
        except Exception as e:
            print(f"Error al obtener fecha de Santiago: {str(e)}")
            # Fallback a hora local (puede no ser correcta si el servidor no está en Chile)
            return datetime.now()
    
    @staticmethod
    def _formatear_fecha_reporte(fecha: datetime) -> str:
        """Formatear fecha como DD/MM/AAAA HH:MM"""
        return fecha.strftime('%d/%m/%Y %H:%M')
    
    @staticmethod
    def _formatear_fecha_simple(fecha: datetime) -> str:
        """Formatear fecha como DD/MM/AAAA"""
        return fecha.strftime('%d/%m/%Y')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        
        # Título principal (como en la imagen) con interlineado 1.5
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            leading=42,  # Interlineado 1.5 (28 * 1.5 = 42)
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold'
        ))
        
        # Texto normal con interlineado 1.5
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leading=18,  # Interlineado 1.5 (12 * 1.5 = 18)
            alignment=TA_LEFT,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica'
        ))
        
        # Texto justificado con interlineado 1.5
        self.styles.add(ParagraphStyle(
            name='TextoJustificado',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leading=18,  # Interlineado 1.5 (12 * 1.5 = 18)
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica'
        ))
        
        # Título de sección (azul oscuro como en las imágenes) con interlineado 1.5
        self.styles.add(ParagraphStyle(
            name='TituloSeccion',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            leading=24,  # Interlineado 1.5 (16 * 1.5 = 24)
            alignment=TA_LEFT,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        ))
        
        # Título de subsección (verde como en las imágenes) con interlineado 1.5
        self.styles.add(ParagraphStyle(
            name='TituloSubseccion',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            leading=21,  # Interlineado 1.5 (14 * 1.5 = 21)
            alignment=TA_LEFT,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold'
        ))
        
        # Lista con viñetas con interlineado 1.5 - punto medio elegante
        self.styles.add(ParagraphStyle(
            name='ListaViñetas',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leading=16.5,  # Interlineado 1.5 (11 * 1.5 = 16.5)
            alignment=TA_LEFT,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            leftIndent=20,
            bulletIndent=10,
            bulletText='•',  # Punto medio elegante
            bulletFontName='Helvetica',
            bulletFontSize=11
        ))
        
        # Estilo destacado con interlineado 1.5
        self.styles.add(ParagraphStyle(
            name='DestacadoC4A',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=12,
            leading=21,  # Interlineado 1.5 (14 * 1.5 = 21)
            alignment=TA_LEFT,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para hallazgos (texto normal)
        self.styles.add(ParagraphStyle(
            name='Hallazgo',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=16.5,  # Interlineado 1.5
            alignment=TA_LEFT,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            leftIndent=20
        ))
        
        # Estilo para controles NIST (en negrita y color diferente)
        self.styles.add(ParagraphStyle(
            name='ControlNIST',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=16.5,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#059669'),  # Verde como títulos de subsección
            fontName='Helvetica-Bold',
            leftIndent=20
        ))

    def generar_informe_profesional(self, datos_evaluacion: Dict[str, Any], usuario: Dict[str, Any]) -> bytes:
        """Generar informe profesional completo"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.2*inch, bottomMargin=1*inch)
        
        story = []
        
        # Portada (REPORTE DE EVALUACIÓN DE CIBERSEGURIDAD)
        story.extend(self._crear_portada(datos_evaluacion, usuario))
        story.append(PageBreak())
        
        # Resumen ejecutivo (incluye MÉTRICAS PRINCIPALES)
        story.extend(self._crear_resumen_ejecutivo(datos_evaluacion))
        story.append(Spacer(1, 0.2*inch))

        # Nuevo: Información contextual del cliente (opcional)
        try:
            story.append(PageBreak())
            story.extend(self._crear_info_contextual(datos_evaluacion, usuario))
            story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            import traceback
            print(f"Advertencia: No se pudo generar información contextual: {str(e)}")
            print(traceback.format_exc())
            story.append(PageBreak())
        
        # Nuevo: Gráfico de barras de dominios (TEMPORALMENTE DESHABILITADO para evitar errores)
        # try:
        #     story.append(PageBreak())
        #     story.extend(self._crear_grafico_barras(datos_evaluacion))
        #     story.append(Spacer(1, 0.2*inch))
        # except Exception as e:
        #     # Si falla el gráfico, continuar sin él
        #     import traceback
        #     print(f"Advertencia: No se pudo generar el gráfico de barras: {str(e)}")
        #     print(traceback.format_exc())
        #     story.append(PageBreak())
        
        # Análisis por Categorías (sin PageBreak innecesario)
        story.extend(self._crear_analisis_categorias(datos_evaluacion))
        story.append(Spacer(1, 0.3*inch))
        
        # Hallazgos por dominio (opcional)
        try:
            story.extend(self._crear_hallazgos(datos_evaluacion))
            story.append(Spacer(1, 0.3*inch))
        except Exception as e:
            import traceback
            print(f"Advertencia: No se pudieron generar los hallazgos: {str(e)}")
            print(traceback.format_exc())
        
        # Recomendaciones (sin PageBreak innecesario)
        story.extend(self._crear_recomendaciones(datos_evaluacion))
        story.append(Spacer(1, 0.2*inch))
        
        # Plan de acción (incluye CRONOGRAMA, INVERSIÓN y ROI)
        story.extend(self._crear_plan_accion(datos_evaluacion))
        
        # Construir PDF con header en cada página
        doc.build(story, onFirstPage=self._draw_header, onLaterPages=self._draw_header)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _draw_header(self, canvas, doc):
        """
        Dibujar el logo de la empresa en la esquina superior izquierda de cada página.
        Usa canvas.drawImage() para agregar el logo en todas las páginas del PDF.
        """
        try:
            # Rutas posibles donde puede estar el logo
            logo_paths = [
                # Ruta absoluta desde Desktop
                os.path.join(os.path.expanduser('~'), 'Desktop', 'c4a 23-10', 'c4a github', 'Logo c4a.jpeg'),
                # Ruta relativa desde el directorio del proyecto
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'Logo c4a.jpeg'),
            ]
            
            logo_path = None
            for path in logo_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    logo_path = path
                    break
            
            if logo_path:
                # Posición y tamaño del logo (esquina superior izquierda)
                # A4: 595x842 points, coordenadas desde abajo izquierda
                x = 40  # 40 puntos desde la izquierda
                y = doc.pagesize[1] - 100  # 100 puntos desde arriba
                width = 60  # Ancho del logo
                height = 60  # Alto del logo
                
                # Dibujar el logo usando ImageReader
                try:
                    img = ImageReader(logo_path)
                    canvas.drawImage(img, x, y, width=width, height=height, preserveAspectRatio=True)
                except Exception:
                    # Si falla, intentar sin ImageReader
                    canvas.drawImage(logo_path, x, y, width=width, height=height, preserveAspectRatio=True)
        except Exception:
            # Si hay error, continuar sin logo (no interrumpir la generación del PDF)
            pass

    def _crear_portada(self, datos: Dict[str, Any], usuario: Dict[str, Any]) -> List:
        """Crear portada del informe con tabla de detalles como en las imágenes."""
        elements = []
        # Obtener fecha y hora en zona horaria de Santiago, Chile
        fecha_actual_santiago = self._obtener_fecha_santiago()
        fecha_evaluacion = datos.get('fecha_evaluacion', self._formatear_fecha_simple(fecha_actual_santiago))
        fecha_reporte = self._formatear_fecha_reporte(fecha_actual_santiago)
        nivel = datos.get('nivel', 'GRATUITO').upper()
        
        # Agregar logo C4A Cybersecurity For All (si existe)
        logo_paths = [
            'static/logo.png',
            'static/logo.jpg',
            'static/c4a_logo.png',
            'static/c4a_logo.jpg',
            'app/static/logo.png',
            'app/static/logo.jpg',
            'aplicaciones/backend/app/static/logo.png',
            'aplicaciones/backend/app/static/logo.jpg',
        ]
        
        logo_path = None
        for path in logo_paths:
            if os.path.exists(path):
                logo_path = path
                break
        
        if logo_path:
            try:
                logo_img = Image(logo_path, width=2*inch, height=0.8*inch)
                logo_img.hAlign = 'CENTER'
                elements.append(Spacer(1, 0.3*inch))
                elements.append(logo_img)
                elements.append(Spacer(1, 0.2*inch))
            except Exception as e:
                print(f"Advertencia: No se pudo cargar el logo: {str(e)}")
        else:
            # Si no hay logo, mostrar texto C4A como alternativa
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph(
                "<b><font size='18' color='#1e40af'>C4A</font> <font size='14'>Cybersecurity For All</font></b>",
                ParagraphStyle(
                    name='LogoText',
                    parent=self.styles['TextoNormal'],
                    alignment=TA_CENTER,
                    spaceAfter=12
                )
            ))
            elements.append(Spacer(1, 0.2*inch))
        
        # Título Portada (centrado y grande como en la imagen) - movido más arriba
        elements.append(Spacer(1, 0.4*inch))  # Reducido espacio después del logo
        elements.append(Paragraph("REPORTE DE EVALUACIÓN DE CIBERSEGURIDAD", self.styles['TituloPrincipal']))
        elements.append(Spacer(1, 0.6*inch))  # Reducido de 1.0 a 0.6
        
        # Información de la Evaluación en formato de tabla (como en imagen 2)
        datos_tabla = [
            ['Organización:', usuario.get('organizacion', 'Empresa Demo')],
            ['Evaluación:', f"{datos.get('cuestionario_nombre', 'Evaluación de Ciberseguridad')} - {fecha_evaluacion}"],
            ['Framework:', datos.get('framework', 'Cuestionario de Prueba (NIST CSF + COBIT 2019)')],
            ['Nivel:', nivel],
            ['Fecha de Evaluación:', fecha_evaluacion],
            ['Fecha de Reporte:', fecha_reporte]
        ]
        
        # Crear tabla con estilo exacto como en las imágenes - arreglado desbordamiento
        t = Table(datos_tabla, colWidths=[2.2*inch, 3.8*inch])  # Ajustado ancho de columnas
        t.setStyle(TableStyle([
            # Estilo de fuente
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),  # Reducido tamaño de fuente
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            
            # Padding ajustado para evitar desbordamiento
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Colores de fondo (gris claro para etiquetas, beige para valores)
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),  # Gris claro
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fef3c7')),  # Beige claro
            
            # Bordes punteados como en la imagen
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            
            # Texto en negro
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black)
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 1.2*inch))  # Reducido de 2.0 a 1.2
        
        # Información del Evaluador (opcional)
        elements.append(Paragraph(f"<b>Reporte generado por:</b> {usuario.get('nombre', 'C4A System')}", self.styles['TextoNormal']))

        return elements
    
    def _crear_resumen_ejecutivo(self, datos: Dict[str, Any]) -> List:
        """Crear resumen ejecutivo y métricas principales."""
        elements = []
        
        elements.append(Paragraph("RESUMEN EJECUTIVO", self.styles['TituloSeccion']))
        elements.append(Spacer(1, 0.2*inch))
        
        puntuacion = datos.get('puntuacion_global', 0)
        nivel_madurez = self._determinar_nivel_madurez(puntuacion)

        # Primer párrafo de contexto
        elements.append(Paragraph(
            f"Su organización ha alcanzado un nivel de madurez en ciberseguridad de <b>{nivel_madurez.upper()}</b> con una puntuación general de <b>{puntuacion:.1f}%</b>.", 
            self.styles['TextoJustificado']
        ))
        elements.append(Paragraph(
            "Este reporte proporciona un análisis detallado de su postura de seguridad, identificando fortalezas, áreas de mejora y recomendaciones específicas para fortalecer su programa de ciberseguridad.", 
            self.styles['TextoJustificado']
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Sección de Métricas Principales (verde como en la imagen)
        elements.append(Paragraph("MÉTRICAS PRINCIPALES", self.styles['TituloSubseccion']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Lógica para la tabla de Métricas Principales - FORZAR USO DE DATOS REALES
        total_preguntas = datos.get('total_preguntas', 0)
        preguntas_completadas = datos.get('preguntas_completadas', total_preguntas)
        
        # Obtener datos reales (prioridad: puntuacion_promedio > puntos_obtenidos > puntuacion_global)
        puntuacion_promedio = datos.get('puntuacion_promedio')
        puntos_obtenidos = datos.get('puntos_obtenidos')
        puntos_maximos = datos.get('puntos_maximos')
        puntuacion_global = datos.get('puntuacion_global', 0)
        
        # Calcular promedio según disponibilidad de datos (SIN valores por defecto)
        if puntuacion_promedio is not None:
            # Usar el promedio proporcionado (mejor opción - datos reales calculados)
            promedio = float(puntuacion_promedio)
        elif puntos_obtenidos is not None and preguntas_completadas > 0:
            # Calcular promedio desde puntos obtenidos: promedio = puntos_obtenidos / preguntas_completadas
            promedio = puntos_obtenidos / preguntas_completadas
        elif puntuacion_global > 0:
            # Calcular promedio desde puntuación global: promedio = (puntuacion_global / 100) * 5
            promedio = (puntuacion_global / 100) * 5
        else:
            # Si no hay datos, usar 0.0 (NO inventar datos)
            promedio = 0.0
        
        # Calcular puntos obtenidos si no está disponible
        if puntos_obtenidos is None:
            if promedio > 0 and preguntas_completadas > 0:
                puntos_obtenidos = promedio * preguntas_completadas
            else:
                puntos_obtenidos = 0.0
        
        # Calcular puntos máximos si no está disponible
        if puntos_maximos is None:
            puntos_maximos = preguntas_completadas * 5 if preguntas_completadas > 0 else 0.0
        
        # Asegurar que los valores sean float (no None)
        promedio = float(promedio) if promedio is not None else 0.0
        puntos_obtenidos = float(puntos_obtenidos) if puntos_obtenidos is not None else 0.0
        puntos_maximos = float(puntos_maximos) if puntos_maximos is not None else 0.0
        
        # Calcular porcentaje como (puntos_obtenidos / puntos_maximos) * 100
        porcentaje_calculado = (puntos_obtenidos / puntos_maximos * 100) if puntos_maximos > 0 else 0.0

        # Tabla simplificada y profesional con solo las métricas esenciales
        metricas_data = [
            ['Métrica', 'Valor'],
            ['Madurez (0-5)', f"{promedio:.1f}/5.0"],
            ['Porcentaje Logrado', f"{puntuacion:.1f}%"],
            ['Nivel de Madurez', nivel_madurez.upper()]
        ]
        
        # Tabla con estilo exacto como en la imagen 7
        metricas_table = Table(metricas_data, colWidths=[2.5*inch, 2.5*inch])
        metricas_table.setStyle(TableStyle([
            # Header con fondo azul oscuro y texto blanco
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Filas de datos con fondo azul claro
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            
            # Alineación
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
        ]))
        
        elements.append(metricas_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _crear_info_contextual(self, datos: Dict[str, Any], usuario: Dict[str, Any]) -> List:
        """Crear tabla con información contextual del cliente"""
        elements = []
        
        elements.append(Paragraph("INFORMACIÓN CONTEXTUAL DEL CLIENTE", self.styles['TituloSeccion']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Extraer información del cliente desde datos_evaluacion o usuario
        client_info = datos.get('client_info', {})
        
        # Si no hay client_info, intentar obtener de usuario/organizacion
        if not client_info:
            client_info = {
                'industria': datos.get('sector', usuario.get('sector', 'No especificado')),
                'tamaño': datos.get('tamaño', usuario.get('tamaño', 'No especificado')),
                'amenazas_comunes': datos.get('amenazas_comunes', self._obtener_amenazas_comunes_por_sector(
                    datos.get('sector', usuario.get('sector', 'general'))
                ))
            }
        
        # Crear tabla con información contextual
        info_data = [
            ['Campo', 'Valor'],
            ['Industria', client_info.get('industria', 'No especificado')],
            ['Tamaño', client_info.get('tamaño', 'No especificado')],
            ['Amenazas Comunes', client_info.get('amenazas_comunes', 'No especificado')]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            # Header con fondo azul oscuro y texto blanco
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Filas de datos con fondo azul claro
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#dbeafe')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            
            # Alineación
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black)
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _obtener_amenazas_comunes_por_sector(self, sector: str) -> str:
        """Obtener amenazas comunes según el sector"""
        amenazas_por_sector = {
            'financiero': 'Phishing, fraude en línea, robo de datos financieros, ataques a infraestructura crítica',
            'salud': 'Ransomware, filtración de datos de pacientes, violación de privacidad, interrupción de servicios',
            'retail': 'Robo de datos de tarjetas, ataques a puntos de venta, skimming, fraude de identidad',
            'gobierno': 'Ataques de estado, filtración de información confidencial, sabotaje, espionaje',
            'educacion': 'Robo de datos de estudiantes, interrupción de servicios educativos, phishing dirigido',
            'tecnologia': 'Robo de propiedad intelectual, ataques a servicios en la nube, compromiso de cadena de suministro',
            'manufactura': 'Sabotaje industrial, espionaje corporativo, interrupción de producción, ransomware',
            'servicios': 'Robo de datos de clientes, interrupción de servicios, phishing, fraude',
            'construccion': 'Robo de información de proyectos, interrupción de operaciones, fraude financiero',
            'mineria': 'Sabotaje de operaciones, robo de información estratégica, interrupción de producción',
            'general': 'Phishing, malware, ransomware, violación de datos, ataques de denegación de servicio'
        }
        
        sector_lower = sector.lower() if sector else 'general'
        return amenazas_por_sector.get(sector_lower, amenazas_por_sector['general'])
    
    def _crear_hallazgos(self, datos: Dict[str, Any]) -> List:
        """Crear lista de hallazgos por dominio con sus controles NIST asociados"""
        elements = []
        
        elements.append(Paragraph("HALLAZGOS POR DOMINIO", self.styles['TituloSeccion']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Obtener hallazgos desde datos_evaluacion
        hallazgos = datos.get('hallazgos', self._generar_hallazgos_desde_puntuaciones(datos))
        
        # Orden específico de dominios
        dominios_orden = ['Gobernanza', 'Proteger', 'Identificar', 'Responder', 'Detectar', 'Recuperar']
        
        for dominio in dominios_orden:
            if dominio in hallazgos:
                hallazgos_dominio = hallazgos[dominio]
                
                if hallazgos_dominio:
                    # Título del dominio en verde
                    elements.append(Paragraph(f"<b>{dominio.upper()}</b>", self.styles['TituloSubseccion']))
                    elements.append(Spacer(1, 0.1*inch))
                    
                    # Iterar sobre los hallazgos del dominio
                    for hallazgo in hallazgos_dominio:
                        # Crear Paragraph con el hallazgo y su control NIST
                        texto_hallazgo = hallazgo.get('hallazgo', '')
                        control_nist = hallazgo.get('control_nist', '')
                        
                        # Formato: Control NIST en negrita y color verde, seguido del hallazgo
                        texto_parrafo = f"<b><font color='#059669'>{control_nist}</font></b> - {texto_hallazgo}"
                        elements.append(Paragraph(texto_parrafo, self.styles['Hallazgo']))
                    
                    elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _generar_hallazgos_desde_puntuaciones(self, datos: Dict[str, Any]) -> Dict[str, List]:
        """Generar hallazgos basados en las puntuaciones de dominio"""
        puntuaciones_dominio = datos.get('puntuaciones_dominio', {})
        
        # Mapeo de dominios y sus controles NIST
        dominios_controles = {
            'Gobernanza': [
                ('ID.GV', 'Gobernanza de riesgos de ciberseguridad'),
                ('PR.GV', 'Políticas de protección'),
                ('DE.GV', 'Gobernanza de detección'),
                ('RS.GV', 'Gobernanza de respuesta'),
                ('RC.GV', 'Gobernanza de recuperación')
            ],
            'Proteger': [
                ('PR.AC', 'Control de acceso'),
                ('PR.AT', 'Concientización y capacitación'),
                ('PR.DS', 'Protección de datos'),
                ('PR.IP', 'Protección de información'),
                ('PR.MA', 'Mantenimiento'),
                ('PR.PT', 'Tecnologías de protección')
            ],
            'Identificar': [
                ('ID.AM', 'Gestión de activos'),
                ('ID.BE', 'Entorno de negocio'),
                ('ID.GV', 'Gobernanza'),
                ('ID.RA', 'Evaluación de riesgos'),
                ('ID.SC', 'Cadena de suministro')
            ],
            'Responder': [
                ('RS.RP', 'Planificación de respuesta'),
                ('RS.CO', 'Comunicación'),
                ('RS.AN', 'Análisis'),
                ('RS.MI', 'Mitigación'),
                ('RS.IM', 'Mejoras')
            ],
            'Detectar': [
                ('DE.AE', 'Eventos anómalos'),
                ('DE.CM', 'Monitoreo continuo'),
                ('DE.DP', 'Procesos de detección')
            ],
            'Recuperar': [
                ('RC.RP', 'Planificación de recuperación'),
                ('RC.IM', 'Mejoras'),
                ('RC.CO', 'Comunicación')
            ]
        }
        
        hallazgos = {}
        
        for dominio, controles in dominios_controles.items():
            hallazgos_dominio = []
            
            for control_nist, descripcion_control in controles:
                puntuacion = puntuaciones_dominio.get(control_nist, 0)
                
                # Generar hallazgo basado en la puntuación
                if puntuacion < 2.0:
                    # Hallazgo crítico
                    hallazgos_dominio.append({
                        'control_nist': control_nist,
                        'hallazgo': f'No existen políticas o procedimientos para {descripcion_control.lower()}'
                    })
                elif puntuacion < 3.5:
                    # Hallazgo importante
                    hallazgos_dominio.append({
                        'control_nist': control_nist,
                        'hallazgo': f'Las políticas de {descripcion_control.lower()} requieren mejoras significativas'
                    })
            
            if hallazgos_dominio:
                hallazgos[dominio] = hallazgos_dominio
        
        return hallazgos
    
    def _crear_grafico_barras(self, datos: Dict[str, Any]) -> List:
        """Crear gráfico de barras que muestre los 6 dominios del NIST CSF"""
        elements = []
        
        try:
            elements.append(Paragraph("VISUALIZACIÓN DE PUNTUACIONES POR DOMINIO", self.styles['TituloSeccion']))
            elements.append(Spacer(1, 0.2*inch))
            
            # Obtener análisis de categorías para las puntuaciones
            analisis_categorias = self._calcular_analisis_categorias(datos)
            
            # Orden específico de dominios: Identificar, Proteger, Detectar, Responder, Recuperar, Gobernar
            dominios_orden = ['Identificar', 'Proteger', 'Detectar', 'Responder', 'Recuperar', 'Gobernanza']
            nombres_cortos = {
                'Identificar': 'Identificar',
                'Proteger': 'Proteger',
                'Detectar': 'Detectar',
                'Responder': 'Responder',
                'Recuperar': 'Recuperar',
                'Gobernanza': 'Gobernar'
            }
            
            # Extraer puntuaciones en el orden correcto
            puntuaciones = []
            nombres = []
            for dominio in dominios_orden:
                if dominio in analisis_categorias:
                    info = analisis_categorias[dominio]
                    # Obtener promedio de la puntuación (formato "X.X/5.0")
                    puntuacion_str = info.get('puntuacion', '0.0/5.0')
                    try:
                        promedio = float(puntuacion_str.split('/')[0])
                    except:
                        promedio = 0.0
                    puntuaciones.append(promedio)
                    nombres.append(nombres_cortos.get(dominio, dominio))
            
            # Si no hay suficientes datos, completar con ceros (NO usar datos de ejemplo)
            # Esto asegura que solo se muestren datos reales
            if len(puntuaciones) < 6:
                # Completar con ceros para mantener la coherencia
                while len(puntuaciones) < 6:
                    puntuaciones.append(0.0)
                    nombres.append('N/A')
            
            # Asegurar que tenemos exactamente 6 valores
            while len(puntuaciones) < 6:
                puntuaciones.append(0.0)
                nombres.append('N/A')
            puntuaciones = puntuaciones[:6]
            nombres = nombres[:6]
            
            # Crear gráfico de barras usando reportlab.graphics
            drawing = Drawing(6*inch, 3*inch)
            
            # Crear gráfico de barras vertical
            chart = VerticalBarChart()
            chart.x = 0.5*inch
            chart.y = 0.5*inch
            chart.width = 5*inch
            chart.height = 2.5*inch
            
            # Configurar datos
            chart.data = [puntuaciones]
            
            # Configurar categorías (nombres de dominios)
            chart.categoryAxis.categoryNames = nombres
            
            # Configurar colores de las barras según semáforo
            # Calcular color promedio para usar un color único
            promedio_color = sum([1 if p < 1.6 else (2 if p < 3.5 else 3) for p in puntuaciones]) / len(puntuaciones) if puntuaciones else 2
            if promedio_color < 1.5:
                color_chart = colors.HexColor('#dc2626')  # Rojo
            elif promedio_color < 2.5:
                color_chart = colors.HexColor('#ea580c')  # Naranja
            else:
                color_chart = colors.HexColor('#16a34a')  # Verde
            
            # Configurar color de las barras - esperar a que se inicialicen
            # Las barras se crean automáticamente cuando se asigna data
            try:
                # Verificar que las barras existan
                if hasattr(chart, 'bars') and chart.bars and len(chart.bars) > 0:
                    chart.bars[0].fillColor = color_chart
                else:
                    # Si no hay barras aún, configurar después de agregar al drawing
                    pass
            except (AttributeError, IndexError) as e:
                # Si falla, el color se aplicará por defecto
                pass
            
            # Configurar rango del eje Y (0 a 5)
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = 5
            chart.valueAxis.valueStep = 1
            
            # Configurar etiquetas de valores en las barras
            if hasattr(chart, 'barLabels'):
                chart.barLabels.nudge = 10
                chart.barLabelFormat = '%.1f'
                chart.barLabels.fontName = 'Helvetica'
                chart.barLabels.fontSize = 9
            
            # Configurar estilo del eje
            if hasattr(chart.categoryAxis, 'labels'):
                chart.categoryAxis.labels.fontName = 'Helvetica'
                chart.categoryAxis.labels.fontSize = 9
            if hasattr(chart.valueAxis, 'labels'):
                chart.valueAxis.labels.fontName = 'Helvetica'
                chart.valueAxis.labels.fontSize = 9
            
            # Asegurar que el color se aplique después de agregar al drawing
            try:
                if hasattr(chart, 'bars') and chart.bars and len(chart.bars) > 0:
                    chart.bars[0].fillColor = color_chart
            except:
                pass
            
            drawing.add(chart)
            elements.append(drawing)
            
            # Leyenda de colores del semáforo
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(
                "<b>Leyenda:</b> <font color='#dc2626'>Rojo</font> (< 1.6) | <font color='#ea580c'>Naranja</font> (1.6 - 3.5) | <font color='#16a34a'>Verde</font> (> 3.5)",
                self.styles['TextoNormal']
            ))
            
        except Exception as e:
            # Si hay error al crear el gráfico, mostrar mensaje en lugar del gráfico
            import traceback
            print(f"Error al crear gráfico de barras: {str(e)}")
            print(traceback.format_exc())
            elements.append(Paragraph(
                f"<i>No se pudo generar el gráfico de barras. Los datos se muestran en la sección de análisis.</i>",
                self.styles['TextoNormal']
            ))
        
        return elements
    
    def _obtener_color_semaforo(self, puntuacion: float) -> str:
        """
        Obtener color según lógica de semáforo:
        - < 1.6: Rojo
        - 1.6 - 3.5: Naranja
        - > 3.5: Verde
        """
        if puntuacion < 1.6:
            return '#dc2626'  # Rojo
        elif 1.6 <= puntuacion <= 3.5:
            return '#ea580c'  # Naranja
        else:  # puntuacion > 3.5
            return '#16a34a'  # Verde
    
    def _obtener_color_semaforo_hexcolor(self, puntuacion: float):
        """Obtener color como HexColor para usar en gráficos"""
        if puntuacion < 1.6:
            return colors.HexColor('#dc2626')  # Rojo
        elif 1.6 <= puntuacion <= 3.5:
            return colors.HexColor('#ea580c')  # Naranja
        else:  # puntuacion > 3.5
            return colors.HexColor('#16a34a')  # Verde
    
    def _crear_grafico_barras_dominios(self, analisis_categorias: Dict[str, Any], dominios_orden: List[str]) -> List:
        """Crear gráfico de barras horizontal con colores de semáforo por dominio"""
        elements = []
        
        try:
            elements.append(Paragraph("VISUALIZACIÓN DE PUNTUACIONES POR DOMINIO", self.styles['TituloSubseccion']))
            elements.append(Spacer(1, 0.15*inch))
            
            # Extraer datos de puntuaciones
            puntuaciones = []
            nombres = []
            nombres_completos = []
            colores_barras = []
            
            # Mapeo de nombres cortos para el gráfico
            nombres_cortos = {
                'Gobernanza': 'Gobern.',
                'Proteger': 'Proteger',
                'Identificar': 'Identif.',
                'Responder': 'Responder',
                'Detectar': 'Detectar',
                'Recuperar': 'Recuperar'
            }
            
            for dominio in dominios_orden:
                if dominio in analisis_categorias:
                    info = analisis_categorias[dominio]
                    puntuacion_str = info.get('puntuacion', '0.0/5.0')
                    try:
                        if '/' in puntuacion_str:
                            puntuacion_valor = float(puntuacion_str.split('/')[0])
                        else:
                            puntuacion_valor = float(puntuacion_str)
                    except (ValueError, AttributeError):
                        puntuacion_valor = 0.0
                    
                    puntuaciones.append(puntuacion_valor)
                    nombres.append(nombres_cortos.get(dominio, dominio[:8]))
                    nombres_completos.append(dominio)
                    colores_barras.append(self._obtener_color_semaforo_hexcolor(puntuacion_valor))
                else:
                    # Si el dominio no está en analisis_categorias, agregar con valor 0
                    puntuaciones.append(0.0)
                    nombres.append(nombres_cortos.get(dominio, dominio[:8]))
                    nombres_completos.append(dominio)
                    colores_barras.append(colors.HexColor('#9ca3af'))  # Gris para datos faltantes
            
            # Si no hay datos suficientes, usar valores por defecto (0.0) pero NO datos de ejemplo
            # Esto asegura que el gráfico muestre los datos reales o cero, nunca valores falsos
            if not puntuaciones:
                print("Advertencia: No se encontraron puntuaciones para el gráfico")
                # Usar ceros en lugar de datos de ejemplo para que sea evidente que faltan datos
                puntuaciones = [0.0] * 6
                nombres = ['Gobern.', 'Proteger', 'Identif.', 'Responder', 'Detectar', 'Recuperar']
                colores_barras = [colors.HexColor('#9ca3af')] * 6  # Gris para datos faltantes
            
            # Asegurar que tenemos exactamente 6 valores
            while len(puntuaciones) < 6:
                puntuaciones.append(0.0)
                nombres.append('N/A')
                colores_barras.append(colors.HexColor('#9ca3af'))  # Gris para N/A
            puntuaciones = puntuaciones[:6]
            nombres = nombres[:6]
            colores_barras = colores_barras[:6]
            
            # Debug: Imprimir datos que se usarán en el gráfico
            print(f"Puntuaciones para gráfico: {puntuaciones}")
            print(f"Nombres de dominios: {nombres}")
            
            # Crear gráfico de barras personalizado con colores individuales
            # Usar formas básicas para tener control total sobre los colores
            # Aumentar tamaño del gráfico para mejor visualización
            drawing = Drawing(7*inch, 4.5*inch)
            
            # Dimensiones del gráfico (más grandes y centradas)
            chart_x = 1.0*inch
            chart_y = 0.5*inch
            chart_width = 5.5*inch
            chart_height = 3.2*inch
            max_value = 5.0
            
            # Calcular ancho de barras y espaciado
            num_barras = len(puntuaciones)
            total_spacing = 0.3*inch * (num_barras - 1)  # Espaciado entre barras
            bar_width = (chart_width - total_spacing) / num_barras
            
            # Crear barras individuales con colores de semáforo
            for i, (puntuacion, nombre, color) in enumerate(zip(puntuaciones, nombres, colores_barras)):
                # Calcular posición y altura de la barra
                bar_x = chart_x + i * (bar_width + 0.3*inch)
                bar_height = max((puntuacion / max_value) * chart_height, 0.05*inch)  # Altura mínima visible
                bar_y = chart_y
                
                # Crear barra con color individual según semáforo
                barra = Rect(
                    bar_x, bar_y,
                    bar_width, bar_height,
                    fillColor=color,
                    strokeColor=colors.black,
                    strokeWidth=1
                )
                drawing.add(barra)
                
                # Agregar etiqueta de valor en la parte superior de la barra
                if bar_height > 0.05*inch:
                    label_y = bar_y + bar_height + 0.08*inch
                    label = String(
                        bar_x + bar_width / 2, label_y,
                        f'{puntuacion:.1f}',
                        textAnchor='middle',
                        fontSize=10,
                        fillColor=color,
                        fontName='Helvetica-Bold'
                    )
                    drawing.add(label)
                
                # Agregar nombre del dominio rotado en la parte inferior
                nombre_label = String(
                    bar_x + bar_width / 2, chart_y - 0.25*inch,
                    nombre,
                    textAnchor='middle',
                    fontSize=9,
                    fillColor=colors.black,
                    fontName='Helvetica'
                )
                drawing.add(nombre_label)
            
            # Agregar línea base (eje X) más gruesa
            base_line = Rect(
                chart_x - 0.05*inch, chart_y - 0.02*inch,
                chart_width + 0.1*inch, 0.03*inch,
                fillColor=colors.black,
                strokeColor=colors.black
            )
            drawing.add(base_line)
            
            # Agregar etiquetas del eje Y con mejor formato
            for y_value in range(0, 6):
                y_pos = chart_y + (y_value / max_value) * chart_height
                y_label = String(
                    chart_x - 0.2*inch, y_pos,
                    str(y_value),
                    textAnchor='end',
                    fontSize=9,
                    fillColor=colors.black,
                    fontName='Helvetica-Bold'
                )
                drawing.add(y_label)
                
                # Agregar línea de cuadrícula horizontal más sutil
                if y_value > 0:
                    grid_line = Line(
                        chart_x, y_pos,
                        chart_x + chart_width, y_pos,
                        strokeColor=colors.HexColor('#e5e7eb'),
                        strokeWidth=0.5
                    )
                    drawing.add(grid_line)
            
            # Agregar gráfico al documento
            elements.append(drawing)
            elements.append(Spacer(1, 0.2*inch))
            
            # Crear leyenda tipo semáforo con rectángulos de color reales
            # Usar una tabla con celdas que contengan rectángulos de color
            # Crear tabla de leyenda con colores reales (sin HTML)
            leyenda_cells = []
            
            # Encabezado
            leyenda_cells.append([
                Paragraph("<b>Color</b>", self.styles['TextoNormal']),
                Paragraph("<b>Rango</b>", self.styles['TextoNormal']),
                Paragraph("<b>Interpretación</b>", self.styles['TextoNormal'])
            ])
            
            # Fila Rojo - Crítico
            color_rojo_drawing = Drawing(0.3*inch, 0.15*inch)
            rect_rojo = Rect(0, 0, 0.3*inch, 0.15*inch, 
                           fillColor=colors.HexColor('#dc2626'),
                           strokeColor=colors.black,
                           strokeWidth=0.5)
            color_rojo_drawing.add(rect_rojo)
            leyenda_cells.append([
                color_rojo_drawing,
                Paragraph("< 1.6", self.styles['TextoNormal']),
                Paragraph("Crítico - Requiere atención inmediata", self.styles['TextoNormal'])
            ])
            
            # Fila Naranja - Importante
            color_naranja_drawing = Drawing(0.3*inch, 0.15*inch)
            rect_naranja = Rect(0, 0, 0.3*inch, 0.15*inch,
                              fillColor=colors.HexColor('#ea580c'),
                              strokeColor=colors.black,
                              strokeWidth=0.5)
            color_naranja_drawing.add(rect_naranja)
            leyenda_cells.append([
                color_naranja_drawing,
                Paragraph("1.6 - 3.5", self.styles['TextoNormal']),
                Paragraph("Importante - Necesita mejoras", self.styles['TextoNormal'])
            ])
            
            # Fila Verde - Adecuado
            color_verde_drawing = Drawing(0.3*inch, 0.15*inch)
            rect_verde = Rect(0, 0, 0.3*inch, 0.15*inch,
                            fillColor=colors.HexColor('#16a34a'),
                            strokeColor=colors.black,
                            strokeWidth=0.5)
            color_verde_drawing.add(rect_verde)
            leyenda_cells.append([
                color_verde_drawing,
                Paragraph("> 3.5", self.styles['TextoNormal']),
                Paragraph("Adecuado - Buen nivel de madurez", self.styles['TextoNormal'])
            ])
            
            leyenda_table = Table(leyenda_cells, colWidths=[0.8*inch, 1.2*inch, 4*inch])
            leyenda_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centrar columna de color
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ]))
            
            elements.append(leyenda_table)
            
        except Exception as e:
            import traceback
            print(f"Error al crear gráfico de barras por dominio: {str(e)}")
            print(traceback.format_exc())
            # Si falla, crear una tabla visual simple con barras de colores
            elements.append(Paragraph(
                "<i>Visualización de puntuaciones por dominio:</i>",
                self.styles['TextoNormal']
            ))
            elements.append(Spacer(1, 0.1*inch))
            
            # Crear tabla visual con barras de progreso de colores
            tabla_visual = []
            tabla_visual.append(['Dominio', 'Puntuación', 'Estado'])
            
            for dominio in dominios_orden:
                if dominio in analisis_categorias:
                    info = analisis_categorias[dominio]
                    puntuacion_str = info.get('puntuacion', '0.0/5.0')
                    try:
                        if '/' in puntuacion_str:
                            puntuacion_valor = float(puntuacion_str.split('/')[0])
                        else:
                            puntuacion_valor = float(puntuacion_str)
                    except:
                        puntuacion_valor = 0.0
                    
                    color = self._obtener_color_semaforo(puntuacion_valor)
                    if puntuacion_valor < 1.6:
                        estado = '● Crítico'
                    elif puntuacion_valor <= 3.5:
                        estado = '● Importante'
                    else:
                        estado = '● Adecuado'
                    
                    tabla_visual.append([
                        dominio,
                        f"<font color='{color}'>{puntuacion_str}</font>",
                        f"<font color='{color}'>{estado}</font>"
                    ])
            
            if len(tabla_visual) > 1:
                visual_table = Table(tabla_visual, colWidths=[2*inch, 1.5*inch, 2.5*inch])
                visual_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ]))
                elements.append(visual_table)
        
        return elements

    def _crear_analisis_categorias(self, datos: Dict[str, Any]) -> List:
        """Crea la sección de Análisis por Categorías (Dominios NIST) como en las imágenes."""
        elements = []
        
        elements.append(Paragraph("ANÁLISIS POR CATEGORÍAS", self.styles['TituloSeccion']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Obtener análisis de categorías basado en las respuestas reales
        analisis_categorias = self._calcular_analisis_categorias(datos)
        
        # Orden específico de dominios como en las imágenes
        dominios_orden = ['Gobernanza', 'Proteger', 'Identificar', 'Responder', 'Detectar', 'Recuperar']
        
        # Crear gráfico de barras con colores de semáforo para los dominios
        try:
            elements.extend(self._crear_grafico_barras_dominios(analisis_categorias, dominios_orden))
            elements.append(Spacer(1, 0.3*inch))
        except Exception as e:
            import traceback
            print(f"Advertencia: No se pudo generar el gráfico de barras por dominio: {str(e)}")
            print(traceback.format_exc())
        
        for categoria in dominios_orden:
            if categoria in analisis_categorias:
                info = analisis_categorias[categoria]
                
                # Título en verde como en las imágenes
                elements.append(Paragraph(f"<b>{categoria.upper()}</b>", self.styles['TituloSubseccion']))
                elements.append(Spacer(1, 0.1*inch))
                
                puntuacion_str = info.get('puntuacion', 'N/A')
                porcentaje = info.get('porcentaje', 0.0)
                porcentaje_str = f"{porcentaje:.1f}%"
                fortalezas = info.get('fortalezas', 0)
                debilidades = info.get('debilidades', 0)
                
                # Extraer valor numérico de la puntuación para aplicar semáforo
                try:
                    # Intentar extraer el valor numérico de la puntuación (formato "X.X/5.0")
                    if '/' in puntuacion_str:
                        puntuacion_valor = float(puntuacion_str.split('/')[0])
                    else:
                        puntuacion_valor = float(puntuacion_str)
                except (ValueError, AttributeError):
                    puntuacion_valor = 0.0
                
                # Aplicar lógica de semáforo para el color de la puntuación
                # < 1.6 = Rojo, 1.6 - 3.5 = Naranja, > 3.5 = Verde
                color_puntuacion = self._obtener_color_semaforo(puntuacion_valor)
                
                # Formato con desglose: Puntuación Obtenida: X/Y (Z%) con color según semáforo
                # El texto de la puntuación debe tener el color aplicado según la lógica del semáforo
                # Usar formato HTML con color hexadecimal para ReportLab (usar comillas simples para consistencia)
                detalle = f"Puntuación Obtenida: <b><font color='{color_puntuacion}'>{puntuacion_str} ({porcentaje_str})</font></b> Fortalezas: <b>{fortalezas}</b> áreas bien implementadas Debilidades: <b>{debilidades}</b> áreas que requieren atención"
                elements.append(Paragraph(detalle, self.styles['TextoNormal']))
                elements.append(Spacer(1, 0.2*inch))
            
        return elements

    def _crear_recomendaciones(self, datos: Dict[str, Any]) -> List:
        """Crea la sección de Recomendaciones Prioritarias, ajustando el formato de totales."""
        elements = []
        
        elements.append(Paragraph("RECOMENDACIONES PRIORITARIAS", self.styles['TituloSeccion']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Calcular recomendaciones basadas en las respuestas reales
        recomendaciones = self._calcular_recomendaciones(datos)
        
        # Totales
        totales = recomendaciones.get('totales', {'total': 0, 'criticas': 0, 'importantes': 0, 'mejoras': 0})
        
        # Total de Recomendaciones: 0 Críticas: 0 Importantes: 0 Mejoras: 0
        totales_str = f"<b>Total de Recomendaciones:</b> {totales['total']} &nbsp;&nbsp; <b>Críticas:</b> {totales['criticas']} &nbsp;&nbsp; <b>Importantes:</b> {totales['importantes']} &nbsp;&nbsp; <b>Mejoras:</b> {totales['mejoras']}"
        elements.append(Paragraph(totales_str, self.styles['TextoNormal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Listar recomendaciones específicas
        for categoria, recs in recomendaciones.get('detalladas', {}).items():
            if recs:
                elements.append(Paragraph(f"<b>{categoria.upper()}</b>", self.styles['TextoNormal']))
                for rec in recs:
                    elements.append(Paragraph(f"{rec}", self.styles['ListaViñetas']))
                elements.append(Spacer(1, 0.1*inch))
        
        return elements

    def _crear_plan_accion(self, datos: Dict[str, Any]) -> List:
        """Crear plan de acción con texto y viñetas como en las imágenes."""
        elements = []
        
        elements.append(Paragraph("PLAN DE ACCIÓN", self.styles['TituloSeccion']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 1. CRONOGRAMA DE IMPLEMENTACIÓN (verde como en las imágenes)
        elements.append(Paragraph("CRONOGRAMA DE IMPLEMENTACIÓN", self.styles['TituloSubseccion']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Fase 1 - Crítico (0-3 meses) - texto con viñetas como en la imagen
        elements.append(Paragraph("<b>Fase 1 - Crítico (0-3 meses)</b>", self.styles['TextoNormal']))
        elements.append(Paragraph("Implementar controles críticos para reducir riesgos inmediatos", self.styles['ListaViñetas']))
        elements.append(Paragraph("<b>Inversión:</b> Alta prioridad, bajo costo inicial", self.styles['ListaViñetas']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Fase 2 - Importante (3-6 meses)
        elements.append(Paragraph("<b>Fase 2 - Importante (3-6 meses)</b>", self.styles['TextoNormal']))
        elements.append(Paragraph("Desarrollar capacidades de seguridad fundamentales", self.styles['ListaViñetas']))
        elements.append(Paragraph("<b>Inversión:</b> Inversión media, beneficios significativos", self.styles['ListaViñetas']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Fase 3 - Optimización (6-12 meses)
        elements.append(Paragraph("<b>Fase 3 - Optimización (6-12 meses)</b>", self.styles['TextoNormal']))
        elements.append(Paragraph("Mejorar y optimizar controles existentes", self.styles['ListaViñetas']))
        elements.append(Paragraph("<b>Inversión:</b> Inversión baja, optimización continua", self.styles['ListaViñetas']))
        elements.append(Spacer(1, 0.3*inch))
        
        # 2. INVERSIÓN ESTIMADA (verde como en las imágenes)
        elements.append(Paragraph("INVERSIÓN ESTIMADA", self.styles['TituloSubseccion']))
        inversion = self._calcular_inversion(datos)
        elements.append(Paragraph(
            f"<b>Inversión Total:</b> ${inversion['total_clp']:,} CLP (${inversion['total_usd']:,} USD) &nbsp;&nbsp; <b>Período:</b> {inversion['periodo']} meses", 
            self.styles['TextoNormal']
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # 3. ROI PROYECTADO (verde como en las imágenes)
        elements.append(Paragraph("ROI PROYECTADO", self.styles['TituloSubseccion']))
        roi = self._calcular_roi(datos)
        
        roi_str = (
            f"<b>Reducción de Riesgo:</b> {roi['reduccion_riesgo']}% &nbsp;&nbsp; "
            f"<b>Beneficio Anual Proyectado:</b> ${roi['beneficio_anual']:,} CLP &nbsp;&nbsp; "
            f"<b>ROI:</b> {roi['roi_porcentaje']:.1f}% &nbsp;&nbsp; "
            f"<b>Período de Recuperación:</b> {roi['recuperacion_meses']:.1f} meses"
        )
        elements.append(Paragraph(roi_str, self.styles['TextoNormal']))
        
        return elements

    def _calcular_analisis_categorias(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular análisis de categorías basado en las respuestas reales"""
        puntuaciones_dominio = datos.get('puntuaciones_dominio', {})
        
        # Obtener puntuación promedio global para usar como fallback
        puntuacion_promedio = datos.get('puntuacion_promedio')
        if puntuacion_promedio is None:
            # Calcular desde puntos obtenidos si está disponible
            puntos_obtenidos = datos.get('puntos_obtenidos')
            puntos_maximos = datos.get('puntos_maximos')
            preguntas_completadas = datos.get('preguntas_completadas', datos.get('total_preguntas', 1))
            
            if puntos_obtenidos is not None and preguntas_completadas > 0:
                puntuacion_promedio = puntos_obtenidos / preguntas_completadas
            else:
                # Usar puntuación global convertida a escala 0-5
                puntuacion_global = datos.get('puntuacion_global', 0)
                puntuacion_promedio = (puntuacion_global / 100) * 5 if puntuacion_global > 0 else 0.0
        else:
            puntuacion_promedio = float(puntuacion_promedio)
        
        # Mapeo de dominios NIST CSF
        dominios_nist = {
            'Gobernanza': ['ID.GV', 'PR.GV', 'DE.GV', 'RS.GV', 'RC.GV'],
            'Proteger': ['PR.AC', 'PR.AT', 'PR.DS', 'PR.IP', 'PR.MA', 'PR.PT'],
            'Identificar': ['ID.AM', 'ID.BE', 'ID.GV', 'ID.RA', 'ID.SC'],
            'Responder': ['RS.RP', 'RS.CO', 'RS.AN', 'RS.MI', 'RS.IM'],
            'Detectar': ['DE.AE', 'DE.CM', 'DE.DP'],
            'Recuperar': ['RC.RP', 'RC.IM', 'RC.CO']
        }
        
        # Mapeo alternativo: nombres de dominios directamente
        dominios_alternativos = {
            'Gobernanza': ['gobernanza', 'governance', 'Gobernanza'],
            'Proteger': ['proteger', 'protect', 'Proteger'],
            'Identificar': ['identificar', 'identify', 'Identificar'],
            'Responder': ['responder', 'respond', 'Responder'],
            'Detectar': ['detectar', 'detect', 'Detectar'],
            'Recuperar': ['recuperar', 'recover', 'Recuperar']
        }
        
        analisis = {}
        for dominio, funciones in dominios_nist.items():
            puntuacion_total = 0
            total_funciones = len(funciones)
            funciones_con_datos = 0
            
            # Intentar obtener puntuaciones desde funciones NIST
            for funcion in funciones:
                puntuacion = puntuaciones_dominio.get(funcion, 0)
                if puntuacion > 0:
                    puntuacion_total += puntuacion
                    funciones_con_datos += 1
            
            # Si no hay datos en funciones NIST, intentar buscar por nombre de dominio
            if funciones_con_datos == 0:
                for nombre_alt in dominios_alternativos.get(dominio, []):
                    if nombre_alt in puntuaciones_dominio:
                        puntuacion_dominio = puntuaciones_dominio[nombre_alt]
                        # Si viene en escala 0-100, convertir a 0-5
                        if puntuacion_dominio > 5:
                            puntuacion_dominio = (puntuacion_dominio / 100) * 5
                        puntuacion_total = puntuacion_dominio * total_funciones
                        funciones_con_datos = total_funciones
                        break
            
            # Si aún no hay datos, usar la puntuación promedio global
            if funciones_con_datos == 0:
                promedio = puntuacion_promedio
                print(f"Advertencia: No se encontraron datos para {dominio}, usando puntuación promedio global: {promedio:.1f}")
            else:
                promedio = puntuacion_total / total_funciones if total_funciones > 0 else puntuacion_promedio
            
            porcentaje = (promedio / 5.0) * 100  # Asumiendo escala de 0-5
            
            # Determinar fortalezas y debilidades
            if funciones_con_datos > 0:
                fortalezas = sum(1 for f in funciones if puntuaciones_dominio.get(f, 0) >= 4)
                debilidades = sum(1 for f in funciones if puntuaciones_dominio.get(f, 0) < 3)
            else:
                # Si no hay datos detallados, estimar desde el promedio
                fortalezas = 0 if promedio < 4 else len(funciones)
                debilidades = len(funciones) if promedio < 3 else 0
            
            analisis[dominio] = {
                'puntuacion': f"{promedio:.1f}/5.0",
                'porcentaje': porcentaje,
                'fortalezas': fortalezas,
                'debilidades': debilidades
            }
        
        return analisis

    def _calcular_recomendaciones(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular recomendaciones basadas en las respuestas reales"""
        puntuaciones_dominio = datos.get('puntuaciones_dominio', {})
        recomendaciones_detalladas = {}
        totales = {'total': 0, 'criticas': 0, 'importantes': 0, 'mejoras': 0}
        
        # Mapeo de dominios y sus recomendaciones
        dominios_recomendaciones = {
            'Gobernanza': {
                'criticas': [
                    'Implementar políticas de seguridad de la información',
                    'Establecer comité de seguridad ejecutivo'
                ],
                'importantes': [
                    'Desarrollar programa de concientización',
                    'Crear procedimientos de gestión de riesgos'
                ],
                'mejoras': [
                    'Optimizar procesos de gobernanza',
                    'Mejorar comunicación de políticas'
                ]
            },
            'Proteger': {
                'criticas': [
                    'Implementar controles de acceso robustos',
                    'Desplegar soluciones de protección de endpoints'
                ],
                'importantes': [
                    'Configurar firewalls y segmentación de red',
                    'Implementar cifrado de datos'
                ],
                'mejoras': [
                    'Optimizar controles de protección',
                    'Mejorar gestión de parches'
                ]
            },
            'Identificar': {
                'criticas': [
                    'Realizar inventario completo de activos',
                    'Implementar gestión de vulnerabilidades'
                ],
                'importantes': [
                    'Desarrollar análisis de riesgos',
                    'Establecer monitoreo de activos'
                ],
                'mejoras': [
                    'Optimizar procesos de identificación',
                    'Mejorar clasificación de activos'
                ]
            },
            'Responder': {
                'criticas': [
                    'Desarrollar plan de respuesta a incidentes',
                    'Establecer equipo de respuesta'
                ],
                'importantes': [
                    'Implementar procedimientos de comunicación',
                    'Crear capacidades de análisis forense'
                ],
                'mejoras': [
                    'Optimizar procesos de respuesta',
                    'Mejorar coordinación entre equipos'
                ]
            },
            'Detectar': {
                'criticas': [
                    'Implementar sistema de monitoreo continuo',
                    'Desplegar herramientas de detección'
                ],
                'importantes': [
                    'Configurar alertas y notificaciones',
                    'Establecer análisis de eventos'
                ],
                'mejoras': [
                    'Optimizar capacidades de detección',
                    'Mejorar correlación de eventos'
                ]
            },
            'Recuperar': {
                'criticas': [
                    'Desarrollar plan de recuperación ante desastres',
                    'Implementar estrategias de respaldo'
                ],
                'importantes': [
                    'Establecer procedimientos de recuperación',
                    'Crear capacidades de restauración'
                ],
                'mejoras': [
                    'Optimizar procesos de recuperación',
                    'Mejorar tiempos de restauración'
                ]
            }
        }
        
        for dominio, recs in dominios_recomendaciones.items():
            puntuacion_promedio = self._calcular_puntuacion_promedio_dominio(dominio, puntuaciones_dominio)
            recomendaciones_dominio = []
            
            if puntuacion_promedio < 2.0:  # Crítico
                recomendaciones_dominio.extend(recs['criticas'])
                totales['criticas'] += len(recs['criticas'])
            elif puntuacion_promedio < 3.5:  # Importante
                recomendaciones_dominio.extend(recs['importantes'])
                totales['importantes'] += len(recs['importantes'])
            else:  # Mejoras
                recomendaciones_dominio.extend(recs['mejoras'])
                totales['mejoras'] += len(recs['mejoras'])
            
            if recomendaciones_dominio:
                recomendaciones_detalladas[dominio] = recomendaciones_dominio
                totales['total'] += len(recomendaciones_dominio)
        
        return {
            'totales': totales,
            'detalladas': recomendaciones_detalladas
        }

    def _calcular_puntuacion_promedio_dominio(self, dominio: str, puntuaciones_dominio: Dict[str, float]) -> float:
        """Calcular puntuación promedio de un dominio"""
        dominios_funciones = {
            'Gobernanza': ['ID.GV', 'PR.GV', 'DE.GV', 'RS.GV', 'RC.GV'],
            'Proteger': ['PR.AC', 'PR.AT', 'PR.DS', 'PR.IP', 'PR.MA', 'PR.PT'],
            'Identificar': ['ID.AM', 'ID.BE', 'ID.GV', 'ID.RA', 'ID.SC'],
            'Responder': ['RS.RP', 'RS.CO', 'RS.AN', 'RS.MI', 'RS.IM'],
            'Detectar': ['DE.AE', 'DE.CM', 'DE.DP'],
            'Recuperar': ['RC.RP', 'RC.IM', 'RC.CO']
        }
        
        funciones = dominios_funciones.get(dominio, [])
        if not funciones:
            return 0.0
        
        puntuacion_total = sum(puntuaciones_dominio.get(f, 0) for f in funciones)
        return puntuacion_total / len(funciones)

    def _calcular_inversion(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular inversión estimada basada en las respuestas"""
        puntuacion_global = datos.get('puntuacion_global', 0)
        
        # Calcular inversión basada en el nivel de madurez
        if puntuacion_global < 30:
            # Nivel inicial - alta inversión
            total_clp = 5000000
            total_usd = 5000
        elif puntuacion_global < 60:
            # Nivel intermedio - inversión media
            total_clp = 3000000
            total_usd = 3000
        else:
            # Nivel avanzado - inversión baja
            total_clp = 1500000
            total_usd = 1500
        
        return {
            'total_clp': total_clp,
            'total_usd': total_usd,
            'periodo': 12
        }

    def _calcular_roi(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Calcular ROI proyectado basado en las respuestas"""
        puntuacion_global = datos.get('puntuacion_global', 0)
        inversion = self._calcular_inversion(datos)
        
        # Calcular ROI basado en el nivel de madurez
        if puntuacion_global < 30:
            reduccion_riesgo = 40
            beneficio_anual = inversion['total_clp'] * 2.5
            roi_porcentaje = 150
            recuperacion_meses = 8
        elif puntuacion_global < 60:
            reduccion_riesgo = 25
            beneficio_anual = inversion['total_clp'] * 1.8
            roi_porcentaje = 80
            recuperacion_meses = 12
        else:
            reduccion_riesgo = 15
            beneficio_anual = inversion['total_clp'] * 1.2
            roi_porcentaje = 20
            recuperacion_meses = 18
        
        return {
            'reduccion_riesgo': reduccion_riesgo,
            'beneficio_anual': beneficio_anual,
            'roi_porcentaje': roi_porcentaje,
            'recuperacion_meses': recuperacion_meses
        }

    def _determinar_nivel_madurez(self, puntuacion: float) -> str:
        """Determinar nivel de madurez basado en la puntuación"""
        if puntuacion < 20:
            return "Inicial"
        elif puntuacion < 40:
            return "Básico"
        elif puntuacion < 60:
            return "Intermedio"
        elif puntuacion < 80:
            return "Avanzado"
        else:
            return "Optimizado"

    def _determinar_estado_nist(self, puntuacion: float) -> str:
        """Determinar estado de una función NIST CSF"""
        if puntuacion < 20:
            return "No implementado"
        elif puntuacion < 40:
            return "Parcial"
        elif puntuacion < 60:
            return "En desarrollo"
        elif puntuacion < 80:
            return "Implementado"
        else:
            return "Optimizado"

    def _obtener_descripcion_nivel_nist_cobit(self, nivel: str, puntuacion: float) -> str:
        """Obtener descripción del nivel basada en NIST CSF y COBIT 2019"""
        return ""

    def _obtener_recomendaciones_nist_cobit(self, funcion: str) -> List[str]:
        """Obtener recomendaciones específicas por función NIST CSF"""
        return ["Placeholder de recomendación específica"]