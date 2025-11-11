#!/usr/bin/env python3
"""
Script para actualizar los montos de las suscripciones a valores más realistas
"""

import os
import sys
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modelos.base import SessionLocal
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion

def actualizar_montos():
    """Actualizar montos de suscripciones a valores realistas"""
    
    db = SessionLocal()
    
    try:
        print("🔄 Actualizando montos de suscripciones...")
        
        # Actualizar suscripciones Pro
        suscripciones_pro = db.query(Suscripcion).filter(
            Suscripcion.nivel == NivelSuscripcion.PRO
        ).all()
        
        for suscripcion in suscripciones_pro:
            if suscripcion.monto_centavos != 2499000:  # Solo actualizar si es diferente
                suscripcion.monto_centavos = 2499000
        
        # Actualizar suscripciones Empresarial
        suscripciones_empresarial = db.query(Suscripcion).filter(
            Suscripcion.nivel == NivelSuscripcion.EMPRESARIAL
        ).all()
        
        for suscripcion in suscripciones_empresarial:
            if suscripcion.monto_centavos != 7999000:  # Solo actualizar si es diferente
                suscripcion.monto_centavos = 7999000
        
        # Actualizar suscripciones Gratuito (asegurar que sean 0)
        suscripciones_gratuito = db.query(Suscripcion).filter(
            Suscripcion.nivel == NivelSuscripcion.GRATUITO
        ).all()
        
        for suscripcion in suscripciones_gratuito:
            if suscripcion.monto_centavos != 0:
                suscripcion.monto_centavos = 0
        
        db.commit()
        
        print("✅ Montos actualizados exitosamente!")
        
        # Mostrar resumen
        print("\n📊 Resumen de suscripciones actualizadas:")
        todas_las_suscripciones = db.query(Suscripcion).all()
        
        for suscripcion in todas_las_suscripciones:
            monto_formateado = f"${suscripcion.monto_centavos // 100:,.0f}" if suscripcion.monto_centavos > 0 else "Gratuito"
            except Exception as e:
        print(f"❌ Error actualizando montos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    actualizar_montos()


