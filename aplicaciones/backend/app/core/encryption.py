"""
Sistema de cifrado para datos sensibles
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
from app.core.config import ConfiguracionSeguridad

class EncryptionService:
    """Servicio de cifrado para datos sensibles"""
    
    def __init__(self):
        self.config = ConfiguracionSeguridad()
        self._fernet = None
    
    @property
    def fernet(self) -> Fernet:
        """Obtener instancia de Fernet para cifrado"""
        if self._fernet is None:
            # Generar clave desde la clave maestra
            key = self._derive_key(self.config.CLAVE_MAESTRA_CIFRADO)
            self._fernet = Fernet(key)
        return self._fernet
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derivar clave de cifrado desde contraseña"""
        if salt is None:
            # Usar salt fijo para consistencia (en producción usar salt único)
            salt = b'c4a_saas_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """Cifrar datos sensibles"""
        if not data:
            return data
        
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"Error cifrando datos: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Descifrar datos sensibles"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Error descifrando datos: {e}")
    
    def encrypt_field(self, field_value: Optional[str]) -> Optional[str]:
        """Cifrar campo de base de datos"""
        if field_value is None:
            return None
        return self.encrypt(field_value)
    
    def decrypt_field(self, encrypted_value: Optional[str]) -> Optional[str]:
        """Descifrar campo de base de datos"""
        if encrypted_value is None:
            return None
        return self.decrypt(encrypted_value)
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """Cifrar campos específicos de un diccionario"""
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field] is not None:
                encrypted_data[field] = self.encrypt(encrypted_data[field])
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """Descifrar campos específicos de un diccionario"""
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field] is not None:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        
        return decrypted_data

# Instancia global del servicio de cifrado
encryption_service: Optional[EncryptionService] = None

def get_encryption_service() -> EncryptionService:
    """Obtener instancia del servicio de cifrado"""
    global encryption_service
    if encryption_service is None:
        encryption_service = EncryptionService()
    return encryption_service

# Funciones de conveniencia
def encrypt_sensitive_data(data: str) -> str:
    """Cifrar datos sensibles"""
    return get_encryption_service().encrypt(data)

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Descifrar datos sensibles"""
    return get_encryption_service().decrypt(encrypted_data)

def encrypt_database_field(field_value: Optional[str]) -> Optional[str]:
    """Cifrar campo de base de datos"""
    return get_encryption_service().encrypt_field(field_value)

def decrypt_database_field(encrypted_value: Optional[str]) -> Optional[str]:
    """Descifrar campo de base de datos"""
    return get_encryption_service().decrypt_field(encrypted_value)
















