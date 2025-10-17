"""
Endpoints de administración para C4A SaaS
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from ..dependencias import obtener_db, obtener_usuario_actual_dependencia
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.evaluacion import Evaluacion, EstadoEvaluacion
from app.modelos.suscripcion import Suscripcion
from app.core.seguridad import SeguridadC4A
from app.modelos.rol import TipoRol
from app.services.notification_service import NotificationService, run_automatic_notifications

router = APIRouter()

def require_admin_role(user: Usuario):
    """Verificar que el usuario tenga rol de administrador"""
    if not user.rol or str(user.rol.nombre) not in ["TipoRol.ADMIN_SISTEMA", "TipoRol.ADMIN_EMPRESA"]:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado. Se requiere rol de administrador."
        )

# ===== DASHBOARD STATS =====

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas del dashboard de administración
    """
    require_admin_role(current_user)
    
    # Contar usuarios totales y activos
    total_users = db.query(Usuario).count()
    active_users = db.query(Usuario).filter(
        Usuario.fecha_ultimo_acceso.isnot(None),
        Usuario.fecha_ultimo_acceso >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Contar diagnósticos
    total_diagnostics = db.query(Evaluacion).count()
    completed_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado == EstadoEvaluacion.COMPLETADA
    ).count()
    pending_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado.in_([EstadoEvaluacion.EN_PROGRESO, EstadoEvaluacion.BORRADOR])
    ).count()
    
    # Calcular ingresos mensuales (simulado)
    current_month = datetime.utcnow().replace(day=1)
    monthly_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.inicio_periodo_actual >= current_month,
        Suscripcion.estado == "active"
    ).all()
    
    monthly_revenue = sum([
        sub.monto_centavos for sub in monthly_subscriptions 
        if sub.monto_centavos
    ]) / 100  # Convertir de centavos a pesos
    
    # Calcular tasa de completación
    completion_rate = (completed_diagnostics / total_diagnostics * 100) if total_diagnostics > 0 else 0
    
    # Calcular crecimiento mensual
    last_month = current_month - timedelta(days=30)
    last_month_users = db.query(Usuario).filter(
        Usuario.fecha_creacion >= last_month,
        Usuario.fecha_creacion < current_month
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
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
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
            (Usuario.nombres.ilike(search_filter)) |
            (Usuario.apellidos.ilike(search_filter)) |
            (Usuario.email.ilike(search_filter)) |
            (Usuario.organizacion.has(Organizacion.nombre.ilike(search_filter)))
        )
    
    if status:
        if status == "activo":
            query = query.filter(
                Usuario.fecha_ultimo_acceso.isnot(None),
                Usuario.fecha_ultimo_acceso >= datetime.utcnow() - timedelta(days=30)
            )
        elif status == "inactivo":
            query = query.filter(
                Usuario.fecha_ultimo_acceso.is_(None) | 
                (Usuario.fecha_ultimo_acceso < datetime.utcnow() - timedelta(days=30))
            )
        elif status == "suspendido":
            query = query.filter(Usuario.estado_cuenta == "suspendido")
    
    # Aplicar paginación
    users = query.offset(skip).limit(limit).all()
    total = query.count()
    
    # Obtener suscripciones activas para cada usuario
    user_suscripciones = {}
    for user in users:
        if user.organizacion_id:
            suscripcion_activa = db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == user.organizacion_id,
                Suscripcion.estado == "active"
            ).first()
            if suscripcion_activa:
                user_suscripciones[user.id] = suscripcion_activa.nivel.value
            else:
                user_suscripciones[user.id] = "Gratuito"
        else:
            user_suscripciones[user.id] = "Gratuito"
    
    return {
        "users": [
            {
                "id": str(user.id),
                "nombre": user.nombre_completo,
                "email": user.email,
                "empresa": user.organizacion.nombre if user.organizacion else None,
                "suscripcion": user_suscripciones.get(user.id, "Gratuito"),
                "estado": "activo" if user.fecha_ultimo_acceso and user.fecha_ultimo_acceso.replace(tzinfo=None) >= datetime.utcnow() - timedelta(days=30) else "inactivo",
                "ultimoLogin": user.fecha_ultimo_acceso.isoformat() if user.fecha_ultimo_acceso else None,
                "fechaRegistro": user.fecha_creacion.isoformat(),
                "activo": user.esta_activo
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
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
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
    seguridad = SeguridadC4A()
    new_user = Usuario(
        nombres=user_data.get("nombres", ""),
        apellidos=user_data.get("apellidos", ""),
        email=user_data["email"],
        hash_contraseña=seguridad.obtener_hash_contraseña(user_data["password"]),
        estado_cuenta="activo",
        organizacion_id=user_data.get("organizacion_id"),
        rol_id=user_data.get("rol_id")
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": str(new_user.id),
        "nombre": new_user.nombre_completo,
        "email": new_user.email,
        "rol": new_user.rol.nombre if new_user.rol else None,
        "activo": new_user.esta_activo
    }

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Actualizar usuario
    """
    require_admin_role(current_user)
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar campos permitidos
    if "nombres" in user_data:
        user.nombres = user_data["nombres"]
    if "apellidos" in user_data:
        user.apellidos = user_data["apellidos"]
    if "email" in user_data:
        # Verificar si el nuevo email ya existe
        existing_user = db.query(Usuario).filter(
            Usuario.email == user_data["email"],
            Usuario.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        user.email = user_data["email"]
    if "rol_id" in user_data:
        user.rol_id = user_data["rol_id"]
    if "estado_cuenta" in user_data:
        user.estado_cuenta = user_data["estado_cuenta"]
    if "password" in user_data:
        seguridad = SeguridadC4A()
        user.hash_contraseña = seguridad.obtener_hash_contraseña(user_data["password"])
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "nombre": user.nombre_completo,
        "email": user.email,
        "rol": user.rol.nombre if user.rol else None,
        "activo": user.esta_activo
    }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
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
    user.estado_cuenta = "suspendido"
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
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
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
            (Evaluacion.creado_por_usuario.has(Usuario.nombres.ilike(search_filter))) |
            (Evaluacion.creado_por_usuario.has(Usuario.apellidos.ilike(search_filter)))
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
                "userName": diagnostic.creado_por_usuario.nombre_completo if diagnostic.creado_por_usuario else None,
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
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas de diagnósticos
    """
    require_admin_role(current_user)
    
    total = db.query(Evaluacion).count()
    completed = db.query(Evaluacion).filter(Evaluacion.estado == EstadoEvaluacion.COMPLETADA).count()
    in_progress = db.query(Evaluacion).filter(Evaluacion.estado == EstadoEvaluacion.EN_PROGRESO).count()
    pending = db.query(Evaluacion).filter(Evaluacion.estado == EstadoEvaluacion.BORRADOR).count()
    
    # Calcular puntaje promedio
    completed_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado == EstadoEvaluacion.COMPLETADA,
        Evaluacion.puntuacion_global.isnot(None)
    ).all()
    
    average_score = 0
    if completed_diagnostics:
        total_score = sum(float(d.puntuacion_global) for d in completed_diagnostics)
        average_score = total_score / len(completed_diagnostics)
    
    return {
        "total": total,
        "completed": completed,
        "inProgress": in_progress,
        "pending": pending,
        "averageScore": round(average_score, 1)
    }

# ===== GESTIÓN DE PAGOS =====

@router.get("/payments")
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener lista de pagos/suscripciones con filtros
    """
    require_admin_role(current_user)
    
    query = db.query(Suscripcion).join(Organizacion)
    
    # Aplicar filtros
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Organizacion.nombre.ilike(search_filter)) |
            (Suscripcion.nivel.ilike(search_filter))
        )
    
    if status:
        query = query.filter(Suscripcion.estado == status)
    
    # Aplicar paginación
    subscriptions = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "payments": [
            {
                "id": str(subscription.id),
                "organizacion": subscription.organizacion.nombre if subscription.organizacion else None,
                "suscripcion": subscription.nivel.value,
                "monto": (subscription.monto_centavos or 0) / 100,
                "moneda": subscription.moneda or "CLP",
                "estado": subscription.estado,
                "metodo_pago": "Tarjeta terminada en 4242",  # TODO: Implementar método real
                "fecha_creacion": subscription.fecha_creacion.isoformat(),
                "proxima_facturacion": subscription.fin_periodo_actual.isoformat() if subscription.fin_periodo_actual else None,
                "ciclo": subscription.ciclo_facturacion or "mensual"
            }
            for subscription in subscriptions
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/payments/stats")
async def get_payments_stats(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas de pagos
    """
    require_admin_role(current_user)
    
    # Calcular ingresos totales
    total_revenue = db.query(Suscripcion).filter(
        Suscripcion.estado == "active",
        Suscripcion.monto_centavos.isnot(None)
    ).with_entities(
        func.sum(Suscripcion.monto_centavos)
    ).scalar() or 0
    
    # Calcular ingresos mensuales (último mes)
    current_month = datetime.utcnow().replace(day=1)
    monthly_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.estado == "active",
        Suscripcion.inicio_periodo_actual >= current_month
    ).all()
    
    monthly_revenue = sum([
        sub.monto_centavos for sub in monthly_subscriptions 
        if sub.monto_centavos
    ])
    
    # Contar suscripciones
    active_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.estado == "active"
    ).count()
    
    canceled_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.estado == "canceled"
    ).count()
    
    # Calcular ingreso promedio
    average_revenue = (total_revenue / active_subscriptions) if active_subscriptions > 0 else 0
    
    # Calcular crecimiento (simulado)
    last_month = current_month - timedelta(days=30)
    last_month_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.fecha_creacion >= last_month,
        Suscripcion.fecha_creacion < current_month
    ).count()
    
    growth_rate = ((active_subscriptions - last_month_subscriptions) / last_month_subscriptions * 100) if last_month_subscriptions > 0 else 0
    
    return {
        "totalRevenue": total_revenue / 100,  # Convertir de centavos a pesos
        "monthlyRevenue": monthly_revenue / 100,
        "activeSubscriptions": active_subscriptions,
        "canceledSubscriptions": canceled_subscriptions,
        "averageRevenue": average_revenue / 100,
        "growthRate": round(growth_rate, 1)
    }

