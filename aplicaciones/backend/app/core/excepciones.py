# app/core/excepciones.py
"""
Excepciones personalizadas para C4A SaaS
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class ExcepcionC4A(Exception):
    """Excepción base para C4A SaaS"""
    
    def __init__(
        self,
        mensaje: str,
        codigo_error: str = "ERROR_GENERAL",
        detalles: Optional[Dict[str, Any]] = None
    ):
        self.mensaje = mensaje
        self.codigo_error = codigo_error
        self.detalles = detalles or {}
        super().__init__(self.mensaje)


class ExcepcionAutenticacion(ExcepcionC4A):
    """Excepción de autenticación"""
    
    def __init__(self, mensaje: str = "Credenciales inválidas"):
        super().__init__(mensaje, "ERROR_AUTENTICACION")


class ExcepcionAutorizacion(ExcepcionC4A):
    """Excepción de autorización"""
    
    def __init__(self, mensaje: str = "No tiene permisos para realizar esta acción"):
        super().__init__(mensaje, "ERROR_AUTORIZACION")


class ExcepcionNivelSuscripcion(ExcepcionC4A):
    """Excepción de nivel de suscripción"""
    
    def __init__(self, mensaje: str = "Nivel de suscripción insuficiente"):
        super().__init__(mensaje, "ERROR_NIVEL_SUSCRIPCION")


class ExcepcionLimiteUso(ExcepcionC4A):
    """Excepción de límite de uso"""
    
    def __init__(self, mensaje: str = "Límite de uso excedido"):
        super().__init__(mensaje, "ERROR_LIMITE_USO")


class ExcepcionValidacion(ExcepcionC4A):
    """Excepción de validación"""
    
    def __init__(self, mensaje: str = "Datos inválidos"):
        super().__init__(mensaje, "ERROR_VALIDACION")


class ExcepcionRecursoNoEncontrado(ExcepcionC4A):
    """Excepción de recurso no encontrado"""
    
    def __init__(self, mensaje: str = "Recurso no encontrado"):
        super().__init__(mensaje, "ERROR_RECURSO_NO_ENCONTRADO")


class ExcepcionBaseDatos(ExcepcionC4A):
    """Excepción de base de datos"""
    
    def __init__(self, mensaje: str = "Error en base de datos"):
        super().__init__(mensaje, "ERROR_BASE_DATOS")


class ExcepcionServicioExterno(ExcepcionC4A):
    """Excepción de servicio externo"""
    
    def __init__(self, mensaje: str = "Error en servicio externo"):
        super().__init__(mensaje, "ERROR_SERVICIO_EXTERNO")


def convertir_excepcion_c4a_a_http(excepcion: ExcepcionC4A) -> HTTPException:
    """Convertir excepción C4A a HTTPException"""
    
    mapeo_codigos = {
        "ERROR_AUTENTICACION": status.HTTP_401_UNAUTHORIZED,
        "ERROR_AUTORIZACION": status.HTTP_403_FORBIDDEN,
        "ERROR_NIVEL_SUSCRIPCION": status.HTTP_402_PAYMENT_REQUIRED,
        "ERROR_LIMITE_USO": status.HTTP_429_TOO_MANY_REQUESTS,
        "ERROR_VALIDACION": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "ERROR_RECURSO_NO_ENCONTRADO": status.HTTP_404_NOT_FOUND,
        "ERROR_BASE_DATOS": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "ERROR_SERVICIO_EXTERNO": status.HTTP_502_BAD_GATEWAY,
        "ERROR_GENERAL": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    codigo_http = mapeo_codigos.get(excepcion.codigo_error, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=codigo_http,
        detail={
            "mensaje": excepcion.mensaje,
            "codigo_error": excepcion.codigo_error,
            "detalles": excepcion.detalles
        }
    )