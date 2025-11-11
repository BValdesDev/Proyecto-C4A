#!/usr/bin/env python3
"""
Script para arreglar suscripciones empresariales
Este script es útil cuando necesitas crear o corregir suscripciones para usuarios empresariales
"""
import sys
import os

# Ajustar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'aplicaciones', 'backend'))

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion
from datetime import datetime, timedelta

def arreglar_suscripciones():
    db = next(obtener_sesion())
    
    try:
        print('🔧 Arreglando suscripciones empresariales...')
        
        # Lista de usuarios empresariales que necesitan suscripción
        usuarios_empresariales = [
            'empresa@c4a.cl',
            'maria@techcorp.cl', 
            'roberto@mineranorte.cl'
        ]
        
        for email in usuarios_empresariales:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            
            if not usuario:
                print(f'❌ Usuario no encontrado: {email}')
                continue
                
            if not usuario.organizacion_id:
                print(f'❌ Usuario sin organización: {email}')
                continue
            
            # Verificar si ya tiene suscripción
            suscripcion_existente = db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == usuario.organizacion_id
            ).first()
            
            if suscripcion_existente:
                print(f'ℹ️  Usuario {email} ya tiene suscripción: {suscripcion_existente.nivel}')
                
                # Actualizar a empresarial si es necesario
                if suscripcion_existente.nivel != NivelSuscripcion.EMPRESARIAL:
                    suscripcion_existente.nivel = NivelSuscripcion.EMPRESARIAL
                    suscripcion_existente.estado = 'active'
                    suscripcion_existente.monto_centavos = 7999000
                    print(f'✅ Suscripción actualizada a empresarial para: {email}')
                continue
            
            # Crear nueva suscripción empresarial
            suscripcion = Suscripcion(
                organizacion_id=usuario.organizacion_id,
                id_cliente_stripe=f'cliente_prueba_{usuario.id}',
                nivel=NivelSuscripcion.EMPRESARIAL,
                estado='active',
                monto_centavos=7999000,  # $79,990 CLP
                moneda='CLP',
                ciclo_facturacion='mensual',
                inicio_periodo_actual=datetime.utcnow(),
                fin_periodo_actual=datetime.utcnow() + timedelta(days=30),
                uso_evaluaciones_periodo_actual=0,
                uso_usuarios_periodo_actual=1
            )
            
            db.add(suscripcion)
            print(f'✅ Suscripción empresarial creada para: {email}')
        
        db.commit()
        print('\n' + '='*60)
        print('🎉 ¡Suscripciones arregladas exitosamente!')
        print('='*60)
        
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    arreglar_suscripciones()




