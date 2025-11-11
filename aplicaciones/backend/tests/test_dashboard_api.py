#!/usr/bin/env python3
"""
Script de prueba para la API del Dashboard
Verifica que todos los endpoints funcionen correctamente
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
TEST_TOKEN = "fake_access_token_16740934-e52d-4ea0-a36c-8986784a0500"  # Token de prueba

def test_dashboard_summary():
    """Probar endpoint de resumen del dashboard"""
    print("🧪 Probando GET /api/v1/dashboard/summary...")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/summary", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Resumen del dashboard obtenido exitosamente:")
        print(f"   - Total evaluaciones: {data.get('total_evaluaciones', 0)}")
        print(f"   - Promedio puntuación: {data.get('promedio_puntuacion', 0)}")
        print(f"   - En progreso: {data.get('en_progreso', 0)}")
        print(f"   - Uso mensual: {data.get('uso_mensual', 0)}")
        print(f"   - Nivel suscripción: {data.get('nivel_suscripcion', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_evaluaciones_recientes():
    """Probar endpoint de evaluaciones recientes"""
    print("\n🧪 Probando GET /api/v1/dashboard/evaluaciones-recientes...")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/evaluaciones-recientes", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Evaluaciones recientes obtenidas: {len(data)} evaluaciones")
        for eval in data[:3]:  # Mostrar solo las primeras 3
            print(f"   - {eval.get('nombre', 'N/A')} ({eval.get('estado', 'N/A')})")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_acciones_rapidas():
    """Probar endpoint de acciones rápidas"""
    print("\n🧪 Probando GET /api/v1/dashboard/acciones...")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/acciones", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Acciones rápidas obtenidas: {len(data)} acciones")
        for accion in data:
            estado = "✅" if accion.get('disponible', False) else "❌"
            print(f"   {estado} {accion.get('nombre', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_estadisticas_uso():
    """Probar endpoint de estadísticas de uso"""
    print("\n🧪 Probando GET /api/v1/dashboard/estadisticas-uso...")
    
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/estadisticas-uso", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Estadísticas de uso obtenidas:")
        org = data.get('organizacion', {})
        usuario = data.get('usuario', {})
        print(f"   - Organización: {org.get('nombre', 'N/A')} ({org.get('nivel_suscripcion', 'N/A')})")
        print(f"   - Usuario: {usuario.get('nombre_completo', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_crear_evaluacion():
    """Probar endpoint de crear evaluación"""
    print("\n🧪 Probando POST /api/v1/dashboard/evaluaciones...")
    
    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "nombre": f"Evaluación de Prueba - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/dashboard/evaluaciones", 
                           headers=headers, 
                           json=payload)
    
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        data = response.json()
        print("✅ Evaluación creada exitosamente:")
        print(f"   - ID: {data.get('id', 'N/A')}")
        print(f"   - Nombre: {data.get('nombre', 'N/A')}")
        print(f"   - Estado: {data.get('estado', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_health_check():
    """Probar endpoint de salud"""
    print("\n🧪 Probando GET /health...")
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Health check exitoso:")
        print(f"   - Status: {data.get('status', 'N/A')}")
        print(f"   - Version: {data.get('version', 'N/A')}")
        print(f"   - Entorno: {data.get('entorno', 'N/A')}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de la API del Dashboard")
    print("=" * 50)
    
    # Lista de pruebas a ejecutar
    tests = [
        ("Health Check", test_health_check),
        ("Dashboard Summary", test_dashboard_summary),
        ("Evaluaciones Recientes", test_evaluaciones_recientes),
        ("Acciones Rápidas", test_acciones_rapidas),
        ("Estadísticas de Uso", test_estadisticas_uso),
        ("Crear Evaluación", test_crear_evaluacion),
    ]
    
    # Ejecutar pruebas
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en prueba {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    exitosas = 0
    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado} {nombre}")
        if resultado:
            exitosas += 1
    
    print(f"\n🎯 Resultado: {exitosas}/{len(resultados)} pruebas exitosas")
    
    if exitosas == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron! El Dashboard API está funcionando correctamente.")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar la configuración.")
        return 1

if __name__ == "__main__":
    exit(main())




