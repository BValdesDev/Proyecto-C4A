#!/usr/bin/env python3
"""
Gestión segura de claves JWT con soporte para rotación
"""
import os
import time
from typing import Optional, Dict, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import redis
import json
from .config import ConfiguracionSeguridad

def get_config():
    """Obtener configuración (lazy loading para evitar imports circulares)"""
    return ConfiguracionSeguridad()

class GestorClavesJWT:
    """Gestor de claves JWT con rotación automática"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Inicializar gestor de claves"""
        self.config = get_config()
        self.redis = redis_client
        self.clave_cache_ttl = 3600  # 1 hora de cache
        
        # Intentar conectar con Redis si no se proporciona
        if not self.redis:
            try:
                self.redis = redis.Redis.from_url(self.config.url_redis)
                self.redis.ping()
            except Exception:
                self.redis = None
                print("Redis no disponible, usando almacenamiento en memoria")
        
        # Cache local de respaldo
        self._cache_local = {}
    
    def _obtener_clave_desde_env(self) -> Optional[Tuple[str, str]]:
        """Obtener claves desde variables de entorno"""
        pub_key = os.getenv("JWT_PUBLIC_KEY")
        priv_key = os.getenv("JWT_PRIVATE_KEY")
        
        if pub_key and priv_key:
            return pub_key, priv_key
        
        # Intentar desde archivos
        pub_file = os.getenv("JWT_PUBLIC_KEY_FILE", "jwt_public.pem")
        priv_file = os.getenv("JWT_PRIVATE_KEY_FILE", "jwt_private.pem")
        
        try:
            if os.path.exists(pub_file) and os.path.exists(priv_file):
                with open(pub_file, 'r') as f:
                    pub_key = f.read()
                with open(priv_file, 'r') as f:
                    priv_key = f.read()
                return pub_key, priv_key
        except Exception:
            pass
        
        return None
    
    def _obtener_clave_desde_redis(self, clave_id: str) -> Optional[str]:
        """Obtener clave desde Redis"""
        if not self.redis:
            return None
        
        try:
            # Buscar en cache local primero
            cache_key = f"key_cache:{clave_id}"
            if cache_key in self._cache_local:
                return self._cache_local[cache_key]
            
            # Buscar en Redis
            key_data = self.redis.get(f"jwt_key:{clave_id}")
            if key_data:
                key_str = key_data.decode('utf-8')
                # Actualizar cache local
                self._cache_local[cache_key] = key_str
                return key_str
        except Exception as e:
            print(f"Error obteniendo clave de Redis: {e}")
        
        return None
    
    def _guardar_clave_en_redis(self, clave_id: str, clave: str, ttl: int = None):
        """Guardar clave en Redis"""
        if not self.redis:
            return False
        
        try:
            self.redis.set(f"jwt_key:{clave_id}", clave, ex=ttl)
            # Actualizar cache local
            self._cache_local[f"key_cache:{clave_id}"] = clave
            return True
        except Exception as e:
            print(f"Error guardando clave en Redis: {e}")
            return False
    
    def obtener_clave_publica(self) -> str:
        """Obtener clave pública JWT actual"""
        # Intentar desde variables de entorno primero
        claves = self._obtener_clave_desde_env()
        if claves:
            return claves[0]
        
        # Buscar en Redis
        clave_actual = self._obtener_clave_actual_id()
        if clave_actual:
            clave = self._obtener_clave_desde_redis(f"public:{clave_actual}")
            if clave:
                return clave
        
        # Fallback a configuración hardcodeada (solo desarrollo)
        if self.config.entorno == "desarrollo":
            print("WARNING: Usando claves hardcodeadas. Configura JWT_PUBLIC_KEY en producción")
            return self.config.clave_publica_jwt
        
        raise ValueError("No se encontró clave pública JWT")
    
    def obtener_clave_privada(self) -> str:
        """Obtener clave privada JWT actual"""
        # Intentar desde variables de entorno primero
        claves = self._obtener_clave_desde_env()
        if claves:
            return claves[1]
        
        # Buscar en Redis
        clave_actual = self._obtener_clave_actual_id()
        if clave_actual:
            clave = self._obtener_clave_desde_redis(f"private:{clave_actual}")
            if clave:
                return clave
        
        # Fallback a configuración hardcodeada (solo desarrollo)
        if self.config.entorno == "desarrollo":
            print("WARNING: Usando claves hardcodeadas. Configura JWT_PRIVATE_KEY en producción")
            return self.config.clave_privada_jwt
        
        raise ValueError("No se encontró clave privada JWT")
    
    def _obtener_clave_actual_id(self) -> Optional[int]:
        """Obtener ID de la clave actual"""
        if not self.redis:
            return None
        
        try:
            current_id = self.redis.get("jwt_key:current")
            if current_id:
                return int(current_id.decode('utf-8'))
        except Exception:
            pass
        
        return None
    
    def _establecer_clave_actual_id(self, key_id: int):
        """Establecer ID de la clave actual"""
        if not self.redis:
            return False
        
        try:
            self.redis.set("jwt_key:current", str(key_id))
            return True
        except Exception:
            return False
    
    def generar_nuevo_par_claves(self) -> Tuple[str, str, int]:
        """Generar nuevo par de claves RSA"""
        # Generar clave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Extraer clave pública
        public_key = private_key.public_key()
        
        # Serializar claves
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        # Generar nuevo ID de clave
        key_id = int(time.time())
        
        return public_pem, private_pem, key_id
    
    def rotar_claves(self) -> bool:
        """Rotar claves JWT (generar nuevas y mantener las viejas por un tiempo)"""
        if not self.redis:
            print("Redis no disponible, no se puede rotar claves")
            return False
        
        try:
            # Generar nuevo par de claves
            pub_key, priv_key, new_id = self.generar_nuevo_par_claves()
            
            # Guardar nuevas claves
            self._guardar_clave_en_redis(f"public:{new_id}", pub_key, ttl=86400 * 30)  # 30 días
            self._guardar_clave_en_redis(f"private:{new_id}", priv_key, ttl=86400 * 30)
            
            # Obtener clave anterior (si existe)
            old_id = self._obtener_clave_actual_id()
            
            # Establecer nueva clave como actual
            self._establecer_clave_actual_id(new_id)
            
            # Guardar historial de claves (últimas 3)
            if old_id:
                self.redis.lpush("jwt_key:history", str(old_id))
                self.redis.ltrim("jwt_key:history", 0, 2)  # Mantener solo 3
        
            print(f"Claves JWT rotadas exitosamente. Nueva clave ID: {new_id}")
            return True
            
        except Exception as e:
            print(f"Error rotando claves: {e}")
            return False
    
    def obtener_claves_validas(self) -> list:
        """Obtener lista de IDs de claves válidas (actual + anteriores para migración)"""
        if not self.redis:
            return []
        
        try:
            current = self._obtener_clave_actual_id()
            history = self.redis.lrange("jwt_key:history", 0, 2)
            
            ids = [current] if current else []
            for h in history:
                try:
                    ids.append(int(h.decode('utf-8')))
                except:
                    pass
            
            return ids
        except Exception:
            return []
    
    def obtener_clave_publica_por_id(self, key_id: int) -> Optional[str]:
        """Obtener clave pública por ID (útil durante migración)"""
        return self._obtener_clave_desde_redis(f"public:{key_id}")
    
    def limpiar_cache_local(self):
        """Limpiar cache local de claves"""
        self._cache_local.clear()

# Instancia global del gestor de claves
_gestor_claves: Optional[GestorClavesJWT] = None

def obtener_gestor_claves() -> GestorClavesJWT:
    """Obtener instancia del gestor de claves"""
    global _gestor_claves
    if _gestor_claves is None:
        _gestor_claves = GestorClavesJWT()
    return _gestor_claves

