# app/modelos/usuario.py
"""
Modelo de Usuario para C4A SaaS
Con autenticación segura y gestión de roles
"""

from sqlalchemy import Column, String, Enum, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base import ModeloConEliminacionLogica

class EstadoCuenta(str, enum.Enum):
    """Estados de cuenta de usuario"""
    ACTIVO = "activo"
    BLOQUEADO = "bloqueado"
    PENDIENTE = "pendiente"
    SUSPENDIDO = "suspendido"

class Usuario(ModeloConEliminacionLogica):
    """Modelo de usuario con autenticación segura"""
    __tablename__ = "usuarios"
    
    # Información personal
    email = Column(String(255), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    
    # Autenticación segura
    hash_contraseña = Column(String(128), nullable=False)  # Argon2id
    fecha_cambio_contraseña = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    organizacion_id = Column(UUID(as_uuid=True), ForeignKey("organizaciones.id", ondelete="CASCADE"), nullable=False)
    rol_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    
    # MFA (Multi-Factor Authentication)
    mfa_habilitado = Column(Boolean, default=False, nullable=False)
    secreto_mfa = Column(String(32), nullable=True)
    
    # Seguridad
    estado_cuenta = Column(Enum(EstadoCuenta), default=EstadoCuenta.PENDIENTE, nullable=False)
    intentos_login_fallidos = Column(Integer, default=0, nullable=False)
    cuenta_bloqueada_hasta = Column(DateTime(timezone=True), nullable=True)
    
    # Actividad
    fecha_ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    ip_ultimo_acceso = Column(String(45), nullable=True)  # IPv6 compatible
    agente_usuario_ultimo = Column(Text, nullable=True)
    
    # Configuración
    idioma_preferido = Column(String(5), default="es_CL", nullable=False)
    zona_horaria = Column(String(50), default="America/Santiago", nullable=False)
    notificaciones_email = Column(Boolean, default=True, nullable=False)
    notificaciones_push = Column(Boolean, default=False, nullable=False)
    
    # Relaciones
    organizacion = relationship("Organizacion", back_populates="usuarios")
    rol = relationship("Rol", back_populates="usuarios")
    evaluaciones_creadas = relationship("Evaluacion", back_populates="creado_por_usuario", foreign_keys="[Evaluacion.creado_por]")
    respuestas = relationship("Respuesta", back_populates="respondido_por_usuario")
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")
    logs_auditoria = relationship("LogAuditoria", back_populates="usuario")
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, email='{self.email}', estado='{self.estado_cuenta}')>"
    
    @property
    def nombre_completo(self) -> str:
        """Obtener nombre completo"""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def esta_activo(self) -> bool:
        """Verificar si el usuario está activo"""
        return (
            self.estado_cuenta == EstadoCuenta.ACTIVO and 
            self.fecha_eliminacion is None and
            not self.cuenta_bloqueada
        )
    
    @property
    def cuenta_bloqueada(self) -> bool:
        """Verificar si la cuenta está bloqueada"""
        if not self.cuenta_bloqueada_hasta:
            return False
        
        from datetime import datetime
        return datetime.utcnow() < self.cuenta_bloqueada_hasta
    
    @property
    def nivel_suscripcion(self):
        """Obtener nivel de suscripción de la organización"""
        return self.organizacion.nivel_suscripcion if self.organizacion else None
    
    def incrementar_intentos_fallidos(self):
        """Incrementar intentos de login fallidos"""
        self.intentos_login_fallidos += 1
        
        # Bloquear cuenta después de 5 intentos fallidos
        if self.intentos_login_fallidos >= 5:
            from datetime import datetime, timedelta
            self.cuenta_bloqueada_hasta = datetime.utcnow() + timedelta(hours=1)
            self.estado_cuenta = EstadoCuenta.BLOQUEADO
    
    def resetear_intentos_fallidos(self):
        """Resetear intentos de login fallidos"""
        self.intentos_login_fallidos = 0
        self.cuenta_bloqueada_hasta = None
        if self.estado_cuenta == EstadoCuenta.BLOQUEADO:
            self.estado_cuenta = EstadoCuenta.ACTIVO
    
    def actualizar_ultimo_acceso(self, ip: str = None, agente_usuario: str = None):
        """Actualizar información del último acceso"""
        from datetime import datetime
        
        self.fecha_ultimo_acceso = datetime.utcnow()
        if ip:
            self.ip_ultimo_acceso = ip
        if agente_usuario:
            self.agente_usuario_ultimo = agente_usuario
    
    def puede_acceder_recurso(self, recurso: str, accion: str) -> bool:
        """Verificar si puede acceder a un recurso específico"""
        if not self.esta_activo:
            return False
        
        # Verificar permisos del rol
        return self.rol.tiene_permiso(recurso, accion)
    
    def puede_crear_evaluacion(self) -> bool:
        """Verificar si puede crear una nueva evaluación"""
        if not self.esta_activo:
            return False
        
        # Verificar permisos del rol
        if not self.puede_acceder_recurso("evaluaciones", "crear"):
            return False
        
        # Verificar límites de la organización
        return self.organizacion.puede_crear_evaluacion
    
    def obtener_estadisticas_uso(self) -> dict:
        """Obtener estadísticas de uso del usuario"""
        evaluaciones_completadas = len([
            e for e in self.evaluaciones_creadas 
            if e.estado == "completada" and e.fecha_eliminacion is None
        ])
        
        evaluaciones_en_progreso = len([
            e for e in self.evaluaciones_creadas 
            if e.estado in ["borrador", "en_progreso"] and e.fecha_eliminacion is None
        ])
        
        total_respuestas = len([
            r for r in self.respuestas 
            if r.evaluacion.fecha_eliminacion is None
        ])
        
        return {
            "evaluaciones_completadas": evaluaciones_completadas,
            "evaluaciones_en_progreso": evaluaciones_en_progreso,
            "total_respuestas": total_respuestas,
            "fecha_ultimo_acceso": self.fecha_ultimo_acceso,
            "dias_desde_ultimo_acceso": self._calcular_dias_desde_ultimo_acceso()
        }
    
    def _calcular_dias_desde_ultimo_acceso(self) -> int:
        """Calcular días desde el último acceso"""
        if not self.fecha_ultimo_acceso:
            return 0
        
        from datetime import datetime
        ahora = datetime.utcnow()
        
        # Normalizar ambas fechas para evitar problemas de timezone
        if self.fecha_ultimo_acceso.tzinfo is not None:
            # Si la fecha de último acceso tiene timezone, convertir a naive
            fecha_ultimo_acceso = self.fecha_ultimo_acceso.replace(tzinfo=None)
        else:
            fecha_ultimo_acceso = self.fecha_ultimo_acceso
        
        # Asegurar que ahora también sea naive
        ahora = ahora.replace(tzinfo=None)
        
        diferencia = ahora - fecha_ultimo_acceso
        return diferencia.days