# app/core/seguridad.py
"""
Módulo de seguridad para C4A SaaS
JWT RS256, Argon2id, cifrado AES-256-GCM
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import secrets
import hashlib
import base64

from .config import config


# Contexto para hash de contraseñas con Argon2id
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Configuración JWT
ALGORITMO_JWT = config.algoritmo_jwt
TIEMPO_EXPIRACION_ACCESO = config.tiempo_expiracion_acceso
TIEMPO_EXPIRACION_REFRESCO = config.tiempo_expiracion_refresco


class SeguridadC4A:
    """Clase principal para operaciones de seguridad"""
    
    def __init__(self):
        self.clave_publica = config.clave_publica_jwt
        self.clave_privada = config.clave_privada_jwt
        self.clave_cifrado = self._generar_clave_cifrado()
    
    def _generar_clave_cifrado(self) -> bytes:
        """Generar clave de cifrado desde la clave maestra"""
        clave_maestra = config.clave_maestra_cifrado.encode()
        hash_clave = hashlib.sha256(clave_maestra).digest()
        return base64.urlsafe_b64encode(hash_clave)
    
    def verificar_contraseña(self, contraseña_plana: str, hash_contraseña: str) -> bool:
        """Verificar contraseña usando Argon2id"""
        return pwd_context.verify(contraseña_plana, hash_contraseña)
    
    def obtener_hash_contraseña(self, contraseña: str) -> str:
        """Generar hash de contraseña usando Argon2id"""
        return pwd_context.hash(contraseña)
    
    def crear_token_acceso(self, datos: Dict[str, Any]) -> str:
        """Crear token de acceso JWT"""
        datos_copia = datos.copy()
        expiracion = datetime.utcnow() + timedelta(minutes=TIEMPO_EXPIRACION_ACCESO)
        datos_copia.update({"exp": expiracion, "type": "access"})
        
        return jwt.encode(datos_copia, self.clave_privada, algorithm=ALGORITMO_JWT)
    
    def crear_token_refresco(self, datos: Dict[str, Any]) -> str:
        """Crear token de refresco JWT"""
        datos_copia = datos.copy()
        expiracion = datetime.utcnow() + timedelta(minutes=TIEMPO_EXPIRACION_REFRESCO)
        datos_copia.update({"exp": expiracion, "type": "refresh"})
        
        return jwt.encode(datos_copia, self.clave_privada, algorithm=ALGORITMO_JWT)
    
    def verificar_token(self, token: str, tipo_esperado: str = "access") -> Optional[Dict[str, Any]]:
        """Verificar y decodificar token JWT"""
        try:
            payload = jwt.decode(token, self.clave_publica, algorithms=[ALGORITMO_JWT])
            
            # Verificar tipo de token
            if payload.get("type") != tipo_esperado:
                return None
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return payload
            
        except JWTError:
            return None
    
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
        """Validar fuerza de contraseña"""
        errores = []
        
        if len(contraseña) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        
        if not any(c.isupper() for c in contraseña):
            errores.append("La contraseña debe contener al menos una letra mayúscula")
        
        if not any(c.islower() for c in contraseña):
            errores.append("La contraseña debe contener al menos una letra minúscula")
        
        if not any(c.isdigit() for c in contraseña):
            errores.append("La contraseña debe contener al menos un número")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in contraseña):
            errores.append("La contraseña debe contener al menos un carácter especial")
        
        return {
            "es_valida": len(errores) == 0,
            "errores": errores,
            "fuerza": self._calcular_fuerza_contraseña(contraseña)
        }
    
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


def obtener_usuario_actual(token: str) -> Optional[Dict[str, Any]]:
    """Obtener usuario actual desde token"""
    payload = seguridad.verificar_token(token)
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