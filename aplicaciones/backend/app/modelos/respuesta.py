# app/modelos/respuesta.py
"""
Modelo de Respuesta para C4A SaaS
Respuestas a preguntas de evaluación
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import ModeloConUUID


class Respuesta(ModeloConUUID):
    """Modelo de respuesta a pregunta de evaluación"""
    __tablename__ = "respuestas"
    
    # Relaciones
    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id", ondelete="CASCADE"), nullable=False)
    pregunta_id = Column(UUID(as_uuid=True), ForeignKey("preguntas.id"), nullable=False)
    respondido_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Datos de respuesta
    valor = Column(Integer, nullable=False)  # 0-5 escala Likert
    texto_evidencia = Column(Text, nullable=True)  # Evidencia o justificación
    comentarios = Column(Text, nullable=True)  # Comentarios adicionales
    nivel_confianza = Column(Integer, nullable=True)  # 1-5 auto-reportado
    
    # Metadatos
    fecha_respuesta = Column(DateTime(timezone=True), nullable=True)
    tiempo_respuesta_segundos = Column(Integer, nullable=True)  # Tiempo en responder
    
    # Relaciones
    evaluacion = relationship("Evaluacion", back_populates="respuestas")
    pregunta = relationship("Pregunta", back_populates="respuestas")
    respondido_por_usuario = relationship("Usuario", back_populates="respuestas")
    
    def __repr__(self):
        return f"<Respuesta(id={self.id}, valor={self.valor}, pregunta='{self.pregunta.codigo if self.pregunta else 'N/A'}')>"
    
    @property
    def puntuacion_calculada(self) -> float:
        """Calcular puntuación basada en el valor y peso de la pregunta"""
        if not self.pregunta:
            return 0.0
        
        return self.pregunta.calcular_puntuacion(self.valor)
    
    @property
    def texto_valor(self) -> str:
        """Obtener texto descriptivo del valor de respuesta"""
        if not self.pregunta:
            return str(self.valor)
        
        return self.pregunta.obtener_texto_respuesta(self.valor)
    
    @property
    def es_respuesta_completa(self) -> bool:
        """Verificar si la respuesta está completa"""
        return (
            self.valor is not None and 
            self.valor >= 0 and 
            self.valor <= 5
        )
    
    def obtener_analisis_calidad(self) -> dict:
        """Obtener análisis de calidad de la respuesta"""
        calidad = {
            "tiene_evidencia": bool(self.texto_evidencia and self.texto_evidencia.strip()),
            "tiene_comentarios": bool(self.comentarios and self.comentarios.strip()),
            "nivel_confianza": self.nivel_confianza,
            "tiempo_respuesta": self.tiempo_respuesta_segundos,
            "puntuacion_calidad": 0
        }
        
        # Calcular puntuación de calidad (0-100)
        puntuacion = 0
        
        # Base por tener respuesta
        if self.es_respuesta_completa:
            puntuacion += 40
        
        # Evidencia
        if calidad["tiene_evidencia"]:
            puntuacion += 30
        
        # Comentarios
        if calidad["tiene_comentarios"]:
            puntuacion += 20
        
        # Nivel de confianza
        if self.nivel_confianza and self.nivel_confianza >= 3:
            puntuacion += 10
        
        calidad["puntuacion_calidad"] = puntuacion
        return calidad
    
    def es_respuesta_consistente(self, otras_respuestas: list) -> bool:
        """Verificar consistencia con otras respuestas similares"""
        if not otras_respuestas:
            return True
        
        # Buscar respuestas a preguntas de la misma categoría
        if not self.pregunta:
            return True
        
        categoria = self.pregunta.categoria
        respuestas_categoria = [
            r for r in otras_respuestas 
            if r.pregunta and r.pregunta.categoria == categoria
        ]
        
        if not respuestas_categoria:
            return True
        
        # Calcular promedio de respuestas en la categoría
        promedio_categoria = sum(r.valor for r in respuestas_categoria) / len(respuestas_categoria)
        
        # Verificar si la respuesta está dentro de un rango razonable
        diferencia = abs(self.valor - promedio_categoria)
        return diferencia <= 2  # Tolerancia de 2 puntos
    
    def obtener_recomendaciones_mejora(self) -> list:
        """Obtener recomendaciones para mejorar la respuesta"""
        recomendaciones = []
        
        if not self.es_respuesta_completa:
            recomendaciones.append("Proporcionar una respuesta válida (0-5)")
        
        if not self.texto_evidencia:
            recomendaciones.append("Agregar evidencia o justificación de la respuesta")
        
        if not self.comentarios:
            recomendaciones.append("Incluir comentarios adicionales si es relevante")
        
        if not self.nivel_confianza or self.nivel_confianza < 3:
            recomendaciones.append("Revisar el nivel de confianza en la respuesta")
        
        if self.tiempo_respuesta_segundos and self.tiempo_respuesta_segundos < 30:
            recomendaciones.append("Considerar dedicar más tiempo a la respuesta")
        
        return recomendaciones
    
    def validar_respuesta(self) -> dict:
        """Validar la respuesta y obtener feedback"""
        errores = []
        advertencias = []
        
        # Validaciones básicas
        if self.valor is None:
            errores.append("El valor de respuesta es requerido")
        elif self.valor < 0 or self.valor > 5:
            errores.append("El valor debe estar entre 0 y 5")
        
        # Advertencias de calidad
        if not self.texto_evidencia:
            advertencias.append("Se recomienda proporcionar evidencia de la respuesta")
        
        if not self.nivel_confianza:
            advertencias.append("Se recomienda indicar el nivel de confianza")
        
        return {
            "es_valida": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias,
            "puntuacion_calidad": self.obtener_analisis_calidad()["puntuacion_calidad"]
        }