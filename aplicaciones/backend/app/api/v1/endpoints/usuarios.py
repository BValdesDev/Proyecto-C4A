# app/api/v1/endpoints/usuarios.py
"""
Endpoints de gestión de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.rol import Rol
from app.modelos.log_auditoria import LogAuditoria
from app.core.seguridad import seguridad
from app.core.excepciones import ExcepcionValidacion, ExcepcionRecursoNoEncontrado
from ..dependencias import (
    obtener_usuario_actual_dependencia, 
    obtener_organizacion_usuario,
    verificar_permiso,
    verificar_limite_usuarios,
    obtener_info_request
)

router = APIRouter()


# Modelos Pydantic
class UsuarioCreateRequest(BaseModel):
    email: EmailStr
    nombres: str
    apellidos: str
    password: str
    rol_id: str


class UsuarioUpdateRequest(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    idioma_preferido: Optional[str] = None
    zona_horaria: Optional[str] = None
    notificaciones_email: Optional[bool] = None
    notificaciones_push: Optional[bool] = None


class UsuarioResponse(BaseModel):
    id: str
    email: str
    nombres: str
    apellidos: str
    estado_cuenta: str
    mfa_habilitado: bool
    fecha_ultimo_acceso: Optional[datetime]
    fecha_creacion: datetime
    rol: dict


class UsuarioListResponse(BaseModel):
    usuarios: List[UsuarioResponse]
    total: int
    pagina: int
    por_pagina: int


# Endpoints
@router.post("/registrar", response_model=UsuarioResponse)
async def registrar_usuario(
    usuario_data: UsuarioCreateRequest,
    organizacion: Organizacion = Depends(verificar_limite_usuarios),
    db: Session = Depends(obtener_sesion)
):
    """Registrar nuevo usuario en la organización"""
    
    try:
        # Verificar que el email no esté en uso
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == usuario_data.email,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if usuario_existente:
            raise ExcepcionValidacion("El email ya está en uso")
        
        # Verificar que el rol existe y es compatible con el nivel
        rol = db.query(Rol).filter(
            Rol.id == usuario_data.rol_id,
            Rol.esta_activo == True
        ).first()
        
        if not rol:
            raise ExcepcionRecursoNoEncontrado("Rol no encontrado")
        
        if not rol.es_compatible_con_nivel(organizacion.nivel_suscripcion):
            raise ExcepcionValidacion("El rol no es compatible con el nivel de suscripción")
        
        # Validar contraseña
        validacion_password = seguridad.validar_fuerza_contraseña(usuario_data.password)
        if not validacion_password["es_valida"]:
            raise ExcepcionValidacion(f"Contraseña no cumple requisitos: {', '.join(validacion_password['errores'])}")
        
        # Crear usuario
        nuevo_usuario = Usuario(
            email=usuario_data.email,
            nombres=usuario_data.nombres,
            apellidos=usuario_data.apellidos,
            hash_contraseña=seguridad.obtener_hash_contraseña(usuario_data.password),
            organizacion_id=organizacion.id,
            rol_id=rol.id,
            idioma_preferido="es_CL",
            zona_horaria="America/Santiago"
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        # Actualizar contador de usuarios
        organizacion.actualizar_uso_usuarios(1)
        db.commit()
        
        # Log de creación
        LogAuditoria.crear_log(
            tipo_evento="usuario",
            accion="crear_usuario",
            exitoso=True,
            organizacion_id=str(organizacion.id),
            tipo_recurso="usuario",
            id_recurso=str(nuevo_usuario.id)
        )
        
        return UsuarioResponse(
            id=str(nuevo_usuario.id),
            email=nuevo_usuario.email,
            nombres=nuevo_usuario.nombres,
            apellidos=nuevo_usuario.apellidos,
            estado_cuenta=nuevo_usuario.estado_cuenta.value,
            mfa_habilitado=nuevo_usuario.mfa_habilitado,
            fecha_ultimo_acceso=nuevo_usuario.fecha_ultimo_acceso,
            fecha_creacion=nuevo_usuario.fecha_creacion,
            rol={
                "id": str(rol.id),
                "nombre": rol.nombre.value,
                "nombre_mostrar": rol.nombre_mostrar
            }
        )
        
    except (ExcepcionValidacion, ExcepcionRecursoNoEncontrado):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/", response_model=UsuarioListResponse)
async def listar_usuarios(
    pagina: int = 1,
    por_pagina: int = 20,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Listar usuarios de la organización"""
    
    try:
        # Calcular offset
        offset = (pagina - 1) * por_pagina
        
        # Obtener usuarios
        usuarios_query = db.query(Usuario).filter(
            Usuario.organizacion_id == organizacion.id,
            Usuario.fecha_eliminacion.is_(None)
        )
        
        total = usuarios_query.count()
        usuarios = usuarios_query.offset(offset).limit(por_pagina).all()
        
        # Formatear respuesta
        usuarios_response = []
        for usuario in usuarios:
            usuarios_response.append(UsuarioResponse(
                id=str(usuario.id),
                email=usuario.email,
                nombres=usuario.nombres,
                apellidos=usuario.apellidos,
                estado_cuenta=usuario.estado_cuenta.value,
                mfa_habilitado=usuario.mfa_habilitado,
                fecha_ultimo_acceso=usuario.fecha_ultimo_acceso,
                fecha_creacion=usuario.fecha_creacion,
                rol={
                    "id": str(usuario.rol.id),
                    "nombre": usuario.rol.nombre.value,
                    "nombre_mostrar": usuario.rol.nombre_mostrar
                }
            ))
        
        return UsuarioListResponse(
            usuarios=usuarios_response,
            total=total,
            pagina=pagina,
            por_pagina=por_pagina
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener usuario específico"""
    
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.organizacion_id == organizacion.id,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario:
            raise ExcepcionRecursoNoEncontrado("Usuario no encontrado")
        
        return UsuarioResponse(
            id=str(usuario.id),
            email=usuario.email,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            estado_cuenta=usuario.estado_cuenta.value,
            mfa_habilitado=usuario.mfa_habilitado,
            fecha_ultimo_acceso=usuario.fecha_ultimo_acceso,
            fecha_creacion=usuario.fecha_creacion,
            rol={
                "id": str(usuario.rol.id),
                "nombre": usuario.rol.nombre.value,
                "nombre_mostrar": usuario.rol.nombre_mostrar
            }
        )
        
    except ExcepcionRecursoNoEncontrado:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdateRequest,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Actualizar usuario"""
    
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.organizacion_id == organizacion.id,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario:
            raise ExcepcionRecursoNoEncontrado("Usuario no encontrado")
        
        # Actualizar campos
        if usuario_data.nombres is not None:
            usuario.nombres = usuario_data.nombres
        if usuario_data.apellidos is not None:
            usuario.apellidos = usuario_data.apellidos
        if usuario_data.idioma_preferido is not None:
            usuario.idioma_preferido = usuario_data.idioma_preferido
        if usuario_data.zona_horaria is not None:
            usuario.zona_horaria = usuario_data.zona_horaria
        if usuario_data.notificaciones_email is not None:
            usuario.notificaciones_email = usuario_data.notificaciones_email
        if usuario_data.notificaciones_push is not None:
            usuario.notificaciones_push = usuario_data.notificaciones_push
        
        db.commit()
        db.refresh(usuario)
        
        # Log de actualización
        LogAuditoria.crear_log(
            tipo_evento="usuario",
            accion="actualizar_usuario",
            exitoso=True,
            organizacion_id=str(organizacion.id),
            tipo_recurso="usuario",
            id_recurso=str(usuario.id)
        )
        
        return UsuarioResponse(
            id=str(usuario.id),
            email=usuario.email,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            estado_cuenta=usuario.estado_cuenta.value,
            mfa_habilitado=usuario.mfa_habilitado,
            fecha_ultimo_acceso=usuario.fecha_ultimo_acceso,
            fecha_creacion=usuario.fecha_creacion,
            rol={
                "id": str(usuario.rol.id),
                "nombre": usuario.rol.nombre.value,
                "nombre_mostrar": usuario.rol.nombre_mostrar
            }
        )
        
    except ExcepcionRecursoNoEncontrado:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.delete("/{usuario_id}")
async def eliminar_usuario(
    usuario_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Eliminar usuario (eliminación lógica)"""
    
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.organizacion_id == organizacion.id,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario:
            raise ExcepcionRecursoNoEncontrado("Usuario no encontrado")
        
        # Eliminación lógica
        usuario.fecha_eliminacion = datetime.utcnow()
        db.commit()
        
        # Actualizar contador de usuarios
        organizacion.actualizar_uso_usuarios(-1)
        db.commit()
        
        # Log de eliminación
        LogAuditoria.crear_log(
            tipo_evento="usuario",
            accion="eliminar_usuario",
            exitoso=True,
            organizacion_id=str(organizacion.id),
            tipo_recurso="usuario",
            id_recurso=str(usuario.id)
        )
        
        return {"mensaje": "Usuario eliminado exitosamente"}
        
    except ExcepcionRecursoNoEncontrado:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/{usuario_id}/estadisticas")
async def obtener_estadisticas_usuario(
    usuario_id: str,
    organizacion: Organizacion = Depends(obtener_organizacion_usuario),
    db: Session = Depends(obtener_sesion)
):
    """Obtener estadísticas de uso del usuario"""
    
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.organizacion_id == organizacion.id,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario:
            raise ExcepcionRecursoNoEncontrado("Usuario no encontrado")
        
        estadisticas = usuario.obtener_estadisticas_uso()
        
        return {
            "usuario_id": str(usuario.id),
            "nombre_completo": usuario.nombre_completo,
            "estadisticas": estadisticas
        }
        
    except ExcepcionRecursoNoEncontrado:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )