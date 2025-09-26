# app/modelos/log_auditoria.py
"""
Modelo de Log de Auditoría para C4A SaaS
Registro de eventos para cumplimiento y seguridad
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship

from .base import ModeloConUUID


class LogAuditoria(ModeloConUUID):
    """Modelo de log de auditoría"""
    __tablename__ = "logs_auditoria"
    
    # Relaciones
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    organizacion_id = Column(UUID(as_uuid=True), ForeignKey("organizaciones.id"), nullable=True)
    
    # Evento
    tipo_evento = Column(String(50), nullable=False)  # "autenticacion", "evaluacion", "reporte", etc.
    accion = Column(String(100), nullable=False)  # "login", "crear_evaluacion", "generar_reporte"
    tipo_recurso = Column(String(50), nullable=True)  # "usuario", "evaluacion", "reporte"
    id_recurso = Column(UUID(as_uuid=True), nullable=True)
    
    # Contexto
    direccion_ip = Column(INET, nullable=True)
    agente_usuario = Column(Text, nullable=True)
    
    # Resultado
    exitoso = Column(Boolean, nullable=False)
    mensaje_error = Column(Text, nullable=True)
    
    # Integridad
    suma_verificacion = Column(String(64), nullable=False)  # SHA-256
    marca_tiempo = Column(DateTime(timezone=True), nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="logs_auditoria")
    organizacion = relationship("Organizacion")
    
    def __repr__(self):
        return f"<LogAuditoria(id={self.id}, evento='{self.tipo_evento}', accion='{self.accion}')>"
    
    @classmethod
    def crear_log(cls, tipo_evento: str, accion: str, exitoso: bool,
                  usuario_id: str = None, organizacion_id: str = None,
                  tipo_recurso: str = None, id_recurso: str = None,
                  direccion_ip: str = None, agente_usuario: str = None,
                  mensaje_error: str = None):
        """Crear nuevo log de auditoría"""
        from datetime import datetime
        import hashlib
        import json
        
        # Crear datos para hash
        datos_hash = {
            "tipo_evento": tipo_evento,
            "accion": accion,
            "usuario_id": usuario_id,
            "organizacion_id": organizacion_id,
            "marca_tiempo": datetime.utcnow().isoformat()
        }
        
        # Generar hash SHA-256
        datos_json = json.dumps(datos_hash, sort_keys=True)
        suma_verificacion = hashlib.sha256(datos_json.encode()).hexdigest()
        
        return cls(
            usuario_id=usuario_id,
            organizacion_id=organizacion_id,
            tipo_evento=tipo_evento,
            accion=accion,
            tipo_recurso=tipo_recurso,
            id_recurso=id_recurso,
            direccion_ip=direccion_ip,
            agente_usuario=agente_usuario,
            exitoso=exitoso,
            mensaje_error=mensaje_error,
            suma_verificacion=suma_verificacion,
            marca_tiempo=datetime.utcnow()
        )
    
    def verificar_integridad(self) -> bool:
        """Verificar integridad del log"""
        import hashlib
        import json
        
        # Recrear datos para hash
        datos_hash = {
            "tipo_evento": self.tipo_evento,
            "accion": self.accion,
            "usuario_id": str(self.usuario_id) if self.usuario_id else None,
            "organizacion_id": str(self.organizacion_id) if self.organizacion_id else None,
            "marca_tiempo": self.marca_tiempo.isoformat()
        }
        
        # Generar hash
        datos_json = json.dumps(datos_hash, sort_keys=True)
        hash_calculado = hashlib.sha256(datos_json.encode()).hexdigest()
        
        return hash_calculado == self.suma_verificacion
    
    def obtener_resumen(self) -> dict:
        """Obtener resumen del log"""
        return {
            "id": str(self.id),
            "tipo_evento": self.tipo_evento,
            "accion": self.accion,
            "exitoso": self.exitoso,
            "marca_tiempo": self.marca_tiempo,
            "usuario": self.usuario.email if self.usuario else None,
            "organizacion": self.organizacion.nombre if self.organizacion else None,
            "direccion_ip": str(self.direccion_ip) if self.direccion_ip else None
        }