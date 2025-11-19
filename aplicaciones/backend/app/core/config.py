# app/core/config.py
"""
Configuración central para C4A SaaS
Configuración por niveles de suscripción y localización Chile
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
import os

class NivelSuscripcion(str, Enum):
    """Niveles de suscripción disponibles"""
    GRATUITO = "gratuito"
    PRO = "pro"
    EMPRESARIAL = "empresarial"

class ConfiguracionSeguridad(BaseSettings):
    """Configuración de seguridad y autenticación"""
    
    # Configuración general
    entorno: str = "produccion"
    debug: bool = False
    habilitar_security_middleware: bool = True
    
    # Configuración de email para notificaciones
    email_user: str = ""  # Requerido desde variable de entorno
    email_password: str = ""  # Requerido desde variable de entorno
    
    # Base de datos
    url_base_datos: str = ""  # Requerido desde variable de entorno
    ssl_requerido: bool = False
    
    # Redis
    url_redis: str = "redis://localhost:6379/0"
    ssl_redis: bool = False
    
    # JWT y autenticación
    algoritmo_jwt: str = "RS256"
    clave_publica_jwt: str = ""  # Requerido desde variable de entorno
    clave_privada_jwt: str = ""  # Requerido desde variable de entorno
    tiempo_expiracion_acceso: int = 15  # minutos
    tiempo_expiracion_refresco: int = 10080  # 7 días en minutos
    
    # Cifrado
    clave_maestra_cifrado: str = ""  # Requerido desde variable de entorno
    
    # Rate limiting por nivel
    limite_velocidad_gratuito: int = 100  # por hora
    limite_velocidad_pro: int = 1000
    limite_velocidad_empresarial: int = 10000
    
    # Headers de seguridad
    headers_seguridad: Dict[str, str] = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # Stripe
    stripe_clave_publica: str = ""
    stripe_clave_secreta: str = ""
    stripe_webhook_secreto: str = ""
    
    # Email
    servidor_smtp: str = "smtp.gmail.com"
    puerto_smtp: int = 587
    usuario_smtp: str = ""
    contraseña_smtp: str = ""
    email_desde: str = "noreply@c4a.cl"
    
    # CORS
    cors_origins: str = "https://c4a.cl,https://app.c4a.cl"
    
    # Configuración Chile
    pais_default: str = "CL"
    zona_horaria: str = "America/Santiago"
    idioma_default: str = "es_CL"
    moneda_default: str = "CLP"
    
    # Precios en CLP (centavos)
    precio_pro_mensual: int = 3200000  # $32.000 CLP
    precio_empresarial_mensual: int = 24000000  # $240.000 CLP
    
    # Límites por nivel
    max_usuarios_gratuito: int = 1
    max_evaluaciones_gratuito: int = 1
    max_preguntas_gratuito: int = 10
    dias_retencion_gratuito: int = 30
    max_recomendaciones_gratuito: int = 3
    
    max_usuarios_pro: int = 10
    max_evaluaciones_pro: int = 50
    max_preguntas_pro: int = 50
    dias_retencion_pro: int = 365
    max_recomendaciones_pro: int = 15
    
    max_usuarios_empresarial: int = 100
    max_evaluaciones_empresarial: int = 1000
    max_preguntas_empresarial: int = 100
    dias_retencion_empresarial: int = 2555  # 7 años
    max_recomendaciones_empresarial: int = 50
    
    # Archivos
    directorio_uploads: str = "uploads"
    directorio_reportes: str = "reportes"
    max_tamaño_archivo: int = 10485760  # 10MB
    
    # Desarrollo (defaults seguros para producción)
    saltar_verificacion_email: bool = False
    saltar_webhooks_stripe: bool = False
    simular_servicios_externos: bool = False

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Ignorar variables de entorno extra que no están en el modelo
    }
    
    def __init__(self, **kwargs):
        """Inicializar configuración validando variables críticas"""
        super().__init__(**kwargs)
        
        # Verificar si las claves JWT están en archivos si no están en variables de entorno
        if not self.clave_publica_jwt or not self.clave_privada_jwt:
            import os
            pub_file = os.getenv("JWT_PUBLIC_KEY_FILE", "jwt_public.pem")
            priv_file = os.getenv("JWT_PRIVATE_KEY_FILE", "jwt_private.pem")
            
            if os.path.exists(pub_file) and os.path.exists(priv_file):
                try:
                    with open(pub_file, 'r') as f:
                        self.clave_publica_jwt = f.read()
                    with open(priv_file, 'r') as f:
                        self.clave_privada_jwt = f.read()
                except Exception as e:
                    print(f"Advertencia: No se pudieron cargar claves desde archivos: {e}")
        
        # Validar que las variables críticas estén configuradas
        if not self.clave_publica_jwt or not self.clave_privada_jwt:
            raise ValueError(
                "CLAVE_PUBLICA_JWT y CLAVE_PRIVADA_JWT deben estar configuradas en variables de entorno o en archivos (jwt_public.pem, jwt_private.pem)"
            )
        if not self.url_base_datos:
            raise ValueError(
                "URL_BASE_DATOS debe estar configurada en variables de entorno"
            )
        if not self.clave_maestra_cifrado:
            raise ValueError(
                "CLAVE_MAESTRA_CIFRADO debe estar configurada en variables de entorno"
            )
    
    @field_validator('url_base_datos')
    @classmethod
    def validar_url_base_datos(cls, v):
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('URL de base de datos debe ser PostgreSQL')
        return v
    
    @field_validator('url_redis')
    @classmethod
    def validar_url_redis(cls, v):
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError('URL de Redis debe ser válida')
        return v

# Configuración de límites por nivel
LIMITES_POR_NIVEL = {
    NivelSuscripcion.GRATUITO: {
        "max_usuarios": 1,
        "max_evaluaciones_mes": 1,
        "max_preguntas": 10,
        "dias_retencion": 30,
        "max_recomendaciones": 3,
        "limite_velocidad": 100
    },
    NivelSuscripcion.PRO: {
        "max_usuarios": 10,
        "max_evaluaciones_mes": 50,
        "max_preguntas": 50,
        "dias_retencion": 365,
        "max_recomendaciones": 15,
        "limite_velocidad": 1000
    },
    NivelSuscripcion.EMPRESARIAL: {
        "max_usuarios": 100,
        "max_evaluaciones_mes": 1000,
        "max_preguntas": 100,
        "dias_retencion": 2555,
        "max_recomendaciones": 50,
        "limite_velocidad": 10000
    }
}

# Configuración de precios
PRECIOS_CLP = {
    NivelSuscripcion.GRATUITO: 0,
    NivelSuscripcion.PRO: 3200000,  # $32.000 CLP
    NivelSuscripcion.EMPRESARIAL: 24000000  # $240.000 CLP
}

# Configuración de características por nivel
CARACTERISTICAS_POR_NIVEL = {
    NivelSuscripcion.GRATUITO: [
        "10 preguntas básicas",
        "3 recomendaciones prioritarias",
        "1 evaluación por mes",
        "Reporte con marca de agua",
        "Soporte por email"
    ],
    NivelSuscripcion.PRO: [
        "50 preguntas detalladas",
        "15 recomendaciones priorizadas",
        "50 evaluaciones por mes",
        "Benchmarking sectorial",
        "Dashboard interactivo",
        "Reportes sin marca de agua",
        "Soporte prioritario"
    ],
    NivelSuscripcion.EMPRESARIAL: [
        "100 preguntas completas",
        "50+ recomendaciones detalladas",
        "1000 evaluaciones por mes",
        "SSO y gestión multi-usuario",
        "API completa",
        "Marca blanca",
        "Soporte dedicado",
        "Consultoría personalizada"
    ]
}

# Instancia global de configuración
config = ConfiguracionSeguridad()