"""
Sistema de rate limiting por niveles de suscripción
"""
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import redis
from app.core.config import ConfiguracionSeguridad

class RateLimiter:
    """Rate limiter por niveles de suscripción"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.limits = {
            "gratuito": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "requests_per_day": 10000,
                "evaluaciones_per_month": 1,
                "reportes_per_month": 1
            },
            "pro": {
                "requests_per_minute": 300,
                "requests_per_hour": 5000,
                "requests_per_day": 50000,
                "evaluaciones_per_month": 10,
                "reportes_per_month": 10
            },
            "empresarial": {
                "requests_per_minute": 1000,
                "requests_per_hour": 20000,
                "requests_per_day": 200000,
                "evaluaciones_per_month": 100,
                "reportes_per_month": 100
            }
        }
    
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
    
    def get_rate_limit_key(self, identifier: str, limit_type: str, window: str) -> str:
        """Generar clave para rate limiting"""
        return f"rate_limit:{limit_type}:{identifier}:{window}"
    
    def check_rate_limit(
        self, 
        identifier: str, 
        limit_type: str, 
        window: str, 
        limit: int
    ) -> Dict[str, any]:
        """Verificar rate limit"""
        key = self.get_rate_limit_key(identifier, limit_type, window)
        
        # Obtener timestamp actual
        now = int(time.time())
        
        # Configurar ventana de tiempo
        if window == "minute":
            window_seconds = 60
        elif window == "hour":
            window_seconds = 3600
        elif window == "day":
            window_seconds = 86400
        else:
            window_seconds = 60
        
        # Usar pipeline para operaciones atómicas
        pipe = self.redis.pipeline()
        
        # Limpiar entradas expiradas
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        
        # Contar requests en la ventana
        pipe.zcard(key)
        
        # Agregar request actual
        pipe.zadd(key, {str(now): now})
        
        # Establecer expiración
        pipe.expire(key, window_seconds)
        
        results = pipe.execute()
        current_requests = results[1]
        
        # Verificar si se excedió el límite
        if current_requests >= limit:
            return {
                "allowed": False,
                "current_requests": current_requests,
                "limit": limit,
                "window": window,
                "reset_time": now + window_seconds
            }
        
        return {
            "allowed": True,
            "current_requests": current_requests + 1,
            "limit": limit,
            "window": window,
            "reset_time": now + window_seconds
        }
    
    def check_api_rate_limit(
        self, 
        request: Request, 
        nivel_suscripcion: str
    ) -> Dict[str, any]:
        """Verificar rate limit para API"""
        client_ip = self.get_client_ip(request)
        limits = self.limits.get(nivel_suscripcion, self.limits["gratuito"])
        
        # Verificar límites por minuto
        minute_result = self.check_rate_limit(
            client_ip, "api", "minute", limits["requests_per_minute"]
        )
        
        if not minute_result["allowed"]:
            return minute_result
        
        # Verificar límites por hora
        hour_result = self.check_rate_limit(
            client_ip, "api", "hour", limits["requests_per_hour"]
        )
        
        if not hour_result["allowed"]:
            return hour_result
        
        # Verificar límites por día
        day_result = self.check_rate_limit(
            client_ip, "api", "day", limits["requests_per_day"]
        )
        
        return day_result
    
    def check_evaluation_limit(
        self, 
        organizacion_id: str, 
        nivel_suscripcion: str
    ) -> Dict[str, any]:
        """Verificar límite de evaluaciones por mes"""
        limits = self.limits.get(nivel_suscripcion, self.limits["gratuito"])
        
        # Obtener mes actual
        now = time.time()
        month_key = time.strftime("%Y-%m", time.localtime(now))
        
        key = f"evaluations:{organizacion_id}:{month_key}"
        
        # Obtener contador actual
        current_count = self.redis.get(key)
        current_count = int(current_count) if current_count else 0
        
        # Verificar límite
        if current_count >= limits["evaluaciones_per_month"]:
            return {
                "allowed": False,
                "current_evaluations": current_count,
                "limit": limits["evaluaciones_per_month"],
                "period": "month"
            }
        
        # Incrementar contador
        self.redis.incr(key)
        self.redis.expire(key, 2678400)  # 31 días en segundos
        
        return {
            "allowed": True,
            "current_evaluations": current_count + 1,
            "limit": limits["evaluaciones_per_month"],
            "period": "month"
        }
    
    def check_report_limit(
        self, 
        organizacion_id: str, 
        nivel_suscripcion: str
    ) -> Dict[str, any]:
        """Verificar límite de reportes por mes"""
        limits = self.limits.get(nivel_suscripcion, self.limits["gratuito"])
        
        # Obtener mes actual
        now = time.time()
        month_key = time.strftime("%Y-%m", time.localtime(now))
        
        key = f"reports:{organizacion_id}:{month_key}"
        
        # Obtener contador actual
        current_count = self.redis.get(key)
        current_count = int(current_count) if current_count else 0
        
        # Verificar límite
        if current_count >= limits["reportes_per_month"]:
            return {
                "allowed": False,
                "current_reports": current_count,
                "limit": limits["reportes_per_month"],
                "period": "month"
            }
        
        # Incrementar contador
        self.redis.incr(key)
        self.redis.expire(key, 2678400)  # 31 días en segundos
        
        return {
            "allowed": True,
            "current_reports": current_count + 1,
            "limit": limits["reportes_per_month"],
            "period": "month"
        }
    
    def get_usage_stats(self, organizacion_id: str) -> Dict[str, any]:
        """Obtener estadísticas de uso"""
        now = time.time()
        month_key = time.strftime("%Y-%m", time.localtime(now))
        
        # Obtener contadores
        evaluations_key = f"evaluations:{organizacion_id}:{month_key}"
        reports_key = f"reports:{organizacion_id}:{month_key}"
        
        evaluations_count = self.redis.get(evaluations_key)
        reports_count = self.redis.get(reports_key)
        
        return {
            "evaluations_this_month": int(evaluations_count) if evaluations_count else 0,
            "reports_this_month": int(reports_count) if reports_count else 0,
            "period": month_key
        }

# Instancia global del rate limiter
rate_limiter: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    """Obtener instancia del rate limiter"""
    global rate_limiter
    if rate_limiter is None:
        import redis
        redis_client = redis.Redis.from_url(ConfiguracionSeguridad().url_redis)
        rate_limiter = RateLimiter(redis_client)
    return rate_limiter
