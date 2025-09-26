"""
Sistema de permisos por niveles de suscripción
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from app.modelos.usuario import Usuario
from app.modelos.organizacion import Organizacion
from app.modelos.rol import Rol

class NivelSuscripcion(str, Enum):
    """Niveles de suscripción disponibles"""
    GRATUITO = "gratuito"
    PRO = "pro"
    EMPRESARIAL = "empresarial"

class Permiso(str, Enum):
    """Permisos disponibles en el sistema"""
    # Permisos de evaluación
    CREAR_EVALUACION = "crear_evaluacion"
    VER_EVALUACIONES = "ver_evaluaciones"
    EDITAR_EVALUACION = "editar_evaluacion"
    ELIMINAR_EVALUACION = "eliminar_evaluacion"
    COMPARTIR_EVALUACION = "compartir_evaluacion"
    
    # Permisos de reportes
    GENERAR_REPORTE_BASICO = "generar_reporte_basico"
    GENERAR_REPORTE_AVANZADO = "generar_reporte_avanzado"
    GENERAR_REPORTE_PDF = "generar_reporte_pdf"
    GENERAR_REPORTE_EXCEL = "generar_reporte_excel"
    VER_BENCHMARKS = "ver_benchmarks"
    EXPORTAR_DATOS = "exportar_datos"
    
    # Permisos de suscripción
    VER_SUSCRIPCION = "ver_suscripcion"
    ACTUALIZAR_SUSCRIPCION = "actualizar_suscripcion"
    CANCELAR_SUSCRIPCION = "cancelar_suscripcion"
    VER_FACTURAS = "ver_facturas"
    
    # Permisos de organización
    VER_ORGANIZACION = "ver_organizacion"
    EDITAR_ORGANIZACION = "editar_organizacion"
    GESTIONAR_USUARIOS = "gestionar_usuarios"
    VER_ESTADISTICAS = "ver_estadisticas"
    
    # Permisos de usuario
    VER_PERFIL = "ver_perfil"
    EDITAR_PERFIL = "editar_perfil"
    CAMBIAR_CONTRASEÑA = "cambiar_contraseña"
    CONFIGURAR_MFA = "configurar_mfa"
    
    # Permisos de administración
    ADMIN_USUARIOS = "admin_usuarios"
    ADMIN_ORGANIZACIONES = "admin_organizaciones"
    ADMIN_SISTEMA = "admin_sistema"
    VER_LOGS_AUDITORIA = "ver_logs_auditoria"

class PermissionService:
    """Servicio de permisos por niveles de suscripción"""
    
    def __init__(self):
        self.permissions_by_level = {
            NivelSuscripcion.GRATUITO: [
                # Evaluaciones básicas
                Permiso.CREAR_EVALUACION,
                Permiso.VER_EVALUACIONES,
                Permiso.EDITAR_EVALUACION,
                
                # Reportes básicos
                Permiso.GENERAR_REPORTE_BASICO,
                
                # Suscripción
                Permiso.VER_SUSCRIPCION,
                Permiso.ACTUALIZAR_SUSCRIPCION,
                
                # Organización básica
                Permiso.VER_ORGANIZACION,
                
                # Usuario
                Permiso.VER_PERFIL,
                Permiso.EDITAR_PERFIL,
                Permiso.CAMBIAR_CONTRASEÑA,
            ],
            
            NivelSuscripcion.PRO: [
                # Todas las de gratuito
                *self.permissions_by_level.get(NivelSuscripcion.GRATUITO, []),
                
                # Evaluaciones avanzadas
                Permiso.ELIMINAR_EVALUACION,
                Permiso.COMPARTIR_EVALUACION,
                
                # Reportes avanzados
                Permiso.GENERAR_REPORTE_AVANZADO,
                Permiso.GENERAR_REPORTE_PDF,
                Permiso.GENERAR_REPORTE_EXCEL,
                Permiso.VER_BENCHMARKS,
                
                # Suscripción
                Permiso.CANCELAR_SUSCRIPCION,
                Permiso.VER_FACTURAS,
                
                # Organización
                Permiso.EDITAR_ORGANIZACION,
                Permiso.GESTIONAR_USUARIOS,
                Permiso.VER_ESTADISTICAS,
                
                # Usuario avanzado
                Permiso.CONFIGURAR_MFA,
            ],
            
            NivelSuscripcion.EMPRESARIAL: [
                # Todas las de pro
                *self.permissions_by_level.get(NivelSuscripcion.PRO, []),
                
                # Exportación de datos
                Permiso.EXPORTAR_DATOS,
                
                # Administración (solo para roles específicos)
                Permiso.ADMIN_USUARIOS,
                Permiso.ADMIN_ORGANIZACIONES,
                Permiso.VER_LOGS_AUDITORIA,
            ]
        }
        
        # Permisos especiales para administradores del sistema
        self.admin_permissions = [
            Permiso.ADMIN_SISTEMA,
            Permiso.ADMIN_USUARIOS,
            Permiso.ADMIN_ORGANIZACIONES,
            Permiso.VER_LOGS_AUDITORIA,
        ]
    
    def has_permission(
        self, 
        usuario: Usuario, 
        permiso: Permiso
    ) -> bool:
        """Verificar si un usuario tiene un permiso específico"""
        
        # Verificar si es administrador del sistema
        if self._is_system_admin(usuario):
            return True
        
        # Verificar permisos del rol
        if self._has_role_permission(usuario, permiso):
            return True
        
        # Verificar permisos del nivel de suscripción
        if self._has_subscription_permission(usuario, permiso):
            return True
        
        return False
    
    def get_user_permissions(self, usuario: Usuario) -> List[Permiso]:
        """Obtener todos los permisos de un usuario"""
        permissions = set()
        
        # Agregar permisos de administrador del sistema
        if self._is_system_admin(usuario):
            permissions.update(self.admin_permissions)
        
        # Agregar permisos del rol
        if usuario.rol:
            permissions.update(usuario.rol.permisos or [])
        
        # Agregar permisos del nivel de suscripción
        if usuario.organizacion:
            nivel = usuario.organizacion.nivel_suscripcion
            permissions.update(self.permissions_by_level.get(nivel, []))
        
        return list(permissions)
    
    def get_available_features(self, usuario: Usuario) -> Dict[str, Any]:
        """Obtener características disponibles para un usuario"""
        nivel = usuario.organizacion.nivel_suscripcion if usuario.organizacion else NivelSuscripcion.GRATUITO
        
        features = {
            "evaluaciones": {
                "max_por_mes": self._get_evaluation_limit(nivel),
                "frameworks_disponibles": self._get_available_frameworks(nivel),
                "puede_compartir": self.has_permission(usuario, Permiso.COMPARTIR_EVALUACION),
                "puede_eliminar": self.has_permission(usuario, Permiso.ELIMINAR_EVALUACION),
            },
            "reportes": {
                "max_por_mes": self._get_report_limit(nivel),
                "tipos_disponibles": self._get_available_report_types(nivel),
                "puede_exportar_pdf": self.has_permission(usuario, Permiso.GENERAR_REPORTE_PDF),
                "puede_exportar_excel": self.has_permission(usuario, Permiso.GENERAR_REPORTE_EXCEL),
                "puede_ver_benchmarks": self.has_permission(usuario, Permiso.VER_BENCHMARKS),
            },
            "organizacion": {
                "max_usuarios": self._get_user_limit(nivel),
                "puede_gestionar_usuarios": self.has_permission(usuario, Permiso.GESTIONAR_USUARIOS),
                "puede_ver_estadisticas": self.has_permission(usuario, Permiso.VER_ESTADISTICAS),
            },
            "suscripcion": {
                "nivel": nivel,
                "puede_actualizar": self.has_permission(usuario, Permiso.ACTUALIZAR_SUSCRIPCION),
                "puede_cancelar": self.has_permission(usuario, Permiso.CANCELAR_SUSCRIPCION),
                "puede_ver_facturas": self.has_permission(usuario, Permiso.VER_FACTURAS),
            }
        }
        
        return features
    
    def _is_system_admin(self, usuario: Usuario) -> bool:
        """Verificar si es administrador del sistema"""
        return (
            usuario.rol and 
            usuario.rol.nombre == "admin" and
            "admin_sistema" in (usuario.rol.permisos or [])
        )
    
    def _has_role_permission(self, usuario: Usuario, permiso: Permiso) -> bool:
        """Verificar si el rol tiene el permiso"""
        if not usuario.rol or not usuario.rol.permisos:
            return False
        
        return permiso in usuario.rol.permisos
    
    def _has_subscription_permission(self, usuario: Usuario, permiso: Permiso) -> bool:
        """Verificar si el nivel de suscripción tiene el permiso"""
        if not usuario.organizacion:
            return False
        
        nivel = usuario.organizacion.nivel_suscripcion
        return permiso in self.permissions_by_level.get(nivel, [])
    
    def _get_evaluation_limit(self, nivel: NivelSuscripcion) -> int:
        """Obtener límite de evaluaciones por mes"""
        limits = {
            NivelSuscripcion.GRATUITO: 1,
            NivelSuscripcion.PRO: 10,
            NivelSuscripcion.EMPRESARIAL: 100
        }
        return limits.get(nivel, 1)
    
    def _get_report_limit(self, nivel: NivelSuscripcion) -> int:
        """Obtener límite de reportes por mes"""
        limits = {
            NivelSuscripcion.GRATUITO: 1,
            NivelSuscripcion.PRO: 10,
            NivelSuscripcion.EMPRESARIAL: 100
        }
        return limits.get(nivel, 1)
    
    def _get_user_limit(self, nivel: NivelSuscripcion) -> int:
        """Obtener límite de usuarios por organización"""
        limits = {
            NivelSuscripcion.GRATUITO: 3,
            NivelSuscripcion.PRO: 25,
            NivelSuscripcion.EMPRESARIAL: 100
        }
        return limits.get(nivel, 3)
    
    def _get_available_frameworks(self, nivel: NivelSuscripcion) -> List[str]:
        """Obtener frameworks disponibles por nivel"""
        frameworks = {
            NivelSuscripcion.GRATUITO: ["nist_csf"],
            NivelSuscripcion.PRO: ["nist_csf", "cobit"],
            NivelSuscripcion.EMPRESARIAL: ["nist_csf", "cobit", "iso27001"]
        }
        return frameworks.get(nivel, ["nist_csf"])
    
    def _get_available_report_types(self, nivel: NivelSuscripcion) -> List[str]:
        """Obtener tipos de reportes disponibles por nivel"""
        report_types = {
            NivelSuscripcion.GRATUITO: ["basico"],
            NivelSuscripcion.PRO: ["basico", "avanzado", "pdf", "excel"],
            NivelSuscripcion.EMPRESARIAL: ["basico", "avanzado", "pdf", "excel", "benchmark", "custom"]
        }
        return report_types.get(nivel, ["basico"])

# Instancia global del servicio de permisos
permission_service = PermissionService()

def get_permission_service() -> PermissionService:
    """Obtener instancia del servicio de permisos"""
    return permission_service

def require_permission(permiso: Permiso):
    """Decorator para requerir un permiso específico"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Obtener usuario del contexto
            usuario = kwargs.get('usuario_actual')
            if not usuario:
                raise HTTPException(status_code=401, detail="Usuario no autenticado")
            
            # Verificar permiso
            if not permission_service.has_permission(usuario, permiso):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permiso requerido: {permiso.value}"
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
















