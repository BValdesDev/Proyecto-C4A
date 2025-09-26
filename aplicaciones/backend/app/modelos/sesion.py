# app/modelos/sesion.py
"""
Modelo de Sesión para C4A SaaS
Gestión de sesiones JWT con tokens de refresco
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import ModeloConUUID


class Sesion(ModeloConUUID):
    """Modelo de sesión de usuario"""
    __tablename__ = "sesiones"
    
    # Relaciones
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    # JWT
    jti = Column(String(36), unique=True, nullable=False)  # JWT ID
    hash_token_refresco = Column(String(128), nullable=False)  # Hash del token de refresco
    
    # Contexto de sesión
    direccion_ip = Column(String(45), nullable=False)  # IPv6 compatible
    agente_usuario = Column(String(500), nullable=True)
    
    # Timing
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)
    fecha_vencimiento = Column(DateTime(timezone=True), nullable=False)
    
    # Estado
    esta_activa = Column(Boolean, default=True, nullable=False)
    fecha_revocacion = Column(DateTime(timezone=True), nullable=True)
    razon_revocacion = Column(String(100), nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")
    
    def __repr__(self):
        return f"<Sesion(id={self.id}, usuario_id={self.usuario_id}, activa={self.esta_activa})>"
    
    @property
    def esta_expirada(self) -> bool:
        """Verificar si la sesión está expirada"""
        from datetime import datetime
        return datetime.utcnow() > self.fecha_vencimiento
    
    @property
    def esta_valida(self) -> bool:
        """Verificar si la sesión es válida"""
        return self.esta_activa and not self.esta_expirada
    
    def revocar(self, razon: str = "Logout manual"):
        """Revocar la sesión"""
        from datetime import datetime
        
        self.esta_activa = False
        self.fecha_revocacion = datetime.utcnow()
        self.razon_revocacion = razon
    
    def extender_vencimiento(self, dias_adicionales: int = 7):
        """Extender la fecha de vencimiento"""
        from datetime import timedelta
        
        self.fecha_vencimiento += timedelta(days=dias_adicionales)
    
    @classmethod
    def crear_sesion(cls, usuario_id: str, jti: str, hash_token_refresco: str,
                     direccion_ip: str, agente_usuario: str = None):
        """Crear nueva sesión"""
        from datetime import datetime, timedelta
        
        return cls(
            usuario_id=usuario_id,
            jti=jti,
            hash_token_refresco=hash_token_refresco,
            direccion_ip=direccion_ip,
            agente_usuario=agente_usuario,
            fecha_creacion=datetime.utcnow(),
            fecha_vencimiento=datetime.utcnow() + timedelta(days=7)
        )