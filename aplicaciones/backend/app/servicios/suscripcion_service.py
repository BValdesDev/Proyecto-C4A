# app/servicios/suscripcion_service.py
"""
Servicio centralizado para gestión de suscripciones
Obtiene el nivel de suscripción desde la tabla suscripciones activa
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.modelos.organizacion import Organizacion
from app.modelos.suscripcion import Suscripcion
from app.core.config import NivelSuscripcion

class ServicioSuscripcion:
    """Servicio para gestión de suscripciones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtener_nivel_suscripcion_activa(self, organizacion_id: str) -> NivelSuscripcion:
        """
        Obtener el nivel de suscripción activa de una organización
        Busca en la tabla suscripciones, no en organizaciones
        """
        try:
            suscripcion_activa = self.db.query(Suscripcion).filter(
                Suscripcion.organizacion_id == organizacion_id,
                Suscripcion.estado == "active"
            ).first()
            
            if suscripcion_activa:
                return suscripcion_activa.nivel
            else:
                # Si no hay suscripción activa, es gratuito
                return NivelSuscripcion.GRATUITO
                
        except Exception:
            return NivelSuscripcion.GRATUITO
    
    def obtener_limites_nivel(self, nivel: NivelSuscripcion) -> dict:
        """
        Obtener límites según el nivel de suscripción
        Basado en el prompt maestro
        """
        limites = {
            NivelSuscripcion.GRATUITO: {
                "maximo_usuarios": 1,
                "maximo_evaluaciones_por_mes": 1,
                "maximo_dias_retencion_datos": 30,
                "preguntas_evaluacion": 10,
                "tiempo_estimado": "5-7 minutos",
                "recomendaciones": 3,
                "benchmarking": False,
                "exportar_excel": False,
                "marca_agua": True
            },
            NivelSuscripcion.PRO: {
                "maximo_usuarios": 10,
                "maximo_evaluaciones_por_mes": 50,
                "maximo_dias_retencion_datos": 365,
                "preguntas_evaluacion": 50,
                "tiempo_estimado": "15-20 minutos",
                "recomendaciones": 15,
                "benchmarking": True,
                "exportar_excel": True,
                "marca_agua": False
            },
            NivelSuscripcion.EMPRESARIAL: {
                "maximo_usuarios": 100,
                "maximo_evaluaciones_por_mes": 1000,
                "maximo_dias_retencion_datos": 2555,  # 7 años
                "preguntas_evaluacion": 100,
                "tiempo_estimado": "30-45 minutos",
                "recomendaciones": 50,
                "benchmarking": True,
                "exportar_excel": True,
                "marca_agua": False
            }
        }
        
        return limites.get(nivel, limites[NivelSuscripcion.GRATUITO])
    
    def verificar_permisos_nivel(self, nivel_usuario: NivelSuscripcion, nivel_requerido: NivelSuscripcion) -> bool:
        """
        Verificar si el usuario tiene permisos para una funcionalidad
        """
        niveles_orden = [NivelSuscripcion.GRATUITO, NivelSuscripcion.PRO, NivelSuscripcion.EMPRESARIAL]
        
        try:
            nivel_usuario_idx = niveles_orden.index(nivel_usuario)
            nivel_requerido_idx = niveles_orden.index(nivel_requerido)
            return nivel_usuario_idx >= nivel_requerido_idx
        except ValueError:
            return False
    
    def sincronizar_nivel_organizacion(self, organizacion_id: str) -> bool:
        """
        Sincronizar el nivel de suscripción en la tabla organizaciones
        con el nivel real de la suscripción activa
        """
        try:
            organizacion = self.db.query(Organizacion).filter(
                Organizacion.id == organizacion_id
            ).first()
            
            if not organizacion:
                return False
            
            # Obtener nivel real desde suscripciones
            nivel_real = self.obtener_nivel_suscripcion_activa(organizacion_id)
            
            # Actualizar organización si es necesario
            if organizacion.nivel_suscripcion != nivel_real:
                organizacion.nivel_suscripcion = nivel_real
                
                # Actualizar límites
                limites = self.obtener_limites_nivel(nivel_real)
                organizacion.maximo_usuarios = limites["maximo_usuarios"]
                organizacion.maximo_evaluaciones_por_mes = limites["maximo_evaluaciones_por_mes"]
                organizacion.maximo_dias_retencion_datos = limites["maximo_dias_retencion_datos"]
                
                self.db.commit()
                return True
            
            return True
            
        except Exception:
            self.db.rollback()
            return False


