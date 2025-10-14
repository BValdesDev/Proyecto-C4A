# app/modelos/framework.py
"""
Modelo de Framework para C4A SaaS
Frameworks de ciberseguridad (NIST CSF 2.0, COBIT 2019)
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from .base import ModeloConUUID
from ..core.config import NivelSuscripcion


class Framework(ModeloConUUID):
    """Modelo de framework de ciberseguridad"""
    __tablename__ = "frameworks"
    
    # Información básica
    nombre = Column(String(50), unique=True, nullable=False)  # "NIST_CSF", "COBIT_2019"
    version = Column(String(20), nullable=False)  # "2.0", "2019"
    nombre_mostrar = Column(String(100), nullable=False)  # "NIST Cybersecurity Framework 2.0"
    descripcion = Column(Text, nullable=True)
    
    # Niveles de suscripción disponibles
    niveles_disponibles = Column(ARRAY(String), default=["gratuito", "pro", "empresarial"], nullable=False)
    
    # Estado
    esta_activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    preguntas = relationship("Pregunta", back_populates="framework", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="framework")
    
    def __repr__(self):
        return f"<Framework(id={self.id}, nombre='{self.nombre_mostrar}')>"
    
    def es_compatible_con_nivel(self, nivel: NivelSuscripcion) -> bool:
        """Verificar si el framework es compatible con un nivel de suscripción"""
        return nivel.value in self.niveles_disponibles
    
    def obtener_preguntas_por_nivel(self, nivel: NivelSuscripcion):
        """Obtener preguntas disponibles para un nivel específico"""
        return [
            p for p in self.preguntas 
            if p.esta_activa and p.es_disponible_para_nivel(nivel)
        ]
    
    def contar_preguntas_activas_para_nivel(self, nivel: NivelSuscripcion) -> int:
        """Contar preguntas activas para un nivel específico"""
        return len([
            p for p in self.preguntas 
            if p.esta_activa and p.es_disponible_para_nivel(nivel)
        ])
    
    def obtener_estadisticas(self) -> dict:
        """Obtener estadísticas del framework"""
        total_preguntas = len([p for p in self.preguntas if p.esta_activa])
        
        preguntas_por_nivel = {}
        for nivel in NivelSuscripcion:
            preguntas_por_nivel[nivel.value] = len(self.obtener_preguntas_por_nivel(nivel))
        
        total_evaluaciones = len([
            e for e in self.evaluaciones 
            if e.fecha_eliminacion is None
        ])
        
        return {
            "total_preguntas": total_preguntas,
            "preguntas_por_nivel": preguntas_por_nivel,
            "total_evaluaciones": total_evaluaciones,
            "niveles_disponibles": self.niveles_disponibles
        }
    
    @classmethod
    def crear_nist_csf_2_0(cls):
        """Crear framework NIST CSF 2.0"""
        return cls(
            nombre="NIST_CSF",
            version="2.0",
            nombre_mostrar="NIST Cybersecurity Framework 2.0",
            descripcion="Marco de Ciberseguridad del Instituto Nacional de Estándares y Tecnología de Estados Unidos",
            niveles_disponibles=["gratuito", "pro", "empresarial"]
        )
    
    @classmethod
    def crear_cobit_2019(cls):
        """Crear framework COBIT 2019"""
        return cls(
            nombre="COBIT_2019",
            version="2019",
            nombre_mostrar="COBIT 2019",
            descripcion="Control Objectives for Information and Related Technologies",
            niveles_disponibles=["pro", "empresarial"]
        )