#!/usr/bin/env python3
"""
Script para arreglar las suscripciones empresariales
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion

def arreglar_suscripciones():
    """Arreglar suscripciones empresariales"""
    
    db = next(obtener_sesion())
    
    try:
        print("🔧 Arreglando suscripciones empresariales...")
        
        # Usuarios que deberían tener plan empresarial
        usuarios_empresariales = [
            "maria@techcorp.cl",
            "roberto@mineranorte.cl"
        ]
        
        for email in usuarios_empresariales:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            
            if not usuario:
                print(f"❌ Usuario no encontrado: {email}")
                continue
                
            if not usuario.organizacion_id:
                print(f"❌ Usuario sin organización: {email}")
                continue
            
            # Verificar si ya tiene suscripción
            suscripcion_existente = db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == usuario.organizacion_id
            ).first()
            
            if suscripcion_existente:
                print(f"ℹ️  Usuario {email} ya tiene suscripción: {suscripcion_existente.nivel}")
                continue
            
            # Crear suscripción empresarial
            suscripcion = Suscripcion(
                organizacion_id=usuario.organizacion_id,
                id_cliente_stripe=f"cliente_prueba_{usuario.id}",
                nivel=NivelSuscripcion.EMPRESARIAL,
                estado="active",
                monto_centavos=7999000,  # $79,990 CLP
                moneda="CLP",
                ciclo_facturacion="mensual",
                inicio_periodo_actual=datetime.utcnow(),
                fin_periodo_actual=datetime.utcnow() + timedelta(days=30),
                uso_evaluaciones_periodo_actual=0,
                uso_usuarios_periodo_actual=1
            )
            
            db.add(suscripcion)
            print(f"✅ Suscripción empresarial creada para: {email}")
        
        db.commit()
        
        print("\n🎉 ¡Suscripciones arregladas exitosamente!")
        print("\n📋 Verificación final:")
        
        for email in usuarios_empresariales:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            if usuario and usuario.organizacion_id:
                suscripcion = db.query(Suscripcion).filter(
                    Suscripcion.organizacion_id == usuario.organizacion_id
                ).first()
                
                if suscripcion:
                    print(f"✅ {email}: {suscripcion.nivel} ({suscripcion.estado})")
                else:
                    print(f"❌ {email}: Sin suscripción")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    arreglar_suscripciones()







