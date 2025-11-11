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
    entorno: str = "desarrollo"
    debug: bool = True
    habilitar_security_middleware: bool = True
    
    # Configuración de email para notificaciones
    email_user: str = "c4a.notifications@gmail.com"
    email_password: str = "c4a_notifications_2024"
    
    # Base de datos
    url_base_datos: str = "postgresql+asyncpg://c4a_user:c4a_password@localhost:5432/c4a_saas"
    ssl_requerido: bool = False
    
    # Redis
    url_redis: str = "redis://localhost:6379/0"
    ssl_redis: bool = False
    
    # JWT y autenticación
    algoritmo_jwt: str = "RS256"
    clave_publica_jwt: str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz647gWvwfmIsqEYQqefy
RTAtP8w7PceHuUQQti92NG/qLSeSg/EfacP6wT4//2qR3T0pIZn2JKgW+ezbQLbQ
kJCDgcPdpb42Axu/MDmpnBJVkIzrxrEB76zx+5fcHB4UylUKGc7e6bs8qvdF90UT
ynM1wPhuti5Z3x7fshPLxprpuqHLAV3vPlw56AFl6x30DwPPW47rvUaRyP6lGxVM
9LJF1P6o53m544Hx714QktnYXA45GtYkH2E+0V6W3XnOlbtMoBcZRQEPwwT5zxip
lt1xXJtcDy/lHZFgrPNOa0adnpu99x4VZR4JmHypOhNu9uKCESz6og1W+X/xb45Y
mwIDAQAB
-----END PUBLIC KEY-----"""
    clave_privada_jwt: str = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDPrjuBa/B+Yiyo
RhCp5/JFMC0/zDs9x4e5RBC2L3Y0b+otJ5KD8R9pw/rBPj//apHdPSkhmfYkqBb5
7NtAttCQkIOBw92lvjYDG78wOamcElWQjOvGsQHvrPH7l9wcHhTKVQoZzt7puzyq
90X3RRPKczXA+G62LlnfHt+yE8vGmum6ocsBXe8+XDnoAWXrHfQPA89bjuu9RpHI
/qUbFUz0skXU/qjnebnjgfHvXhCS2dhcDjka1iQfYT7RXpbdec6Vu0ygFxlFAQ/D
BPnPGKmW3XFcm1wPL+UdkWCs805rRp2em733HhVlHgmYfKk6E2724oIRLPqiDVb5
f/FvjlibAgMBAAECggEABDmOgw3/uPXlCIgryVNY+krqrU6AhJcmUneW77puu2B/
LLSy4bD3+Pvpb+o7xlgK3yurIcCAs7xX8HTsj3ytKMltiSgxPlUjebiR2i+DQZPm
wv5lMKN/VhYTqUfROmoPrFrnO8WZp7rfcm8052F83V2uxnlnVE+Wppf5jNwRPD3S
trCBd7IiIjZxqQvbJF78Lo8UhlDWEYSG8DXhcXIVdNM/1T5ezQFfy9YBa7SHas1T
GiW2VZYrCEt1csfCsgdyH9vM5uFtNJrzwl4kbZDmBtHFyb3/qbiJtHRfBa7G/1SY
4sJrXOoVURQfT6SA5C5drnobDkyyVRhBlpdoVXW65QKBgQDqn0QJkV10vvJzbkwT
0IGT1W6W2XMmhqm5JLoM2OPcQlJPWjKNlB5SDkaDLNy3ljCi43wgjoFr1cP/bgMV
vCXWZSDQN85ZQHfwTjx6dWKVJsA3FThZKNIhB3jmgEm/GIb6Vh9nBN1OIcvgtwzx
PCTOBdzwtDtUvdR/IXjVd0yVPwKBgQDimokUh0yCRstbrLMMhdB1DON6ppPKI0hs
CayOZy29/Mh8W63M9yC2wLXuc62cinXZVef1YQtYspSrfS9N0djQ3Si0+f1TXvyQ
ncU0LUdkP29q883jF7QbC0lyMgW/lMVGR0LjqIBYtlnViRNWlw68UgR94LcZPOO3
i7AjzKEZpQKBgQCwerwitkUl27tjOEPhY6UUHibhMQ98my5vJUENCNfchcaECcSc
2h00e6huYwBi14YeAB8OHiMbid+z8nw/jRao/ciA1nlQiT2udCrpsgJFTrCmvj90
UVA9p/E48KaIJ1rgUoesZexRKPrCPO5vRl4o2iAmrmsygtekCPlrGCFy4QKBgAYD
Sb3ktTADxuOg2oNrjZN9iw+3GdbURtivDQgeTsVqzrsWB6+XoyOWS32PTj0II4Zn
1Cbbs1xgKLfAM6AiAFnSdIEQ3Rr4O0VvGkt/JBTR5hf1bjInb90D2KgSEbr6rJ1n
yKuXzggMlqem4n96tKZkmr/oVZNy3SwCpeLdTC0NAoGAfY1XnW68Z7nbo6UcE+3k
999BVlXciKSbc4M+08Df+UMhZfRpvoFaosoxWBaiAgssMuysiZefLaAMuAbkmUbY
Kl9FSvf+BHBYPteFpNSvHQivk1Sl7i6v00XKQGITCIvG3rFBjFuyGJCvBi8CF4+B
Qn6caGISM5fcqWt4bvr6eh8=
-----END PRIVATE KEY-----"""
    tiempo_expiracion_acceso: int = 15  # minutos
    tiempo_expiracion_refresco: int = 10080  # 7 días en minutos
    
    # Cifrado
    clave_maestra_cifrado: str = "clave-maestra-desarrollo"
    
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
    
    # Desarrollo
    saltar_verificacion_email: bool = True
    saltar_webhooks_stripe: bool = True
    simular_servicios_externos: bool = True

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }
    
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