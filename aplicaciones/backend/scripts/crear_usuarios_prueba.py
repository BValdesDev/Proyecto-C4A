#!/usr/bin/env python3
"""
Script para crear usuarios de prueba para el sistema C4A SaaS
Incluye usuarios admin, usuarios normales y organizaciones de prueba
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modelos.base import engine, SessionLocal
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.rol import Rol
from app.modelos.suscripcion import Suscripcion, PlanSuscripcion
from app.core.seguridad import get_password_hash

def crear_usuarios_prueba():
    """Crear usuarios de prueba para desarrollo"""
    
    db: Session = SessionLocal()
    
    try:
        print("🚀 Iniciando creación de usuarios de prueba...")
        
        # 1. Crear roles si no existen
        roles_data = [
            {"nombre": "admin", "descripcion": "Administrador del sistema"},
            {"nombre": "mantenedor", "descripcion": "Mantenedor de la plataforma"},
            {"nombre": "usuario", "descripcion": "Usuario estándar"},
        ]
        
        for rol_data in roles_data:
            rol_existente = db.query(Rol).filter(Rol.nombre == rol_data["nombre"]).first()
            if not rol_existente:
                rol = Rol(**rol_data)
                db.add(rol)
                print(f"✅ Rol creado: {rol_data['nombre']}")
            else:
                print(f"ℹ️  Rol ya existe: {rol_data['nombre']}")
        
        # 2. Crear planes de suscripción si no existen
        planes_data = [
            {
                "nombre": "Gratuito",
                "descripcion": "Plan básico gratuito",
                "precio_mensual": 0,
                "precio_anual": 0,
                "max_evaluaciones": 1,
                "max_usuarios": 1,
                "caracteristicas": ["1 evaluación mensual", "Reporte básico"]
            },
            {
                "nombre": "Pro",
                "descripcion": "Plan profesional",
                "precio_mensual": 29990,
                "precio_anual": 299900,
                "max_evaluaciones": 10,
                "max_usuarios": 5,
                "caracteristicas": ["10 evaluaciones mensuales", "Reportes avanzados", "Soporte prioritario"]
            },
            {
                "nombre": "Empresarial",
                "descripcion": "Plan empresarial",
                "precio_mensual": 99990,
                "precio_anual": 999900,
                "max_evaluaciones": -1,  # Ilimitado
                "max_usuarios": -1,      # Ilimitado
                "caracteristicas": ["Evaluaciones ilimitadas", "Múltiples frameworks", "Soporte 24/7", "API access"]
            }
        ]
        
        for plan_data in planes_data:
            plan_existente = db.query(PlanSuscripcion).filter(PlanSuscripcion.nombre == plan_data["nombre"]).first()
            if not plan_existente:
                plan = PlanSuscripcion(**plan_data)
                db.add(plan)
                print(f"✅ Plan creado: {plan_data['nombre']}")
            else:
                print(f"ℹ️  Plan ya existe: {plan_data['nombre']}")
        
        db.commit()
        
        # 3. Crear organizaciones de prueba
        organizaciones_data = [
            {
                "nombre": "Empresa ABC",
                "descripcion": "Empresa de tecnología líder en Chile",
                "sector": "Tecnología",
                "tamaño": "Mediana",
                "pais": "Chile",
                "region": "Metropolitana"
            },
            {
                "nombre": "TechCorp Chile",
                "descripcion": "Consultora en transformación digital",
                "sector": "Consultoría",
                "tamaño": "Grande",
                "pais": "Chile",
                "region": "Valparaíso"
            },
            {
                "nombre": "Startup Innovadora",
                "descripcion": "Startup en fase de crecimiento",
                "sector": "Fintech",
                "tamaño": "Pequeña",
                "pais": "Chile",
                "region": "Metropolitana"
            },
            {
                "nombre": "Consultora Digital",
                "descripcion": "Especialistas en ciberseguridad",
                "sector": "Seguridad",
                "tamaño": "Mediana",
                "pais": "Chile",
                "region": "Metropolitana"
            }
        ]
        
        organizaciones = []
        for org_data in organizaciones_data:
            org_existente = db.query(Organizacion).filter(Organizacion.nombre == org_data["nombre"]).first()
            if not org_existente:
                organizacion = Organizacion(**org_data)
                db.add(organizacion)
                organizaciones.append(organizacion)
                print(f"✅ Organización creada: {org_data['nombre']}")
            else:
                organizaciones.append(org_existente)
                print(f"ℹ️  Organización ya existe: {org_data['nombre']}")
        
        db.commit()
        
        # 4. Crear usuarios de prueba
        usuarios_data = [
            # Usuario Admin (el que mencionaste)
            {
                "nombre": "Frank Bailey",
                "email": "frankbailey440@gmail.com",
                "password": "Fr@nk15481548",
                "rol": "admin",
                "organizacion": None,  # Admin no necesita organización
                "activo": True
            },
            # Usuarios normales
            {
                "nombre": "Juan Pérez",
                "email": "juan@empresaabc.cl",
                "password": "Password123!",
                "rol": "usuario",
                "organizacion": "Empresa ABC",
                "activo": True
            },
            {
                "nombre": "María González",
                "email": "maria@techcorp.cl",
                "password": "Password123!",
                "rol": "usuario",
                "organizacion": "TechCorp Chile",
                "activo": True
            },
            {
                "nombre": "Carlos Silva",
                "email": "carlos@startup.cl",
                "password": "Password123!",
                "rol": "usuario",
                "organizacion": "Startup Innovadora",
                "activo": True
            },
            {
                "nombre": "Ana Martínez",
                "email": "ana@consultora.cl",
                "password": "Password123!",
                "rol": "usuario",
                "organizacion": "Consultora Digital",
                "activo": True
            },
            # Usuario mantenedor
            {
                "nombre": "Admin Mantenedor",
                "email": "mantenedor@c4a.cl",
                "password": "Mantenedor123!",
                "rol": "mantenedor",
                "organizacion": None,
                "activo": True
            }
        ]
        
        for user_data in usuarios_data:
            # Verificar si el usuario ya existe
            usuario_existente = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
            if usuario_existente:
                print(f"ℹ️  Usuario ya existe: {user_data['email']}")
                continue
            
            # Buscar rol
            rol = db.query(Rol).filter(Rol.nombre == user_data["rol"]).first()
            if not rol:
                print(f"❌ Error: Rol '{user_data['rol']}' no encontrado")
                continue
            
            # Buscar organización si se especifica
            organizacion = None
            if user_data["organizacion"]:
                organizacion = db.query(Organizacion).filter(
                    Organizacion.nombre == user_data["organizacion"]
                ).first()
            
            # Crear usuario
            usuario = Usuario(
                nombre=user_data["nombre"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                rol_id=rol.id,
                organizacion_id=organizacion.id if organizacion else None,
                activo=user_data["activo"],
                fecha_registro=datetime.utcnow(),
                ultimo_login=datetime.utcnow() - timedelta(hours=1)  # Simular login reciente
            )
            
            db.add(usuario)
            print(f"✅ Usuario creado: {user_data['email']} ({user_data['rol']})")
        
        db.commit()
        
        # 5. Crear suscripciones de prueba
        planes = db.query(PlanSuscripcion).all()
        usuarios_normales = db.query(Usuario).filter(Usuario.rol_id != db.query(Rol).filter(Rol.nombre == "admin").first().id).all()
        
        suscripciones_data = [
            {"usuario": "juan@empresaabc.cl", "plan": "Pro"},
            {"usuario": "maria@techcorp.cl", "plan": "Empresarial"},
            {"usuario": "carlos@startup.cl", "plan": "Gratuito"},
            {"usuario": "ana@consultora.cl", "plan": "Pro"},
        ]
        
        for susc_data in suscripciones_data:
            usuario = db.query(Usuario).filter(Usuario.email == susc_data["usuario"]).first()
            plan = db.query(PlanSuscripcion).filter(PlanSuscripcion.nombre == susc_data["plan"]).first()
            
            if usuario and plan:
                # Verificar si ya tiene suscripción activa
                suscripcion_existente = db.query(Suscripcion).filter(
                    Suscripcion.usuario_id == usuario.id,
                    Suscripcion.estado == "activa"
                ).first()
                
                if not suscripcion_existente:
                    suscripcion = Suscripcion(
                        usuario_id=usuario.id,
                        plan_id=plan.id,
                        estado="activa",
                        fecha_inicio=datetime.utcnow(),
                        fecha_fin=datetime.utcnow() + timedelta(days=30)
                    )
                    db.add(suscripcion)
                    print(f"✅ Suscripción creada: {susc_data['usuario']} -> {susc_data['plan']}")
        
        db.commit()
        
        print("\n🎉 ¡Usuarios de prueba creados exitosamente!")
        print("\n📋 Resumen de usuarios creados:")
        print("=" * 50)
        
        usuarios_creados = db.query(Usuario).all()
        for usuario in usuarios_creados:
            rol = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
            org = db.query(Organizacion).filter(Organizacion.id == usuario.organizacion_id).first() if usuario.organizacion_id else None
            
            print(f"👤 {usuario.nombre}")
            print(f"   📧 Email: {usuario.email}")
            print(f"   🔑 Rol: {rol.nombre if rol else 'N/A'}")
            print(f"   🏢 Organización: {org.nombre if org else 'N/A'}")
            print(f"   ✅ Activo: {usuario.activo}")
            print()
        
        print("🔐 Credenciales de acceso:")
        print("=" * 50)
        print("👑 ADMIN:")
        print("   Email: frankbailey440@gmail.com")
        print("   Password: Fr@nk15481548")
        print()
        print("👨‍💼 MANTENEDOR:")
        print("   Email: mantenedor@c4a.cl")
        print("   Password: Mantenedor123!")
        print()
        print("👥 USUARIOS NORMALES:")
        print("   Email: juan@empresaabc.cl | Password: Password123!")
        print("   Email: maria@techcorp.cl | Password: Password123!")
        print("   Email: carlos@startup.cl | Password: Password123!")
        print("   Email: ana@consultora.cl | Password: Password123!")
        print()
        print("🌐 URLs de acceso:")
        print("   Frontend: http://localhost:3000")
        print("   Admin: http://localhost:3000/admin")
        print("   API Docs: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error creando usuarios de prueba: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    crear_usuarios_prueba()
