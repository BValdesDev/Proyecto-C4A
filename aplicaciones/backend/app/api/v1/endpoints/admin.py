"""
Endpoints de administración para C4A SaaS
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ....core.dependencias import get_db, get_current_user
from ....modelos.usuario import Usuario
from ....modelos.organizacion import Organizacion
from ....modelos.evaluacion import Evaluacion
from ....modelos.suscripcion import Suscripcion
from ....core.seguridad import verify_password, get_password_hash
from ....core.permissions import require_admin_role

router = APIRouter()

# ===== DASHBOARD STATS =====

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas del dashboard de administración
    """
    require_admin_role(current_user)
    
    # Contar usuarios totales y activos
    total_users = db.query(Usuario).count()
    active_users = db.query(Usuario).filter(
        Usuario.ultimo_login >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Contar diagnósticos
    total_diagnostics = db.query(Evaluacion).count()
    completed_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado == "completado"
    ).count()
    pending_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado.in_(["en_progreso", "pendiente"])
    ).count()
    
    # Calcular ingresos mensuales (simulado)
    current_month = datetime.utcnow().replace(day=1)
    monthly_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.fecha_inicio >= current_month,
        Suscripcion.estado == "activa"
    ).all()
    
    monthly_revenue = sum([
        sub.plan.precio_mensual for sub in monthly_subscriptions 
        if sub.plan and sub.plan.precio_mensual
    ])
    
    # Calcular tasa de completación
    completion_rate = (completed_diagnostics / total_diagnostics * 100) if total_diagnostics > 0 else 0
    
    # Calcular crecimiento mensual (simulado)
    last_month = current_month - timedelta(days=30)
    last_month_users = db.query(Usuario).filter(
        Usuario.fecha_registro >= last_month,
        Usuario.fecha_registro < current_month
    ).count()
    
    growth_rate = ((active_users - last_month_users) / last_month_users * 100) if last_month_users > 0 else 0
    
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalDiagnostics": total_diagnostics,
        "completedDiagnostics": completed_diagnostics,
        "pendingDiagnostics": pending_diagnostics,
        "monthlyRevenue": monthly_revenue,
        "completionRate": round(completion_rate, 1),
        "growthRate": round(growth_rate, 1)
    }

# ===== GESTIÓN DE USUARIOS =====

@router.get("/users")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios con filtros
    """
    require_admin_role(current_user)
    
    query = db.query(Usuario)
    
    # Aplicar filtros
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Usuario.nombre.ilike(search_filter)) |
            (Usuario.email.ilike(search_filter)) |
            (Usuario.organizacion.has(Organizacion.nombre.ilike(search_filter)))
        )
    
    if status:
        if status == "activo":
            query = query.filter(Usuario.ultimo_login >= datetime.utcnow() - timedelta(days=30))
        elif status == "inactivo":
            query = query.filter(Usuario.ultimo_login < datetime.utcnow() - timedelta(days=30))
        elif status == "suspendido":
            query = query.filter(Usuario.activo == False)
    
    # Aplicar paginación
    users = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "nombre": user.nombre,
                "email": user.email,
                "empresa": user.organizacion.nombre if user.organizacion else None,
                "suscripcion": user.suscripcion_actual.plan.nombre if user.suscripcion_actual else "Gratuito",
                "estado": "activo" if user.ultimo_login and user.ultimo_login >= datetime.utcnow() - timedelta(days=30) else "inactivo",
                "ultimoLogin": user.ultimo_login.isoformat() if user.ultimo_login else None,
                "fechaRegistro": user.fecha_registro.isoformat(),
                "activo": user.activo
            }
            for user in users
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/users")
async def create_user(
    user_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear nuevo usuario (admin)
    """
    require_admin_role(current_user)
    
    # Verificar si el email ya existe
    existing_user = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear usuario
    new_user = Usuario(
        nombre=user_data["nombre"],
        email=user_data["email"],
        password_hash=get_password_hash(user_data["password"]),
        rol=user_data.get("rol", "usuario"),
        activo=True,
        fecha_registro=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": str(new_user.id),
        "nombre": new_user.nombre,
        "email": new_user.email,
        "rol": new_user.rol,
        "activo": new_user.activo
    }

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario
    """
    require_admin_role(current_user)
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar campos permitidos
    if "nombre" in user_data:
        user.nombre = user_data["nombre"]
    if "email" in user_data:
        # Verificar si el nuevo email ya existe
        existing_user = db.query(Usuario).filter(
            Usuario.email == user_data["email"],
            Usuario.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        user.email = user_data["email"]
    if "rol" in user_data:
        user.rol = user_data["rol"]
    if "activo" in user_data:
        user.activo = user_data["activo"]
    if "password" in user_data:
        user.password_hash = get_password_hash(user_data["password"])
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol,
        "activo": user.activo
    }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario (soft delete)
    """
    require_admin_role(current_user)
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # No permitir eliminar el propio usuario
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")
    
    # Soft delete
    user.activo = False
    db.commit()
    
    return {"message": "Usuario desactivado exitosamente"}

