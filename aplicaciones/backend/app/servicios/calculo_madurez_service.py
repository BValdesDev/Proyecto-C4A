# app/servicios/calculo_madurez_service.py
"""
Servicio para cálculo de madurez y generación de resultados de diagnósticos
"""

from typing import Dict, List, Tuple, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..modelos.evaluacion import Evaluacion
from ..modelos.respuesta import Respuesta
from ..modelos.cuestionario import Cuestionario, CuestionarioPregunta
from ..modelos.pregunta import Pregunta

class CalculoMadurezService:
    """Servicio para calcular niveles de madurez"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calcular_puntuacion_global(self, respuestas: List[Respuesta]) -> float:
        """
        Calcula la puntuación global basada en todas las respuestas.
        
        Returns:
            float: Puntuación de 0 a 100
        """
        if not respuestas:
            return 0.0
        
        puntuacion_total = 0.0
        peso_total = 0
        
        for respuesta in respuestas:
            if respuesta.pregunta:
                # Normalizar valor (0-5) a escala 0-100
                valor_normalizado = (respuesta.valor / 5.0) * 100
                peso = respuesta.pregunta.peso
                
                puntuacion_total += valor_normalizado * peso
                peso_total += peso
        
        if peso_total == 0:
            return 0.0
        
        return round(puntuacion_total / peso_total, 2)
    
    def calcular_puntuaciones_por_seccion(
        self, 
        respuestas: List[Respuesta],
        cuestionario_id: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calcula puntuaciones por sección del cuestionario.
        
        Returns:
            Dict[str, float]: Diccionario con puntuaciones por sección
        """
        if not respuestas:
            return {}
        
        # Agrupar respuestas por sección
        secciones: Dict[str, List[Tuple[int, int]]] = {}  # seccion: [(valor, peso), ...]
        
        for respuesta in respuestas:
            if not respuesta.pregunta:
                continue
            
            # Si hay cuestionario_id, obtener la sección desde la asignación
            if cuestionario_id:
                asignacion = self.db.query(CuestionarioPregunta).filter(
                    CuestionarioPregunta.cuestionario_id == cuestionario_id,
                    CuestionarioPregunta.pregunta_id == respuesta.pregunta_id
                ).first()
                
                seccion = asignacion.seccion if asignacion else respuesta.pregunta.categoria
            else:
                seccion = respuesta.pregunta.categoria
            
            if not seccion:
                seccion = "General"
            
            if seccion not in secciones:
                secciones[seccion] = []
            
            peso = respuesta.pregunta.peso
            secciones[seccion].append((respuesta.valor, peso))
        
        # Calcular puntuación por sección
        puntuaciones = {}
        for seccion, valores_pesos in secciones.items():
            puntuacion_total = 0.0
            peso_total = 0
            
            for valor, peso in valores_pesos:
                valor_normalizado = (valor / 5.0) * 100
                puntuacion_total += valor_normalizado * peso
                peso_total += peso
            
            if peso_total > 0:
                puntuaciones[seccion] = round(puntuacion_total / peso_total, 2)
        
        return puntuaciones
    
    def determinar_nivel_madurez(
        self, 
        puntuacion: float, 
        cuestionario: Cuestionario
    ) -> Dict[str, any]:
        """
        Determina el nivel de madurez según la puntuación y la configuración del cuestionario.
        
        Returns:
            Dict con información del nivel de madurez
        """
        niveles_resultado = cuestionario.niveles_resultado
        
        for rango, datos in niveles_resultado.items():
            min_val, max_val = map(int, rango.split("-"))
            if min_val <= puntuacion <= max_val:
                return {
                    "nombre": datos["nombre"],
                    "descripcion": datos["descripcion"],
                    "color": datos["color"],
                    "rango": rango,
                    "puntuacion": puntuacion
                }
        
        # Valor por defecto si no se encuentra en ningún rango
        return {
            "nombre": "Sin Clasificar",
            "descripcion": "La puntuación no se encuentra en ningún rango definido",
            "color": "#6B7280",
            "rango": "0-0",
            "puntuacion": puntuacion
        }
    
    def generar_recomendaciones(
        self, 
        puntuacion_global: float,
        puntuaciones_secciones: Dict[str, float],
        nivel_madurez: Dict[str, any]
    ) -> List[str]:
        """
        Genera recomendaciones basadas en los resultados del diagnóstico.
        
        Returns:
            List[str]: Lista de recomendaciones
        """
        recomendaciones = []
        
        # Recomendaciones basadas en nivel global
        if puntuacion_global < 20:
            recomendaciones.extend([
                "Iniciar un programa básico de concientización en ciberseguridad para todo el personal",
                "Establecer políticas fundamentales de contraseñas y control de acceso",
                "Implementar un sistema regular de respaldos de información crítica",
                "Designar un responsable de ciberseguridad en la organización",
                "Realizar una evaluación inicial de activos críticos de información"
            ])
        elif puntuacion_global < 40:
            recomendaciones.extend([
                "Documentar formalmente todos los procesos de seguridad implementados",
                "Establecer un programa de capacitación continua en ciberseguridad",
                "Implementar controles de acceso basados en roles (RBAC)",
                "Desarrollar un plan de respuesta a incidentes documentado",
                "Realizar evaluaciones de vulnerabilidades trimestrales"
            ])
        elif puntuacion_global < 60:
            recomendaciones.extend([
                "Implementar un sistema de monitoreo continuo de seguridad",
                "Establecer métricas clave de desempeño (KPIs) de ciberseguridad",
                "Desarrollar un programa formal de gestión de riesgos",
                "Implementar soluciones de detección y prevención de intrusiones (IDS/IPS)",
                "Realizar auditorías de seguridad anuales por terceros"
            ])
        elif puntuacion_global < 80:
            recomendaciones.extend([
                "Implementar un programa de mejora continua basado en métricas",
                "Establecer un centro de operaciones de seguridad (SOC) o servicio gestionado",
                "Realizar ejercicios de simulación de incidentes (red team/blue team)",
                "Implementar inteligencia de amenazas (threat intelligence)",
                "Obtener certificaciones de seguridad relevantes (ISO 27001, etc.)"
            ])
        else:
            recomendaciones.extend([
                "Mantener y optimizar el programa de mejora continua existente",
                "Participar en comunidades de seguridad y compartir mejores prácticas",
                "Implementar tecnologías emergentes de seguridad (IA, ML)",
                "Establecer un programa de bug bounty o pruebas de penetración continuas",
                "Considerar liderar iniciativas de seguridad en su industria"
            ])
        
        # Recomendaciones basadas en secciones débiles
        if puntuaciones_secciones:
            secciones_debiles = {
                seccion: puntuacion 
                for seccion, puntuacion in puntuaciones_secciones.items() 
                if puntuacion < 50
            }
            
            for seccion, puntuacion in sorted(secciones_debiles.items(), key=lambda x: x[1])[:3]:
                recomendaciones.append(
                    f"Priorizar mejoras en la sección '{seccion}' (puntuación actual: {puntuacion:.1f}%)"
                )
        
        return recomendaciones[:8]  # Máximo 8 recomendaciones
    
    def calcular_distribucion_respuestas(self, respuestas: List[Respuesta]) -> Dict[int, int]:
        """
        Calcula la distribución de respuestas por nivel.
        
        Returns:
            Dict[int, int]: Diccionario con cantidad de respuestas por nivel (1-5)
        """
        distribucion = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for respuesta in respuestas:
            if 1 <= respuesta.valor <= 5:
                distribucion[respuesta.valor] += 1
        
        return distribucion
    
    def calcular_calidad_respuestas(self, respuestas: List[Respuesta]) -> Dict[str, any]:
        """
        Evalúa la calidad de las respuestas (evidencias, comentarios, etc.)
        
        Returns:
            Dict con métricas de calidad
        """
        total = len(respuestas)
        if total == 0:
            return {
                "porcentaje_con_evidencia": 0,
                "porcentaje_con_comentarios": 0,
                "confianza_promedio": 0,
                "calidad_general": 0
            }
        
        con_evidencia = sum(1 for r in respuestas if r.texto_evidencia and r.texto_evidencia.strip())
        con_comentarios = sum(1 for r in respuestas if r.comentarios and r.comentarios.strip())

        respuestas_con_confianza = [
            r.id for r in respuestas if r.nivel_confianza is not None
        ]
        confianza_promedio = 0.0
        if respuestas_con_confianza:
            confianza_promedio = self.db.query(
                func.avg(Respuesta.nivel_confianza)
            ).filter(
                Respuesta.id.in_(respuestas_con_confianza)
            ).scalar() or 0.0
        
        return {
            "porcentaje_con_evidencia": round((con_evidencia / total) * 100, 1),
            "porcentaje_con_comentarios": round((con_comentarios / total) * 100, 1),
            "confianza_promedio": round(confianza_promedio, 1) if respuestas_con_confianza else 0,
            "calidad_general": round(
                ((con_evidencia / total) * 40 + 
                 (con_comentarios / total) * 30 + 
                 ((confianza_promedio / 5) if respuestas_con_confianza else 0) * 30),
                1
            )
        }
    
    def generar_analisis_completo(
        self, 
        evaluacion: Evaluacion,
        cuestionario: Optional[Cuestionario] = None
    ) -> Dict[str, any]:
        """
        Genera un análisis completo de la evaluación.
        
        Returns:
            Dict con análisis completo de la evaluación
        """
        if not evaluacion.respuestas:
            return {
                "error": "No hay respuestas para analizar"
            }
        
        # Si no se proporciona cuestionario, intentar obtenerlo
        if not cuestionario and evaluacion.cuestionario_id:
            cuestionario = self.db.query(Cuestionario).filter(
                Cuestionario.id == evaluacion.cuestionario_id
            ).first()
        
        # Calcular puntuación global
        puntuacion_global = self.calcular_puntuacion_global(evaluacion.respuestas)
        
        # Calcular puntuaciones por sección
        puntuaciones_secciones = self.calcular_puntuaciones_por_seccion(
            evaluacion.respuestas,
            str(cuestionario.id) if cuestionario else None
        )
        
        # Determinar nivel de madurez
        nivel_madurez = self.determinar_nivel_madurez(
            puntuacion_global,
            cuestionario
        ) if cuestionario else {
            "nombre": "No disponible",
            "descripcion": "Cuestionario no encontrado",
            "color": "#6B7280",
            "rango": "0-0",
            "puntuacion": puntuacion_global
        }
        
        # Generar recomendaciones
        recomendaciones = self.generar_recomendaciones(
            puntuacion_global,
            puntuaciones_secciones,
            nivel_madurez
        )
        
        # Calcular distribución de respuestas
        distribucion = self.calcular_distribucion_respuestas(evaluacion.respuestas)
        
        # Evaluar calidad de respuestas
        calidad = self.calcular_calidad_respuestas(evaluacion.respuestas)
        
        return {
            "evaluacion_id": str(evaluacion.id),
            "cuestionario_id": str(cuestionario.id) if cuestionario else None,
            "cuestionario_nombre": cuestionario.nombre if cuestionario else None,
            "total_preguntas": evaluacion.total_preguntas,
            "preguntas_completadas": len(evaluacion.respuestas),
            "puntuacion_global": puntuacion_global,
            "nivel_madurez": nivel_madurez,
            "puntuaciones_por_seccion": puntuaciones_secciones,
            "distribucion_respuestas": distribucion,
            "calidad_respuestas": calidad,
            "recomendaciones": recomendaciones,
            "fecha_analisis": evaluacion.fecha_completada or evaluacion.fecha_actualizacion
        }
    
    def comparar_evaluaciones(
        self,
        evaluacion_actual: Evaluacion,
        evaluacion_anterior: Evaluacion
    ) -> Dict[str, any]:
        """
        Compara dos evaluaciones para mostrar evolución.
        
        Returns:
            Dict con análisis comparativo
        """
        analisis_actual = self.generar_analisis_completo(evaluacion_actual)
        analisis_anterior = self.generar_analisis_completo(evaluacion_anterior)
        
        diferencia_puntuacion = (
            analisis_actual["puntuacion_global"] - 
            analisis_anterior["puntuacion_global"]
        )
        
        mejoras = []
        retrocesos = []
        
        # Comparar secciones
        for seccion, puntuacion_actual in analisis_actual["puntuaciones_por_seccion"].items():
            puntuacion_anterior = analisis_anterior["puntuaciones_por_seccion"].get(seccion, 0)
            diferencia = puntuacion_actual - puntuacion_anterior
            
            if diferencia > 5:  # Mejora significativa
                mejoras.append({
                    "seccion": seccion,
                    "diferencia": round(diferencia, 1),
                    "anterior": round(puntuacion_anterior, 1),
                    "actual": round(puntuacion_actual, 1)
                })
            elif diferencia < -5:  # Retroceso significativo
                retrocesos.append({
                    "seccion": seccion,
                    "diferencia": round(diferencia, 1),
                    "anterior": round(puntuacion_anterior, 1),
                    "actual": round(puntuacion_actual, 1)
                })
        
        return {
            "evaluacion_actual_id": str(evaluacion_actual.id),
            "evaluacion_anterior_id": str(evaluacion_anterior.id),
            "diferencia_puntuacion_global": round(diferencia_puntuacion, 2),
            "porcentaje_cambio": round((diferencia_puntuacion / analisis_anterior["puntuacion_global"]) * 100, 1) if analisis_anterior["puntuacion_global"] > 0 else 0,
            "mejoras_significativas": sorted(mejoras, key=lambda x: x["diferencia"], reverse=True),
            "retrocesos_significativos": sorted(retrocesos, key=lambda x: x["diferencia"]),
            "nivel_anterior": analisis_anterior["nivel_madurez"]["nombre"],
            "nivel_actual": analisis_actual["nivel_madurez"]["nombre"],
            "ha_mejorado_nivel": (
                self._nivel_a_numero(analisis_actual["nivel_madurez"]["nombre"]) >
                self._nivel_a_numero(analisis_anterior["nivel_madurez"]["nombre"])
            )
        }
    
    def _nivel_a_numero(self, nivel: str) -> int:
        """Convierte nombre de nivel a número para comparación"""
        niveles = {
            "Inicial": 1,
            "Repetible": 2,
            "Definido": 3,
            "Gestionado": 4,
            "Optimizado": 5
        }
        return niveles.get(nivel, 0)
    
    def obtener_areas_criticas(
        self, 
        respuestas: List[Respuesta],
        umbral: int = 2
    ) -> List[Dict[str, any]]:
        """
        Identifica áreas críticas (respuestas con valor <= umbral).
        
        Returns:
            List con áreas críticas y sus detalles
        """
        areas_criticas = []
        
        for respuesta in respuestas:
            if respuesta.valor <= umbral and respuesta.pregunta:
                areas_criticas.append({
                    "pregunta_codigo": respuesta.pregunta.codigo,
                    "pregunta_texto": respuesta.pregunta.texto_pregunta,
                    "categoria": respuesta.pregunta.categoria,
                    "valor": respuesta.valor,
                    "texto_valor": respuesta.pregunta.obtener_texto_respuesta(respuesta.valor),
                    "peso": respuesta.pregunta.peso,
                    "prioridad": "Alta" if respuesta.pregunta.peso >= 3 else "Media"
                })
        
        # Ordenar por peso (mayor peso = mayor prioridad)
        areas_criticas.sort(key=lambda x: x["peso"], reverse=True)
        
        return areas_criticas
    
    def obtener_fortalezas(
        self, 
        respuestas: List[Respuesta],
        umbral: int = 4
    ) -> List[Dict[str, any]]:
        """
        Identifica fortalezas (respuestas con valor >= umbral).
        
        Returns:
            List con fortalezas y sus detalles
        """
        fortalezas = []
        
        for respuesta in respuestas:
            if respuesta.valor >= umbral and respuesta.pregunta:
                fortalezas.append({
                    "pregunta_codigo": respuesta.pregunta.codigo,
                    "pregunta_texto": respuesta.pregunta.texto_pregunta,
                    "categoria": respuesta.pregunta.categoria,
                    "valor": respuesta.valor,
                    "texto_valor": respuesta.pregunta.obtener_texto_respuesta(respuesta.valor)
                })
        
        return fortalezas
    
    def generar_resumen_ejecutivo(
        self, 
        evaluacion: Evaluacion,
        cuestionario: Optional[Cuestionario] = None
    ) -> str:
        """
        Genera un resumen ejecutivo del diagnóstico en formato texto.
        
        Returns:
            str: Resumen ejecutivo
        """
        analisis = self.generar_analisis_completo(evaluacion, cuestionario)
        
        resumen = f"""
RESUMEN EJECUTIVO - DIAGNÓSTICO DE MADUREZ EN CIBERSEGURIDAD

Evaluación: {analisis.get('cuestionario_nombre', 'Diagnóstico')}
Fecha: {analisis['fecha_analisis']}

RESULTADO GENERAL:
- Puntuación Global: {analisis['puntuacion_global']:.1f}%
- Nivel de Madurez: {analisis['nivel_madurez']['nombre']}
- {analisis['nivel_madurez']['descripcion']}

DETALLES:
- Total de preguntas evaluadas: {analisis['preguntas_completadas']}
- Calidad de respuestas: {analisis['calidad_respuestas']['calidad_general']:.1f}%
- Respuestas con evidencia: {analisis['calidad_respuestas']['porcentaje_con_evidencia']:.1f}%

PRINCIPALES RECOMENDACIONES:
"""
        
        for idx, rec in enumerate(analisis['recomendaciones'][:5], 1):
            resumen += f"\n{idx}. {rec}"
        
        return resumen.strip()

