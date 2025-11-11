#!/usr/bin/env python3
"""
Script para resetear contraseñas de usuarios del sistema
Uso:
  - Sin argumentos: resetea contraseñas de admin y empresa
  - Con argumento 'all': resetea todas las contraseñas de usuarios
"""
import sys
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.modelos.base import SessionLocal
from app.modelos.usuario import Usuario
from app.core.seguridad import SeguridadC4A

def resetear_password_usuario(db: Session, email: str, nueva_password: str, seguridad: SeguridadC4A):
    """Resetea la contraseña de un usuario específico"""
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if usuario:
        usuario.hash_contraseña = seguridad.obtener_hash_contraseña(nueva_password)
        usuario.estado_cuenta = "activo"
        usuario.intentos_login_fallidos = 0
        usuario.cuenta_bloqueada_hasta = None
        return True
    else:
        return False

def resetear_passwords_principales():
    """Resetea las contraseñas de los usuarios principales (admin y empresa)"""
    db = SessionLocal()
    seguridad = SeguridadC4A()
    
    try:
        print("\n" + "="*60)
        print("🔐 RESETEAR CONTRASEÑAS PRINCIPALES")
        print("="*60 + "\n")
        
        usuarios = [
            ("admin@c4a.cl", "Admin123!"),
            ("empresa@c4a.cl", "empresarial123"),
        ]
        
        for email, password in usuarios:
            resetear_password_usuario(db, email, password, seguridad)
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ CONTRASEÑAS ACTUALIZADAS")
        print("="*60)
        print("\nCredenciales:")
        print("  admin@c4a.cl / Admin123!")
        print("  empresa@c4a.cl / empresarial123")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def resetear_todas_passwords():
    """Resetea las contraseñas de TODOS los usuarios del sistema"""
    db = SessionLocal()
    seguridad = SeguridadC4A()
    
    try:
        print("\n" + "="*60)
        print("🔐 RESETEAR TODAS LAS CONTRASEÑAS")
        print("="*60 + "\n")
        
        # Obtener todos los usuarios
        usuarios = db.query(Usuario).all()
        
        # Password por defecto: basado en el email
        for usuario in usuarios:
            # Generar password: primera parte del email + "123!"
            # Ejemplo: admin@c4a.cl -> Admin123!
            nombre_base = usuario.email.split('@')[0].capitalize()
            nueva_password = f"{nombre_base}123!"
            
            usuario.hash_contraseña = seguridad.obtener_hash_contraseña(nueva_password)
            usuario.estado_cuenta = "activo"
            usuario.intentos_login_fallidos = 0
            usuario.cuenta_bloqueada_hasta = None
            
            db.commit()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS CONTRASEÑAS ACTUALIZADAS")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        resetear_todas_passwords()
    else:
        resetear_passwords_principales()

