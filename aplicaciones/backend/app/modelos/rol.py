# app/modelos/rol.py
"""
Modelo de Rol para C4A SaaS
Sistema de permisos basado en roles con soporte para niveles de suscripción
"""

from sqlalchemy import Column, String, Enum, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum

from .base import ModeloConUUID
from ..core.config import NivelSuscripcion


class TipoRol(str, enum.Enum):
    """Tipos de roles disponibles"""
    ADMIN_SISTEMA = "admin_sistema"
    ADMIN_EMPRESA = "admin_empresa"
    EVALUADOR = "evaluador"
    USUARIO_BASICO = "usuario_basico"
    AUDITOR = "auditor"


class Rol(ModeloConUUID):
    """Modelo de rol con sistema de permisos"""
    __tablename__ = "roles"
    
    # Información básica
    nombre = Column(Enum(TipoRol), unique=True, nullable=False)
    nombre_mostrar = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Permisos (JSONB para flexibilidad)
    permisos = Column(Text, nullable=False, default="[]")  # JSON como string
    
    # Niveles de suscripción disponibles para este rol
    niveles_disponibles = Column(ARRAY(String), default=["gratuito", "pro", "empresarial"], nullable=False)
    
    # Estado
    esta_activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="rol")
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre}', activo={self.esta_activo})>"
    
    def tiene_permiso(self, recurso: str, accion: str) -> bool:
        """Verificar si el rol tiene un permiso específico"""
        import json
        
        try:
            permisos = json.loads(self.permisos)
        except (json.JSONDecodeError, TypeError):
            return False
        
        # Verificar permiso específico
        permiso_especifico = f"{recurso}:{accion}"
        if permiso_especifico in permisos:
            return True
        
        # Verificar permiso wildcard
        permiso_wildcard = f"{recurso}:*"
        if permiso_wildcard in permisos:
            return True
        
        # Verificar permiso global
        if "*:*" in permisos:
            return True
        
        return False
    
    def agregar_permiso(self, recurso: str, accion: str):
        """Agregar un permiso al rol"""
        import json
        
        try:
            permisos = json.loads(self.permisos)
        except (json.JSONDecodeError, TypeError):
            permisos = []
        
        permiso = f"{recurso}:{accion}"
        if permiso not in permisos:
            permisos.append(permiso)
            self.permisos = json.dumps(permisos)
    
    def remover_permiso(self, recurso: str, accion: str):
        """Remover un permiso del rol"""
        import json
        
        try:
            permisos = json.loads(self.permisos)
        except (json.JSONDecodeError, TypeError):
            return
        
        permiso = f"{recurso}:{accion}"
        if permiso in permisos:
            permisos.remove(permiso)
            self.permisos = json.dumps(permisos)
    
    def es_compatible_con_nivel(self, nivel: NivelSuscripcion) -> bool:
        """Verificar si el rol es compatible con un nivel de suscripción"""
        return nivel.value in self.niveles_disponibles
    
    def obtener_permisos_lista(self) -> list:
        """Obtener lista de permisos"""
        import json
        
        try:
            return json.loads(self.permisos)
        except (json.JSONDecodeError, TypeError):
            return []
    
    @classmethod
    def crear_rol_admin_sistema(cls):
        """Crear rol de administrador del sistema"""
        return cls(
            nombre=TipoRol.ADMIN_SISTEMA,
            nombre_mostrar="Administrador Sistema",
            descripcion="Acceso total al sistema",
            permisos='["*:*"]',
            niveles_disponibles=["gratuito", "pro", "empresarial"]
        )
    
    @classmethod
    def crear_rol_admin_empresa(cls):
        """Crear rol de administrador de empresa"""
        return cls(
            nombre=TipoRol.ADMIN_EMPRESA,
            nombre_mostrar="Administrador Empresa",
            descripcion="Gestión completa de la organización",
            permisos='["organizaciones:*", "usuarios:*", "evaluaciones:*", "reportes:*", "suscripciones:*"]',
            niveles_disponibles=["pro", "empresarial"]
        )
    
    @classmethod
    def crear_rol_evaluador(cls):
        """Crear rol de evaluador"""
        return cls(
            nombre=TipoRol.EVALUADOR,
            nombre_mostrar="Evaluador",
            descripcion="Crear y responder evaluaciones",
            permisos='["evaluaciones:crear", "evaluaciones:responder", "evaluaciones:ver", "reportes:ver"]',
            niveles_disponibles=["gratuito", "pro", "empresarial"]
        )
    
    @classmethod
    def crear_rol_usuario_basico(cls):
        """Crear rol de usuario básico"""
        return cls(
            nombre=TipoRol.USUARIO_BASICO,
            nombre_mostrar="Usuario Básico",
            descripcion="Solo lectura",
            permisos='["evaluaciones:ver", "reportes:ver"]',
            niveles_disponibles=["gratuito", "pro", "empresarial"]
        )
    
    @classmethod
    def crear_rol_auditor(cls):
        """Crear rol de auditor"""
        return cls(
            nombre=TipoRol.AUDITOR,
            nombre_mostrar="Auditor",
            descripcion="Acceso de solo lectura para auditorías",
            permisos='["evaluaciones:ver", "reportes:ver", "logs:ver"]',
            niveles_disponibles=["empresarial"]
        )