# app/api/v1/dependencias.py
"""
Dependencias para la API v1
Autenticación, autorización y validaciones
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.modelos.base import obtener_sesion
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.core.seguridad import obtener_usuario_actual, verificar_permisos_nivel
from app.core.config import NivelSuscripcion
from app.core.excepciones import ExcepcionAutenticacion, ExcepcionAutorizacion, ExcepcionNivelSuscripcion

# Esquema de autenticación
security = HTTPBearer()

# Dependencia para obtener sesión de base de datos
def obtener_db() -> Session:
    """Obtener sesión de base de datos"""
    db = next(obtener_sesion())
    try:
        yield db
    finally:
        db.close()

# Dependencia para obtener usuario actual
async def obtener_usuario_actual_dependencia(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(obtener_sesion)
) -> Usuario:
    """Obtener usuario actual desde token JWT"""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido"
        )
    
    # Para tokens fake, extraer el ID del usuario del token
    token = credentials.credentials
    if token.startswith("fake_access_token_"):
        usuario_id = token.replace("fake_access_token_", "")
        
        # Obtener usuario de la base de datos
        usuario = db.query(Usuario).filter(
            Usuario.id == usuario_id,
            Usuario.fecha_eliminacion.is_(None)
        ).first()
    else:
        # Verificar token JWT real
        payload = obtener_usuario_actual(token)
        print(f"Payload obtenido: {payload}")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        
        # Obtener usuario de la base de datos
        usuario = db.query(Usuario).filter(
            Usuario.id == payload["id"],
            Usuario.fecha_eliminacion.is_(None)
        ).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
    
    if not usuario.esta_activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    return usuario

# Dependencia para obtener organización del usuario
async def obtener_organizacion_usuario(
    usuario: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
) -> Organizacion:
    """Obtener organización del usuario actual"""
    
    organizacion = db.query(Organizacion).filter(
        Organizacion.id == usuario.organizacion_id,
        Organizacion.fecha_eliminacion.is_(None)
    ).first()
    
    if not organizacion:
        raise ExcepcionAutorizacion("Organización no encontrada")
    
    return organizacion

# Dependencia para verificar nivel de suscripción
def verificar_nivel_suscripcion(nivel_requerido: NivelSuscripcion):
    """Decorador para verificar nivel de suscripción"""
    
    async def verificar_nivel(
        organizacion: Organizacion = Depends(obtener_organizacion_usuario)
    ) -> Organizacion:
        """Verificar que la organización tenga el nivel requerido"""
        
        if not verificar_permisos_nivel(organizacion.nivel_suscripcion.value, nivel_requerido.value):
            raise ExcepcionNivelSuscripcion(
                f"Nivel de suscripción insuficiente. Requerido: {nivel_requerido.value}, "
                f"Actual: {organizacion.nivel_suscripcion.value}"
            )
        
        return organizacion
    
    return verificar_nivel

# Dependencia para verificar permisos específicos
def verificar_permiso(recurso: str, accion: str):
    """Decorador para verificar permisos específicos"""
    
    async def verificar_permiso_usuario(
        usuario: Usuario = Depends(obtener_usuario_actual_dependencia)
    ) -> Usuario:
        """Verificar que el usuario tenga el permiso requerido"""
        
        if not usuario.puede_acceder_recurso(recurso, accion):
            raise ExcepcionAutorizacion(
                f"No tiene permisos para {accion} en {recurso}"
            )
        
        return usuario
    
    return verificar_permiso_usuario

# Dependencia para obtener información del request
async def obtener_info_request(request: Request) -> dict:
    """Obtener información del request para auditoría"""
    
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    return {
        "direccion_ip": client_ip,
        "agente_usuario": user_agent,
        "url": str(request.url),
        "metodo": request.method
    }

# Dependencia para verificar límites de uso
async def verificar_limites_uso(
    organizacion: Organizacion = Depends(obtener_organizacion_usuario)
) -> Organizacion:
    """Verificar límites de uso de la organización"""
    
    # Verificar si la suscripción está vencida
    if organizacion.suscripcion_vencida:
        raise ExcepcionNivelSuscripcion("Suscripción vencida")
    
    return organizacion

# Dependencia para verificar límites de evaluaciones
async def verificar_limite_evaluaciones(
    organizacion: Organizacion = Depends(verificar_limites_uso)
) -> Organizacion:
    """Verificar límite de evaluaciones"""
    
    if not organizacion.puede_crear_evaluacion:
        raise ExcepcionNivelSuscripcion(
            f"Límite de evaluaciones excedido. "
            f"Máximo permitido: {organizacion.maximo_evaluaciones_por_mes}"
        )
    
    return organizacion

# Dependencia para verificar límites de usuarios
async def verificar_limite_usuarios(
    organizacion: Organizacion = Depends(verificar_limites_uso)
) -> Organizacion:
    """Verificar límite de usuarios"""
    
    if not organizacion.puede_agregar_usuario:
        raise ExcepcionNivelSuscripcion(
            f"Límite de usuarios excedido. "
            f"Máximo permitido: {organizacion.maximo_usuarios}"
        )
    
    return organizacion

# Dependencia para obtener usuario opcional (para endpoints públicos)
async def obtener_usuario_opcional(
    request: Request,
    db: Session = Depends(obtener_db)
) -> Optional[Usuario]:
    """Obtener usuario opcional (puede ser None)"""
    
    # Verificar si hay token en el header Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    try:
        # Para tokens fake, extraer el ID del usuario del token
        if token.startswith("fake_access_token_"):
            usuario_id = token.replace("fake_access_token_", "")
            
            # Obtener usuario de la base de datos
            usuario = db.query(Usuario).filter(
                Usuario.id == usuario_id,
                Usuario.fecha_eliminacion.is_(None)
            ).first()
            
        else:
            # Verificar token JWT real
            payload = obtener_usuario_actual(token)
            if not payload:
                return None
            
            # Obtener usuario de la base de datos
            usuario = db.query(Usuario).filter(
                Usuario.id == payload["id"],
                Usuario.fecha_eliminacion.is_(None)
            ).first()
        
        return usuario if usuario and usuario.esta_activo else None
    
    except Exception:
        return None

# Dependencia para verificar que el usuario esté autenticado
async def requerir_autenticacion(
    usuario: Optional[Usuario] = Depends(obtener_usuario_opcional)
) -> Usuario:
    """Requerir que el usuario esté autenticado"""
    
    if not usuario:
        raise ExcepcionAutenticacion("Autenticación requerida")
    
    return usuario