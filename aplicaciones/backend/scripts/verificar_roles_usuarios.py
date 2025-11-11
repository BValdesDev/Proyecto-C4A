#!/usr/bin/env python3
"""
Script para verificar los roles y permisos de los usuarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.rol import Rol
from app.modelos.organizacion import Organizacion

def verificar_roles_usuarios():
    db = next(obtener_sesion())
    try:
        print("=" * 80)
        
        # Obtener todos los usuarios
        usuarios = db.query(Usuario).all()
        
        for usuario in usuarios:
            # Obtener rol
            rol = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
            if rol:
                ")
                print(f"   Descripción: {rol.descripcion}")
                print(f"   Activo: {rol.esta_activo}")
                print(f"   Permisos: {rol.permisos}")
            else:
                # Obtener organización
            if usuario.organizacion_id:
                org = db.query(Organizacion).filter(Organizacion.id == usuario.organizacion_id).first()
                if org:
                    print(f"   Nivel Suscripción: {org.nivel_suscripcion}")
                else:
                    else:
                print("-" * 40)
        
        print(f"\n📊 RESUMEN DE ROLES:")
        print("=" * 40)
        
        # Contar usuarios por rol
        roles_count = {}
        for usuario in usuarios:
            rol = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
            if rol:
                if rol.nombre not in roles_count:
                    roles_count[rol.nombre] = 0
                roles_count[rol.nombre] += 1
        
        for rol_nombre, count in roles_count.items():
            print("\n🔧 PROBLEMAS IDENTIFICADOS:")
        print("=" * 40)
        
        # Verificar problemas específicos
        problemas = []
        
        for usuario in usuarios:
            rol = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
            if not rol:
                problemas.append(f"❌ {usuario.email}: Sin rol asignado")
            
            if usuario.email == "admin@c4a.cl" and rol and rol.nombre != "ADMIN_SISTEMA":
                problemas.append(f"❌ {usuario.email}: Debería ser ADMIN_SISTEMA, pero es {rol.nombre}")
            
            if usuario.email == "empresa@c4a.cl" and rol and rol.nombre != "ADMIN_EMPRESA":
                problemas.append(f"❌ {usuario.email}: Debería ser ADMIN_EMPRESA, pero es {rol.nombre}")
            
            if not usuario.organizacion_id:
                problemas.append(f"⚠️  {usuario.email}: Sin organización asignada")
        
        if problemas:
            for problema in problemas:
                print(f"   {problema}")
        else:
            print("   ✅ No se encontraron problemas")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_roles_usuarios()

