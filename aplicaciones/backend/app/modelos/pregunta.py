# app/modelos/pregunta.py
"""
Modelo de Pregunta para C4A SaaS
Preguntas de evaluación con soporte para niveles de suscripción
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import ModeloConUUID
from ..core.config import NivelSuscripcion

class Pregunta(ModeloConUUID):
    """Modelo de pregunta de evaluación"""
    __tablename__ = "preguntas"
    
    # Información básica
    codigo = Column(String(50), unique=True, nullable=False)  # "NIST_ID_AM_01"
    texto_pregunta = Column(Text, nullable=False)
    texto_ayuda = Column(Text, nullable=True)
    
    # Relación con framework
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.id"), nullable=False)
    
    # Clasificación
    categoria = Column(String(100), nullable=True)  # "Identificar", "Proteger", etc.
    subcategoria = Column(String(100), nullable=True)
    
    # Configuración por nivel (CRÍTICO para modelo de negocio)
    disponibilidad_por_nivel = Column(JSONB, nullable=False, default={
        "gratuito": False,
        "pro": False,
        "empresarial": False
    })
    
    # Parámetros de puntuación
    peso = Column(Integer, default=1, nullable=False)  # 1-5 importancia
    tipo_respuesta = Column(String(20), default="likert_5", nullable=False)
    
    # Lógica condicional
    logica_condicional = Column(JSONB, nullable=True)  # Para preguntas que dependen de otras
    
    # Metadatos
    esta_activa = Column(Boolean, default=True, nullable=False)
    orden = Column(Integer, default=0, nullable=False)  # Para ordenar preguntas
    
    # Relaciones
    framework = relationship("Framework", back_populates="preguntas")
    respuestas = relationship("Respuesta", back_populates="pregunta", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pregunta(id={self.id}, codigo='{self.codigo}', activa={self.esta_activa})>"
    
    def es_disponible_para_nivel(self, nivel: NivelSuscripcion) -> bool:
        """Verificar si la pregunta está disponible para un nivel específico"""
        return self.disponibilidad_por_nivel.get(nivel.value, False)
    
    def obtener_texto_respuesta(self, valor: int) -> str:
        """Obtener texto descriptivo para un valor de respuesta"""
        textos_likert_5 = {
            0: "No implementado",
            1: "Parcialmente implementado",
            2: "Implementado básicamente",
            3: "Bien implementado",
            4: "Completamente implementado",
            5: "Excelentemente implementado"
        }
        
        textos_likert_3 = {
            0: "No",
            1: "Parcialmente",
            2: "Sí"
        }
        
        if self.tipo_respuesta == "likert_5":
            return textos_likert_5.get(valor, "Desconocido")
        elif self.tipo_respuesta == "likert_3":
            return textos_likert_3.get(valor, "Desconocido")
        else:
            return str(valor)
    
    def calcular_puntuacion(self, valor_respuesta: int) -> float:
        """Calcular puntuación basada en el valor de respuesta y peso"""
        # Normalizar valor de respuesta (0-5) a escala 0-100
        puntuacion_base = (valor_respuesta / 5.0) * 100
        
        # Aplicar peso
        puntuacion_final = puntuacion_base * (self.peso / 5.0)
        
        return min(puntuacion_final, 100.0)  # Máximo 100
    
    def obtener_estadisticas_respuestas(self) -> dict:
        """Obtener estadísticas de respuestas para esta pregunta"""
        if not self.respuestas:
            return {
                "total_respuestas": 0,
                "promedio": 0.0,
                "distribucion": {}
            }
        
        valores = [r.valor for r in self.respuestas]
        total = len(valores)
        promedio = sum(valores) / total if total > 0 else 0
        
        # Distribución de respuestas
        distribucion = {}
        for i in range(6):  # 0-5
            distribucion[i] = valores.count(i)
        
        return {
            "total_respuestas": total,
            "promedio": round(promedio, 2),
            "distribucion": distribucion,
            "puntuacion_promedio": round(self.calcular_puntuacion(promedio), 2)
        }
    
    def es_pregunta_critica(self) -> bool:
        """Verificar si es una pregunta crítica (disponible en nivel gratuito)"""
        return self.disponibilidad_por_nivel.get("gratuito", False)
    
    def obtener_niveles_disponibles(self) -> list:
        """Obtener lista de niveles donde está disponible"""
        return [
            nivel for nivel, disponible in self.disponibilidad_por_nivel.items()
            if disponible
        ]
    
    @classmethod
    def crear_pregunta_nist(cls, codigo: str, texto: str, categoria: str, 
                           niveles_disponibles: list = None, peso: int = 1):
        """Crear pregunta NIST CSF"""
        if niveles_disponibles is None:
            niveles_disponibles = ["gratuito"]
        
        disponibilidad = {
            "gratuito": "gratuito" in niveles_disponibles,
            "pro": "pro" in niveles_disponibles,
            "empresarial": "empresarial" in niveles_disponibles
        }
        
        return cls(
            codigo=codigo,
            texto_pregunta=texto,
            categoria=categoria,
            disponibilidad_por_nivel=disponibilidad,
            peso=peso,
            tipo_respuesta="likert_5"
        )