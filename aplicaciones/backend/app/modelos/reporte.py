# app/modelos/reporte.py
"""
Modelo de Reporte para C4A SaaS
Reportes de evaluación con soporte para niveles
"""

from sqlalchemy import Column, String, Enum, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import ModeloConEliminacionLogica
from ..core.config import NivelSuscripcion


class Reporte(ModeloConEliminacionLogica):
    """Modelo de reporte de evaluación"""
    __tablename__ = "reportes"
    
    # Relaciones
    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id"), nullable=False)
    organizacion_id = Column(UUID(as_uuid=True), ForeignKey("organizaciones.id"), nullable=False)
    generado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Configuración
    tipo_reporte = Column(String(50), nullable=False)  # "completo", "ejecutivo", "técnico"
    nivel_generado = Column(Enum(NivelSuscripcion), nullable=False)
    titulo = Column(String(255), nullable=False)
    
    # Contenido
    puntuacion_global = Column(Numeric(5, 2), nullable=False)
    fortalezas = Column(JSONB, nullable=True)
    debilidades = Column(JSONB, nullable=True)
    recomendaciones = Column(JSONB, nullable=True)
    
    # Archivos
    url_pdf = Column(String(500), nullable=True)
    tiene_marca_agua = Column(Boolean, default=True, nullable=False)
    
    # Metadatos
    fecha_generacion = Column(DateTime(timezone=True), nullable=False)
    version_reporte = Column(String(20), default="1.0", nullable=False)
    
    # Relaciones
    evaluacion = relationship("Evaluacion", back_populates="reportes")
    organizacion = relationship("Organizacion")
    generado_por_usuario = relationship("Usuario")
    
    def __repr__(self):
        return f"<Reporte(id={self.id}, titulo='{self.titulo}', nivel='{self.nivel_generado}')>"
    
    @property
    def es_reporte_completo(self) -> bool:
        """Verificar si es un reporte completo"""
        return self.tipo_reporte == "completo"
    
    @property
    def tiene_archivo_pdf(self) -> bool:
        """Verificar si tiene archivo PDF"""
        return bool(self.url_pdf)
    
    def obtener_resumen_ejecutivo(self) -> dict:
        """Obtener resumen ejecutivo del reporte"""
        return {
            "titulo": self.titulo,
            "fecha_generacion": self.fecha_generacion,
            "puntuacion_global": float(self.puntuacion_global),
            "nivel_generado": self.nivel_generado.value,
            "total_fortalezas": len(self.fortalezas) if self.fortalezas else 0,
            "total_debilidades": len(self.debilidades) if self.debilidades else 0,
            "total_recomendaciones": len(self.recomendaciones) if self.recomendaciones else 0,
            "tiene_marca_agua": self.tiene_marca_agua
        }
    
    def obtener_recomendaciones_priorizadas(self, limite: int = None) -> list:
        """Obtener recomendaciones priorizadas"""
        if not self.recomendaciones:
            return []
        
        # Ordenar por prioridad
        recomendaciones_ordenadas = sorted(
            self.recomendaciones,
            key=lambda x: x.get("prioridad", "media"),
            reverse=True
        )
        
        # Aplicar límite si se especifica
        if limite:
            recomendaciones_ordenadas = recomendaciones_ordenadas[:limite]
        
        return recomendaciones_ordenadas
    
    def obtener_analisis_brechas(self) -> dict:
        """Obtener análisis de brechas"""
        if not self.debilidades:
            return {}
        
        # Categorizar debilidades por tipo
        brechas = {
            "criticas": [],
            "importantes": [],
            "menores": []
        }
        
        for debilidad in self.debilidades:
            nivel_impacto = debilidad.get("nivel_impacto", "medio")
            
            if nivel_impacto == "alto":
                brechas["criticas"].append(debilidad)
            elif nivel_impacto == "medio":
                brechas["importantes"].append(debilidad)
            else:
                brechas["menores"].append(debilidad)
        
        return brechas
    
    def obtener_roadmap_mejora(self, meses: int = 6) -> dict:
        """Obtener roadmap de mejora"""
        if not self.recomendaciones:
            return {}
        
        # Agrupar recomendaciones por plazo
        roadmap = {
            "corto_plazo": [],  # 1-3 meses
            "mediano_plazo": [],  # 3-6 meses
            "largo_plazo": []  # 6+ meses
        }
        
        for recomendacion in self.recomendaciones:
            plazo_estimado = recomendacion.get("plazo_estimado", "3 meses")
            
            if "1" in plazo_estimado or "2" in plazo_estimado or "3" in plazo_estimado:
                roadmap["corto_plazo"].append(recomendacion)
            elif "4" in plazo_estimado or "5" in plazo_estimado or "6" in plazo_estimado:
                roadmap["mediano_plazo"].append(recomendacion)
            else:
                roadmap["largo_plazo"].append(recomendacion)
        
        return roadmap
    
    def calcular_inversion_estimada(self) -> dict:
        """Calcular inversión estimada para implementar recomendaciones"""
        if not self.recomendaciones:
            return {"total": 0, "por_prioridad": {}}
        
        total_inversion = 0
        inversion_por_prioridad = {}
        
        for recomendacion in self.recomendaciones:
            costo_estimado = recomendacion.get("costo_estimado", 0)
            prioridad = recomendacion.get("prioridad", "media")
            
            total_inversion += costo_estimado
            
            if prioridad not in inversion_por_prioridad:
                inversion_por_prioridad[prioridad] = 0
            
            inversion_por_prioridad[prioridad] += costo_estimado
        
        return {
            "total": total_inversion,
            "por_prioridad": inversion_por_prioridad,
            "moneda": "CLP"
        }
    
    def obtener_estadisticas_benchmark(self) -> dict:
        """Obtener estadísticas de benchmarking (solo para niveles Pro+)"""
        if self.nivel_generado == NivelSuscripcion.GRATUITO:
            return {"disponible": False, "mensaje": "Benchmarking disponible en plan Pro+"}
        
        # Aquí se implementaría la lógica de benchmarking
        # Por ahora retornamos datos de ejemplo
        return {
            "disponible": True,
            "puntuacion_industria": 72.5,
            "puntuacion_organizacion": float(self.puntuacion_global),
            "posicion_percentil": 65,
            "comparacion": "Por encima del promedio"
        }
    
    def validar_contenido(self) -> dict:
        """Validar contenido del reporte"""
        errores = []
        advertencias = []
        
        # Validaciones básicas
        if not self.titulo or not self.titulo.strip():
            errores.append("El título del reporte es requerido")
        
        if not self.puntuacion_global:
            errores.append("La puntuación global es requerida")
        
        if not self.fortalezas:
            advertencias.append("No se encontraron fortalezas")
        
        if not self.debilidades:
            advertencias.append("No se encontraron debilidades")
        
        if not self.recomendaciones:
            advertencias.append("No se generaron recomendaciones")
        
        # Validaciones por nivel
        if self.nivel_generado == NivelSuscripcion.GRATUITO:
            if self.recomendaciones and len(self.recomendaciones) > 3:
                advertencias.append("Plan gratuito limitado a 3 recomendaciones")
        
        return {
            "es_valido": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias
        }