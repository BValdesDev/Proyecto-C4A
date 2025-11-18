#!/usr/bin/env python3
"""
Script para rotar claves JWT de forma segura
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.gestion_claves import obtener_gestor_claves
from app.core.config import ConfiguracionSeguridad
import argparse

def main():
    parser = argparse.ArgumentParser(description='Rotar claves JWT')
    parser.add_argument('--force', action='store_true', help='Forzar rotación sin confirmación')
    args = parser.parse_args()
    
    config = ConfiguracionSeguridad()
    
    if not args.force:
        print("⚠️  ADVERTENCIA: Esta acción rotará las claves JWT activas")
        print("Los tokens emitidos con claves anteriores seguirán siendo válidos durante el período de migración")
        print()
        confirmacion = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")
        
        if confirmacion.upper() != 'SI':
            print("Rotación cancelada")
            return
    
    print("🔄 Iniciando rotación de claves JWT...")
    
    try:
        gestor = obtener_gestor_claves()
        
        # Generar nuevo par de claves
        pub_key, priv_key, key_id = gestor.generar_nuevo_par_claves()
        
        print(f"✅ Nuevo par de claves generado (ID: {key_id})")
        
        # Rotar claves en Redis
        if gestor.rotar_claves():
            print("✅ Claves rotadas exitosamente en Redis")
            print()
            print("📋 Información de la nueva clave:")
            print(f"   - ID: {key_id}")
            print(f"   - Clave pública: {pub_key[:50]}...")
            print(f"   - Clave privada: {priv_key[:50]}...")
            print()
            print("⚠️  NOTA: Las claves anteriores se mantendrán válidas por 30 días")
            print("para permitir que los tokens existentes sigan funcionando")
            
        else:
            print("❌ Error rotando claves en Redis")
            print()
            print("Las claves se generaron pero no se guardaron en Redis")
            print("Puedes guardarlas manualmente en variables de entorno:")
            print()
            print("export JWT_PUBLIC_KEY='<clave_publica>'")
            print("export JWT_PRIVATE_KEY='<clave_privada>'")
            return 1
        
    except Exception as e:
        print(f"❌ Error durante la rotación: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("✅ Rotación completada exitosamente")
    return 0

if __name__ == "__main__":
    sys.exit(main())





























