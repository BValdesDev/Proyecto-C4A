#!/usr/bin/env python3
"""
Script para configurar el usuario empresarial (empresa@c4a.cl)
Asegura que tenga suscripción empresarial activa y nivel correcto
"""

import os
import sys
from datetime import datetime, timedelta

# Ajustar path para imports
sys.path.insert(0, '/app')

from app.modelos.base import SessionLocal
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion
from app.servicios.suscripcion_service import ServicioSuscripcion
from app.core.seguridad import SeguridadC4A

def configurar_usuario_empresarial():
    """Configurar usuario empresarial con suscripción activa"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Configurando Usuario Empresarial")
        print("=" * 60)
        print()
        
        # Buscar usuario
        usuario = db.query(Usuario).filter(
            Usuario.email == "empresa@c4a.cl"
        ).first()
        
        if not usuario:
            print("❌ Usuario empresa@c4a.cl no encontrado")
            print("   Ejecuta primero: python scripts/crear_usuarios_prueba.py basico")
            return False
        
        print(f"✅ Usuario encontrado: {usuario.nombres} {usuario.apellidos}")
        print(f"   Email: {usuario.email}")
        print(f"   Organización ID: {usuario.organizacion_id}")
        print()
        
        if not usuario.organizacion_id:
            print("❌ Usuario sin organización asignada")
            return False
        
        # Buscar organización
        organizacion = db.query(Organizacion).filter(
            Organizacion.id == usuario.organizacion_id
        ).first()
        
        if not organizacion:
            print("❌ Organización no encontrada")
            return False
        
        print(f"✅ Organización encontrada: {organizacion.nombre}")
        print(f"   Nivel actual en organización: {organizacion.nivel_suscripcion.value}")
        print()
        
        # Verificar o crear suscripción empresarial
        suscripcion = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        if suscripcion:
            print(f"ℹ️  Suscripción existente encontrada:")
            print(f"   Nivel: {suscripcion.nivel.value}")
            print(f"   Estado: {suscripcion.estado}")
            
            if suscripcion.nivel != NivelSuscripcion.EMPRESARIAL:
                print(f"   ⚠️  Actualizando nivel a EMPRESARIAL...")
                suscripcion.nivel = NivelSuscripcion.EMPRESARIAL
                suscripcion.estado = "active"
                suscripcion.monto_centavos = 24000000  # $240.000 CLP
                suscripcion.fin_periodo_actual = datetime.utcnow() + timedelta(days=30)
                print(f"   ✅ Suscripción actualizada a EMPRESARIAL")
            else:
                print(f"   ✅ Suscripción ya es EMPRESARIAL")
        else:
            print("📝 Creando nueva suscripción empresarial...")
            suscripcion = Suscripcion(
                organizacion_id=organizacion.id,
                id_cliente_stripe="cliente_demo_empresarial",
                nivel=NivelSuscripcion.EMPRESARIAL,
                estado="active",
                monto_centavos=24000000,  # $240.000 CLP
                moneda="CLP",
                ciclo_facturacion="mensual",
                inicio_periodo_actual=datetime.utcnow(),
                fin_periodo_actual=datetime.utcnow() + timedelta(days=30),
                uso_evaluaciones_periodo_actual=0,
                uso_usuarios_periodo_actual=1
            )
            db.add(suscripcion)
            print("   ✅ Suscripción empresarial creada")
        
        db.commit()
        print()
        
        # Sincronizar nivel en organización
        print("🔄 Sincronizando nivel en organización...")
        servicio = ServicioSuscripcion(db)
        nivel_real = servicio.obtener_nivel_suscripcion_activa(str(organizacion.id))
        
        if nivel_real != NivelSuscripcion.EMPRESARIAL:
            print(f"   ⚠️  Nivel real: {nivel_real.value}, esperado: EMPRESARIAL")
        else:
            print(f"   ✅ Nivel real confirmado: {nivel_real.value}")
        
        # Sincronizar
        if servicio.sincronizar_nivel_organizacion(str(organizacion.id)):
            print("   ✅ Organización sincronizada correctamente")
        else:
            print("   ⚠️  Error al sincronizar organización")
        
        db.commit()
        print()
        
        # Verificación final
        print("=" * 60)
        print("Verificación Final")
        print("=" * 60)
        
        organizacion_refresh = db.query(Organizacion).filter(
            Organizacion.id == organizacion.id
        ).first()
        
        suscripcion_final = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        print(f"📊 Estado Final:")
        print(f"   Organización: {organizacion_refresh.nombre}")
        print(f"   Nivel en organización: {organizacion_refresh.nivel_suscripcion.value}")
        print(f"   Suscripción activa: {suscripcion_final.nivel.value if suscripcion_final else 'N/A'}")
        print(f"   Estado suscripción: {suscripcion_final.estado if suscripcion_final else 'N/A'}")
        print()
        
        if organizacion_refresh.nivel_suscripcion == NivelSuscripcion.EMPRESARIAL:
            print("✅ ¡Configuración exitosa!")
            print()
            print("🔐 Credenciales:")
            print("   Email: empresa@c4a.cl")
            print("   Password: empresarial123")
            print()
            print("📋 El usuario debería poder ver 100 preguntas del plan empresarial")
            return True
        else:
            print("❌ Error: El nivel no se configuró correctamente")
            return False
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = configurar_usuario_empresarial()
    sys.exit(0 if success else 1)









