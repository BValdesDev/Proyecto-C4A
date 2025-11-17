#!/usr/bin/env python3
"""
Script para crear usuario con plan gratuito
Email: gratuito@c4a.cl
Password: gratuito123
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Ajustar path para imports
sys.path.insert(0, '/app')

from app.modelos.base import engine, SessionLocal
from app.modelos.usuario import Usuario, EstadoCuenta
from app.modelos.organizacion import Organizacion, Sector, TamañoEmpresa
from app.modelos.rol import Rol, TipoRol
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion
from app.core.seguridad import SeguridadC4A

def crear_usuario_gratuito():
    """Crear usuario con plan gratuito"""
    db: Session = SessionLocal()
    
    try:
        print("\n🔧 Creando usuario con plan gratuito...")
        
        # Verificar si el usuario ya existe
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == "gratuito@c4a.cl",
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if usuario_existente:
            print("⚠️  El usuario gratuito@c4a.cl ya existe")
            print("   Eliminando usuario existente para recrearlo...")
            # Eliminar suscripciones asociadas
            if usuario_existente.organizacion_id:
                suscripciones = db.query(Suscripcion).filter(
                    Suscripcion.organizacion_id == usuario_existente.organizacion_id
                ).all()
                for susc in suscripciones:
                    db.delete(susc)
            db.delete(usuario_existente)
            db.commit()
        
        # Crear o buscar roles
        print("\n📋 Verificando roles...")
        rol_evaluador = db.query(Rol).filter(Rol.nombre == TipoRol.EVALUADOR).first()
        if not rol_evaluador:
            print("   Creando rol EVALUADOR...")
            rol_evaluador = Rol.crear_rol_evaluador()
            db.add(rol_evaluador)
            db.commit()
            db.refresh(rol_evaluador)
        else:
            print("   ✅ Rol EVALUADOR encontrado")
        
        # Crear o buscar organización
        print("\n🏢 Creando organización...")
        organizacion = db.query(Organizacion).filter(
            Organizacion.nombre == "Usuario Gratuito"
        ).first()
        
        if not organizacion:
            organizacion = Organizacion(
                nombre="Usuario Gratuito",
                descripcion="Organización de prueba con plan gratuito",
                sector=Sector.TECNOLOGIA,
                tamaño=TamañoEmpresa.PEQUEÑA,
                pais="CL",
                region="Metropolitana",
                nivel_suscripcion=NivelSuscripcion.GRATUITO
            )
            db.add(organizacion)
            db.flush()
            print("   ✅ Organización creada")
        else:
            # Actualizar nivel de suscripción
            organizacion.nivel_suscripcion = NivelSuscripcion.GRATUITO
            print("   ✅ Organización encontrada, actualizando nivel a GRATUITO")
        
        # Crear usuario
        print("\n👤 Creando usuario...")
        seguridad = SeguridadC4A()
        hash_password = seguridad.obtener_hash_contraseña("gratuito123")
        
        usuario = Usuario(
            nombres="Usuario",
            apellidos="Gratuito",
            email="gratuito@c4a.cl",
            hash_contraseña=hash_password,
            rol_id=rol_evaluador.id,
            organizacion_id=organizacion.id,
            estado_cuenta=EstadoCuenta.ACTIVO,
            idioma_preferido="es_CL",
            zona_horaria="America/Santiago",
            fecha_ultimo_acceso=datetime.utcnow() - timedelta(hours=1)
        )
        
        db.add(usuario)
        db.flush()
        print("   ✅ Usuario creado")
        
        # Crear suscripción activa
        print("\n💳 Creando suscripción...")
        suscripcion_existente = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == organizacion.id,
            Suscripcion.estado == "active"
        ).first()
        
        if not suscripcion_existente:
            suscripcion = Suscripcion(
                organizacion_id=organizacion.id,
                id_cliente_stripe=f"cliente_gratuito_{organizacion.id}",
                nivel=NivelSuscripcion.GRATUITO,
                estado="active",
                monto_centavos=0,  # Plan gratuito
                moneda="CLP",
                ciclo_facturacion="mensual",
                inicio_periodo_actual=datetime.utcnow(),
                fin_periodo_actual=datetime.utcnow() + timedelta(days=365),  # 1 año
                uso_evaluaciones_periodo_actual=0,
                uso_usuarios_periodo_actual=1
            )
            db.add(suscripcion)
            print("   ✅ Suscripción GRATUITA creada")
        else:
            # Actualizar suscripción existente
            suscripcion_existente.nivel = NivelSuscripcion.GRATUITO
            suscripcion_existente.estado = "active"
            suscripcion_existente.monto_centavos = 0
            print("   ✅ Suscripción actualizada a GRATUITO")
        
        db.commit()
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("✅ USUARIO CREADO EXITOSAMENTE")
        print("="*60)
        print(f"\n📧 Email: gratuito@c4a.cl")
        print(f"🔑 Password: gratuito123")
        print(f"👤 Rol: EVALUADOR")
        print(f"🏢 Organización: {organizacion.nombre}")
        print(f"💳 Plan: GRATUITO")
        print(f"📊 Características:")
        print(f"   - 10 preguntas (5-7 minutos)")
        print(f"   - 3 recomendaciones prioritarias")
        print(f"   - 1 evaluación por mes")
        print(f"   - Reportes con marca de agua")
        print(f"\n🌐 Acceso:")
        print(f"   URL: http://localhost:3000/login")
        print(f"   Redirige a: /app/dashboard")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    crear_usuario_gratuito()