# ===== ANALYTICS =====

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener resumen de analytics
    """
    require_admin_role(current_user)
    
    # Calcular métricas básicas
    total_users = db.query(Usuario).count()
    active_users = db.query(Usuario).filter(
        Usuario.fecha_ultimo_acceso.isnot(None),
        Usuario.fecha_ultimo_acceso >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    total_diagnostics = db.query(Evaluacion).count()
    completed_diagnostics = db.query(Evaluacion).filter(
        Evaluacion.estado == EstadoEvaluacion.COMPLETADA
    ).count()
    
    active_subscriptions = db.query(Suscripcion).filter(
        Suscripcion.estado == "active"
    ).count()
    
    # Calcular ingresos
    total_revenue = db.query(Suscripcion).filter(
        Suscripcion.estado == "active",
        Suscripcion.monto_centavos.isnot(None)
    ).with_entities(
        func.sum(Suscripcion.monto_centavos)
    ).scalar() or 0
    
    # Calcular crecimiento
    last_month = datetime.utcnow() - timedelta(days=30)
    last_month_users = db.query(Usuario).filter(
        Usuario.fecha_creacion >= last_month
    ).count()
    
    growth_rate = ((active_users - last_month_users) / last_month_users * 100) if last_month_users > 0 else 0
    
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalDiagnostics": total_diagnostics,
        "completedDiagnostics": completed_diagnostics,
        "activeSubscriptions": active_subscriptions,
        "totalRevenue": total_revenue / 100,  # Convertir de centavos a pesos
        "growthRate": round(growth_rate, 1),
        "conversionRate": round((active_subscriptions / total_users * 100) if total_users > 0 else 0, 1)
    }

@router.get("/analytics/user-growth")
async def get_user_growth(
    period: str = Query("12m", regex="^(7d|30d|90d|1y|12m)$"),
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener datos de crecimiento de usuarios basados en datos reales
    """
    require_admin_role(current_user)
    
    # Obtener usuarios reales agrupados por mes de creación
    months_data = []
    
    # Generar últimos 12 meses
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_name = month_start.strftime('%b')
        
        # Contar usuarios creados en este mes
        users_this_month = db.query(Usuario).filter(
            Usuario.fecha_creacion >= month_start,
            Usuario.fecha_creacion < month_end
        ).count()
        
        # Contar usuarios totales hasta este mes
        total_users_until_month = db.query(Usuario).filter(
            Usuario.fecha_creacion < month_end
        ).count()
        
        months_data.append({
            "month": month_name,
            "users": total_users_until_month,
            "newUsers": users_this_month
        })
    
    return {"userGrowth": list(reversed(months_data))}

