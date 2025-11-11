#!/usr/bin/env python3
"""
Servicio de generación de reportes de ciberseguridad
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.modelos.evaluacion import Evaluacion
from app.modelos.respuesta import Respuesta
from app.modelos.pregunta import Pregunta
from app.modelos.organizacion import Organizacion
import json

class ReporteCiberseguridadService:
    """Servicio para generar reportes de ciberseguridad"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generar_reporte_evaluacion(self, evaluacion_id: str) -> Dict[str, Any]:
        """
        Generar reporte completo de evaluación de ciberseguridad
        
        Args:
            evaluacion_id: ID de la evaluación
            
        Returns:
            Diccionario con el reporte completo
        """
        # Obtener evaluación
        evaluacion = self.db.query(Evaluacion).filter(
            Evaluacion.id == evaluacion_id,
            Evaluacion.fecha_eliminacion.is_(None)
        ).first()
        
        if not evaluacion:
            raise ValueError("Evaluación no encontrada")
        
        # Obtener respuestas
        respuestas = self.db.query(Respuesta).filter(
            Respuesta.evaluacion_id == evaluacion_id
        ).all()
        
        if not respuestas:
            raise ValueError("No se encontraron respuestas para esta evaluación")
        
        # Obtener preguntas
        pregunta_ids = [r.pregunta_id for r in respuestas]
        preguntas = self.db.query(Pregunta).filter(
            Pregunta.id.in_(pregunta_ids)
        ).all()
        
        # Crear diccionario de preguntas para acceso rápido
        preguntas_dict = {p.id: p for p in preguntas}
        
        # Calcular métricas
        metricas = self._calcular_metricas(respuestas, preguntas_dict)
        
        # Generar análisis por categoría
        analisis_categorias = self._analizar_por_categoria(respuestas, preguntas_dict)
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(respuestas, preguntas_dict, metricas)
        
        # Generar plan de acción
        plan_accion = self._generar_plan_accion(recomendaciones, evaluacion.nivel_usado)
        
        # Crear reporte
        reporte = {
            "evaluacion": {
                "id": str(evaluacion.id),
                "nombre": evaluacion.nombre,
                "fecha_creacion": evaluacion.fecha_creacion.isoformat(),
                "fecha_completada": evaluacion.fecha_completada.isoformat() if evaluacion.fecha_completada else None,
                "nivel_usado": evaluacion.nivel_usado.value,
                "framework": evaluacion.framework.nombre_mostrar
            },
            "organizacion": {
                "nombre": evaluacion.organizacion.nombre,
                "nivel_suscripcion": evaluacion.organizacion.nivel_suscripcion.value
            },
            "metricas": metricas,
            "analisis_categorias": analisis_categorias,
            "recomendaciones": recomendaciones,
            "plan_accion": plan_accion,
            "fecha_generacion": datetime.now().isoformat()
        }
        
        return reporte
    
    def _calcular_metricas(self, respuestas: List[Respuesta], preguntas_dict: Dict) -> Dict[str, Any]:
        """Calcular métricas generales de la evaluación"""
        
        total_respuestas = len(respuestas)
        valores_respuestas = [r.valor for r in respuestas]
        
        # Métricas básicas
        puntuacion_total = sum(valores_respuestas)
        puntuacion_maxima = total_respuestas * 5
        puntuacion_promedio = puntuacion_total / total_respuestas if total_respuestas > 0 else 0
        porcentaje_logrado = (puntuacion_total / puntuacion_maxima) * 100 if puntuacion_maxima > 0 else 0
        
        # Distribución de respuestas
        distribucion = {
            "0": valores_respuestas.count(0),
            "1": valores_respuestas.count(1),
            "2": valores_respuestas.count(2),
            "3": valores_respuestas.count(3),
            "4": valores_respuestas.count(4),
            "5": valores_respuestas.count(5)
        }
        
        # Nivel de madurez
        nivel_madurez = self._determinar_nivel_madurez(porcentaje_logrado)
        
        return {
            "total_respuestas": total_respuestas,
            "puntuacion_total": puntuacion_total,
            "puntuacion_maxima": puntuacion_maxima,
            "puntuacion_promedio": round(puntuacion_promedio, 2),
            "porcentaje_logrado": round(porcentaje_logrado, 1),
            "nivel_madurez": nivel_madurez,
            "distribucion_respuestas": distribucion
        }
    
    def _analizar_por_categoria(self, respuestas: List[Respuesta], preguntas_dict: Dict) -> Dict[str, Any]:
        """Analizar resultados por categoría de ciberseguridad"""
        
        categorias = {}
        
        for respuesta in respuestas:
            pregunta = preguntas_dict.get(respuesta.pregunta_id)
            if not pregunta:
                continue
            
            categoria = pregunta.categoria or "Sin categoría"
            
            if categoria not in categorias:
                categorias[categoria] = {
                    "preguntas": [],
                    "puntuacion_total": 0,
                    "puntuacion_maxima": 0,
                    "porcentaje": 0,
                    "fortalezas": [],
                    "debilidades": []
                }
            
            categorias[categoria]["preguntas"].append({
                "codigo": pregunta.codigo,
                "texto": pregunta.texto_pregunta,
                "respuesta": respuesta.valor,
                "evidencia": respuesta.texto_evidencia,
                "comentarios": respuesta.comentarios
            })
            
            categorias[categoria]["puntuacion_total"] += respuesta.valor
            categorias[categoria]["puntuacion_maxima"] += 5
        
        # Calcular porcentajes y identificar fortalezas/debilidades
        for categoria, datos in categorias.items():
            if datos["puntuacion_maxima"] > 0:
                datos["porcentaje"] = round((datos["puntuacion_total"] / datos["puntuacion_maxima"]) * 100, 1)
            
            # Identificar fortalezas (respuestas 4-5)
            fortalezas = [p for p in datos["preguntas"] if p["respuesta"] >= 4]
            datos["fortalezas"] = fortalezas
            
            # Identificar debilidades (respuestas 0-2)
            debilidades = [p for p in datos["preguntas"] if p["respuesta"] <= 2]
            datos["debilidades"] = debilidades
        
        return categorias
    
    def _generar_recomendaciones(self, respuestas: List[Respuesta], preguntas_dict: Dict, metricas: Dict) -> List[Dict[str, Any]]:
        """Generar recomendaciones específicas basadas en las respuestas"""
        
        recomendaciones = []
        
        # Analizar cada respuesta
        for respuesta in respuestas:
            pregunta = preguntas_dict.get(respuesta.pregunta_id)
            if not pregunta:
                continue
            
            # Generar recomendación basada en la respuesta
            if respuesta.valor <= 2:
                recomendacion = self._crear_recomendacion_critica(pregunta, respuesta)
                recomendaciones.append(recomendacion)
            elif respuesta.valor == 3:
                recomendacion = self._crear_recomendacion_mejora(pregunta, respuesta)
                recomendaciones.append(recomendacion)
        
        # Agregar recomendaciones generales basadas en métricas
        recomendaciones_generales = self._generar_recomendaciones_generales(metricas)
        recomendaciones.extend(recomendaciones_generales)
        
        # Ordenar por prioridad
        recomendaciones.sort(key=lambda x: x["prioridad"], reverse=True)
        
        return recomendaciones[:10]  # Top 10 recomendaciones
    
    def _crear_recomendacion_critica(self, pregunta: Pregunta, respuesta: Respuesta) -> Dict[str, Any]:
        """Crear recomendación crítica para respuesta baja"""
        
        recomendaciones_por_categoria = {
            "Gobernanza": {
                "accion": "Implementar política formal de seguridad de la información",
                "beneficio": "Establecer marco de trabajo para la gestión de riesgos de ciberseguridad",
                "tiempo_estimado": "2-4 semanas",
                "costo": "Bajo",
                "prioridad": 9
            },
            "Proteger": {
                "accion": "Implementar controles de protección básicos",
                "beneficio": "Reducir significativamente la superficie de ataque",
                "tiempo_estimado": "1-3 meses",
                "costo": "Medio",
                "prioridad": 8
            },
            "Identificar": {
                "accion": "Realizar inventario completo de activos y capacitación",
                "beneficio": "Mejorar la visibilidad y conciencia de seguridad",
                "tiempo_estimado": "1-2 meses",
                "costo": "Bajo",
                "prioridad": 7
            },
            "Detectar": {
                "accion": "Implementar sistemas de monitoreo y detección",
                "beneficio": "Detección temprana de amenazas y incidentes",
                "tiempo_estimado": "2-6 meses",
                "costo": "Alto",
                "prioridad": 8
            },
            "Responder": {
                "accion": "Desarrollar plan de respuesta a incidentes",
                "beneficio": "Minimizar el impacto de incidentes de seguridad",
                "tiempo_estimado": "1-2 meses",
                "costo": "Medio",
                "prioridad": 8
            },
            "Recuperar": {
                "accion": "Implementar estrategia de continuidad del negocio",
                "beneficio": "Asegurar la recuperación rápida ante incidentes",
                "tiempo_estimado": "2-4 meses",
                "costo": "Alto",
                "prioridad": 7
            }
        }
        
        categoria = pregunta.categoria or "Gobernanza"
        template = recomendaciones_por_categoria.get(categoria, recomendaciones_por_categoria["Gobernanza"])
        
        return {
            "categoria": categoria,
            "pregunta": pregunta.texto_pregunta,
            "codigo": pregunta.codigo,
            "respuesta_actual": respuesta.valor,
            "nivel_criticidad": "CRÍTICO",
            "accion": template["accion"],
            "descripcion": f"Su organización tiene una puntuación baja ({respuesta.valor}/5) en {pregunta.codigo}",
            "beneficio": template["beneficio"],
            "tiempo_estimado": template["tiempo_estimado"],
            "costo": template["costo"],
            "prioridad": template["prioridad"],
            "pasos_concretos": self._generar_pasos_concretos(pregunta.codigo, categoria)
        }
    
    def _crear_recomendacion_mejora(self, pregunta: Pregunta, respuesta: Respuesta) -> Dict[str, Any]:
        """Crear recomendación de mejora para respuesta media"""
        
        return {
            "categoria": pregunta.categoria or "Gobernanza",
            "pregunta": pregunta.texto_pregunta,
            "codigo": pregunta.codigo,
            "respuesta_actual": respuesta.valor,
            "nivel_criticidad": "MEJORA",
            "accion": "Optimizar y fortalecer controles existentes",
            "descripcion": f"Su organización tiene una puntuación media ({respuesta.valor}/5) en {pregunta.codigo}",
            "beneficio": "Mejorar la eficacia de los controles de seguridad existentes",
            "tiempo_estimado": "2-6 semanas",
            "costo": "Bajo",
            "prioridad": 5,
            "pasos_concretos": self._generar_pasos_optimizacion(pregunta.codigo)
        }
    
    def _generar_recomendaciones_generales(self, metricas: Dict) -> List[Dict[str, Any]]:
        """Generar recomendaciones generales basadas en métricas"""
        
        recomendaciones = []
        
        if metricas["porcentaje_logrado"] < 40:
            recomendaciones.append({
                "categoria": "GENERAL",
                "pregunta": "Postura general de ciberseguridad",
                "codigo": "GENERAL_01",
                "respuesta_actual": metricas["puntuacion_promedio"],
                "nivel_criticidad": "CRÍTICO",
                "accion": "Implementar programa integral de ciberseguridad",
                "descripcion": f"Su organización tiene una puntuación general de {metricas['porcentaje_logrado']:.1f}%, indicando la necesidad de mejoras significativas",
                "beneficio": "Establecer una base sólida de seguridad de la información",
                "tiempo_estimado": "6-12 meses",
                "costo": "Alto",
                "prioridad": 10,
                "pasos_concretos": [
                    "Realizar evaluación de riesgos detallada",
                    "Desarrollar política de seguridad integral",
                    "Implementar controles básicos de seguridad",
                    "Capacitar al personal en ciberseguridad",
                    "Establecer programa de auditoría regular"
                ]
            })
        
        return recomendaciones
    
    def _generar_plan_accion(self, recomendaciones: List[Dict], nivel_usado) -> Dict[str, Any]:
        """Generar plan de acción basado en las recomendaciones"""
        
        # Agrupar por prioridad
        criticas = [r for r in recomendaciones if r["prioridad"] >= 8]
        importantes = [r for r in recomendaciones if 5 <= r["prioridad"] < 8]
        mejoras = [r for r in recomendaciones if r["prioridad"] < 5]
        
        # Generar cronograma
        cronograma = self._generar_cronograma(recomendaciones, nivel_usado)
        
        return {
            "resumen": {
                "total_recomendaciones": len(recomendaciones),
                "criticas": len(criticas),
                "importantes": len(importantes),
                "mejoras": len(mejoras)
            },
            "prioridades": {
                "criticas": criticas[:3],  # Top 3 críticas
                "importantes": importantes[:3],  # Top 3 importantes
                "mejoras": mejoras[:3]  # Top 3 mejoras
            },
            "cronograma": cronograma,
            "inversion_estimada": self._calcular_inversion_estimada(recomendaciones),
            "roi_proyectado": self._calcular_roi_proyectado(recomendaciones)
        }
    
    def _generar_cronograma(self, recomendaciones: List[Dict], nivel_usado) -> List[Dict]:
        """Generar cronograma de implementación"""
        
        cronograma = [
            {
                "fase": "Fase 1 - Crítico (0-3 meses)",
                "descripcion": "Implementar controles críticos para reducir riesgos inmediatos",
                "recomendaciones": [r for r in recomendaciones if r["prioridad"] >= 8],
                "inversion": "Alta prioridad, bajo costo inicial"
            },
            {
                "fase": "Fase 2 - Importante (3-6 meses)",
                "descripcion": "Desarrollar capacidades de seguridad fundamentales",
                "recomendaciones": [r for r in recomendaciones if 5 <= r["prioridad"] < 8],
                "inversion": "Inversión media, beneficios significativos"
            },
            {
                "fase": "Fase 3 - Optimización (6-12 meses)",
                "descripcion": "Mejorar y optimizar controles existentes",
                "recomendaciones": [r for r in recomendaciones if r["prioridad"] < 5],
                "inversion": "Inversión baja, optimización continua"
            }
        ]
        
        return cronograma
    
    def _generar_pasos_concretos(self, codigo: str, categoria: str) -> List[str]:
        """Generar pasos concretos basados en el código de pregunta"""
        
        pasos_por_codigo = {
            "PRUEBA_01": [
                "Documentar política actual de seguridad",
                "Revisar y actualizar políticas existentes",
                "Aprobar política por la alta dirección",
                "Comunicar política a todos los empleados",
                "Establecer proceso de revisión anual"
            ],
            "PRUEBA_02": [
                "Realizar inventario de datos críticos",
                "Implementar solución de backup automatizada",
                "Establecer procedimientos de backup diario",
                "Probar restauración de datos regularmente",
                "Almacenar backups en ubicación segura"
            ],
            "PRUEBA_03": [
                "Desarrollar programa de capacitación en ciberseguridad",
                "Realizar sesiones de capacitación mensuales",
                "Implementar simulacros de phishing",
                "Establecer métricas de conciencia de seguridad",
                "Crear materiales de capacitación personalizados"
            ],
            "PRUEBA_04": [
                "Formar equipo de respuesta a incidentes",
                "Desarrollar procedimientos de respuesta",
                "Establecer canales de comunicación",
                "Realizar ejercicios de respuesta",
                "Crear plantillas de reporte de incidentes"
            ],
            "PRUEBA_05": [
                "Implementar sistema de gestión de parches",
                "Establecer ventanas de mantenimiento",
                "Automatizar actualizaciones críticas",
                "Monitorear vulnerabilidades conocidas",
                "Mantener inventario actualizado de software"
            ]
        }
        
        return pasos_por_codigo.get(codigo, [
            "Evaluar situación actual",
            "Definir objetivos de mejora",
            "Implementar controles básicos",
            "Monitorear efectividad",
            "Realizar mejoras continuas"
        ])
    
    def _generar_pasos_optimizacion(self, codigo: str) -> List[str]:
        """Generar pasos de optimización para respuestas medias"""
        
        return [
            "Auditar implementación actual",
            "Identificar áreas de mejora",
            "Optimizar procesos existentes",
            "Implementar mejores prácticas",
            "Establecer métricas de rendimiento"
        ]
    
    def _determinar_nivel_madurez(self, porcentaje: float) -> str:
        """Determinar nivel de madurez basado en porcentaje"""
        
        if porcentaje >= 80:
            return "AVANZADO"
        elif porcentaje >= 60:
            return "INTERMEDIO"
        elif porcentaje >= 40:
            return "BÁSICO"
        else:
            return "INICIAL"
    
    def _calcular_inversion_estimada(self, recomendaciones: List[Dict]) -> Dict[str, Any]:
        """Calcular inversión estimada"""
        
        costo_total = 0
        distribucion = {"Bajo": 0, "Medio": 0, "Alto": 0}
        
        for rec in recomendaciones:
            if rec["costo"] == "Bajo":
                costo_total += 50000  # $50,000 CLP
                distribucion["Bajo"] += 1
            elif rec["costo"] == "Medio":
                costo_total += 200000  # $200,000 CLP
                distribucion["Medio"] += 1
            else:  # Alto
                costo_total += 500000  # $500,000 CLP
                distribucion["Alto"] += 1
        
        return {
            "total_clp": costo_total,
            "total_usd": round(costo_total / 950, 0),  # Aprox 950 CLP = 1 USD
            "distribucion": distribucion,
            "periodo": "12 meses"
        }
    
    def _calcular_roi_proyectado(self, recomendaciones: List[Dict]) -> Dict[str, Any]:
        """Calcular ROI proyectado"""
        
        # Costo promedio de incidente de ciberseguridad en Chile
        costo_incidente_promedio = 50000000  # $50,000,000 CLP
        
        # Reducción de riesgo estimada
        reduccion_riesgo = min(len(recomendaciones) * 5, 70)  # Máximo 70% de reducción
        
        # Beneficio anual proyectado
        beneficio_anual = costo_incidente_promedio * (reduccion_riesgo / 100)
        
        # Inversión total
        inversion_total = sum([
            50000 if r["costo"] == "Bajo" else 200000 if r["costo"] == "Medio" else 500000
            for r in recomendaciones
        ])
        
        # ROI
        roi = ((beneficio_anual - inversion_total) / inversion_total) * 100 if inversion_total > 0 else 0
        
        return {
            "reduccion_riesgo": reduccion_riesgo,
            "beneficio_anual_clp": beneficio_anual,
            "inversion_total_clp": inversion_total,
            "roi_porcentaje": round(roi, 1),
            "periodo_recuperacion": round(inversion_total / (beneficio_anual / 12), 1) if beneficio_anual > 0 else 0
        }

