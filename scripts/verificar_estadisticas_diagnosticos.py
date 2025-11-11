#!/usr/bin/env python3
"""
Script para verificar que las estadísticas de diagnósticos se calculen correctamente
"""

import requests
import json

def verificar_estadisticas():
    """Verificar que las estadísticas se calculen correctamente"""
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Hacer login
        print("1. Haciendo login...")
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
        print("   OK - Login exitoso")
        
        # 2. Obtener diagnósticos
        print("\n2. Obteniendo diagnósticos...")
        diagnostics_response = requests.get(f"{base_url}/api/v1/admin/diagnostics", headers=headers)
        
        if diagnostics_response.status_code != 200:
            print(f"Error obteniendo diagnósticos: {diagnostics_response.status_code}")
            return False
            
        diagnostics_data = diagnostics_response.json()
        diagnostics = diagnostics_data.get('diagnostics', [])
        
        print(f"   Total diagnósticos: {len(diagnostics)}")
        
        # 3. Calcular estadísticas manualmente
        print("\n3. Calculando estadísticas...")
        
        total = len(diagnostics)
        completadas = len([d for d in diagnostics if d.get('status') == 'completada'])
        en_progreso = len([d for d in diagnostics if d.get('status') == 'en_progreso'])
        pendientes = len([d for d in diagnostics if d.get('status') == 'pendiente'])
        
        # Calcular puntaje promedio
        completadas_con_puntaje = [d for d in diagnostics if d.get('status') == 'completada' and d.get('score', 0) > 0]
        puntaje_promedio = 0
        if completadas_con_puntaje:
            puntaje_promedio = sum(d.get('score', 0) for d in completadas_con_puntaje) / len(completadas_con_puntaje)
        
        print(f"   - Total: {total}")
        print(f"   - Completadas: {completadas}")
        print(f"   - En Progreso: {en_progreso}")
        print(f"   - Pendientes: {pendientes}")
        print(f"   - Puntaje Promedio: {puntaje_promedio:.1f}")
        
        # 4. Mostrar detalles de cada diagnóstico
        print("\n4. Detalles de diagnósticos:")
        for i, diag in enumerate(diagnostics, 1):
            print(f"   {i}. {diag.get('companyName', 'N/A')} - {diag.get('userName', 'N/A')} - Estado: {diag.get('status', 'N/A')} - Puntaje: {diag.get('score', 0)}")
        
        # 5. Verificar consistencia
        print("\n5. Verificando consistencia...")
        if completadas > 0:
            print(f"   ✅ Se encontraron {completadas} diagnósticos completados")
        else:
            print("   ❌ No se encontraron diagnósticos completados")
            
        if en_progreso > 0:
            print(f"   ✅ Se encontraron {en_progreso} diagnósticos en progreso")
        else:
            print("   ⚠️  No se encontraron diagnósticos en progreso")
            
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    verificar_estadisticas()
