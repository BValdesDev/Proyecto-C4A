# app/modelos/suscripcion.py
"""
Modelo de Suscripción para C4A SaaS
Gestión de suscripciones con integración Stripe
"""

from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import ModeloConUUID
from ..core.config import NivelSuscripcion

class Suscripcion(ModeloConUUID):
    """Modelo de suscripción"""
    __tablename__ = "suscripciones"
    
    # Relaciones
    organizacion_id = Column(UUID(as_uuid=True), ForeignKey("organizaciones.id", ondelete="CASCADE"), nullable=False)
    
    # Stripe
    id_suscripcion_stripe = Column(String(100), unique=True, nullable=True)
    id_cliente_stripe = Column(String(100), nullable=False)
    
    # Detalles de suscripción
    nivel = Column(Enum(NivelSuscripcion), nullable=False)
    estado = Column(String(20), nullable=False)  # active, canceled, past_due, etc.
    
    # Facturación CLP
    monto_centavos = Column(Integer, nullable=False)  # En centavos de peso chileno
    moneda = Column(String(3), default="CLP", nullable=False)
    ciclo_facturacion = Column(String(20), default="mensual", nullable=False)
    
    # Períodos
    inicio_periodo_actual = Column(DateTime(timezone=True), nullable=False)
    fin_periodo_actual = Column(DateTime(timezone=True), nullable=False)
    
    # Uso del período actual
    uso_evaluaciones_periodo_actual = Column(Integer, default=0, nullable=False)
    uso_usuarios_periodo_actual = Column(Integer, default=0, nullable=False)
    
    # Relaciones
    organizacion = relationship("Organizacion", back_populates="suscripciones")
    
    def __repr__(self):
        return f"<Suscripcion(id={self.id}, nivel='{self.nivel}', estado='{self.estado}')>"
    
    @property
    def monto_clp(self) -> float:
        """Obtener monto en CLP"""
        return self.monto_centavos / 100.0
    
    @property
    def esta_activa(self) -> bool:
        """Verificar si la suscripción está activa"""
        return self.estado == "active"
    
    @property
    def esta_vencida(self) -> bool:
        """Verificar si la suscripción está vencida"""
        from datetime import datetime
        return datetime.utcnow() > self.fin_periodo_actual
    
    def actualizar_uso_evaluaciones(self, cantidad: int = 1):
        """Actualizar uso de evaluaciones"""
        self.uso_evaluaciones_periodo_actual += cantidad
    
    def actualizar_uso_usuarios(self, cantidad: int = 1):
        """Actualizar uso de usuarios"""
        self.uso_usuarios_periodo_actual += cantidad
    
    def obtener_limites_uso(self) -> dict:
        """Obtener límites de uso según el nivel"""
        from ..core.config import LIMITES_POR_NIVEL
        
        limites = LIMITES_POR_NIVEL.get(self.nivel, LIMITES_POR_NIVEL[NivelSuscripcion.GRATUITO])
        
        return {
            "max_evaluaciones": limites["max_evaluaciones_mes"],
            "max_usuarios": limites["max_usuarios"],
            "evaluaciones_usadas": self.uso_evaluaciones_periodo_actual,
            "usuarios_activos": self.uso_usuarios_periodo_actual
        }
    
    def verificar_limite_evaluaciones(self) -> bool:
        """Verificar si se puede crear más evaluaciones"""
        limites = self.obtener_limites_uso()
        return self.uso_evaluaciones_periodo_actual < limites["max_evaluaciones"]
    
    def verificar_limite_usuarios(self) -> bool:
        """Verificar si se puede agregar más usuarios"""
        limites = self.obtener_limites_uso()
        return self.uso_usuarios_periodo_actual < limites["max_usuarios"]
    
    def obtener_estadisticas_uso(self) -> dict:
        """Obtener estadísticas de uso"""
        limites = self.obtener_limites_uso()
        
        return {
            "evaluaciones": {
                "usadas": self.uso_evaluaciones_periodo_actual,
                "limite": limites["max_evaluaciones"],
                "disponibles": limites["max_evaluaciones"] - self.uso_evaluaciones_periodo_actual,
                "porcentaje_uso": (self.uso_evaluaciones_periodo_actual / limites["max_evaluaciones"]) * 100
            },
            "usuarios": {
                "activos": self.uso_usuarios_periodo_actual,
                "limite": limites["max_usuarios"],
                "disponibles": limites["max_usuarios"] - self.uso_usuarios_periodo_actual,
                "porcentaje_uso": (self.uso_usuarios_periodo_actual / limites["max_usuarios"]) * 100
            },
            "periodo": {
                "inicio": self.inicio_periodo_actual,
                "fin": self.fin_periodo_actual,
                "dias_restantes": self._calcular_dias_restantes()
            }
        }
    
    def _calcular_dias_restantes(self) -> int:
        """Calcular días restantes en el período"""
        from datetime import datetime
        
        if self.esta_vencida:
            return 0
        
        diferencia = self.fin_periodo_actual - datetime.utcnow()
        return diferencia.days
    
    def renovar_periodo(self):
        """Renovar el período de facturación"""
        from datetime import datetime, timedelta
        
        # Calcular nuevo período
        if self.ciclo_facturacion == "mensual":
            duracion = timedelta(days=30)
        elif self.ciclo_facturacion == "anual":
            duracion = timedelta(days=365)
        else:
            duracion = timedelta(days=30)  # Default mensual
        
        # Actualizar fechas
        self.inicio_periodo_actual = self.fin_periodo_actual
        self.fin_periodo_actual = self.inicio_periodo_actual + duracion
        
        # Resetear contadores de uso
        self.uso_evaluaciones_periodo_actual = 0
        self.uso_usuarios_periodo_actual = 0