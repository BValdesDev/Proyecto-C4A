#!/usr/bin/env python3
"""
Generar par de claves RSA para JWT
"""
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import sys

def generar_claves():
    """Generar par de claves RSA 2048 bits"""
    
    # Generar clave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Extraer clave pública
    public_key = private_key.public_key()
    
    # Serializar clave privada
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serializar clave pública
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Guardar claves en archivos
    with open("jwt_private.pem", "w") as f:
        f.write(private_pem)
    
    with open("jwt_public.pem", "w") as f:
        f.write(public_pem)
    
    print("✅ Claves RSA generadas exitosamente")
    print()
    print("Archivos creados:")
    print("  - jwt_private.pem (clave privada)")
    print("  - jwt_public.pem (clave pública)")
    print()
    print("⚠️  IMPORTANTE:")
    print("  1. NUNCA commits estas claves al repositorio")
    print("  2. Agrega 'jwt_*.pem' a tu .gitignore")
    print("  3. Guarda las claves en un lugar seguro")
    print("  4. En producción, usa un gestor de secretos (Azure Key Vault, AWS Secrets Manager, etc.)")
    print()
    print("Para usar estas claves, configura en .env:")
    print("  JWT_PUBLIC_KEY_FILE=jwt_public.pem")
    print("  JWT_PRIVATE_KEY_FILE=jwt_private.pem")

if __name__ == "__main__":
    try:
        generar_claves()
    except Exception as e:
        print(f"❌ Error generando claves: {e}")
        sys.exit(1)





















