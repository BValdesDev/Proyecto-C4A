# app/modelos/__init__.py
"""
Modelos de base de datos para C4A SaaS
"""

from .base import Base, ModeloConUUID, ModeloConEliminacionLogica, crear_tablas, obtener_sesion
from .organizacion import Organizacion, TamañoEmpresa, Sector
from .usuario import Usuario, EstadoCuenta
from .rol import Rol, TipoRol
from .framework import Framework
from .pregunta import Pregunta
from .cuestionario import Cuestionario, CuestionarioPregunta, NivelCuestionario, TipoSeccion
from .evaluacion import Evaluacion, EstadoEvaluacion
from .respuesta import Respuesta
from .sesion import Sesion
from .suscripcion import Suscripcion
from .reporte import Reporte
from .log_auditoria import LogAuditoria

__all__ = [
    "Base",
    "ModeloConUUID", 
    "ModeloConEliminacionLogica",
    "crear_tablas",
    "obtener_sesion",
    "Organizacion",
    "TamañoEmpresa",
    "Sector",
    "Usuario",
    "EstadoCuenta",
    "Rol",
    "TipoRol",
    "Framework",
    "Pregunta",
    "Cuestionario",
    "CuestionarioPregunta",
    "NivelCuestionario",
    "TipoSeccion",
    "Evaluacion",
    "EstadoEvaluacion",
    "Respuesta",
    "Sesion",
    "Suscripcion",
    "Reporte",
    "LogAuditoria"
]