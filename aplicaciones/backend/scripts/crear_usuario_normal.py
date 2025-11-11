#!/usr/bin/env python3
"""
Script para crear un usuario normal (no admin) que vaya al dashboard de usuario
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario, EstadoCuenta
from app.modelos.organizacion import Organizacion, Sector, TamañoEmpresa
from app.modelos.rol import Rol, TipoRol
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion
from app.core.seguridad import SeguridadC4A

def crear_usuario_normal():
    db = next(obtener_sesion())
    try:
        ...")
        
        # Buscar rol EVALUADOR
        rol_evaluador = db.query(Rol).filter(Rol.nombre == TipoRol.EVALUADOR).first()
        if not rol_evaluador:
            print("❌ Error: Rol EVALUADOR no encontrado")
            return
        
        # Crear o buscar organización
        org = db.query(Organizacion).filter(Organizacion.nombre == "Empresa Usuario Normal").first()
        if not org:
            org = Organizacion(
                nombre="Empresa Usuario Normal",
                sector=Sector.TECNOLOGIA,
                tamaño=TamañoEmpresa.MEDIANA,
                pais="CL",
                region="Metropolitana",
                nivel_suscripcion=NivelSuscripcion.PRO,
                maximo_usuarios=5,
                maximo_evaluaciones_por_mes=10,
                maximo_dias_retencion_datos=90,
                consentimiento_otorgado=True,
                politica_privacidad_aceptada=True
            )
            db.add(org)
            db.flush()  # Para obtener el ID
            # Crear usuario
        usuario_existente = db.query(Usuario).filter(Usuario.email == "usuario@normal.cl").first()
        if usuario_existente:
            return
        
        # Hash de contraseña
        seguridad = SeguridadC4A()
        hash_password = seguridad.obtener_hash_contraseña("Usuario123!")
        
        usuario = Usuario(
            email="usuario@normal.cl",
            nombres="Usuario",
            apellidos="Normal",
            hash_contraseña=hash_password,
            organizacion_id=org.id,
            rol_id=rol_evaluador.id,
            estado_cuenta=EstadoCuenta.ACTIVO,
            idioma_preferido="es_CL",
            zona_horaria="America/Santiago",
            notificaciones_email=True,
            notificaciones_push=False
        )
        
        db.add(usuario)
        db.commit()
        
        print(f"   Nivel: {org.nivel_suscripcion}")
        print(f"   Redirige a: /app/dashboard")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    crear_usuario_normal()
