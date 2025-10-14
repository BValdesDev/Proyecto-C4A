# app/modelos/organizacion.py
"""
Modelo de Organización para C4A SaaS
Con soporte para niveles de suscripción y configuración Chile
"""

from sqlalchemy import Column, String, Enum, DateTime, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import ModeloConEliminacionLogica
from ..core.config import NivelSuscripcion


class TamañoEmpresa(str, enum.Enum):
    """Tamaños de empresa según clasificación chilena"""
    MICRO = "micro"  # < 10 empleados
    PEQUEÑA = "pequeña"  # 10-49 empleados
    MEDIANA = "mediana"  # 50-199 empleados
    GRANDE = "grande"  # 200+ empleados


class Sector(str, enum.Enum):
    """Sectores económicos chilenos"""
    FINANCIERO = "financiero"
    SALUD = "salud"
    RETAIL = "retail"
    GOBIERNO = "gobierno"
    EDUCACION = "educacion"
    TECNOLOGIA = "tecnologia"
    MANUFACTURA = "manufactura"
    SERVICIOS = "servicios"
    CONSTRUCCION = "construccion"
    MINERIA = "mineria"


class Organizacion(ModeloConEliminacionLogica):
    """Modelo de organización con soporte para niveles de suscripción"""
    __tablename__ = "organizaciones"
    
    # Información básica
    nombre = Column(String(255), nullable=False)
    rut = Column(String(12), unique=True, nullable=True)  # RUT chileno
    sector = Column(Enum(Sector), nullable=False)
    tamaño = Column(Enum(TamañoEmpresa), nullable=False)
    
    # Configuración geográfica
    pais = Column(String(2), default="CL", nullable=False)
    region = Column(String(100), nullable=True)
    comuna = Column(String(100), nullable=True)
    
    # Gestión de suscripción (CRÍTICO para modelo de negocio)
    nivel_suscripcion = Column(Enum(NivelSuscripcion), default=NivelSuscripcion.GRATUITO, nullable=False)
    fecha_inicio_suscripcion = Column(DateTime(timezone=True), nullable=True)
    fecha_vencimiento_suscripcion = Column(DateTime(timezone=True), nullable=True)
    
    # Información de facturación
    email_facturacion = Column(String(255), nullable=True)
    metodo_pago_stripe_id = Column(String(100), nullable=True)
    
    # Límites de uso por nivel
    maximo_usuarios = Column(Integer, default=1, nullable=False)
    maximo_evaluaciones_por_mes = Column(Integer, default=1, nullable=False)
    maximo_dias_retencion_datos = Column(Integer, default=30, nullable=False)
    
    # Cumplimiento Ley 19.628 Chile
    consentimiento_otorgado = Column(Boolean, default=False, nullable=False)
    fecha_consentimiento = Column(DateTime(timezone=True), nullable=True)
    politica_privacidad_aceptada = Column(Boolean, default=False, nullable=False)
    fecha_aceptacion_politica = Column(DateTime(timezone=True), nullable=True)
    
    # Configuración adicional
    descripcion = Column(Text, nullable=True)
    sitio_web = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="organizacion", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="organizacion", cascade="all, delete-orphan")
    suscripciones = relationship("Suscripcion", back_populates="organizacion", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Organizacion(id={self.id}, nombre='{self.nombre}', nivel='{self.nivel_suscripcion}')>"
    
    @property
    def esta_activa(self) -> bool:
        """Verificar si la organización está activa"""
        return self.fecha_eliminacion is None
    
    @property
    def suscripcion_vencida(self) -> bool:
        """Verificar si la suscripción está vencida"""
        if self.nivel_suscripcion == NivelSuscripcion.GRATUITO:
            return False
        
        if not self.fecha_vencimiento_suscripcion:
            return True
        
        from datetime import datetime
        ahora = datetime.utcnow()
        # Asegurar que ambas fechas tengan el mismo timezone
        if self.fecha_vencimiento_suscripcion.tzinfo is None:
            ahora = ahora.replace(tzinfo=None)
        else:
            # Si la fecha de vencimiento tiene timezone, convertir ahora a timezone-naive
            ahora = ahora.replace(tzinfo=None)
            vencimiento = self.fecha_vencimiento_suscripcion.replace(tzinfo=None)
            return ahora > vencimiento
        return ahora > self.fecha_vencimiento_suscripcion
    
    @property
    def puede_crear_evaluacion(self) -> bool:
        """Verificar si puede crear una nueva evaluación"""
        if self.suscripcion_vencida:
            return False
        
        # Contar evaluaciones del mes actual
        from datetime import datetime, timedelta
        ahora = datetime.utcnow().replace(tzinfo=None)
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        evaluaciones_mes = len([
            e for e in self.evaluaciones 
            if e.fecha_creacion.replace(tzinfo=None) >= inicio_mes and e.fecha_eliminacion is None
        ])
        
        return evaluaciones_mes < self.maximo_evaluaciones_por_mes
    
    @property
    def puede_agregar_usuario(self) -> bool:
        """Verificar si puede agregar un nuevo usuario"""
        if self.suscripcion_vencida:
            return False
        
        usuarios_activos = len([u for u in self.usuarios if u.fecha_eliminacion is None])
        return usuarios_activos < self.maximo_usuarios
    
    def actualizar_limites_nivel(self):
        """Actualizar límites según el nivel de suscripción"""
        from ..core.config import LIMITES_POR_NIVEL
        
        limites = LIMITES_POR_NIVEL.get(self.nivel_suscripcion, LIMITES_POR_NIVEL[NivelSuscripcion.GRATUITO])
        
        self.maximo_usuarios = limites["max_usuarios"]
        self.maximo_evaluaciones_por_mes = limites["max_evaluaciones_mes"]
        self.maximo_dias_retencion_datos = limites["dias_retencion"]
    
    def obtener_uso_mensual(self) -> dict:
        """Obtener uso del mes actual"""
        from datetime import datetime, timedelta
        
        inicio_mes = datetime.utcnow().replace(tzinfo=None, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        evaluaciones_mes = len([
            e for e in self.evaluaciones 
            if e.fecha_creacion.replace(tzinfo=None) >= inicio_mes and e.fecha_eliminacion is None
        ])
        
        usuarios_activos = len([u for u in self.usuarios if u.fecha_eliminacion is None])
        
        return {
            "evaluaciones_usadas": evaluaciones_mes,
            "evaluaciones_limite": self.maximo_evaluaciones_por_mes,
            "usuarios_activos": usuarios_activos,
            "usuarios_limite": self.maximo_usuarios,
            "porcentaje_uso_evaluaciones": (evaluaciones_mes / self.maximo_evaluaciones_por_mes) * 100,
            "porcentaje_uso_usuarios": (usuarios_activos / self.maximo_usuarios) * 100
        }