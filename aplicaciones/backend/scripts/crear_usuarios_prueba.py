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
from app.modelos.usuario import Usuario, EstadoCuenta
from app.modelos.organizacion import Organizacion, Sector, TamañoEmpresa
from app.modelos.rol import Rol, TipoRol
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion
from app.core.seguridad import SeguridadC4A

def crear_usuarios_prueba():
    """Crear usuarios de prueba para desarrollo"""
    
    db: Session = SessionLocal()
    
    try:
        print("🚀 Iniciando creación de usuarios de prueba...")
        
        # 1. Crear roles si no existen usando los métodos de clase
        roles_para_crear = [
            ("ADMIN_SISTEMA", Rol.crear_rol_admin_sistema),
            ("ADMIN_EMPRESA", Rol.crear_rol_admin_empresa),
            ("EVALUADOR", Rol.crear_rol_evaluador),
            ("USUARIO_BASICO", Rol.crear_rol_usuario_basico),
            ("AUDITOR", Rol.crear_rol_auditor),
        ]
        
        for tipo_rol, metodo_creacion in roles_para_crear:
            rol_existente = db.query(Rol).filter(Rol.nombre == getattr(TipoRol, tipo_rol)).first()
            if not rol_existente:
                rol = metodo_creacion()
                db.add(rol)
                print(f"✅ Rol creado: {tipo_rol}")
            else:
                print(f"ℹ️  Rol ya existe: {tipo_rol}")
        
        # 2. Los planes están definidos en NivelSuscripcion enum
        print("ℹ️  Planes de suscripción disponibles:")
        for nivel in NivelSuscripcion:
            print(f"   - {nivel.value}")
        
        # 3. Crear organizaciones de prueba
        organizaciones_data = [
            {
                "nombre": "Empresa ABC",
                "descripcion": "Empresa de tecnología líder en Chile",
                "sector": Sector.TECNOLOGIA,
                "tamaño": TamañoEmpresa.MEDIANA,
                "pais": "CL",
                "region": "Metropolitana"
            },
            {
                "nombre": "TechCorp Chile",
                "descripcion": "Consultora en transformación digital",
                "sector": Sector.SERVICIOS,
                "tamaño": TamañoEmpresa.GRANDE,
                "pais": "CL",
                "region": "Valparaíso"
            },
            {
                "nombre": "Startup Innovadora",
                "descripcion": "Startup en fase de crecimiento",
                "sector": Sector.FINANCIERO,
                "tamaño": TamañoEmpresa.PEQUEÑA,
                "pais": "CL",
                "region": "Metropolitana"
            },
            {
                "nombre": "Consultora Digital",
                "descripcion": "Especialistas en ciberseguridad",
                "sector": Sector.TECNOLOGIA,
                "tamaño": TamañoEmpresa.MEDIANA,
                "pais": "CL",
                "region": "Metropolitana"
            },
                {
                    "nombre": "C4A Administración",
                    "descripcion": "Organización interna para administradores del sistema",
                    "sector": Sector.TECNOLOGIA,
                    "tamaño": TamañoEmpresa.MEDIANA,
                    "pais": "CL",
                    "region": "Metropolitana"
                },
                {
                    "nombre": "Minera del Norte",
                    "descripcion": "Empresa minera con operaciones en el norte de Chile",
                    "sector": Sector.TECNOLOGIA,  # Usando sector existente
                    "tamaño": TamañoEmpresa.GRANDE,
                    "pais": "CL",
                    "region": "Antofagasta"
                },
                {
                    "nombre": "Retail Solutions",
                    "descripcion": "Cadena de retail con múltiples sucursales",
                    "sector": Sector.SERVICIOS,  # Usando sector existente
                    "tamaño": TamañoEmpresa.GRANDE,
                    "pais": "CL",
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
                "nombres": "Frank",
                "apellidos": "Bailey",
                "email": "frankbailey440@gmail.com",
                "password": "Fr@nk15481548",
                "rol": "ADMIN_SISTEMA",
                "organizacion": "C4A Administración",
                "activo": True
            },
            # Usuarios normales
            {
                "nombres": "Juan",
                "apellidos": "Pérez",
                "email": "juan@empresaabc.cl",
                "password": "Password123!",
                "rol": "EVALUADOR",
                "organizacion": "Empresa ABC",
                "activo": True
            },
            {
                "nombres": "María",
                "apellidos": "González",
                "email": "maria@techcorp.cl",
                "password": "Password123!",
                "rol": "EVALUADOR",
                "organizacion": "TechCorp Chile",
                "activo": True
            },
            {
                "nombres": "Carlos",
                "apellidos": "Silva",
                "email": "carlos@startup.cl",
                "password": "Password123!",
                "rol": "EVALUADOR",
                "organizacion": "Startup Innovadora",
                "activo": True
            },
            {
                "nombres": "Ana",
                "apellidos": "Martínez",
                "email": "ana@consultora.cl",
                "password": "Password123!",
                "rol": "EVALUADOR",
                "organizacion": "Consultora Digital",
                "activo": True
            },
                # Usuario mantenedor
                {
                    "nombres": "Admin",
                    "apellidos": "Mantenedor",
                    "email": "mantenedor@c4a.cl",
                    "password": "Mantenedor123!",
                    "rol": "ADMIN_EMPRESA",
                    "organizacion": "C4A Administración",
                    "activo": True
                },
                # Usuarios adicionales para datos más realistas
                {
                    "nombres": "Roberto",
                    "apellidos": "Silva",
                    "email": "roberto@mineranorte.cl",
                    "password": "Password123!",
                    "rol": "EVALUADOR",
                    "organizacion": "Minera del Norte",
                    "activo": True
                },
                {
                    "nombres": "Patricia",
                    "apellidos": "Morales",
                    "email": "patricia@retailsolutions.cl",
                    "password": "Password123!",
                    "rol": "EVALUADOR",
                    "organizacion": "Retail Solutions",
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
            tipo_rol = getattr(TipoRol, user_data["rol"])
            rol = db.query(Rol).filter(Rol.nombre == tipo_rol).first()
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
                nombres=user_data["nombres"],
                apellidos=user_data["apellidos"],
                email=user_data["email"],
                hash_contraseña=SeguridadC4A().obtener_hash_contraseña(user_data["password"]),
                rol_id=rol.id,
                organizacion_id=organizacion.id if organizacion else None,
                estado_cuenta=EstadoCuenta.ACTIVO if user_data["activo"] else EstadoCuenta.SUSPENDIDO,
                fecha_ultimo_acceso=datetime.utcnow() - timedelta(hours=1)  # Simular login reciente
            )
            
            db.add(usuario)
            print(f"✅ Usuario creado: {user_data['email']} ({user_data['rol']})")
        
        db.commit()
        
        # 5. Crear suscripciones de prueba (solo para usuarios con organizaciones)
        usuarios_con_org = db.query(Usuario).filter(Usuario.organizacion_id.isnot(None)).all()
        
        suscripciones_data = [
                {"usuario": "juan@empresaabc.cl", "nivel": NivelSuscripcion.PRO, "estado": "active"},
                {"usuario": "maria@techcorp.cl", "nivel": NivelSuscripcion.EMPRESARIAL, "estado": "active"},
                {"usuario": "carlos@startup.cl", "nivel": NivelSuscripcion.GRATUITO, "estado": "active"},
                {"usuario": "ana@consultora.cl", "nivel": NivelSuscripcion.PRO, "estado": "active"},
                {"usuario": "roberto@mineranorte.cl", "nivel": NivelSuscripcion.EMPRESARIAL, "estado": "past_due"},
                {"usuario": "patricia@retailsolutions.cl", "nivel": NivelSuscripcion.PRO, "estado": "active"},
            ]
        
        for susc_data in suscripciones_data:
            usuario = db.query(Usuario).filter(Usuario.email == susc_data["usuario"]).first()
            
            if usuario and usuario.organizacion_id:
                # Verificar si ya tiene suscripción activa
                suscripcion_existente = db.query(Suscripcion).filter(
                    Suscripcion.organizacion_id == usuario.organizacion_id,
                    Suscripcion.estado == susc_data.get("estado", "active")
                ).first()
                
                if not suscripcion_existente:
                    # Calcular monto según nivel (valores realistas para Chile)
                    montos = {
                        NivelSuscripcion.GRATUITO: 0,
                        NivelSuscripcion.PRO: 2499000,  # $24,990 CLP en centavos
                        NivelSuscripcion.EMPRESARIAL: 7999000,  # $79,990 CLP en centavos
                    }
                    
                    suscripcion = Suscripcion(
                        organizacion_id=usuario.organizacion_id,
                        id_cliente_stripe=f"cliente_prueba_{usuario.id}",
                        nivel=susc_data["nivel"],
                        estado=susc_data.get("estado", "active"),
                        monto_centavos=montos.get(susc_data["nivel"], 0),
                        moneda="CLP",
                        ciclo_facturacion="mensual",
                        inicio_periodo_actual=datetime.utcnow(),
                        fin_periodo_actual=datetime.utcnow() + timedelta(days=30),
                        uso_evaluaciones_periodo_actual=0,
                        uso_usuarios_periodo_actual=1
                    )
                    db.add(suscripcion)
                    print(f"✅ Suscripción creada: {susc_data['usuario']} -> {susc_data['nivel'].value}")
        
        db.commit()
        
        print("\n🎉 ¡Usuarios de prueba creados exitosamente!")
        print("\n📋 Resumen de usuarios creados:")
        print("=" * 50)
        
        usuarios_creados = db.query(Usuario).all()
        for usuario in usuarios_creados:
            rol = db.query(Rol).filter(Rol.id == usuario.rol_id).first()
            org = db.query(Organizacion).filter(Organizacion.id == usuario.organizacion_id).first() if usuario.organizacion_id else None
            
            print(f"👤 {usuario.nombres} {usuario.apellidos}")
            print(f"   📧 Email: {usuario.email}")
            print(f"   🔑 Rol: {rol.nombre if rol else 'N/A'}")
            print(f"   🏢 Organización: {org.nombre if org else 'N/A'}")
            print(f"   ✅ Estado: {usuario.estado_cuenta}")
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