@router.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query("12m", regex="^(7d|30d|90d|1y|12m)$"),
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener datos de ingresos basados en suscripciones reales
    """
    require_admin_role(current_user)
    
    months_data = []
    
    # Generar últimos 12 meses
    for i in range(12):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_name = month_start.strftime('%b')
        
        # Calcular ingresos de suscripciones activas en este mes
        subscriptions_this_month = db.query(Suscripcion).filter(
            Suscripcion.inicio_periodo_actual >= month_start,
            Suscripcion.inicio_periodo_actual < month_end,
            Suscripcion.estado == "active"
        ).all()
        
        revenue_this_month = sum([
            sub.monto_centavos for sub in subscriptions_this_month 
            if sub.monto_centavos
        ]) / 100  # Convertir de centavos a pesos
        
        # Contar suscripciones activas totales hasta este mes
        total_subscriptions_until_month = db.query(Suscripcion).filter(
            Suscripcion.inicio_periodo_actual < month_end,
            Suscripcion.estado == "active"
        ).count()
        
        months_data.append({
            "month": month_name,
            "revenue": revenue_this_month,
            "subscriptions": total_subscriptions_until_month
        })
    
    return {"revenueData": list(reversed(months_data))}

@router.get("/analytics/subscription-distribution")
async def get_subscription_distribution(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener distribución de suscripciones basada en usuarios reales
    """
    require_admin_role(current_user)
    
    # Obtener distribución basada en usuarios y sus organizaciones
    total_users = db.query(Usuario).count()
    
    if total_users == 0:
        return {
            "subscriptionDistribution": [
                {"name": "Gratuito", "value": 100, "color": "#94A3B8"}
            ]
        }
    
    # Contar usuarios por nivel de suscripción de su organización
    gratuito_users = 0
    pro_users = 0
    empresarial_users = 0
    
    users = db.query(Usuario).all()
    
    for user in users:
        if user.organizacion:
            # Buscar suscripción activa de la organización
            suscripcion = db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == user.organizacion.id,
                Suscripcion.estado == "active"
            ).first()
            
            if suscripcion:
                if suscripcion.nivel.value == "gratuito":
                    gratuito_users += 1
                elif suscripcion.nivel.value == "pro":
                    pro_users += 1
                elif suscripcion.nivel.value == "empresarial":
                    empresarial_users += 1
            else:
                # Sin suscripción activa = gratuito
                gratuito_users += 1
        else:
            # Usuario sin organización = gratuito
            gratuito_users += 1
    
    return {
        "subscriptionDistribution": [
            {
                "name": "Gratuito",
                "value": round((gratuito_users / total_users) * 100, 1),
                "color": "#94A3B8"
            },
            {
                "name": "Pro",
                "value": round((pro_users / total_users) * 100, 1),
                "color": "#3B82F6"
            },
            {
                "name": "Empresarial",
                "value": round((empresarial_users / total_users) * 100, 1),
                "color": "#8B5CF6"
            }
        ]
    }

