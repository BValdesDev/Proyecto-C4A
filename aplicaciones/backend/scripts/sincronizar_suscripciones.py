#!/usr/bin/env python3
"""
Script para sincronizar los niveles de suscripción entre las tablas organizaciones y suscripciones
"""
import sys
sys.path.insert(0, '/app')

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion
from datetime import datetime, timedelta

def sincronizar_niveles_suscripcion():
    """Sincronizar niveles de suscripción entre organizaciones y suscripciones"""
    
    db = next(obtener_sesion())
    
    try:
        print("🔧 Sincronizando niveles de suscripción...")
        
        # Obtener todas las organizaciones
        organizaciones = db.query(Organizacion).all()
        
        for org in organizaciones:
            # Buscar suscripción activa
            suscripcion_activa = db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == org.id,
                Suscripcion.estado == "active"
            ).first()
            
            if suscripcion_activa:
                print(f"   Suscripción encontrada: {suscripcion_activa.nivel}")
                
                # Si los niveles no coinciden, actualizar la organización
                if org.nivel_suscripcion != suscripcion_activa.nivel:
                    org.nivel_suscripcion = suscripcion_activa.nivel
                    
                    # Actualizar límites según el nivel
                    if suscripcion_activa.nivel == NivelSuscripcion.GRATUITO:
                        org.maximo_usuarios = 1
                        org.maximo_evaluaciones_por_mes = 1
                        org.maximo_dias_retencion_datos = 30
                    elif suscripcion_activa.nivel == NivelSuscripcion.PRO:
                        org.maximo_usuarios = 10
                        org.maximo_evaluaciones_por_mes = 50
                        org.maximo_dias_retencion_datos = 365
                    elif suscripcion_activa.nivel == NivelSuscripcion.EMPRESARIAL:
                        org.maximo_usuarios = 100
                        org.maximo_evaluaciones_por_mes = 1000
                        org.maximo_dias_retencion_datos = 2555  # 7 años
                    
                    else:
                    print(f"   ✅ Niveles ya coinciden")
            else:
                print(f"   ❌ No hay suscripción activa")
                # Si no hay suscripción, crear una gratuita
                if org.nivel_suscripcion != NivelSuscripcion.GRATUITO:
                    print(f"   🔄 Creando suscripción gratuita...")
                    
                    suscripcion_gratuita = Suscripcion(
                        organizacion_id=org.id,
                        id_cliente_stripe="gratuito",
                        nivel=NivelSuscripcion.GRATUITO,
                        estado="active",
                        monto_centavos=0,
                        moneda="CLP",
                        ciclo_facturacion="mensual",
                        inicio_periodo_actual=datetime.utcnow(),
                        fin_periodo_actual=datetime.utcnow() + timedelta(days=365)
                    )
                    db.add(suscripcion_gratuita)
                    org.nivel_suscripcion = NivelSuscripcion.GRATUITO
                    print(f"   ✅ Suscripción gratuita creada")
        
        db.commit()
        print("\n🎉 ¡Sincronización completada exitosamente!")
        
        # Verificación final
        print("\n📊 Verificación final:")
        usuarios_empresariales = ['empresa@c4a.cl', 'maria@techcorp.cl', 'roberto@mineranorte.cl']
        
        for email in usuarios_empresariales:
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            if usuario and usuario.organizacion:
                suscripcion = db.query(Suscripcion).filter(
                    Suscripcion.organizacion_id == usuario.organizacion_id,
                    Suscripcion.estado == "active"
                ).first()
                
                if suscripcion:
                    print(f"   Nivel suscripción: {suscripcion.nivel}")
                    print(f"   Estado: {suscripcion.estado}")
                    print(f"   Monto: ${suscripcion.monto_clp:,.0f} CLP")
                else:
                    print(f"   ❌ Sin suscripción activa")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sincronizar_niveles_suscripcion()

