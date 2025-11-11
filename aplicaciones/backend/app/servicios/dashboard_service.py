# app/servicios/dashboard_service.py
"""
Servicio del Dashboard para C4A SaaS
Maneja la lógica de negocio del dashboard
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import uuid

from app.modelos.usuario import Usuario
from app.modelos.evaluacion import Evaluacion, EstadoEvaluacion
from app.modelos.organizacion import Organizacion
from app.modelos.framework import Framework
from app.core.config import NivelSuscripcion, LIMITES_POR_NIVEL
from app.core.excepciones import ExcepcionC4A, ExcepcionValidacion

class DashboardService:
    """Servicio para lógica de negocio del dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtener_resumen_dashboard(self, usuario: Usuario) -> Dict[str, Any]:
        """
        Obtener resumen completo del dashboard
        
        Args:
            usuario: Usuario autenticado
            
        Returns:
            Diccionario con estadísticas del dashboard
        """
        try:
            organizacion = usuario.organizacion
            
            # Obtener evaluaciones de la organización
            evaluaciones = self.db.query(Evaluacion).filter(
                Evaluacion.organizacion_id == organizacion.id,
                Evaluacion.fecha_eliminacion.is_(None)
            ).all()
            
            # Calcular estadísticas básicas
            estadisticas = self._calcular_estadisticas_basicas(evaluaciones)
            
            # Calcular uso mensual
            uso_mensual = self._calcular_uso_mensual(evaluaciones)
            
            # Obtener información del plan
            info_plan = self._obtener_info_plan(organizacion)
            
            return {
                **estadisticas,
                **uso_mensual,
                **info_plan,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            raise ExcepcionC4A(
                mensaje=f"Error al obtener resumen del dashboard: {str(e)}",
                codigo_error="DASHBOARD_ERROR"
            )
    
    def obtener_evaluaciones_recientes(self, usuario: Usuario, limite: int = 5) -> List[Dict[str, Any]]:
        """
        Obtener evaluaciones recientes del usuario
        
        Args:
            usuario: Usuario autenticado
            limite: Número máximo de evaluaciones a retornar
            
        Returns:
            Lista de evaluaciones recientes
        """
        try:
            organizacion = usuario.organizacion
            
            evaluaciones = self.db.query(Evaluacion).filter(
                Evaluacion.organizacion_id == organizacion.id,
                Evaluacion.fecha_eliminacion.is_(None)
            ).order_by(Evaluacion.fecha_creacion.desc()).limit(limite).all()
            
            evaluaciones_recientes = []
            for evaluacion in evaluaciones:
                evaluaciones_recientes.append({
                    "id": str(evaluacion.id),
                    "nombre": evaluacion.nombre,
                    "fecha_creacion": evaluacion.fecha_creacion,
                    "estado": evaluacion.estado.value,
                    "puntuacion": float(evaluacion.puntuacion_global) if evaluacion.puntuacion_global else None,
                    "porcentaje_completado": round(evaluacion.porcentaje_completado, 2),
                    "framework": evaluacion.framework.nombre if evaluacion.framework else None,
                    "nivel_usado": evaluacion.nivel_usado.value
                })
            
            return evaluaciones_recientes
            
        except Exception as e:
            raise ExcepcionC4A(
                mensaje=f"Error al obtener evaluaciones recientes: {str(e)}",
                codigo_error="EVALUACIONES_RECIENTES_ERROR"
            )
    
    def crear_nueva_evaluacion(self, usuario: Usuario, nombre: str, framework_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Crear una nueva evaluación
        
        Args:
            usuario: Usuario autenticado
            nombre: Nombre de la evaluación
            framework_id: ID del framework (opcional)
            
        Returns:
            Información de la evaluación creada
        """
        try:
            # Validar permisos
            self._validar_permisos_creacion_evaluacion(usuario)
            
            # Obtener framework
            framework = self._obtener_framework(framework_id)
            
            # Crear evaluación
            organizacion = usuario.organizacion
            nueva_evaluacion = Evaluacion(
                nombre=nombre,
                organizacion_id=organizacion.id,
                framework_id=framework.id,
                creado_por=usuario.id,
                nivel_usado=organizacion.nivel_suscripcion,
                total_preguntas=framework.contar_preguntas_activas_para_nivel(organizacion.nivel_suscripcion),
                estado=EstadoEvaluacion.EN_PROGRESO
            )
            
            # Iniciar evaluación
            nueva_evaluacion.iniciar_evaluacion()
            
            self.db.add(nueva_evaluacion)
            self.db.commit()
            self.db.refresh(nueva_evaluacion)
            
            return {
                "id": str(nueva_evaluacion.id),
                "nombre": nueva_evaluacion.nombre,
                "estado": nueva_evaluacion.estado.value,
                "fecha_creacion": nueva_evaluacion.fecha_creacion,
                "framework": framework.nombre,
                "nivel_usado": nueva_evaluacion.nivel_usado.value,
                "total_preguntas": nueva_evaluacion.total_preguntas,
                "mensaje": "Evaluación creada exitosamente"
            }
            
        except ExcepcionC4A:
            raise
        except Exception as e:
            self.db.rollback()
            raise ExcepcionC4A(
                mensaje=f"Error al crear evaluación: {str(e)}",
                codigo_error="CREAR_EVALUACION_ERROR"
            )
    
    def obtener_acciones_rapidas(self, usuario: Usuario) -> List[Dict[str, Any]]:
        """
        Obtener acciones rápidas disponibles para el usuario
        
        Args:
            usuario: Usuario autenticado
            
        Returns:
            Lista de acciones rápidas disponibles
        """
        try:
            organizacion = usuario.organizacion
            acciones = []
            
            # Acción: Crear Nueva Evaluación
            puede_crear_evaluacion = (
                usuario.puede_crear_evaluacion() and 
                organizacion.puede_crear_evaluacion
            )
            acciones.append({
                "id": "crear_nueva_evaluacion",
                "nombre": "Crear Nueva Evaluación",
                "descripcion": "Iniciar una nueva evaluación de ciberseguridad",
                "disponible": puede_crear_evaluacion,
                "icono": "plus-circle",
                "ruta": "/evaluaciones/nueva",
                "categoria": "evaluaciones"
            })
            
            # Acción: Ver Reportes
            puede_ver_reportes = usuario.puede_acceder_recurso("reportes", "leer")
            acciones.append({
                "id": "ver_reportes",
                "nombre": "Ver Reportes",
                "descripcion": "Acceder a reportes y análisis de evaluaciones",
                "disponible": puede_ver_reportes,
                "icono": "bar-chart",
                "ruta": "/reportes",
                "categoria": "reportes"
            })
            
            # Acción: Gestionar Usuarios
            puede_gestionar_usuarios = (
                usuario.puede_acceder_recurso("usuarios", "gestionar") and
                organizacion.nivel_suscripcion in [NivelSuscripcion.PRO, NivelSuscripcion.EMPRESARIAL]
            )
            acciones.append({
                "id": "gestionar_usuarios",
                "nombre": "Gestionar Usuarios",
                "descripcion": "Administrar usuarios de la organización",
                "disponible": puede_gestionar_usuarios,
                "icono": "users",
                "ruta": "/usuarios",
                "categoria": "usuarios"
            })
            
            # Acción: Actualizar Plan
            puede_actualizar_plan = (
                usuario.puede_acceder_recurso("suscripciones", "gestionar") and
                organizacion.nivel_suscripcion != NivelSuscripcion.EMPRESARIAL
            )
            acciones.append({
                "id": "actualizar_plan",
                "nombre": "Actualizar Plan",
                "descripcion": "Mejorar tu plan de suscripción",
                "disponible": puede_actualizar_plan,
                "icono": "credit-card",
                "ruta": "/suscripciones",
                "categoria": "suscripciones"
            })
            
            # Acción: Ver Dashboard
            acciones.append({
                "id": "ver_dashboard",
                "nombre": "Ver Dashboard",
                "descripcion": "Acceder al panel principal",
                "disponible": True,
                "icono": "home",
                "ruta": "/dashboard",
                "categoria": "navegacion"
            })
            
            return acciones
            
        except Exception as e:
            raise ExcepcionC4A(
                mensaje=f"Error al obtener acciones rápidas: {str(e)}",
                codigo_error="ACCIONES_RAPIDAS_ERROR"
            )
    
    def obtener_estadisticas_detalladas(self, usuario: Usuario) -> Dict[str, Any]:
        """
        Obtener estadísticas detalladas de uso
        
        Args:
            usuario: Usuario autenticado
            
        Returns:
            Estadísticas detalladas
        """
        try:
            organizacion = usuario.organizacion
            
            # Estadísticas de la organización
            uso_organizacion = organizacion.obtener_uso_mensual()
            
            # Estadísticas del usuario
            estadisticas_usuario = usuario.obtener_estadisticas_uso()
            
            # Estadísticas de evaluaciones por estado
            evaluaciones_por_estado = self._calcular_evaluaciones_por_estado(organizacion.id)
            
            # Tendencias de uso (últimos 6 meses)
            tendencias = self._calcular_tendencias_uso(organizacion.id)
            
            return {
                "organizacion": {
                    "id": str(organizacion.id),
                    "nombre": organizacion.nombre,
                    "nivel_suscripcion": organizacion.nivel_suscripcion.value,
                    "sector": organizacion.sector.value,
                    "tamaño": organizacion.tamaño.value,
                    "uso_mensual": uso_organizacion
                },
                "usuario": {
                    "id": str(usuario.id),
                    "nombre_completo": usuario.nombre_completo,
                    "email": usuario.email,
                    "rol": usuario.rol.nombre_mostrar,
                    "estadisticas": estadisticas_usuario
                },
                "evaluaciones": evaluaciones_por_estado,
                "tendencias": tendencias,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            raise ExcepcionC4A(
                mensaje=f"Error al obtener estadísticas detalladas: {str(e)}",
                codigo_error="ESTADISTICAS_DETALLADAS_ERROR"
            )
    
    def _calcular_estadisticas_basicas(self, evaluaciones: List[Evaluacion]) -> Dict[str, Any]:
        """Calcular estadísticas básicas de evaluaciones"""
        total_evaluaciones = len(evaluaciones)
        
        en_progreso = len([e for e in evaluaciones if e.estado in [
            EstadoEvaluacion.BORRADOR, EstadoEvaluacion.EN_PROGRESO
        ]])
        
        completadas = [e for e in evaluaciones if e.estado == EstadoEvaluacion.COMPLETADA and e.puntuacion_global]
        if completadas:
            promedio_puntuacion = sum(float(e.puntuacion_global) for e in completadas) / len(completadas)
        else:
            promedio_puntuacion = 0.0
        
        return {
            "total_evaluaciones": total_evaluaciones,
            "en_progreso": en_progreso,
            "promedio_puntuacion": round(promedio_puntuacion, 2),
            "evaluaciones_completadas": len(completadas)
        }
    
    def _calcular_uso_mensual(self, evaluaciones: List[Evaluacion]) -> Dict[str, Any]:
        """Calcular uso mensual"""
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        uso_mensual = len([e for e in evaluaciones if e.fecha_creacion >= inicio_mes])
        
        return {
            "uso_mensual": uso_mensual
        }
    
    def _obtener_info_plan(self, organizacion: Organizacion) -> Dict[str, Any]:
        """Obtener información del plan de suscripción"""
        limite_mensual = organizacion.maximo_evaluaciones_por_mes
        limite_usuarios = organizacion.maximo_usuarios
        
        # Calcular porcentaje de uso
        inicio_mes = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        evaluaciones_mes = len([e for e in organizacion.evaluaciones 
                               if e.fecha_creacion >= inicio_mes and e.fecha_eliminacion is None])
        porcentaje_uso_evaluaciones = (evaluaciones_mes / limite_mensual) * 100 if limite_mensual > 0 else 0
        
        usuarios_activos = len([u for u in organizacion.usuarios if u.fecha_eliminacion is None])
        porcentaje_uso_usuarios = (usuarios_activos / limite_usuarios) * 100 if limite_usuarios > 0 else 0
        
        return {
            "nivel_suscripcion": organizacion.nivel_suscripcion.value,
            "limite_mensual": limite_mensual,
            "limite_usuarios": limite_usuarios,
            "porcentaje_uso_evaluaciones": round(porcentaje_uso_evaluaciones, 2),
            "porcentaje_uso_usuarios": round(porcentaje_uso_usuarios, 2),
            "suscripcion_vencida": organizacion.suscripcion_vencida
        }
    
    def _validar_permisos_creacion_evaluacion(self, usuario: Usuario):
        """Validar permisos para crear evaluación"""
        if not usuario.esta_activo:
            raise ExcepcionValidacion("Usuario no está activo")
        
        if not usuario.puede_crear_evaluacion():
            raise ExcepcionValidacion("No tienes permisos para crear evaluaciones")
        
        organizacion = usuario.organizacion
        if not organizacion.puede_crear_evaluacion:
            raise ExcepcionValidacion(
                f"Has alcanzado el límite de {organizacion.maximo_evaluaciones_por_mes} evaluaciones por mes"
            )
    
    def _obtener_framework(self, framework_id: Optional[str] = None) -> Framework:
        """Obtener framework para la evaluación"""
        if framework_id:
            framework = self.db.query(Framework).filter(
                Framework.id == uuid.UUID(framework_id),
                Framework.esta_activo == True
            ).first()
            if not framework:
                raise ExcepcionValidacion("Framework no encontrado")
        else:
            # Usar el framework por defecto
            framework = self.db.query(Framework).filter(
                Framework.esta_activo == True
            ).first()
            if not framework:
                raise ExcepcionValidacion("No hay frameworks disponibles")
        
        return framework
    
    def _calcular_evaluaciones_por_estado(self, organizacion_id: str) -> Dict[str, int]:
        """Calcular evaluaciones por estado"""
        evaluaciones = self.db.query(Evaluacion).filter(
            Evaluacion.organizacion_id == organizacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).all()
        
        estados = {}
        for evaluacion in evaluaciones:
            estado = evaluacion.estado.value
            estados[estado] = estados.get(estado, 0) + 1
        
        return estados
    
    def _calcular_tendencias_uso(self, organizacion_id: str) -> Dict[str, Any]:
        """Calcular tendencias de uso de los últimos 6 meses"""
        # Calcular fechas de los últimos 6 meses
        ahora = datetime.utcnow()
        tendencias = {}
        
        for i in range(6):
            fecha_inicio = (ahora - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fecha_fin = (fecha_inicio + timedelta(days=30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            evaluaciones_mes = self.db.query(Evaluacion).filter(
                Evaluacion.organizacion_id == organizacion_id,
                Evaluacion.fecha_creacion >= fecha_inicio,
                Evaluacion.fecha_creacion < fecha_fin,
                Evaluacion.fecha_eliminacion.is_(None)
            ).count()
            
            mes_key = fecha_inicio.strftime("%Y-%m")
            tendencias[mes_key] = evaluaciones_mes
        
        return tendencias