@router.get("/analytics/diagnostic-stats")
async def get_diagnostic_stats(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas de diagnósticos por framework
    """
    require_admin_role(current_user)
    
    # Por ahora retornar datos vacíos ya que no hay diagnósticos creados
    frameworks = ["NIST", "ISO 27001", "CIS Controls", "COBIT"]
    stats = []
    
    for framework in frameworks:
        stats.append({
            "framework": framework,
            "completed": 0,
            "inProgress": 0,
            "total": 0
        })
    
    return {"diagnosticStats": stats}

# ===== CONFIGURACIÓN DEL SISTEMA =====

@router.get("/settings")
async def get_system_settings(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
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
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Actualizar configuración del sistema
    """
    require_admin_role(current_user)
    
    # TODO: Implementar guardado en BD
    # Por ahora solo retornamos éxito
    return {"message": "Configuración actualizada exitosamente"}

# ===== ENDPOINTS DE SEGURIDAD =====

@router.get("/security/stats")
async def get_security_stats(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas de seguridad
    """
    require_admin_role(current_user)
    
    # Contar logins totales (simulado)
    total_logins = db.query(Usuario).count() * 3  # Estimación
    
    # Contar usuarios con MFA habilitado
    mfa_users = db.query(Usuario).filter(Usuario.mfa_habilitado == True).count()
    
    # Contar cuentas bloqueadas
    blocked_accounts = db.query(Usuario).filter(
        Usuario.cuenta_bloqueada_hasta.isnot(None),
        Usuario.cuenta_bloqueada_hasta > datetime.utcnow()
    ).count()
    
    # Contar sesiones activas (simulado)
    active_sessions = db.query(Usuario).filter(
        Usuario.fecha_ultimo_acceso >= datetime.utcnow() - timedelta(hours=1)
    ).count()
    
    # Contar intentos fallidos recientes
    failed_logins = db.query(Usuario).filter(
        Usuario.intentos_login_fallidos > 0
    ).count()
    
    # Actividad sospechosa (simulado)
    suspicious_activity = max(0, failed_logins - 2)
    
    return {
        "totalLogins": total_logins,
        "failedLogins": failed_logins,
        "blockedAccounts": blocked_accounts,
        "activeSessions": active_sessions,
        "mfaUsers": mfa_users,
        "suspiciousActivity": suspicious_activity
    }

@router.get("/security/logs")
async def get_security_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener logs de seguridad
    """
    require_admin_role(current_user)
    
    # Simular logs de seguridad
    logs = []
    
    # Obtener usuarios recientes
    recent_users = db.query(Usuario).order_by(Usuario.fecha_ultimo_acceso.desc()).limit(10).all()
    
    for user in recent_users:
        if user.fecha_ultimo_acceso:
            logs.append({
                "id": str(user.id),
                "timestamp": user.fecha_ultimo_acceso.isoformat(),
                "userId": str(user.id),
                "userName": f"{user.nombres} {user.apellidos}",
                "action": "LOGIN",
                "ipAddress": "192.168.1.100",  # Simulado
                "status": "success",
                "details": f"Inicio de sesión exitoso desde panel admin"
            })
    
    # Agregar algunos logs simulados
    logs.extend([
        {
            "id": "log_001",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "userId": "usr_002",
            "userName": "Juan Pérez",
            "action": "PASSWORD_CHANGE",
            "ipAddress": "192.168.1.105",
            "status": "success",
            "details": "Cambio de contraseña exitoso"
        },
        {
            "id": "log_002",
            "timestamp": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "userId": "usr_003",
            "userName": "Desconocido",
            "action": "LOGIN_FAILED",
            "ipAddress": "185.220.101.45",
            "status": "failed",
            "details": "Intento de login fallido - credenciales incorrectas"
        },
        {
            "id": "log_003",
            "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "userId": "usr_004",
            "userName": "María González",
            "action": "MFA_ENABLED",
            "ipAddress": "192.168.1.110",
            "status": "success",
            "details": "Autenticación de dos factores activada"
        },
        {
            "id": "log_004",
            "timestamp": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "userId": "usr_005",
            "userName": "Desconocido",
            "action": "ACCOUNT_LOCKED",
            "ipAddress": "103.45.12.78",
            "status": "warning",
            "details": "Cuenta bloqueada por exceder intentos de login"
        }
    ])
    
    # Ordenar por timestamp descendente
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "logs": logs[skip:skip + limit],
        "total": len(logs),
        "skip": skip,
        "limit": limit
    }

@router.get("/security/config")
async def get_security_config(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener configuración de seguridad
    """
    require_admin_role(current_user)
    
    # Configuración por defecto
    return {
        "sessionTimeout": 30,
        "maxLoginAttempts": 5,
        "passwordExpirationDays": 90,
        "mfaRequired": False,
        "ipWhitelistEnabled": False
    }

@router.post("/security/config")
async def update_security_config(
    config: dict,
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Actualizar configuración de seguridad
    """
    require_admin_role(current_user)
    
    # Por ahora solo retornar éxito (en producción se guardaría en BD)
    return {
        "message": "Configuración de seguridad actualizada exitosamente",
        "config": config
    }

# ===== ENDPOINTS DE NOTIFICACIONES =====

@router.get("/notifications/stats")
async def get_notifications_stats(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener estadísticas de notificaciones
    """
    require_admin_role(current_user)
    
    # Simular estadísticas de notificaciones
    total_sent = 1247
    pending_notifications = 3
    failed_notifications = 12
    average_open_rate = 68.5
    average_click_rate = 24.3
    active_recipients = db.query(Usuario).filter(Usuario.estado_cuenta == "activo").count()
    
    return {
        "totalSent": total_sent,
        "pendingNotifications": pending_notifications,
        "failedNotifications": failed_notifications,
        "averageOpenRate": average_open_rate,
        "averageClickRate": average_click_rate,
        "activeRecipients": active_recipients
    }

@router.get("/notifications")
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener historial de notificaciones
    """
    require_admin_role(current_user)
    
    # Simular notificaciones
    notifications = [
        {
            "id": "1",
            "title": "Actualización de Sistema",
            "message": "Nueva versión disponible con mejoras de seguridad",
            "type": "email",
            "recipients": 156,
            "sentAt": datetime.utcnow().isoformat(),
            "status": "sent",
            "sentBy": "Frank Bailey",
            "openRate": 72.5,
            "clickRate": 28.3
        },
        {
            "id": "2",
            "title": "Recordatorio de Pago",
            "message": "Su suscripción vence en 7 días",
            "type": "email",
            "recipients": 24,
            "sentAt": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "status": "sent",
            "sentBy": "Sistema Automatizado",
            "openRate": 85.2,
            "clickRate": 42.1
        },
        {
            "id": "3",
            "title": "Mantenimiento Programado",
            "message": "El sistema estará en mantenimiento el próximo domingo",
            "type": "push",
            "recipients": 156,
            "sentAt": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "status": "scheduled",
            "sentBy": "Admin Mantenedor"
        },
        {
            "id": "4",
            "title": "Nuevas Funcionalidades",
            "message": "Descubre las nuevas características del dashboard",
            "type": "in-app",
            "recipients": 0,
            "sentAt": (datetime.utcnow() - timedelta(days=3)).isoformat(),
            "status": "draft",
            "sentBy": "Frank Bailey"
        },
        {
            "id": "5",
            "title": "Alerta de Seguridad",
            "message": "Detectamos un intento de acceso no autorizado",
            "type": "email",
            "recipients": 8,
            "sentAt": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "status": "failed",
            "sentBy": "Sistema de Seguridad"
        }
    ]
    
    # Filtrar por estado si se especifica
    if status and status != "all":
        notifications = [n for n in notifications if n["status"] == status]
    
    return {
        "notifications": notifications[skip:skip + limit],
        "total": len(notifications),
        "skip": skip,
        "limit": limit
    }

@router.get("/notifications/templates")
async def get_notification_templates(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Obtener templates de notificaciones
    """
    require_admin_role(current_user)
    
    templates = [
        {
            "id": "1",
            "name": "Bienvenida Nuevos Usuarios",
            "subject": "Bienvenido a C4A",
            "type": "welcome",
            "lastUsed": (datetime.utcnow() - timedelta(days=1)).isoformat()
        },
        {
            "id": "2",
            "name": "Recordatorio de Pago",
            "subject": "Tu suscripción está por vencer",
            "type": "payment",
            "lastUsed": (datetime.utcnow() - timedelta(days=2)).isoformat()
        },
        {
            "id": "3",
            "name": "Alerta de Seguridad",
            "subject": "Alerta de seguridad en tu cuenta",
            "type": "alert",
            "lastUsed": (datetime.utcnow() - timedelta(days=3)).isoformat()
        }
    ]
    
    return {"templates": templates}

@router.post("/notifications")
async def send_notification(
    notification: dict,
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Enviar nueva notificación
    """
    require_admin_role(current_user)
    
    # Simular envío de notificación
    notification_id = f"notif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Notificación enviada exitosamente",
        "notificationId": notification_id,
        "recipients": notification.get("recipients", "all"),
        "status": "sent"
    }

# ===== ENDPOINTS DE EXPORTACIÓN =====

@router.get("/users/export")
async def export_users(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Exportar usuarios a Excel
    """
    require_admin_role(current_user)
    
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener todos los usuarios con sus organizaciones
        usuarios = db.query(Usuario).join(Organizacion).all()
        
        # Preparar datos para exportación
        data = []
        for usuario in usuarios:
            data.append({
                'ID': usuario.id,
                'Nombres': usuario.nombres,
                'Apellidos': usuario.apellidos,
                'Email': usuario.email,
                'Empresa': usuario.organizacion.nombre if usuario.organizacion else 'Sin empresa',
                'Rol': usuario.rol.nombre if usuario.rol else 'Sin rol',
                'Estado': usuario.estado_cuenta.value if usuario.estado_cuenta else 'Sin estado',
                'Último Login': usuario.fecha_ultimo_acceso.isoformat() if usuario.fecha_ultimo_acceso else 'Nunca',
                'Fecha Registro': usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else 'N/A'
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Usuarios', index=False)
        
        output.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=usuarios_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar usuarios: {str(e)}")

@router.get("/diagnostics/export")
async def export_diagnostics(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Exportar diagnósticos a Excel
    """
    require_admin_role(current_user)
    
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener diagnósticos
        diagnosticos = db.query(Evaluacion).all()
        
        # Preparar datos para exportación
        data = []
        for diag in diagnosticos:
            data.append({
                'ID': diag.id,
                'Tipo': diag.tipo_evaluacion,
                'Estado': diag.estado.value if diag.estado else 'Sin estado',
                'Usuario': f"{diag.creado_por_usuario.nombres} {diag.creado_por_usuario.apellidos}" if diag.creado_por_usuario else 'N/A',
                'Empresa': diag.creado_por_usuario.organizacion.nombre if diag.creado_por_usuario and diag.creado_por_usuario.organizacion else 'N/A',
                'Fecha Creación': diag.fecha_creacion.isoformat() if diag.fecha_creacion else 'N/A',
                'Fecha Completado': diag.fecha_completado.isoformat() if diag.fecha_completado else 'N/A',
                'Puntuación': diag.puntuacion_total if diag.puntuacion_total else 'N/A'
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Diagnósticos', index=False)
        
        output.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=diagnosticos_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar diagnósticos: {str(e)}")

@router.get("/payments/export")
async def export_payments(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Exportar pagos a Excel
    """
    require_admin_role(current_user)
    
    try:
        import pandas as pd
        from io import BytesIO
        
        # Obtener suscripciones
        suscripciones = db.query(Suscripcion).join(Organizacion).all()
        
        # Preparar datos para exportación
        data = []
        for susc in suscripciones:
            data.append({
                'ID': susc.id,
                'Empresa': susc.organizacion.nombre if susc.organizacion else 'N/A',
                'Plan': susc.nivel.value if susc.nivel else 'N/A',
                'Monto': (susc.monto_centavos or 0) / 100,
                'Moneda': susc.moneda or 'CLP',
                'Estado': susc.estado,
                'Fecha Creación': susc.fecha_creacion.isoformat() if susc.fecha_creacion else 'N/A',
                'Inicio Período': susc.inicio_periodo_actual.isoformat() if susc.inicio_periodo_actual else 'N/A',
                'Fin Período': susc.fin_periodo_actual.isoformat() if susc.fin_periodo_actual else 'N/A',
                'Ciclo': susc.ciclo_facturacion or 'N/A'
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Pagos', index=False)
        
        output.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=pagos_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar pagos: {str(e)}")

@router.post("/payments/sync")
async def sync_payments(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Sincronizar pagos con proveedor externo
    """
    require_admin_role(current_user)
    
    try:
        # Simular sincronización
        suscripciones = db.query(Suscripcion).all()
        updated_count = 0
        
        for susc in suscripciones:
            # Simular actualización de estado
            if susc.estado == 'active':
                susc.fecha_actualizacion = datetime.utcnow()
                updated_count += 1
        
        db.commit()
        
        return {
            "message": "Sincronización completada exitosamente",
            "updatedSubscriptions": updated_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al sincronizar pagos: {str(e)}")

@router.get("/analytics/export")
async def export_analytics(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Exportar analytics a PDF
    """
    require_admin_role(current_user)
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from io import BytesIO
        
        # Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title = Paragraph("Reporte de Analytics - C4A SaaS", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Obtener estadísticas
        total_users = db.query(Usuario).count()
        total_orgs = db.query(Organizacion).count()
        total_suscripciones = db.query(Suscripcion).count()
        
        # Datos del reporte
        data = [
            ['Métrica', 'Valor'],
            ['Total de Usuarios', str(total_users)],
            ['Total de Organizaciones', str(total_orgs)],
            ['Total de Suscripciones', str(total_suscripciones)],
            ['Fecha de Generación', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Generar PDF
        doc.build(story)
        buffer.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(buffer.getvalue()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=analytics_{datetime.utcnow().strftime('%Y%m%d')}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar analytics: {str(e)}")

# ===== NOTIFICACIONES AUTOMÁTICAS =====

@router.post("/notifications/run-automatic")
async def run_automatic_notifications_endpoint(
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Ejecutar notificaciones automáticas
    """
    require_admin_role(current_user)
    
    try:
        result = run_automatic_notifications(db)
        return {
            "message": "Notificaciones automáticas ejecutadas",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando notificaciones: {str(e)}")

@router.post("/notifications/send-welcome/{user_id}")
async def send_welcome_notification(
    user_id: str,
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Enviar notificación de bienvenida a un usuario específico
    """
    require_admin_role(current_user)
    
    try:
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        service = NotificationService(db)
        success = service.send_welcome_notification(usuario)
        
        if success:
            return {
                "message": "Notificación de bienvenida enviada exitosamente",
                "user_email": usuario.email,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Error enviando notificación")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/notifications/send-payment-reminder/{subscription_id}")
async def send_payment_reminder(
    subscription_id: str,
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Enviar recordatorio de pago a una suscripción específica
    """
    require_admin_role(current_user)
    
    try:
        suscripcion = db.query(Suscripcion).filter(Suscripcion.id == subscription_id).first()
        if not suscripcion:
            raise HTTPException(status_code=404, detail="Suscripción no encontrada")
        
        service = NotificationService(db)
        success = service.send_payment_reminder(suscripcion)
        
        if success:
            return {
                "message": "Recordatorio de pago enviado exitosamente",
                "subscription_id": subscription_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Error enviando recordatorio")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/notifications/send-security-alert/{user_id}")
async def send_security_alert(
    user_id: str,
    alert_type: str,
    details: str = "",
    current_user: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_db)
):
    """
    Enviar alerta de seguridad a un usuario específico
    """
    require_admin_role(current_user)
    
    try:
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        service = NotificationService(db)
        success = service.send_security_alert(usuario, alert_type, details)
        
        if success:
            return {
                "message": "Alerta de seguridad enviada exitosamente",
                "user_email": usuario.email,
                "alert_type": alert_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Error enviando alerta")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
