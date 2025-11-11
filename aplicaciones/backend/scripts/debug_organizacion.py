#!/usr/bin/env python3
"""
Script para debuggear la organización y sus límites
"""
import sys
sys.path.insert(0, '/app')

from sqlalchemy.orm import Session
from app.modelos.base import SessionLocal
from app.modelos.organizacion import Organizacion
from app.modelos.usuario import Usuario
from datetime import datetime

def debug_organizacion():
    db = SessionLocal()
    
    try:
        # Buscar usuario empresa@c4a.cl
        usuario = db.query(Usuario).filter(Usuario.email == "empresa@c4a.cl").first()
        if not usuario:
            return
        
        organizacion = usuario.organizacion
        # Contar evaluaciones del mes actual
        ahora = datetime.utcnow().replace(tzinfo=None)
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        evaluaciones_mes = len([
            e for e in organizacion.evaluaciones 
            if e.fecha_creacion.replace(tzinfo=None) >= inicio_mes and e.fecha_eliminacion is None
        ])
        
        print(f"\n📈 ESTADÍSTICAS DEL MES ACTUAL:")
        # Verificar todas las evaluaciones
        for i, eval in enumerate(organizacion.evaluaciones):
            if eval.fecha_eliminacion is None:
                print(f"\n🔧 DIAGNÓSTICO:")
        if organizacion.suscripcion_vencida:
            print("   ❌ Suscripción vencida")
        elif evaluaciones_mes >= organizacion.maximo_evaluaciones_por_mes:
            ")
        else:
            ")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_organizacion()

