#!/usr/bin/env python3
"""
Script para probar específicamente los endpoints de analytics
"""

import requests
import json

def test_analytics_endpoints():
    """Probar todos los endpoints de analytics"""
    
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
        
        # 2. Probar endpoint de overview
        print("\n2. Probando analytics/overview...")
        overview_response = requests.get(f"{base_url}/api/v1/admin/analytics/overview", headers=headers)
        if overview_response.status_code == 200:
            overview = overview_response.json()
            print("   OK - Overview funcionando")
            print(f"   - Total usuarios: {overview.get('totalUsers', 0)}")
            print(f"   - Usuarios activos: {overview.get('activeUsers', 0)}")
            print(f"   - Total diagnósticos: {overview.get('totalDiagnostics', 0)}")
            print(f"   - Diagnósticos completados: {overview.get('completedDiagnostics', 0)}")
            print(f"   - Ingresos totales: ${overview.get('totalRevenue', 0):,.0f} CLP")
        else:
            print(f"   ERROR - Status: {overview_response.status_code}")
            print(f"   Response: {overview_response.text}")
        
        # 3. Probar endpoint de user-growth
        print("\n3. Probando analytics/user-growth...")
        growth_response = requests.get(f"{base_url}/api/v1/admin/analytics/user-growth?period=12m", headers=headers)
        if growth_response.status_code == 200:
            growth = growth_response.json()
            print("   OK - User growth funcionando")
            print(f"   - Datos de crecimiento: {len(growth.get('userGrowth', []))} meses")
            if growth.get('userGrowth'):
                print("   - Últimos datos:")
                for data in growth['userGrowth'][-3:]:
                    print(f"     {data.get('month', 'N/A')}: {data.get('users', 0)} usuarios, {data.get('newUsers', 0)} nuevos")
        else:
            print(f"   ERROR - Status: {growth_response.status_code}")
            print(f"   Response: {growth_response.text}")
        
        # 4. Probar endpoint de revenue
        print("\n4. Probando analytics/revenue...")
        revenue_response = requests.get(f"{base_url}/api/v1/admin/analytics/revenue?period=12m", headers=headers)
        if revenue_response.status_code == 200:
            revenue = revenue_response.json()
            print("   OK - Revenue funcionando")
            print(f"   - Datos de ingresos: {len(revenue.get('revenueData', []))} meses")
            if revenue.get('revenueData'):
                print("   - Últimos datos:")
                for data in revenue['revenueData'][-3:]:
                    print(f"     {data.get('month', 'N/A')}: ${data.get('revenue', 0):,.0f} CLP, {data.get('subscriptions', 0)} suscripciones")
        else:
            print(f"   ERROR - Status: {revenue_response.status_code}")
            print(f"   Response: {revenue_response.text}")
        
        # 5. Probar endpoint de subscription-distribution
        print("\n5. Probando analytics/subscription-distribution...")
        distribution_response = requests.get(f"{base_url}/api/v1/admin/analytics/subscription-distribution", headers=headers)
        if distribution_response.status_code == 200:
            distribution = distribution_response.json()
            print("   OK - Subscription distribution funcionando")
            print("   - Distribución:")
            for dist in distribution.get('subscriptionDistribution', []):
                print(f"     {dist.get('name', 'N/A')}: {dist.get('value', 0)}%")
        else:
            print(f"   ERROR - Status: {distribution_response.status_code}")
            print(f"   Response: {distribution_response.text}")
        
        # 6. Probar endpoint de diagnostic-stats
        print("\n6. Probando analytics/diagnostic-stats...")
        diagnostic_response = requests.get(f"{base_url}/api/v1/admin/analytics/diagnostic-stats", headers=headers)
        if diagnostic_response.status_code == 200:
            diagnostic = diagnostic_response.json()
            print("   OK - Diagnostic stats funcionando")
            print("   - Estadísticas por framework:")
            for stat in diagnostic.get('diagnosticStats', []):
                print(f"     {stat.get('framework', 'N/A')}: {stat.get('completed', 0)} completados, {stat.get('inProgress', 0)} en progreso, {stat.get('total', 0)} total")
        else:
            print(f"   ERROR - Status: {diagnostic_response.status_code}")
            print(f"   Response: {diagnostic_response.text}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_analytics_endpoints()
