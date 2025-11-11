#!/usr/bin/env python3
"""
Script para crear usuarios de prueba para el sistema C4A SaaS
Incluye usuarios admin, usuarios normales y organizaciones de prueba

USO:
  python scripts/crear_usuarios_prueba.py          - Crear todos los usuarios
  python scripts/crear_usuarios_prueba.py basico   - Solo admin y empresa
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

def crear_roles(db: Session):
    """Crear roles básicos del sistema"""
    print("\n📋 Creando roles...")
    
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
    
    db.commit()

def crear_usuarios_basicos(db: Session):
    """Crear solo los usuarios básicos (admin y empresa)"""
    # Crear organizaciones básicas
    org_admin = db.query(Organizacion).filter(Organizacion.nombre == "C4A Admin").first()
    if not org_admin:
        org_admin = Organizacion(
            nombre="C4A Admin",
            descripcion="Organización administrativa del sistema",
            sector=Sector.TECNOLOGIA,
            tamaño=TamañoEmpresa.MEDIANA,
            pais="CL",
            region="Metropolitana"
        )
        db.add(org_admin)
        org_empresa = db.query(Organizacion).filter(Organizacion.nombre == "Empresa Demo").first()
    if not org_empresa:
        org_empresa = Organizacion(
            nombre="Empresa Demo",
            descripcion="Empresa de demostración con plan empresarial",
            sector=Sector.TECNOLOGIA,
            tamaño=TamañoEmpresa.GRANDE,
            pais="CL",
            region="Metropolitana"
        )
        db.add(org_empresa)
        db.commit()
    
    # Crear usuarios básicos
    usuarios_basicos = [
        {
            "nombres": "Admin",
            "apellidos": "Sistema",
            "email": "admin@c4a.cl",
            "password": "Admin123!",
            "rol": "ADMIN_SISTEMA",
            "organizacion": "C4A Admin",
            "activo": True
        },
        {
            "nombres": "Usuario",
            "apellidos": "Empresarial",
            "email": "empresa@c4a.cl",
            "password": "empresarial123",
            "rol": "ADMIN_EMPRESA",
            "organizacion": "Empresa Demo",
            "activo": True
        },
    ]
    
    for user_data in usuarios_basicos:
        # Verificar si el usuario ya existe
        usuario_existente = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
        if usuario_existente:
            continue
        
        # Buscar rol
        tipo_rol = getattr(TipoRol, user_data["rol"])
        rol = db.query(Rol).filter(Rol.nombre == tipo_rol).first()
        if not rol:
            continue
        
        # Buscar organización
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
            fecha_ultimo_acceso=datetime.utcnow() - timedelta(hours=1)
        )
        
        db.add(usuario)
        ")
    
    db.commit()
    
    # Crear suscripción empresarial para empresa@c4a.cl
    usuario_empresa = db.query(Usuario).filter(Usuario.email == "empresa@c4a.cl").first()
    if usuario_empresa and usuario_empresa.organizacion_id:
        susc_existente = db.query(Suscripcion).filter(
            Suscripcion.organizacion_id == usuario_empresa.organizacion_id
        ).first()
        
        if not susc_existente:
            suscripcion = Suscripcion(
                organizacion_id=usuario_empresa.organizacion_id,
                id_cliente_stripe="cliente_demo_empresarial",
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
            print("✅ Suscripción empresarial creada para empresa@c4a.cl")
    
    db.commit()

def crear_usuarios_completos(db: Session):
    """Crear usuarios completos incluyendo datos de prueba adicionales"""
    # Primero crear los usuarios básicos
    crear_usuarios_basicos(db)
    
    # Crear organizaciones adicionales
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
    ]
    
    for org_data in organizaciones_data:
        org_existente = db.query(Organizacion).filter(Organizacion.nombre == org_data["nombre"]).first()
        if not org_existente:
            organizacion = Organizacion(**org_data)
            db.add(organizacion)
            else:
            db.commit()
    
    # Crear usuarios adicionales
    usuarios_adicionales = [
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
    ]
    
    for user_data in usuarios_adicionales:
        usuario_existente = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
        if usuario_existente:
            continue
        
        tipo_rol = getattr(TipoRol, user_data["rol"])
        rol = db.query(Rol).filter(Rol.nombre == tipo_rol).first()
        
        organizacion = db.query(Organizacion).filter(
            Organizacion.nombre == user_data["organizacion"]
        ).first()
        
        usuario = Usuario(
            nombres=user_data["nombres"],
            apellidos=user_data["apellidos"],
            email=user_data["email"],
            hash_contraseña=SeguridadC4A().obtener_hash_contraseña(user_data["password"]),
            rol_id=rol.id,
            organizacion_id=organizacion.id if organizacion else None,
            estado_cuenta=EstadoCuenta.ACTIVO if user_data["activo"] else EstadoCuenta.SUSPENDIDO,
            fecha_ultimo_acceso=datetime.utcnow() - timedelta(hours=1)
        )
        
        db.add(usuario)
        ")
    
    db.commit()
    
    # Crear suscripciones para usuarios adicionales
    suscripciones_data = [
        {"usuario": "juan@empresaabc.cl", "nivel": NivelSuscripcion.PRO},
        {"usuario": "maria@techcorp.cl", "nivel": NivelSuscripcion.EMPRESARIAL},
        {"usuario": "carlos@startup.cl", "nivel": NivelSuscripcion.GRATUITO},
    ]
    
    for susc_data in suscripciones_data:
        usuario = db.query(Usuario).filter(Usuario.email == susc_data["usuario"]).first()
        
        if usuario and usuario.organizacion_id:
            susc_existente = db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == usuario.organizacion_id
            ).first()
            
            if not susc_existente:
                montos = {
                    NivelSuscripcion.GRATUITO: 0,
                    NivelSuscripcion.PRO: 2499000,
                    NivelSuscripcion.EMPRESARIAL: 7999000,
                }
                
                suscripcion = Suscripcion(
                    organizacion_id=usuario.organizacion_id,
                    id_cliente_stripe=f"cliente_prueba_{usuario.id}",
                    nivel=susc_data["nivel"],
                    estado="active",
                    monto_centavos=montos.get(susc_data["nivel"], 0),
                    moneda="CLP",
                    ciclo_facturacion="mensual",
                    inicio_periodo_actual=datetime.utcnow(),
                    fin_periodo_actual=datetime.utcnow() + timedelta(days=30),
                    uso_evaluaciones_periodo_actual=0,
                    uso_usuarios_periodo_actual=1
                )
                db.add(suscripcion)
                db.commit()

def mostrar_resumen(db: Session):
    """Mostrar resumen de usuarios creados"""
    print("\n" + "="*60)
    print("="*60)
    
    print("\n🔐 CREDENCIALES PRINCIPALES:")
    print("-" * 60)
    print("\n👑 Administrador del Sistema:")
    print("   URL: http://localhost:3000/login")
    print("   Redirige a: /admin/dashboard")
    
    print("   URL: http://localhost:3000/login")
    print("   Redirige a: /app/dashboard")
    
    usuarios_adicionales = db.query(Usuario).filter(
        Usuario.email.notin_(["admin@c4a.cl", "empresa@c4a.cl"])
    ).all()
    
    if usuarios_adicionales:
        for usuario in usuarios_adicionales:
            print("\n🌐 URLs de Acceso:")
    print("   Frontend: http://localhost:3000")
    print("   Admin Panel: http://localhost:3000/admin")
    print("   API Docs: http://localhost:8000/docs")
    print("="*60 + "\n")

def main():
    """Función principal"""
    db: Session = SessionLocal()
    
    try:
        # Crear roles primero
        crear_roles(db)
        
        # Verificar si se pasó argumento "basico"
        modo_basico = len(sys.argv) > 1 and sys.argv[1] == "basico"
        
        if modo_basico:
            print("\n📌 Modo BÁSICO: Solo creando admin y empresa")
            crear_usuarios_basicos(db)
        else:
            crear_usuarios_completos(db)
        
        # Mostrar resumen
        mostrar_resumen(db)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
