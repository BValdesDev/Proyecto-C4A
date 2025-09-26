"""
Middleware de seguridad para C4A SaaS
"""
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
from typing import Callable
from app.core.rate_limiting import get_rate_limiter
from app.core.config import ConfiguracionSeguridad
from app.modelos.log_auditoria import LogAuditoria
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from sqlalchemy.orm import Session
from app.modelos.base import obtener_sesion

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de seguridad principal"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config = ConfiguracionSeguridad()
        self.rate_limiter = get_rate_limiter()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesar request con middleware de seguridad"""
        
        # Generar ID único para el request
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Obtener timestamp de inicio
        start_time = time.time()
        
        # Obtener información del request
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # Verificar rate limiting
        if request.url.path.startswith("/api/"):
            try:
                # Obtener nivel de suscripción del usuario (si está autenticado)
                nivel_suscripcion = await self.get_user_subscription_level(request)
                
                # Verificar rate limit
                rate_limit_result = self.rate_limiter.check_api_rate_limit(
                    request, nivel_suscripcion
                )
                
                if not rate_limit_result["allowed"]:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": f"Too many requests. Limit: {rate_limit_result['limit']} per {rate_limit_result['window']}",
                            "retry_after": rate_limit_result["reset_time"] - int(time.time()),
                            "request_id": request_id
                        },
                        headers={
                            "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                            "X-RateLimit-Remaining": str(rate_limit_result["limit"] - rate_limit_result["current_requests"]),
                            "X-RateLimit-Reset": str(rate_limit_result["reset_time"]),
                            "Retry-After": str(rate_limit_result["reset_time"] - int(time.time()))
                        }
                    )
                
                # Agregar headers de rate limit
                request.state.rate_limit_headers = {
                    "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                    "X-RateLimit-Remaining": str(rate_limit_result["limit"] - rate_limit_result["current_requests"]),
                    "X-RateLimit-Reset": str(rate_limit_result["reset_time"])
                }
                
            except Exception as e:
                # En caso de error en rate limiting, continuar pero loggear
                print(f"Error en rate limiting: {e}")
        
        # Procesar request
        try:
            response = await call_next(request)
        except Exception as e:
            # Loggear error
            await self.log_request(
                request, client_ip, user_agent, start_time, 
                success=False, error_message=str(e)
            )
            raise
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Agregar headers de seguridad
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Agregar headers de rate limit si existen
        if hasattr(request.state, "rate_limit_headers"):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value
        
        # Loggear request exitoso
        await self.log_request(
            request, client_ip, user_agent, start_time, 
            success=True, response_status=response.status_code
        )
        
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Obtener IP del cliente"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def get_user_subscription_level(self, request: Request) -> str:
        """Obtener nivel de suscripción del usuario"""
        try:
            # Intentar obtener usuario del token JWT
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
                
                # Decodificar token (simplificado)
                from app.core.seguridad import decode_token
                payload = decode_token(token)
                
                if payload and "usuario_id" in payload:
                    # Obtener usuario de la base de datos
                    db = next(obtener_sesion())
                    try:
                        usuario = db.query(Usuario).filter(
                            Usuario.id == payload["usuario_id"]
                        ).first()
                        
                        if usuario and usuario.organizacion:
                            return usuario.organizacion.nivel_suscripcion
                    finally:
                        db.close()
            
            return "gratuito"  # Default para usuarios no autenticados
            
        except Exception:
            return "gratuito"  # Default en caso de error
    
    async def log_request(
        self, 
        request: Request, 
        client_ip: str, 
        user_agent: str, 
        start_time: float,
        success: bool,
        response_status: int = None,
        error_message: str = None
    ):
        """Loggear request para auditoría"""
        try:
            # Obtener información del request
            method = request.method
            path = request.url.path
            query_params = str(request.query_params) if request.query_params else None
            
            # Determinar tipo de evento
            if path.startswith("/api/auth/"):
                tipo_evento = "autenticacion"
            elif path.startswith("/api/evaluaciones/"):
                tipo_evento = "evaluacion"
            elif path.startswith("/api/reportes/"):
                tipo_evento = "reporte"
            elif path.startswith("/api/suscripciones/"):
                tipo_evento = "suscripcion"
            else:
                tipo_evento = "api"
            
            # Crear log de auditoría
            log_data = {
                "tipo_evento": tipo_evento,
                "accion": f"{method} {path}",
                "ip_address": client_ip,
                "user_agent": user_agent,
                "exitoso": success,
                "mensaje_error": error_message,
                "metadatos": {
                    "method": method,
                    "path": path,
                    "query_params": query_params,
                    "response_status": response_status,
                    "process_time": time.time() - start_time,
                    "request_id": getattr(request.state, "request_id", None)
                }
            }
            
            # Obtener usuario si está autenticado
            try:
                authorization = request.headers.get("Authorization")
                if authorization and authorization.startswith("Bearer "):
                    token = authorization.split(" ")[1]
                    from app.core.seguridad import decode_token
                    payload = decode_token(token)
                    
                    if payload and "usuario_id" in payload:
                        log_data["usuario_id"] = payload["usuario_id"]
                        log_data["organizacion_id"] = payload.get("organizacion_id")
            except Exception:
                pass  # Ignorar errores de autenticación en logs
            
            # Guardar log en base de datos
            db = next(obtener_sesion())
            try:
                log = LogAuditoria(**log_data)
                db.add(log)
                db.commit()
            except Exception as e:
                print(f"Error guardando log de auditoría: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error en logging de auditoría: {e}")

class CORSMiddleware(BaseHTTPMiddleware):
    """Middleware CORS personalizado"""
    
    def __init__(self, app: ASGIApp, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Procesar CORS"""
        origin = request.headers.get("Origin")
        
        # Verificar origen
        if origin and origin in self.allowed_origins:
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return response
        
        # Para requests sin origen (como Postman)
        if not origin:
            response = await call_next(request)
            return response
        
        # Origen no permitido
        return JSONResponse(
            status_code=403,
            content={"error": "Origin not allowed"}
        )

class TrustedHostMiddleware(BaseHTTPMiddleware):
    """Middleware para verificar hosts confiables"""
    
    def __init__(self, app: ASGIApp, allowed_hosts: list):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Verificar host confiable"""
        host = request.headers.get("Host")
        
        if host and host not in self.allowed_hosts:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid host"}
            )
        
        return await call_next(request)
