#!/usr/bin/env python3
"""
Script para probar específicamente el endpoint de diagnósticos
"""

import requests
import json

def test_diagnostics_endpoint():
    """Probar el endpoint de diagnósticos específicamente"""
    
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
            print(login_response.text)
            return False
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   OK - Login exitoso")
        
        # 2. Probar endpoint de diagnósticos
        print("\n2. Probando endpoint de diagnósticos...")
        diagnostics_response = requests.get(f"{base_url}/api/v1/admin/diagnostics", headers=headers)
        
        print(f"   Status Code: {diagnostics_response.status_code}")
        print(f"   Response Headers: {dict(diagnostics_response.headers)}")
        
        if diagnostics_response.status_code == 200:
            data = diagnostics_response.json()
            print("   OK - Endpoint funcionando")
            print(f"   Total diagnósticos: {data.get('total', 0)}")
            print(f"   Diagnósticos en respuesta: {len(data.get('diagnostics', []))}")
            
            if data.get('diagnostics'):
                print("   Primeros diagnósticos:")
                for i, diag in enumerate(data['diagnostics'][:3]):
                    print(f"     {i+1}. {diag.get('companyName', 'N/A')} - {diag.get('userName', 'N/A')} - {diag.get('status', 'N/A')}")
        else:
            print(f"   ERROR - Status: {diagnostics_response.status_code}")
            print(f"   Response: {diagnostics_response.text}")
            
        return diagnostics_response.status_code == 200
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_diagnostics_endpoint()
