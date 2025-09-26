# app/api/v1/endpoints/auth.py
"""
Endpoints de autenticación
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.sesion import Sesion
from app.modelos.log_auditoria import LogAuditoria
from app.core.seguridad import seguridad
from app.core.config import config
from app.core.excepciones import ExcepcionAutenticacion, ExcepcionValidacion
from ..dependencias import obtener_usuario_actual_dependencia

router = APIRouter()
security_scheme = HTTPBearer()


# Modelos Pydantic
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegistroRequest(BaseModel):
    email: EmailStr
    password: str
    nombres: str
    apellidos: str
    nombre_organizacion: str
    sector: Optional[str] = None
    tamaño: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    usuario: dict


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UsuarioResponse(BaseModel):
    id: str
    email: str
    nombres: str
    apellidos: str
    organizacion: dict
    rol: dict
    nivel_suscripcion: str
    mfa_habilitado: bool
    estado_cuenta: str
    fecha_ultimo_acceso: Optional[datetime]


class CambioPasswordRequest(BaseModel):
    password_actual: str
    password_nuevo: str


# Endpoints
@router.post("/iniciar-sesion", response_model=LoginResponse)
async def iniciar_sesion(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(obtener_sesion)
):
    """Iniciar sesión de usuario"""
    
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(
            Usuario.email == login_data.email,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar contraseña
        if not seguridad.verificar_contraseña(login_data.password, usuario.hash_contraseña):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        # Verificar estado de cuenta
        if not usuario.esta_activo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cuenta inactiva"
            )
        
        # Generar tokens simples
        access_token = "fake_access_token_" + str(usuario.id)
        refresh_token = "fake_refresh_token_" + str(usuario.id)
        
        return LoginResponse(
            access_token=access_token,
            expires_in=900,  # 15 minutos
            refresh_token=refresh_token,
            usuario={
                "id": str(usuario.id),
                "email": usuario.email,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "organizacion": {
                    "id": str(usuario.organizacion.id),
                    "nombre": usuario.organizacion.nombre,
                    "nivel_suscripcion": usuario.organizacion.nivel_suscripcion.value
                },
                "rol": {
                    "id": str(usuario.rol.id),
                    "nombre": usuario.rol.nombre.value,
                    "nombre_mostrar": usuario.rol.nombre_mostrar
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/registro")
async def registrar_usuario(
    request: Request,
    db: Session = Depends(obtener_sesion)
):
    """Registrar nuevo usuario y organización"""
    
    try:
        # Obtener datos del request
        data = await request.json()
        print(f"Datos de registro recibidos: {data}")
        
        # Validar datos básicos
        if not data.get("email") or not data.get("password"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email y contraseña son requeridos"
            )
        # Verificar si el email ya existe
        usuario_existente = db.query(Usuario).filter(
            Usuario.email == data.get("email"),
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear organización
        organizacion = Organizacion(
            nombre=data.get("nombre_organizacion", "Organizacion sin nombre"),
            nivel_suscripcion="gratuito",  # Por defecto gratuito
            sector=data.get("sector", "tecnologia"),  # Valor por defecto
            tamaño=data.get("tamaño", "pequeña")  # Valor por defecto
        )
        db.add(organizacion)
        db.flush()  # Para obtener el ID
        
        # Obtener rol de usuario estándar
        from app.modelos.rol import Rol, TipoRol
        rol_usuario = db.query(Rol).filter(Rol.nombre == TipoRol.USUARIO_BASICO).first()
        if not rol_usuario:
            # Si no existe, crear rol básico
            rol_usuario = Rol(
                nombre=TipoRol.USUARIO_BASICO,
                nombre_mostrar="Usuario Básico",
                descripcion="Usuario estándar de la plataforma",
                permisos='["evaluar", "ver_reportes_basicos"]'
            )
            db.add(rol_usuario)
            db.flush()
        
        # Crear usuario
        from app.modelos.usuario import EstadoCuenta
        hash_password = seguridad.obtener_hash_contraseña(data.get("password"))
        usuario = Usuario(
            email=data.get("email"),
            hash_contraseña=hash_password,
            nombres=data.get("nombres", "Usuario"),
            apellidos=data.get("apellidos", "Sin apellido"),
            organizacion_id=organizacion.id,
            rol_id=rol_usuario.id,
            estado_cuenta=EstadoCuenta.ACTIVO,
            mfa_habilitado=False
        )
        db.add(usuario)
        db.commit()
        
        # Generar tokens
        access_token = "fake_access_token_" + str(usuario.id)
        refresh_token = "fake_refresh_token_" + str(usuario.id)
        
        return LoginResponse(
            access_token=access_token,
            expires_in=900,  # 15 minutos
            refresh_token=refresh_token,
            usuario={
                "id": str(usuario.id),
                "email": usuario.email,
                "nombres": usuario.nombres,
                "apellidos": usuario.apellidos,
                "organizacion": {
                    "id": str(usuario.organizacion.id),
                    "nombre": usuario.organizacion.nombre,
                    "nivel_suscripcion": usuario.organizacion.nivel_suscripcion.value
                },
                "rol": {
                    "id": str(usuario.rol.id),
                    "nombre": usuario.rol.nombre.value,
                    "nombre_mostrar": usuario.rol.nombre_mostrar
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en registro: {e}")
        print(f"Tipo de error: {type(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.post("/renovar-token", response_model=dict)
async def renovar_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(obtener_sesion)
):
    """Renovar token de acceso"""
    
    # Obtener información del request de forma simple
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    info_request = {
        "direccion_ip": client_ip,
        "agente_usuario": user_agent
    }
    
    try:
        # Verificar token de refresco
        payload = seguridad.verificar_token(refresh_data.refresh_token, "refresh")
        if not payload:
            raise ExcepcionAutenticacion("Token de refresco inválido")
        
        # Buscar sesión
        sesion = db.query(Sesion).filter(
            Sesion.jti == payload["jti"],
            Sesion.esta_activa == True
        ).first()
        
        if not sesion or not sesion.esta_valida:
            raise ExcepcionAutenticacion("Sesión inválida")
        
        # Verificar hash del token
        if not seguridad.verificar_contraseña(refresh_data.refresh_token, sesion.hash_token_refresco):
            raise ExcepcionAutenticacion("Token de refresco inválido")
        
        # Buscar usuario
        usuario = db.query(Usuario).filter(
            Usuario.id == payload["sub"],
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario or not usuario.esta_activo:
            raise ExcepcionAutenticacion("Usuario no encontrado o inactivo")
        
        # Generar nuevo token de acceso
        datos_token = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "org_id": str(usuario.organizacion_id),
            "nivel_suscripcion": usuario.organizacion.nivel_suscripcion.value,
            "rol": usuario.rol.nombre.value,
            "jti": sesion.jti
        }
        
        access_token = seguridad.crear_token_acceso(datos_token)
        
        # Log de renovación exitosa
        LogAuditoria.crear_log(
            tipo_evento="autenticacion",
            accion="renovar_token",
            exitoso=True,
            usuario_id=str(usuario.id),
            organizacion_id=str(usuario.organizacion_id),
            direccion_ip=info_request["direccion_ip"],
            agente_usuario=info_request["agente_usuario"]
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": config.tiempo_expiracion_acceso * 60
        }
        
    except ExcepcionAutenticacion:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/cerrar-sesion")
async def cerrar_sesion(
    request: Request,
    db: Session = Depends(obtener_sesion)
):
    """Cerrar sesión de usuario"""
    
    # Obtener información del request de forma simple
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    info_request = {
        "direccion_ip": client_ip,
        "agente_usuario": user_agent
    }
    
    try:
        # Obtener token del header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise ExcepcionAutenticacion("Token requerido")
        
        token = authorization.split(" ")[1]
        payload = seguridad.verificar_token(token)
        
        if not payload:
            raise ExcepcionAutenticacion("Token inválido")
        
        # Buscar y revocar sesión
        sesion = db.query(Sesion).filter(
            Sesion.jti == payload["jti"],
            Sesion.esta_activa == True
        ).first()
        
        if sesion:
            sesion.revocar("Logout manual")
            db.commit()
        
        # Log de logout
        LogAuditoria.crear_log(
            tipo_evento="autenticacion",
            accion="logout",
            exitoso=True,
            usuario_id=payload.get("sub"),
            organizacion_id=payload.get("org_id"),
            direccion_ip=info_request["direccion_ip"],
            agente_usuario=info_request["agente_usuario"]
        )
        
        return {"mensaje": "Sesión cerrada exitosamente"}
        
    except ExcepcionAutenticacion:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/mi-perfil")
async def obtener_mi_perfil(
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Obtener perfil del usuario actual"""
    
    try:
        # Obtener datos actualizados del usuario
        usuario_actual = db.query(Usuario).filter(
            Usuario.id == usuario.id,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        
        if not usuario_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return {
            "id": str(usuario_actual.id),
            "email": usuario_actual.email,
            "nombres": usuario_actual.nombres,
            "apellidos": usuario_actual.apellidos,
            "organizacion": {
                "id": str(usuario_actual.organizacion.id),
                "nombre": usuario_actual.organizacion.nombre,
                "nivel_suscripcion": usuario_actual.organizacion.nivel_suscripcion.value,
                "sector": usuario_actual.organizacion.sector.value if usuario_actual.organizacion.sector else None,
                "tamaño": usuario_actual.organizacion.tamaño.value if usuario_actual.organizacion.tamaño else None
            },
            "rol": {
                "id": str(usuario_actual.rol.id),
                "nombre": usuario_actual.rol.nombre.value,
                "nombre_mostrar": usuario_actual.rol.nombre_mostrar
            },
            "mfa_habilitado": usuario_actual.mfa_habilitado,
            "estado_cuenta": usuario_actual.estado_cuenta.value,
            "fecha_ultimo_acceso": usuario_actual.fecha_ultimo_acceso.isoformat() if usuario_actual.fecha_ultimo_acceso else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en obtener_mi_perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/cambiar-password")
async def cambiar_password(
    password_data: CambioPasswordRequest,
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """Cambiar contraseña del usuario"""
    
    try:
        # Verificar contraseña actual
        if not seguridad.verificar_contraseña(password_data.password_actual, usuario.hash_contraseña):
            raise ExcepcionAutenticacion("Contraseña actual incorrecta")
        
        # Validar nueva contraseña
        validacion = seguridad.validar_fuerza_contraseña(password_data.password_nuevo)
        if not validacion["es_valida"]:
            raise ExcepcionValidacion(f"Contraseña no cumple requisitos: {', '.join(validacion['errores'])}")
        
        # Actualizar contraseña
        usuario.hash_contraseña = seguridad.obtener_hash_contraseña(password_data.password_nuevo)
        usuario.fecha_cambio_contraseña = datetime.utcnow()
        
        # Revocar todas las sesiones activas
        sesiones_activas = db.query(Sesion).filter(
            Sesion.usuario_id == usuario.id,
            Sesion.esta_activa == True
        ).all()
        
        for sesion in sesiones_activas:
            sesion.revocar("Cambio de contraseña")
        
        db.commit()
        
        return {"mensaje": "Contraseña actualizada exitosamente"}
        
    except (ExcepcionAutenticacion, ExcepcionValidacion):
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )