#!/usr/bin/env python3
"""
Script para crear frameworks (NIST CSF y COBIT 2019) en C4A SaaS
"""
import sys
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.modelos.base import SessionLocal
from app.modelos.framework import Framework

def crear_frameworks():
    db = SessionLocal()
    
    try:
        print("🚀 Creando frameworks...")
        
        # 1. Framework NIST CSF 2.0
        framework_nist = db.query(Framework).filter(Framework.nombre == "NIST_CSF").first()
        if not framework_nist:
            framework_nist = Framework(
                nombre="NIST_CSF",
                version="2.0",
                nombre_mostrar="NIST Cybersecurity Framework 2.0",
                descripcion="Marco de Ciberseguridad del Instituto Nacional de Estándares y Tecnología de Estados Unidos",
                niveles_disponibles=["gratuito", "pro", "empresarial"],
                esta_activo=True
            )
            db.add(framework_nist)
            db.flush()
            print(f"✅ Framework NIST CSF 2.0 creado (ID: {framework_nist.id})")
        else:
            print(f"ℹ️  Framework NIST CSF 2.0 ya existe (ID: {framework_nist.id})")
        
        # 2. Framework COBIT 2019
        framework_cobit = db.query(Framework).filter(Framework.nombre == "COBIT_2019").first()
        if not framework_cobit:
            framework_cobit = Framework(
                nombre="COBIT_2019",
                version="2019",
                nombre_mostrar="COBIT 2019",
                descripcion="Control Objectives for Information and Related Technologies",
                niveles_disponibles=["pro", "empresarial"],
                esta_activo=True
            )
            db.add(framework_cobit)
            db.flush()
            print(f"✅ Framework COBIT 2019 creado (ID: {framework_cobit.id})")
        else:
            print(f"ℹ️  Framework COBIT 2019 ya existe (ID: {framework_cobit.id})")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✅ FRAMEWORKS CREADOS EXITOSAMENTE")
        print("="*60)
        print(f"\n📚 FRAMEWORKS DISPONIBLES:\n")
        print(f"1. NIST CSF 2.0")
        print(f"   ID: {framework_nist.id}")
        print(f"   Niveles: {', '.join(framework_nist.niveles_disponibles)}\n")
        print(f"2. COBIT 2019")
        print(f"   ID: {framework_cobit.id}")
        print(f"   Niveles: {', '.join(framework_cobit.niveles_disponibles)}\n")
        print("="*60)
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_frameworks()

