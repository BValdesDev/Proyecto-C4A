#!/usr/bin/env python3
"""
Script para verificar que todos los datos del panel de administración sean reales
"""

import requests
import json
from datetime import datetime
import sys
import os

# Agregar el directorio del backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'aplicaciones', 'backend'))

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.evaluacion import Evaluacion
from app.modelos.suscripcion import Suscripcion
from sqlalchemy.orm import Session

def verificar_datos_reales():
    """Verificar que todos los datos del panel de administración sean reales"""
    
    print("🔍 VERIFICANDO DATOS REALES DEL PANEL DE ADMINISTRACIÓN")
    print("=" * 60)
    
    # Obtener sesión de base de datos
    db = next(obtener_sesion())
    
    try:
        # 1. Verificar usuarios reales
        print("\n📊 USUARIOS REALES:")
        usuarios = db.query(Usuario).all()
        print(f"   Total de usuarios: {len(usuarios)}")
        
        usuarios_activos = [u for u in usuarios if u.esta_activo]
        print(f"   Usuarios activos: {len(usuarios_activos)}")
        
        usuarios_recientes = [u for u in usuarios if u.fecha_ultimo_acceso and u.fecha_ultimo_acceso >= datetime.utcnow().replace(tzinfo=None) - timedelta(days=30)]
        print(f"   Usuarios activos (últimos 30 días): {len(usuarios_recientes)}")
        
        # Mostrar algunos usuarios
        print("\n   Usuarios de ejemplo:")
        for i, usuario in enumerate(usuarios[:5]):
            print(f"   - {usuario.nombre_completo} ({usuario.email}) - {usuario.estado_cuenta}")
        
        # 2. Verificar organizaciones reales
        print("\n🏢 ORGANIZACIONES REALES:")
        organizaciones = db.query(Organizacion).all()
        print(f"   Total de organizaciones: {len(organizaciones)}")
        
        for org in organizaciones:
            print(f"   - {org.nombre} (Nivel: {org.nivel_suscripcion.value})")
        
        # 3. Verificar evaluaciones reales
        print("\n📋 EVALUACIONES REALES:")
        evaluaciones = db.query(Evaluacion).all()
        print(f"   Total de evaluaciones: {len(evaluaciones)}")
        
        evaluaciones_completadas = [e for e in evaluaciones if e.estado.value == 'completada']
        print(f"   Evaluaciones completadas: {len(evaluaciones_completadas)}")
        
        evaluaciones_en_progreso = [e for e in evaluaciones if e.estado.value == 'en_progreso']
        print(f"   Evaluaciones en progreso: {len(evaluaciones_en_progreso)}")
        
        # 4. Verificar suscripciones reales
        print("\n💳 SUSCRIPCIONES REALES:")
        suscripciones = db.query(Suscripcion).all()
        print(f"   Total de suscripciones: {len(suscripciones)}")
        
        suscripciones_activas = [s for s in suscripciones if s.estado == 'active']
        print(f"   Suscripciones activas: {len(suscripciones_activas)}")
        
        # Calcular ingresos reales
        ingresos_totales = sum([s.monto_centavos for s in suscripciones_activas if s.monto_centavos]) / 100
        print(f"   Ingresos totales: ${ingresos_totales:,.0f} CLP")
        
        # 5. Verificar endpoints del admin
        print("\n🔗 VERIFICANDO ENDPOINTS DEL ADMIN:")
        
        base_url = "http://localhost:8000"
        
        # Obtener token de admin
        login_data = {
            "email": "admin@c4a.cl",
            "password": "Admin123!"
        }
        
        try:
            response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
            if response.status_code == 200:
                token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Probar endpoint de estadísticas
                stats_response = requests.get(f"{base_url}/api/v1/admin/dashboard/stats", headers=headers)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print("   ✅ Endpoint de estadísticas funcionando")
                    print(f"   - Total usuarios: {stats.get('totalUsers', 0)}")
                    print(f"   - Usuarios activos: {stats.get('activeUsers', 0)}")
                    print(f"   - Total diagnósticos: {stats.get('totalDiagnostics', 0)}")
                    print(f"   - Ingresos mensuales: ${stats.get('monthlyRevenue', 0):,.0f} CLP")
                else:
                    print(f"   ❌ Error en endpoint de estadísticas: {stats_response.status_code}")
                
                # Probar endpoint de usuarios
                users_response = requests.get(f"{base_url}/api/v1/admin/users", headers=headers)
                if users_response.status_code == 200:
                    users_data = users_response.json()
                    print("   ✅ Endpoint de usuarios funcionando")
                    print(f"   - Usuarios en respuesta: {len(users_data.get('users', []))}")
                else:
                    print(f"   ❌ Error en endpoint de usuarios: {users_response.status_code}")
                
                # Probar endpoint de analytics
                analytics_response = requests.get(f"{base_url}/api/v1/admin/analytics/overview", headers=headers)
                if analytics_response.status_code == 200:
                    analytics = analytics_response.json()
                    print("   ✅ Endpoint de analytics funcionando")
                    print(f"   - Total usuarios: {analytics.get('totalUsers', 0)}")
                    print(f"   - Total diagnósticos: {analytics.get('totalDiagnostics', 0)}")
                else:
                    print(f"   ❌ Error en endpoint de analytics: {analytics_response.status_code}")
                    
            else:
                print(f"   ❌ Error al hacer login: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error conectando con la API: {str(e)}")
        
        print("\n✅ VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        print("📋 RESUMEN:")
        print(f"   - Usuarios reales: {len(usuarios)}")
        print(f"   - Organizaciones reales: {len(organizaciones)}")
        print(f"   - Evaluaciones reales: {len(evaluaciones)}")
        print(f"   - Suscripciones reales: {len(suscripciones)}")
        print(f"   - Ingresos reales: ${ingresos_totales:,.0f} CLP")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando datos: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import timedelta
    verificar_datos_reales()
