#!/usr/bin/env python3
"""
Sistema de blacklist de tokens JWT usando Redis
Permite revocar tokens antes de que expiren
"""
import hashlib
import time
from typing import Optional, Set
from datetime import datetime, timedelta
import redis
import json
from .config import ConfiguracionSeguridad

def get_config():
    """Obtener configuración (lazy loading para evitar imports circulares)"""
    return ConfiguracionSeguridad()

class TokenBlacklist:
    """Manejo de blacklist de tokens usando Redis"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Inicializar blacklist"""
        self.config = get_config()
        self.redis = redis_client
        self.prefix = "jwt_blacklist:"
        
        # Intentar conectar con Redis si no se proporciona
        if not self.redis:
            try:
                self.redis = redis.Redis.from_url(self.config.url_redis)
                self.redis.ping()
            except Exception as e:
                print(f"Redis no disponible para blacklist: {e}")
                self.redis = None
                # Fallback a memoria (solo para desarrollo)
                self._fallback_set: Set[str] = set()
    
    def _hash_token(self, token: str) -> str:
        """Crear hash del token para almacenamiento"""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
    
    def _get_redis_key(self, token_hash: str) -> str:
        """Obtener clave Redis para token"""
        return f"{self.prefix}{token_hash}"
    
    def revocar_token(self, token: str, expiracion: Optional[datetime] = None, motivo: str = "Usuario cerro sesión") -> bool:
        """
        Revocar token agregándolo a la blacklist
        
        Args:
            token: Token JWT a revocar
            expiracion: Fecha de expiración del token (para limpieza automática)
            motivo: Razón de la revocación
        
        Returns:
            True si se revocó exitosamente
        """
        token_hash = self._hash_token(token)
        
        if self.redis:
            try:
                # Calcular TTL hasta la expiración del token
                ttl = None
                if expiracion:
                    now = datetime.utcnow()
                    delta = expiracion - now
                    if delta.total_seconds() > 0:
                        ttl = int(delta.total_seconds()) + 60  # +1 minuto extra por seguridad
                
                # Almacenar en Redis con metadata
                metadata = {
                    "hash": token_hash,
                    "revoked_at": datetime.utcnow().isoformat(),
                    "motivo": motivo,
                    "expires_at": expiracion.isoformat() if expiracion else None
                }
                
                # Guardar en Redis
                if ttl:
                    self.redis.setex(
                        self._get_redis_key(token_hash),
                        ttl,
                        json.dumps(metadata)
                    )
                else:
                    # Si no hay expiración, usar TTL por defecto de 24 horas
                    self.redis.setex(
                        self._get_redis_key(token_hash),
                        86400,
                        json.dumps(metadata)
                    )
                
                return True
                
            except Exception as e:
                print(f"Error revocando token en Redis: {e}")
                return False
        else:
            # Fallback a memoria
            self._fallback_set.add(token_hash)
            print(f"Token revocado en memoria (fallback)")
            return True
    
    def revocar_token_por_jti(self, jti: str, expiracion: Optional[datetime] = None, motivo: str = "Usuario cerro sesión") -> bool:
        """
        Revocar token por su JTI (JWT ID)
        
        Args:
            jti: JWT ID del token
            expiracion: Fecha de expiración del token
            motivo: Razón de la revocación
        
        Returns:
            True si se revocó exitosamente
        """
        if self.redis:
            try:
                # Calcular TTL hasta la expiración del token
                ttl = None
                if expiracion:
                    now = datetime.utcnow()
                    delta = expiracion - now
                    if delta.total_seconds() > 0:
                        ttl = int(delta.total_seconds()) + 60  # +1 minuto extra
                
                metadata = {
                    "jti": jti,
                    "revoked_at": datetime.utcnow().isoformat(),
                    "motivo": motivo,
                    "expires_at": expiracion.isoformat() if expiracion else None
                }
                
                key = f"{self.prefix}jti:{jti}"
                
                if ttl:
                    self.redis.setex(key, ttl, json.dumps(metadata))
                else:
                    self.redis.setex(key, 86400, json.dumps(metadata))
                
                return True
                
            except Exception as e:
                print(f"Error revocando token por JTI en Redis: {e}")
                return False
        else:
            # Fallback a memoria
            self._fallback_set.add(jti)
            print(f"JTI revocado en memoria (fallback)")
            return True
    
    def is_token_revoked(self, token: str) -> bool:
        """
        Verificar si un token está revocado
        
        Args:
            token: Token JWT a verificar
        
        Returns:
            True si el token está revocado
        """
        token_hash = self._hash_token(token)
        
        if self.redis:
            try:
                return self.redis.exists(self._get_redis_key(token_hash)) > 0
            except Exception as e:
                print(f"Error verificando token en Redis: {e}")
                return False
        else:
            # Fallback a memoria
            return token_hash in self._fallback_set
    
    def is_jti_revoked(self, jti: str) -> bool:
        """
        Verificar si un JTI está revocado
        
        Args:
            jti: JWT ID a verificar
        
        Returns:
            True si el JTI está revocado
        """
        if self.redis:
            try:
                return self.redis.exists(f"{self.prefix}jti:{jti}") > 0
            except Exception as e:
                print(f"Error verificando JTI en Redis: {e}")
                return False
        else:
            # Fallback a memoria
            return jti in self._fallback_set
    
    def obtener_info_revocacion(self, token: str) -> Optional[dict]:
        """
        Obtener información sobre la revocación de un token
        
        Args:
            token: Token JWT
        
        Returns:
            Metadata de revocación o None si no está revocado
        """
        token_hash = self._hash_token(token)
        
        if self.redis:
            try:
                data = self.redis.get(self._get_redis_key(token_hash))
                if data:
                    return json.loads(data.decode('utf-8'))
            except Exception as e:
                print(f"Error obteniendo info de revocación: {e}")
        
        return None
    
    def revocar_todos_tokens_usuario(self, usuario_id: str, motivo: str = "Cambio de contraseña o seguridad") -> int:
        """
        Revocar todos los tokens de un usuario
        
        Args:
            usuario_id: ID del usuario
            motivo: Razón de la revocación
        
        Returns:
            Número de tokens revocados
        """
        if not self.redis:
            print("Redis no disponible para revocar todos los tokens")
            return 0
        
        try:
            # Buscar todos los tokens del usuario
            pattern = f"{self.prefix}user:{usuario_id}:*"
            keys = self.redis.keys(pattern)
            
            # Revocar cada token
            for key in keys:
                metadata_data = self.redis.get(key)
                if metadata_data:
                    try:
                        metadata = json.loads(metadata_data.decode('utf-8'))
                        metadata["revoked_at"] = datetime.utcnow().isoformat()
                        metadata["motivo_masivo"] = motivo
                        self.redis.set(key, json.dumps(metadata))
                    except Exception:
                        pass
            
            return len(keys)
            
        except Exception as e:
            print(f"Error revocando todos los tokens del usuario: {e}")
            return 0
    
    def limpiar_tokens_expirados(self) -> int:
        """
        Limpiar tokens expirados de la blacklist
        
        Returns:
            Número de tokens eliminados
        """
        if not self.redis:
            return 0
        
        try:
            pattern = f"{self.prefix}*"
            keys = self.redis.keys(pattern)
            
            eliminados = 0
            for key in keys:
                try:
                    ttl = self.redis.ttl(key)
                    if ttl < 0:  # Token expirado
                        self.redis.delete(key)
                        eliminados += 1
                except Exception:
                    pass
            
            return eliminados
            
        except Exception as e:
            print(f"Error limpiando tokens expirados: {e}")
            return 0
    
    def obtener_estadisticas(self) -> dict:
        """Obtener estadísticas de la blacklist"""
        if not self.redis:
            return {
                "total_revocados": len(self._fallback_set),
                "tipo": "memoria"
            }
        
        try:
            pattern = f"{self.prefix}*"
            keys = self.redis.keys(pattern)
            
            return {
                "total_revocados": len(keys),
                "tipo": "redis"
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                "total_revocados": 0,
                "tipo": "error"
            }

# Instancia global de blacklist
_token_blacklist: Optional[TokenBlacklist] = None

def obtener_blacklist() -> TokenBlacklist:
    """Obtener instancia de la blacklist"""
    global _token_blacklist
    if _token_blacklist is None:
        _token_blacklist = TokenBlacklist()
    return _token_blacklist

