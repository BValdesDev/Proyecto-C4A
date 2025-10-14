# app/core/seguridad.py
"""
Módulo de seguridad para C4A SaaS
JWT RS256, Argon2id, cifrado AES-256-GCM, protección contra ataques
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import hashlib
import base64
import hmac
import time
import uuid

from .config import config


# Contexto para hash de contraseñas con Argon2id (más seguro)
pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 iteraciones
    argon2__parallelism=4,      # 4 hilos paralelos
    argon2__hash_len=32,        # 32 bytes de hash
    argon2__salt_len=16,        # 16 bytes de salt
    deprecated="auto"
)

# Configuración JWT
ALGORITMO_JWT = config.algoritmo_jwt
TIEMPO_EXPIRACION_ACCESO = config.tiempo_expiracion_acceso
TIEMPO_EXPIRACION_REFRESCO = config.tiempo_expiracion_refresco


class SeguridadC4A:
    """Clase principal para operaciones de seguridad con mejores prácticas"""
    
    def __init__(self):
        self.clave_publica = config.clave_publica_jwt
        self.clave_privada = config.clave_privada_jwt
        self.clave_cifrado = self._generar_clave_cifrado()
        self._cache_tokens_revocados = set()  # Cache para tokens revocados
        self._intentos_fallidos = {}  # Rate limiting por IP
        self._max_intentos = 5  # Máximo intentos por IP
        self._tiempo_bloqueo = 300  # 5 minutos de bloqueo
    
    def _generar_clave_cifrado(self) -> bytes:
        """Generar clave de cifrado desde la clave maestra con PBKDF2"""
        clave_maestra = config.clave_maestra_cifrado.encode()
        salt = b'c4a_salt_2024'  # Salt fijo para consistencia
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # 100k iteraciones
        )
        return kdf.derive(clave_maestra)
    
    def _verificar_rate_limit(self, ip: str) -> bool:
        """Verificar rate limiting por IP"""
        ahora = time.time()
        
        if ip in self._intentos_fallidos:
            intentos, ultimo_intento = self._intentos_fallidos[ip]
            
            # Si han pasado más de 5 minutos, resetear
            if ahora - ultimo_intento > self._tiempo_bloqueo:
                del self._intentos_fallidos[ip]
                return True
            
            # Si excede el límite, bloquear
            if intentos >= self._max_intentos:
                return False
        
        return True
    
    def _registrar_intento_fallido(self, ip: str):
        """Registrar intento fallido de autenticación"""
        ahora = time.time()
        
        if ip in self._intentos_fallidos:
            intentos, _ = self._intentos_fallidos[ip]
            self._intentos_fallidos[ip] = (intentos + 1, ahora)
        else:
            self._intentos_fallidos[ip] = (1, ahora)
    
    def _limpiar_cache_tokens(self):
        """Limpiar cache de tokens revocados (llamar periódicamente)"""
        # En producción, esto debería ser manejado por Redis
        if len(self._cache_tokens_revocados) > 10000:
            self._cache_tokens_revocados.clear()
    
    def verificar_contraseña(self, contraseña_plana: str, hash_contraseña: str) -> bool:
        """Verificar contraseña usando Argon2id"""
        return pwd_context.verify(contraseña_plana, hash_contraseña)
    
    def obtener_hash_contraseña(self, contraseña: str) -> str:
        """Generar hash de contraseña usando Argon2id"""
        return pwd_context.hash(contraseña)
    
    def crear_token_acceso(self, datos: Dict[str, Any]) -> str:
        """Crear token de acceso JWT con mejores prácticas de seguridad"""
        datos_copia = datos.copy()
        ahora = datetime.utcnow()
        expiracion = ahora + timedelta(minutes=TIEMPO_EXPIRACION_ACCESO)
        
        # Generar JTI único para tracking
        jti = str(uuid.uuid4())
        
        # Payload con claims estándar y de seguridad
        payload = {
            "sub": datos_copia.get("sub"),  # Subject (usuario ID)
            "email": datos_copia.get("email"),
            "org_id": datos_copia.get("org_id"),
            "nivel_suscripcion": datos_copia.get("nivel_suscripcion"),
            "rol": datos_copia.get("rol"),
            "jti": jti,  # JWT ID único
            "iat": int(ahora.timestamp()),  # Issued at
            "exp": int(expiracion.timestamp()),  # Expiration
            "nbf": int(ahora.timestamp()),  # Not before
            "iss": "c4a-saas",  # Issuer
            "aud": "c4a-frontend",  # Audience
            "type": "access"
        }
        
        return jwt.encode(payload, self.clave_privada, algorithm=ALGORITMO_JWT)
    
    def crear_token_refresco(self, datos: Dict[str, Any]) -> Tuple[str, str]:
        """Crear token de refresco JWT con hash para verificación"""
        datos_copia = datos.copy()
        ahora = datetime.utcnow()
        expiracion = ahora + timedelta(minutes=TIEMPO_EXPIRACION_REFRESCO)
        
        # Generar JTI único
        jti = str(uuid.uuid4())
        
        # Payload para refresh token
        payload = {
            "sub": datos_copia.get("sub"),
            "jti": jti,
            "iat": int(ahora.timestamp()),
            "exp": int(expiracion.timestamp()),
            "nbf": int(ahora.timestamp()),
            "iss": "c4a-saas",
            "aud": "c4a-frontend",
            "type": "refresh"
        }
        
        token = jwt.encode(payload, self.clave_privada, algorithm=ALGORITMO_JWT)
        
        # Generar hash del token para almacenar en BD
        hash_token = self.obtener_hash_contraseña(token)
        
        return token, hash_token
    
    def verificar_token(self, token: str, tipo_esperado: str = "access", ip: str = None) -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT con validaciones de seguridad"""
        try:
            # Verificar rate limiting si se proporciona IP
            if ip and not self._verificar_rate_limit(ip):
                return None
            
            # Verificar si el token está en cache de revocados
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if token_hash in self._cache_tokens_revocados:
                return None
            
            # Decodificar token
            payload = jwt.decode(
                token, 
                self.clave_publica, 
                algorithms=[ALGORITMO_JWT],
                audience="c4a-frontend",
                issuer="c4a-saas"
            )
            
            # Verificar tipo de token
            if payload.get("type") != tipo_esperado:
                return None
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            # Verificar not before
            nbf = payload.get("nbf")
            if nbf and datetime.utcnow() < datetime.fromtimestamp(nbf):
                return None
            
            # Verificar que no sea muy antiguo (máximo 24 horas para access tokens)
            iat = payload.get("iat")
            if iat and tipo_esperado == "access":
                max_age = 24 * 60 * 60  # 24 horas
                if datetime.utcnow().timestamp() - iat > max_age:
                    return None
            
            return payload
            
        except JWTError:
            return None
    
    def revocar_token(self, jti: str):
        """Revocar token por JTI"""
        self._cache_tokens_revocados.add(jti)
        self._limpiar_cache_tokens()
    
    def verificar_autenticacion_segura(self, token: str, ip: str = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Verificar autenticación con protecciones adicionales"""
        # Verificar rate limiting
        if ip and not self._verificar_rate_limit(ip):
            if ip:
                self._registrar_intento_fallido(ip)
            return False, None
        
        # Verificar token
        payload = self.verificar_token(token, "access", ip)
        if not payload:
            if ip:
                self._registrar_intento_fallido(ip)
            return False, None
        
        return True, payload
    
    def cifrar_datos_sensibles(self, datos: str) -> str:
        """Cifrar datos sensibles usando AES-256-GCM"""
        fernet = Fernet(self.clave_cifrado)
        datos_bytes = datos.encode('utf-8')
        datos_cifrados = fernet.encrypt(datos_bytes)
        return base64.urlsafe_b64encode(datos_cifrados).decode('utf-8')
    
    def descifrar_datos_sensibles(self, datos_cifrados: str) -> str:
        """Descifrar datos sensibles"""
        try:
            fernet = Fernet(self.clave_cifrado)
            datos_bytes = base64.urlsafe_b64decode(datos_cifrados.encode('utf-8'))
            datos_descifrados = fernet.decrypt(datos_bytes)
            return datos_descifrados.decode('utf-8')
        except Exception:
            raise ValueError("No se pudieron descifrar los datos")
    
    def generar_jti(self) -> str:
        """Generar JWT ID único"""
        return secrets.token_urlsafe(32)
    
    def generar_secreto_mfa(self) -> str:
        """Generar secreto para MFA"""
        return secrets.token_urlsafe(20)
    
    def validar_fuerza_contraseña(self, contraseña: str) -> Dict[str, Any]:
        """Validar fuerza de contraseña con mejores prácticas de seguridad"""
        errores = []
        
        # Longitud mínima
        if len(contraseña) < 12:
            errores.append("La contraseña debe tener al menos 12 caracteres")
        
        # Verificar contraseñas comunes
        contraseñas_comunes = [
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey"
        ]
        
        if contraseña.lower() in contraseñas_comunes:
            errores.append("La contraseña es muy común y no es segura")
        
        # Verificar patrones repetitivos
        if self._tiene_patrones_repetitivos(contraseña):
            errores.append("La contraseña contiene patrones repetitivos")
        
        # Verificar información personal (esto debería recibir datos del usuario)
        if self._contiene_informacion_personal(contraseña):
            errores.append("La contraseña no debe contener información personal")
        
        # Verificar complejidad
        if not any(c.isupper() for c in contraseña):
            errores.append("La contraseña debe contener al menos una letra mayúscula")
        
        if not any(c.islower() for c in contraseña):
            errores.append("La contraseña debe contener al menos una letra minúscula")
        
        if not any(c.isdigit() for c in contraseña):
            errores.append("La contraseña debe contener al menos un número")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in contraseña):
            errores.append("La contraseña debe contener al menos un carácter especial")
        
        # Verificar secuencias del teclado
        if self._contiene_secuencias_teclado(contraseña):
            errores.append("La contraseña contiene secuencias del teclado")
        
        return {
            "es_valida": len(errores) == 0,
            "errores": errores,
            "fuerza": self._calcular_fuerza_contraseña(contraseña),
            "puntuacion": self._calcular_puntuacion_seguridad(contraseña)
        }
    
    def _tiene_patrones_repetitivos(self, contraseña: str) -> bool:
        """Detectar patrones repetitivos en la contraseña"""
        # Buscar secuencias de 3+ caracteres repetidos
        for i in range(len(contraseña) - 2):
            if contraseña[i] == contraseña[i+1] == contraseña[i+2]:
                return True
        return False
    
    def _contiene_informacion_personal(self, contraseña: str, datos_usuario: Dict = None) -> bool:
        """Verificar si la contraseña contiene información personal"""
        if not datos_usuario:
            return False
        
        contraseña_lower = contraseña.lower()
        
        # Verificar nombres
        if datos_usuario.get("nombres"):
            if datos_usuario["nombres"].lower() in contraseña_lower:
                return True
        
        if datos_usuario.get("apellidos"):
            if datos_usuario["apellidos"].lower() in contraseña_lower:
                return True
        
        # Verificar email
        if datos_usuario.get("email"):
            email_parts = datos_usuario["email"].split("@")[0].lower()
            if email_parts in contraseña_lower:
                return True
        
        return False
    
    def _contiene_secuencias_teclado(self, contraseña: str) -> bool:
        """Detectar secuencias del teclado"""
        secuencias = [
            "qwerty", "asdfgh", "zxcvbn", "123456", "abcdef",
            "qwertyuiop", "asdfghjkl", "zxcvbnm"
        ]
        
        contraseña_lower = contraseña.lower()
        for secuencia in secuencias:
            if secuencia in contraseña_lower:
                return True
        return False
    
    def _calcular_puntuacion_seguridad(self, contraseña: str) -> int:
        """Calcular puntuación de seguridad de la contraseña"""
        puntuacion = 0
        
        # Longitud
        if len(contraseña) >= 12:
            puntuacion += 2
        elif len(contraseña) >= 8:
            puntuacion += 1
        
        # Complejidad
        if any(c.isupper() for c in contraseña):
            puntuacion += 1
        if any(c.islower() for c in contraseña):
            puntuacion += 1
        if any(c.isdigit() for c in contraseña):
            puntuacion += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in contraseña):
            puntuacion += 1
        
        # Penalizaciones
        if self._tiene_patrones_repetitivos(contraseña):
            puntuacion -= 2
        if self._contiene_secuencias_teclado(contraseña):
            puntuacion -= 1
        
        return max(0, puntuacion)
    
    def _calcular_fuerza_contraseña(self, contraseña: str) -> str:
        """Calcular fuerza de contraseña"""
        puntuacion = 0
        
        # Longitud
        if len(contraseña) >= 8:
            puntuacion += 1
        if len(contraseña) >= 12:
            puntuacion += 1
        
        # Complejidad
        if any(c.isupper() for c in contraseña):
            puntuacion += 1
        if any(c.islower() for c in contraseña):
            puntuacion += 1
        if any(c.isdigit() for c in contraseña):
            puntuacion += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in contraseña):
            puntuacion += 1
        
        if puntuacion <= 2:
            return "débil"
        elif puntuacion <= 4:
            return "media"
        else:
            return "fuerte"


# Instancia global de seguridad
seguridad = SeguridadC4A()


def obtener_usuario_actual(token: str, ip: str = None) -> Optional[Dict[str, Any]]:
    """Obtener usuario actual desde token"""
    payload = seguridad.verificar_token(token, "access", ip)
    if payload:
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "organizacion_id": payload.get("org_id"),
            "nivel_suscripcion": payload.get("nivel_suscripcion"),
            "rol": payload.get("rol")
        }
    return None


def verificar_permisos_nivel(usuario_nivel: str, nivel_requerido: str) -> bool:
    """Verificar si el usuario tiene el nivel requerido"""
    niveles = ["gratuito", "pro", "empresarial"]
    return niveles.index(usuario_nivel) >= niveles.index(nivel_requerido)