# app/modelos/evaluacion.py
"""
Modelo de Evaluación para C4A SaaS
Evaluaciones de ciberseguridad con soporte para niveles
"""

from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from .base import ModeloConEliminacionLogica
from ..core.config import NivelSuscripcion

class EstadoEvaluacion(str, enum.Enum):
    """Estados de evaluación"""
    BORRADOR = "borrador"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    ARCHIVADA = "archivada"

class Evaluacion(ModeloConEliminacionLogica):
    """Modelo de evaluación de ciberseguridad"""
    __tablename__ = "evaluaciones"
    
    # Información básica
    nombre = Column(String(255), nullable=False)
    
    # Relaciones
    organizacion_id = Column(UUID(as_uuid=True), ForeignKey("organizaciones.id", ondelete="CASCADE"), nullable=False)
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.id"), nullable=False)
    cuestionario_id = Column(UUID(as_uuid=True), ForeignKey("cuestionarios.id"), nullable=True)  # Opcional
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Gestión de nivel (CRÍTICO)
    nivel_usado = Column(Enum(NivelSuscripcion), nullable=False)
    
    # Configuración
    total_preguntas = Column(Integer, nullable=False)
    preguntas_completadas = Column(Integer, default=0, nullable=False)
    estado = Column(Enum(EstadoEvaluacion), default=EstadoEvaluacion.BORRADOR, nullable=False)
    
    # Resultados
    puntuacion_global = Column(Numeric(5, 2), nullable=True)  # 0.00-100.00
    puntuaciones_dominio = Column(JSONB, nullable=True)  # {"identificar": 75.5, "proteger": 68.2}
    
    # Metadatos
    fecha_inicio = Column(DateTime(timezone=True), nullable=True)
    fecha_completada = Column(DateTime(timezone=True), nullable=True)
    tiempo_estimado_minutos = Column(Integer, nullable=True)
    tiempo_real_minutos = Column(Integer, nullable=True)
    
    # Relaciones
    organizacion = relationship("Organizacion", back_populates="evaluaciones")
    framework = relationship("Framework", back_populates="evaluaciones")
    cuestionario = relationship("Cuestionario", back_populates="evaluaciones")
    creado_por_usuario = relationship("Usuario", back_populates="evaluaciones_creadas", foreign_keys=[creado_por])
    respuestas = relationship("Respuesta", back_populates="evaluacion", cascade="all, delete-orphan")
    reportes = relationship("Reporte", back_populates="evaluacion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Evaluacion(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')>"
    
    @property
    def porcentaje_completado(self) -> float:
        """Calcular porcentaje de completado"""
        if self.total_preguntas == 0:
            return 0.0
        return (self.preguntas_completadas / self.total_preguntas) * 100
    
    @property
    def esta_completada(self) -> bool:
        """Verificar si la evaluación está completada"""
        return self.estado == EstadoEvaluacion.COMPLETADA
    
    @property
    def puede_continuar(self) -> bool:
        """Verificar si se puede continuar la evaluación"""
        return self.estado in [EstadoEvaluacion.BORRADOR, EstadoEvaluacion.EN_PROGRESO]
    
    def iniciar_evaluacion(self):
        """Iniciar la evaluación"""
        from datetime import datetime
        
        if self.estado == EstadoEvaluacion.BORRADOR:
            self.estado = EstadoEvaluacion.EN_PROGRESO
            self.fecha_inicio = datetime.utcnow()
    
    def completar_evaluacion(self):
        """Completar la evaluación"""
        from datetime import datetime
        
        if self.estado == EstadoEvaluacion.EN_PROGRESO:
            self.estado = EstadoEvaluacion.COMPLETADA
            self.fecha_completada = datetime.utcnow()
            
            # Calcular tiempo real si hay fecha de inicio
            if self.fecha_inicio:
                diferencia = self.fecha_completada - self.fecha_inicio
                self.tiempo_real_minutos = int(diferencia.total_seconds() / 60)
    
    def agregar_respuesta(self, pregunta_id: str, valor: int, usuario_id: str, 
                         texto_evidencia: str = None, comentarios: str = None):
        """Agregar respuesta a la evaluación"""
        from ..modelos.respuesta import Respuesta
        
        # Verificar si ya existe respuesta para esta pregunta
        respuesta_existente = next(
            (r for r in self.respuestas if str(r.pregunta_id) == pregunta_id), 
            None
        )
        
        if respuesta_existente:
            # Actualizar respuesta existente
            respuesta_existente.valor = valor
            respuesta_existente.texto_evidencia = texto_evidencia
            respuesta_existente.comentarios = comentarios
        else:
            # Crear nueva respuesta
            nueva_respuesta = Respuesta(
                evaluacion_id=self.id,
                pregunta_id=pregunta_id,
                respondido_por=usuario_id,
                valor=valor,
                texto_evidencia=texto_evidencia,
                comentarios=comentarios
            )
            self.respuestas.append(nueva_respuesta)
            self.preguntas_completadas += 1
        
        # Actualizar estado si es necesario
        if self.estado == EstadoEvaluacion.BORRADOR:
            self.iniciar_evaluacion()
        
        # Verificar si está completada
        if self.preguntas_completadas >= self.total_preguntas:
            self.completar_evaluacion()
    
    def calcular_puntuacion_global(self) -> float:
        """Calcular puntuación global basada en respuestas"""
        if not self.respuestas:
            return 0.0
        
        puntuacion_total = 0.0
        peso_total = 0
        
        for respuesta in self.respuestas:
            if respuesta.pregunta:
                puntuacion_pregunta = respuesta.pregunta.calcular_puntuacion(respuesta.valor)
                peso = respuesta.pregunta.peso
                
                puntuacion_total += puntuacion_pregunta * peso
                peso_total += peso
        
        if peso_total == 0:
            return 0.0
        
        return round(puntuacion_total / peso_total, 2)
    
    def calcular_puntuaciones_dominio(self) -> dict:
        """Calcular puntuaciones por dominio/categoría"""
        if not self.respuestas:
            return {}
        
        dominios = {}
        
        for respuesta in self.respuestas:
            if respuesta.pregunta:
                categoria = respuesta.pregunta.categoria
                if not categoria:
                    categoria = "general"
                
                if categoria not in dominios:
                    dominios[categoria] = {"puntuacion_total": 0.0, "peso_total": 0}
                
                puntuacion_pregunta = respuesta.pregunta.calcular_puntuacion(respuesta.valor)
                peso = respuesta.pregunta.peso
                
                dominios[categoria]["puntuacion_total"] += puntuacion_pregunta * peso
                dominios[categoria]["peso_total"] += peso
        
        # Calcular promedios
        puntuaciones_finales = {}
        for categoria, datos in dominios.items():
            if datos["peso_total"] > 0:
                puntuaciones_finales[categoria] = round(
                    datos["puntuacion_total"] / datos["peso_total"], 2
                )
        
        return puntuaciones_finales
    
    def obtener_estadisticas(self) -> dict:
        """Obtener estadísticas de la evaluación"""
        return {
            "total_preguntas": self.total_preguntas,
            "preguntas_completadas": self.preguntas_completadas,
            "porcentaje_completado": self.porcentaje_completado,
            "puntuacion_global": float(self.puntuacion_global) if self.puntuacion_global else 0.0,
            "estado": self.estado.value,
            "nivel_usado": self.nivel_usado.value,
            "tiempo_estimado": self.tiempo_estimado_minutos,
            "tiempo_real": self.tiempo_real_minutos,
            "fecha_inicio": self.fecha_inicio,
            "fecha_completada": self.fecha_completada
        }
    
    def obtener_progreso_detallado(self) -> dict:
        """Obtener progreso detallado por categoría"""
        if not self.respuestas:
            return {}
        
        categorias = {}
        
        for respuesta in self.respuestas:
            if respuesta.pregunta:
                categoria = respuesta.pregunta.categoria or "general"
                
                if categoria not in categorias:
                    categorias[categoria] = {
                        "total_preguntas": 0,
                        "preguntas_respondidas": 0,
                        "puntuacion_promedio": 0.0
                    }
                
                categorias[categoria]["preguntas_respondidas"] += 1
        
        # Contar preguntas totales por categoría
        for pregunta in self.framework.preguntas:
            if pregunta.esta_activa and pregunta.es_disponible_para_nivel(self.nivel_usado):
                categoria = pregunta.categoria or "general"
                if categoria in categorias:
                    categorias[categoria]["total_preguntas"] += 1
        
        return categorias