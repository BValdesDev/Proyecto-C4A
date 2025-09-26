# app/main.py
"""
Aplicación principal FastAPI para C4A SaaS
Configuración de seguridad, middleware y rutas
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging
from typing import Dict, Any

from .core.config import config
from .core.excepciones import ExcepcionC4A, convertir_excepcion_c4a_a_http
from .api.v1.endpoints import auth, usuarios, organizaciones, evaluaciones, reportes, suscripciones
from .modelos.base import crear_tablas


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando C4A SaaS API...")
    
    # Crear tablas si no existen
    try:
        crear_tablas()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Cerrando C4A SaaS API...")


# Crear aplicación FastAPI
app = FastAPI(
    title="C4A SaaS API",
    description="API para la plataforma de evaluación de ciberseguridad C4A SaaS",
    version="1.0.0",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    lifespan=lifespan
)

# Configurar middleware de seguridad personalizado
from .core.middleware import SecurityMiddleware, CORSMiddleware as CustomCORSMiddleware, TrustedHostMiddleware as CustomTrustedHostMiddleware

# Deshabilitar TrustedHostMiddleware en desarrollo
if not config.debug:
    app.add_middleware(
        CustomTrustedHostMiddleware,
        allowed_hosts=["c4a.cl", "*.c4a.cl", "localhost", "127.0.0.1"]
    )

# Middleware CORS personalizado (deshabilitado temporalmente para desarrollo)
# app.add_middleware(
#     CustomCORSMiddleware,
#     allowed_origins=[
#         "https://c4a.cl",
#         "https://app.c4a.cl",
#         "http://localhost:3000",
#         "http://localhost:5173"
#     ] if not config.debug else ["*"]
# )

# Usar middleware CORS estándar de FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.debug else ["https://c4a.cl", "https://app.c4a.cl"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de seguridad principal (deshabilitado temporalmente para desarrollo)
# app.add_middleware(SecurityMiddleware)

# Middleware para agregar headers de seguridad (deshabilitado temporalmente para desarrollo)
# @app.middleware("http")
# async def agregar_headers_seguridad(request: Request, call_next):
#     """Agregar headers de seguridad a todas las respuestas"""
#     start_time = time.time()
#     
#     response = await call_next(request)
#     
#     # Agregar headers de seguridad
#     for header, valor in config.headers_seguridad.items():
#         response.headers[header] = valor
#     
#     # Agregar tiempo de procesamiento
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     
#     return response

# Middleware para logging de requests (deshabilitado temporalmente para desarrollo)
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     """Log de requests para auditoría"""
#     start_time = time.time()
#     
#     # Obtener información del request
#     client_ip = request.client.host if request.client else "unknown"
#     user_agent = request.headers.get("user-agent", "unknown")
#     
#     response = await call_next(request)
#     
#     # Calcular tiempo de procesamiento
#     process_time = time.time() - start_time
#     
#     # Log del request
#     logger.info(
#         f"{request.method} {request.url.path} - "
#         f"Status: {response.status_code} - "
#         f"Time: {process_time:.3f}s - "
#         f"IP: {client_ip}"
#     )
#     
#     return response

# Manejador de excepciones personalizadas
@app.exception_handler(ExcepcionC4A)
async def excepcion_c4a_handler(request: Request, exc: ExcepcionC4A):
    """Manejador de excepciones C4A"""
    logger.error(f"Excepción C4A: {exc.mensaje} - {exc.codigo_error}")
    return convertir_excepcion_c4a_a_http(exc)

# Manejador de excepciones de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador de excepciones de validación"""
    logger.error(f"Error de validación: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "mensaje": "Error de validación en los datos enviados",
            "codigo_error": "ERROR_VALIDACION",
            "detalles": exc.errors()
        }
    )

# Manejador de excepciones HTTP
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador de excepciones HTTP"""
    logger.error(f"Error HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "mensaje": exc.detail,
            "codigo_error": f"HTTP_{exc.status_code}"
        }
    )

# Manejador de excepciones generales
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador de excepciones generales"""
    logger.error(f"Error interno: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "mensaje": "Error interno del servidor",
            "codigo_error": "ERROR_INTERNO"
        }
    )

# Endpoint de salud
@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "entorno": config.entorno,
        "timestamp": time.time()
    }

# Endpoint raíz
@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "mensaje": "C4A SaaS API - Plataforma de Evaluación de Ciberseguridad",
        "version": "1.0.0",
        "documentacion": "/docs" if config.debug else "Documentación no disponible en producción",
        "salud": "/health"
    }

# Incluir routers de la API
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)

app.include_router(
    usuarios.router,
    prefix="/api/v1/usuarios",
    tags=["Usuarios"]
)

app.include_router(
    organizaciones.router,
    prefix="/api/v1/organizaciones",
    tags=["Organizaciones"]
)

app.include_router(
    evaluaciones.router,
    prefix="/api/v1/evaluaciones",
    tags=["Evaluaciones"]
)

app.include_router(
    reportes.router,
    prefix="/api/v1/reportes",
    tags=["Reportes"]
)

app.include_router(
    suscripciones.router,
    prefix="/api/v1/suscripciones",
    tags=["Suscripciones"]
)

# Configuración de logging para producción
if not config.debug:
    # Configurar logging para producción
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.debug,
        log_level="info" if config.debug else "warning"
    )