# ===== GESTIÓN DE DIAGNÓSTICOS =====

@router.get("/diagnostics")
async def get_diagnostics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    framework: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de diagnósticos con filtros
    """
    require_admin_role(current_user)
    
    query = db.query(Evaluacion)
    
    # Aplicar filtros
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Evaluacion.organizacion.has(Organizacion.nombre.ilike(search_filter))) |
            (Evaluacion.usuario.has(Usuario.nombre.ilike(search_filter)))
        )
    
    if status:
        query = query.filter(Evaluacion.estado == status)
    
    if framework:
        query = query.filter(Evaluacion.framework == framework)
    
    # Aplicar paginación
    diagnostics = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "diagnostics": [
            {
                "id": str(diagnostic.id),
                "companyName": diagnostic.organizacion.nombre if diagnostic.organizacion else None,
                "userName": diagnostic.usuario.nombre if diagnostic.usuario else None,
                "framework": diagnostic.framework,
                "status": diagnostic.estado,
                "score": diagnostic.puntaje_final or 0,
                "maxScore": diagnostic.puntaje_maximo or 100,
                "progress": diagnostic.progreso or 0,
                "createdAt": diagnostic.fecha_creacion.isoformat(),
                "completedAt": diagnostic.fecha_completado.isoformat() if diagnostic.fecha_completado else None
            }
            for diagnostic in diagnostics
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/diagnostics/stats")
async def get_diagnostics_stats(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de diagnósticos
    """
    require_admin_role(current_user)
    
    total = db.query(Evaluacion).count()
    completed = db.query(Evaluacion).filter(Evaluacion.estado == "completado").count()
    in_progress = db.query(Evaluacion).filter(Evaluacion.estado == "en_progreso").count()
    pending = db.query(Evaluacion).filter(Evaluacion.estado == "pendiente").count()
    
    # Calcular puntaje promedio
    completed_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado == "completado",
        Evaluacion.puntaje_final.isnot(None)
    ).all()
    
    average_score = 0
    if completed_diagnostics:
        total_score = sum(d.puntaje_final for d in completed_diagnostics)
        average_score = total_score / len(completed_diagnostics)
    
    return {
        "total": total,
        "completed": completed,
        "inProgress": in_progress,
        "pending": pending,
        "averageScore": round(average_score, 1)
    }

# ===== CONFIGURACIÓN DEL SISTEMA =====

@router.get("/settings")
async def get_system_settings(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener configuración del sistema
    """
    require_admin_role(current_user)
    
    # TODO: Implementar tabla de configuración en la BD
    return {
        "general": {
            "siteName": "C4A SaaS",
            "siteDescription": "Plataforma de evaluación de ciberseguridad para PyMEs",
            "supportEmail": "soporte@c4a.cl",
            "contactPhone": "+56 9 1234 5678"
        },
        "security": {
            "passwordMinLength": 8,
            "sessionTimeout": 30,
            "maxLoginAttempts": 5,
            "enableTwoFactor": True,
            "requireEmailVerification": True
        },
        "features": {
            "enableRegistration": True,
            "enablePublicDiagnostics": False,
            "enableNotifications": True,
            "maintenanceMode": False
        }
    }

@router.put("/settings")
async def update_system_settings(
    settings: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar configuración del sistema
    """
    require_admin_role(current_user)
    
    # TODO: Implementar guardado en BD
    # Por ahora solo retornamos éxito
    return {"message": "Configuración actualizada exitosamente"}
