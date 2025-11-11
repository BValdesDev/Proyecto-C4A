#!/usr/bin/env python3
"""
Script para obtener todos los usuarios con sus datos completos
"""

import requests
import json

def obtener_usuarios_completos():
    """Obtener todos los usuarios con sus datos completos"""
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Hacer login
        print("OBTENIENDO TODOS LOS USUARIOS DEL SISTEMA")
        print("=" * 60)
        
        login_data = {
            "email": "admin@c4a.cl",
            "password": "Admin123!"
        }
        
        login_response = requests.post(f"{base_url}/api/v1/auth/iniciar-sesion", json=login_data)
        if login_response.status_code != 200:
            print(f"Error en login: {login_response.status_code}")
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("OK - Login exitoso como administrador")
        
        # 2. Obtener todos los usuarios
        print("\nOBTENIENDO USUARIOS...")
        users_response = requests.get(f"{base_url}/api/v1/admin/users", headers=headers)
        
        if users_response.status_code != 200:
            print(f"Error obteniendo usuarios: {users_response.status_code}")
            return False
            
        users_data = users_response.json()
        users = users_data.get('users', [])
        total = users_data.get('total', 0)
        
        print(f"Total de usuarios: {total}")
        print(f"Usuarios en respuesta: {len(users)}")
        
        # 3. Mostrar todos los usuarios
        print("\nLISTA COMPLETA DE USUARIOS:")
        print("-" * 60)
        
        for i, user in enumerate(users, 1):
            print(f"\n{i}. {user.get('nombre', 'N/A')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Empresa: {user.get('empresa', 'Sin empresa')}")
            print(f"   Suscripcion: {user.get('suscripcion', 'N/A')}")
            print(f"   Estado: {user.get('estado', 'N/A')}")
            print(f"   Ultimo Login: {user.get('ultimoLogin', 'Nunca')}")
            print(f"   Fecha Registro: {user.get('fechaRegistro', 'N/A')}")
            print(f"   Activo: {user.get('activo', 'N/A')}")
        
        # 4. Resumen por categorías
        print("\n" + "=" * 60)
        print("RESUMEN POR CATEGORIAS:")
        print("-" * 60)
        
        # Contar por estado
        activos = len([u for u in users if u.get('estado') == 'activo'])
        inactivos = len([u for u in users if u.get('estado') == 'inactivo'])
        
        print(f"Usuarios Activos: {activos}")
        print(f"Usuarios Inactivos: {inactivos}")
        
        # Contar por suscripción
        suscripciones = {}
        for user in users:
            susc = user.get('suscripcion', 'Sin suscripción')
            suscripciones[susc] = suscripciones.get(susc, 0) + 1
        
        print("\nDistribución por Suscripción:")
        for susc, count in suscripciones.items():
            print(f"  {susc}: {count} usuarios")
        
        # Contar por empresa
        empresas = {}
        for user in users:
            empresa = user.get('empresa', 'Sin empresa')
            empresas[empresa] = empresas.get(empresa, 0) + 1
        
        print("\nDistribución por Empresa:")
        for empresa, count in empresas.items():
            print(f"  {empresa}: {count} usuarios")
        
        print("\n" + "=" * 60)
        print("LISTA COMPLETA FINALIZADA")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    obtener_usuarios_completos()
