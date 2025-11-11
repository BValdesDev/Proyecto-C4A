# app/modelos/cuestionario.py
"""
Modelo de Cuestionario/Diagnóstico para C4A SaaS
Gestión de cuestionarios predefinidos (Básico, Intermedio, Avanzado)
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from .base import ModeloConEliminacionLogica, ModeloConUUID
from ..core.config import NivelSuscripcion

class NivelCuestionario(str, enum.Enum):
    """Niveles de cuestionario"""
    basico = "basico"  # 10 ítems - Introductorio
    intermedio = "intermedio"  # 50 ítems - Departamentos TI
    avanzado = "avanzado"  # 100 ítems - Diagnóstico completo

class TipoSeccion(str, enum.Enum):
    """Tipos de sección según framework"""
    # NIST CSF
    identify = "identify"
    protect = "protect"
    detect = "detect"
    respond = "respond"
    recover = "recover"
    
    # COBIT 2019
    gobernanza = "gobernanza"
    gestion = "gestion"
    
    # Adicionales
    cultura = "cultura"
    grc = "grc"
    general = "general"

class Cuestionario(ModeloConEliminacionLogica):
    """Modelo de cuestionario de diagnóstico"""
    __tablename__ = "cuestionarios"
    
    # Información básica
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)  # "DIAG_BASICO_V1"
    descripcion = Column(Text, nullable=True)
    
    # Nivel y tipo
    nivel = Column(Enum(NivelCuestionario), nullable=False)
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.id"), nullable=False)
    
    # Configuración
    total_items = Column(Integer, nullable=False)  # 10, 50 o 100
    tiempo_estimado_minutos = Column(Integer, nullable=False)
    
    # Diseño y formato
    configuracion_formato = Column(JSONB, nullable=False, default={
        "color_institucional": "#1E3A8A",  # Azul marino
        "color_secundario": "#6B7280",  # Gris
        "tipografia": "Roboto",
        "incluir_logo": True,
        "incluir_portada": True,
        "incluir_instrucciones": True
    })
    
    # Instrucciones
    texto_instrucciones = Column(Text, nullable=True)
    
    # Escala de madurez
    escala_madurez = Column(JSONB, nullable=False, default={
        "1": "No implementado",
        "2": "Parcialmente implementado",
        "3": "En desarrollo",
        "4": "Implementado",
        "5": "Optimizado/Mejorado continuamente"
    })
    
    # Niveles de resultado
    niveles_resultado = Column(JSONB, nullable=False, default={
        "0-20": {"nombre": "Inicial", "descripcion": "Prácticas básicas no implementadas", "color": "#EF4444"},
        "21-40": {"nombre": "Repetible", "descripcion": "Procesos básicos en marcha", "color": "#F59E0B"},
        "41-60": {"nombre": "Definido", "descripcion": "Procesos documentados y seguidos", "color": "#EAB308"},
        "61-80": {"nombre": "Gestionado", "descripcion": "Procesos medidos y controlados", "color": "#3B82F6"},
        "81-100": {"nombre": "Optimizado", "descripcion": "Mejora continua activa", "color": "#10B981"}
    })
    
    # Estructura de secciones
    estructura_secciones = Column(JSONB, nullable=False)
    # Ejemplo para básico:
    # [
    #   {"nombre": "Identificación de Activos", "tipo": "identify", "items": 2},
    #   {"nombre": "Evaluación de Riesgos", "tipo": "protect", "items": 2},
    #   ...
    # ]
    
    # Estado
    esta_activo = Column(Boolean, default=True, nullable=False)
    es_editable_por_admin = Column(Boolean, default=True, nullable=False)
    es_plantilla = Column(Boolean, default=False, nullable=False)
    
    # Versión
    version = Column(String(20), default="1.0", nullable=False)
    
    # Relaciones
    framework = relationship("Framework", back_populates="cuestionarios")
    preguntas_asignadas = relationship("CuestionarioPregunta", back_populates="cuestionario", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="cuestionario")
    
    def __repr__(self):
        return f"<Cuestionario(id={self.id}, codigo='{self.codigo}', nivel='{self.nivel}', items={self.total_items})>"
    
    def obtener_nivel_madurez(self, puntuacion: float) -> dict:
        """Obtener nivel de madurez según puntuación"""
        for rango, datos in self.niveles_resultado.items():
            min_val, max_val = map(int, rango.split("-"))
            if min_val <= puntuacion <= max_val:
                return {
                    "rango": rango,
                    "nombre": datos["nombre"],
                    "descripcion": datos["descripcion"],
                    "color": datos["color"],
                    "puntuacion": puntuacion
                }
        
        return {
            "rango": "0-20",
            "nombre": "Inicial",
            "descripcion": "Evaluación incompleta",
            "color": "#6B7280",
            "puntuacion": puntuacion
        }
    
    def obtener_preguntas_ordenadas(self):
        """Obtener preguntas ordenadas por sección y orden"""
        return sorted(
            self.preguntas_asignadas,
            key=lambda x: (x.orden_seccion, x.orden_pregunta)
        )
    
    def obtener_estadisticas(self) -> dict:
        """Obtener estadísticas del cuestionario"""
        return {
            "nombre": self.nombre,
            "codigo": self.codigo,
            "nivel": self.nivel.value,
            "total_items": self.total_items,
            "tiempo_estimado": self.tiempo_estimado_minutos,
            "total_evaluaciones": len(self.evaluaciones) if self.evaluaciones else 0,
            "esta_activo": self.esta_activo,
            "version": self.version
        }
    
    def validar_estructura(self) -> dict:
        """Validar que la estructura del cuestionario es correcta"""
        errores = []
        advertencias = []
        
        # Validar total de items
        items_secciones = sum(seccion.get("items", 0) for seccion in self.estructura_secciones)
        if items_secciones != self.total_items:
            errores.append(f"Total de items en secciones ({items_secciones}) no coincide con total_items ({self.total_items})")
        
        # Validar que hay preguntas asignadas
        if not self.preguntas_asignadas:
            errores.append("No hay preguntas asignadas al cuestionario")
        elif len(self.preguntas_asignadas) != self.total_items:
            advertencias.append(f"Preguntas asignadas ({len(self.preguntas_asignadas)}) no coincide con total_items ({self.total_items})")
        
        # Validar niveles de resultado
        if not self.niveles_resultado or len(self.niveles_resultado) == 0:
            errores.append("No hay niveles de resultado definidos")
        
        return {
            "es_valido": len(errores) == 0,
            "errores": errores,
            "advertencias": advertencias
        }
    
    def clonar_cuestionario(self, nuevo_nombre: str, nuevo_codigo: str):
        """Clonar cuestionario para crear una versión personalizada"""
        nuevo_cuestionario = Cuestionario(
            nombre=nuevo_nombre,
            codigo=nuevo_codigo,
            descripcion=self.descripcion,
            nivel=self.nivel,
            framework_id=self.framework_id,
            total_items=self.total_items,
            tiempo_estimado_minutos=self.tiempo_estimado_minutos,
            configuracion_formato=self.configuracion_formato.copy(),
            texto_instrucciones=self.texto_instrucciones,
            escala_madurez=self.escala_madurez.copy(),
            niveles_resultado=self.niveles_resultado.copy(),
            estructura_secciones=self.estructura_secciones.copy(),
            esta_activo=True,
            es_editable_por_admin=True,
            es_plantilla=False,
            version="1.0"
        )
        
        return nuevo_cuestionario
    
    @classmethod
    def crear_cuestionario_basico(cls, nombre: str, framework_id: str):
        """Crear cuestionario básico (10 ítems)"""
        return cls(
            nombre=nombre,
            codigo=f"DIAG_BASICO_{nombre[:10].upper()}",
            nivel=NivelCuestionario.basico,
            framework_id=framework_id,
            total_items=10,
            tiempo_estimado_minutos=15,
            texto_instrucciones="""
# Instrucciones para el Diagnóstico Básico

Este diagnóstico está diseñado para proporcionar una evaluación rápida del estado de ciberseguridad de su organización.

## Escala de Madurez:
- **1 - No implementado**: La práctica no existe en la organización
- **2 - Parcialmente implementado**: Iniciativas aisladas sin coordinación
- **3 - En desarrollo**: Procesos en implementación activa
- **4 - Implementado**: Práctica establecida y operativa
- **5 - Optimizado**: Mejora continua y medición regular

## Tiempo estimado: 15 minutos

Por favor, responda cada pregunta seleccionando el nivel que mejor describa la situación actual de su organización.
            """,
            estructura_secciones=[
                {"nombre": "Identificación de Activos Críticos", "tipo": TipoSeccion.identify.value, "items": 1},
                {"nombre": "Evaluación de Riesgos Básicos", "tipo": TipoSeccion.identify.value, "items": 1},
                {"nombre": "Protección de Contraseñas y Accesos", "tipo": TipoSeccion.protect.value, "items": 1},
                {"nombre": "Copias de Seguridad", "tipo": TipoSeccion.protect.value, "items": 1},
                {"nombre": "Actualización de Software", "tipo": TipoSeccion.protect.value, "items": 1},
                {"nombre": "Gestión de Incidentes", "tipo": TipoSeccion.detect.value, "items": 1},
                {"nombre": "Roles y Responsabilidades", "tipo": TipoSeccion.respond.value, "items": 1},
                {"nombre": "Políticas de Uso Aceptable", "tipo": TipoSeccion.protect.value, "items": 1},
                {"nombre": "Sensibilización y Capacitación", "tipo": TipoSeccion.protect.value, "items": 1},
                {"nombre": "Cumplimiento Legal Básico", "tipo": TipoSeccion.general.value, "items": 1}
            ]
        )
    
    @classmethod
    def crear_cuestionario_intermedio(cls, nombre: str, framework_id: str):
        """Crear cuestionario intermedio (50 ítems)"""
        return cls(
            nombre=nombre,
            codigo=f"DIAG_INTERMEDIO_{nombre[:10].upper()}",
            nivel=NivelCuestionario.intermedio,
            framework_id=framework_id,
            total_items=50,
            tiempo_estimado_minutos=45,
            texto_instrucciones="""
# Instrucciones para la Evaluación Intermedia

Esta evaluación está basada en las 5 funciones del NIST Cybersecurity Framework e integra conceptos de COBIT 2019.

## Escala de Madurez:
- **1 - No implementado**: La práctica no existe en la organización
- **2 - Parcialmente implementado**: Iniciativas aisladas sin coordinación
- **3 - En desarrollo**: Procesos en implementación activa
- **4 - Implementado**: Práctica establecida y operativa
- **5 - Optimizado**: Mejora continua y medición regular

## Tiempo estimado: 45 minutos

La evaluación está organizada en 5 funciones principales:
- **Identify** (Identificar): Comprender el contexto de riesgos
- **Protect** (Proteger): Implementar salvaguardas
- **Detect** (Detectar): Identificar incidentes de ciberseguridad
- **Respond** (Responder): Actuar ante incidentes detectados
- **Recover** (Recuperar): Restaurar capacidades después de incidentes
            """,
            estructura_secciones=[
                {"nombre": "Identify - Gestión de Activos", "tipo": TipoSeccion.identify.value, "items": 5},
                {"nombre": "Identify - Evaluación de Riesgos", "tipo": TipoSeccion.identify.value, "items": 5},
                {"nombre": "Protect - Control de Acceso", "tipo": TipoSeccion.protect.value, "items": 5},
                {"nombre": "Protect - Protección de Datos", "tipo": TipoSeccion.protect.value, "items": 5},
                {"nombre": "Detect - Monitoreo Continuo", "tipo": TipoSeccion.detect.value, "items": 5},
                {"nombre": "Detect - Análisis de Anomalías", "tipo": TipoSeccion.detect.value, "items": 5},
                {"nombre": "Respond - Planificación de Respuesta", "tipo": TipoSeccion.respond.value, "items": 5},
                {"nombre": "Respond - Comunicaciones", "tipo": TipoSeccion.respond.value, "items": 5},
                {"nombre": "Recover - Planificación de Recuperación", "tipo": TipoSeccion.recover.value, "items": 5},
                {"nombre": "Recover - Mejoras Post-Incidente", "tipo": TipoSeccion.recover.value, "items": 5}
            ]
        )
    
    @classmethod
    def crear_cuestionario_avanzado(cls, nombre: str, framework_id: str):
        """Crear cuestionario avanzado (100 ítems)"""
        return cls(
            nombre=nombre,
            codigo=f"DIAG_AVANZADO_{nombre[:10].upper()}",
            nivel=NivelCuestionario.avanzado,
            framework_id=framework_id,
            total_items=100,
            tiempo_estimado_minutos=90,
            texto_instrucciones="""
# Instrucciones para la Evaluación Avanzada de Madurez Organizacional

Este diagnóstico completo integra las mejores prácticas de NIST CSF y COBIT 2019 para proporcionar una evaluación exhaustiva de la madurez en ciberseguridad y gobernanza de TI.

## Escala de Madurez:
- **1 - No implementado**: La práctica no existe en la organización
- **2 - Parcialmente implementado**: Iniciativas aisladas sin coordinación
- **3 - En desarrollo**: Procesos en implementación activa
- **4 - Implementado**: Práctica establecida y operativa
- **5 - Optimizado**: Mejora continua y medición regular

## Tiempo estimado: 90 minutos

## Estructura de la Evaluación:

### Gobernanza y Gestión (COBIT 2019) - 40 preguntas
- Gobernanza organizacional
- Gestión de recursos y riesgos
- Alineación estratégica

### Funciones NIST CSF - 40 preguntas
- Identify (8 preguntas)
- Protect (8 preguntas)
- Detect (8 preguntas)
- Respond (8 preguntas)
- Recover (8 preguntas)

### Cultura y Mejora Continua - 10 preguntas
- Cultura de seguridad
- Capacitación y concientización

### GRC (Governance, Risk & Compliance) - 10 preguntas
- Cumplimiento normativo
- Gestión de riesgos empresariales
            """,
            estructura_secciones=[
                {"nombre": "Gobernanza - Marco Estratégico", "tipo": TipoSeccion.gobernanza.value, "items": 10},
                {"nombre": "Gobernanza - Gestión de Riesgos", "tipo": TipoSeccion.gobernanza.value, "items": 10},
                {"nombre": "Gestión - Recursos y Capacidades", "tipo": TipoSeccion.gestion.value, "items": 10},
                {"nombre": "Gestión - Evaluación del Desempeño", "tipo": TipoSeccion.gestion.value, "items": 10},
                {"nombre": "NIST - Identify", "tipo": TipoSeccion.identify.value, "items": 8},
                {"nombre": "NIST - Protect", "tipo": TipoSeccion.protect.value, "items": 8},
                {"nombre": "NIST - Detect", "tipo": TipoSeccion.detect.value, "items": 8},
                {"nombre": "NIST - Respond", "tipo": TipoSeccion.respond.value, "items": 8},
                {"nombre": "NIST - Recover", "tipo": TipoSeccion.recover.value, "items": 8},
                {"nombre": "Cultura y Mejora Continua", "tipo": TipoSeccion.cultura.value, "items": 10},
                {"nombre": "GRC - Governance, Risk & Compliance", "tipo": TipoSeccion.grc.value, "items": 10}
            ]
        )

class CuestionarioPregunta(ModeloConUUID):
    """Relación entre cuestionario y preguntas con orden"""
    __tablename__ = "cuestionario_preguntas"
    
    # Relaciones
    cuestionario_id = Column(UUID(as_uuid=True), ForeignKey("cuestionarios.id", ondelete="CASCADE"), nullable=False)
    pregunta_id = Column(UUID(as_uuid=True), ForeignKey("preguntas.id", ondelete="CASCADE"), nullable=False)
    
    # Organización
    seccion = Column(String(100), nullable=False)  # Nombre de la sección
    tipo_seccion = Column(Enum(TipoSeccion), nullable=False)
    orden_seccion = Column(Integer, nullable=False)  # Orden de la sección
    orden_pregunta = Column(Integer, nullable=False)  # Orden dentro de la sección
    
    # Configuración específica
    es_obligatoria = Column(Boolean, default=True, nullable=False)
    peso_personalizado = Column(Integer, nullable=True)  # Sobrescribir peso de la pregunta
    
    # Texto personalizado
    texto_pregunta_personalizado = Column(Text, nullable=True)  # Si el admin quiere cambiar el texto
    texto_ayuda_personalizado = Column(Text, nullable=True)
    
    # Relaciones
    cuestionario = relationship("Cuestionario", back_populates="preguntas_asignadas")
    pregunta = relationship("Pregunta")
    
    def __repr__(self):
        return f"<CuestionarioPregunta(cuestionario={self.cuestionario_id}, pregunta={self.pregunta_id}, orden={self.orden_pregunta})>"
    
    @property
    def texto_final(self) -> str:
        """Obtener texto final de la pregunta (personalizado o original)"""
        return self.texto_pregunta_personalizado or self.pregunta.texto_pregunta
    
    @property
    def texto_ayuda_final(self) -> str:
        """Obtener texto de ayuda final"""
        return self.texto_ayuda_personalizado or self.pregunta.texto_ayuda or ""
    
    @property
    def peso_final(self) -> int:
        """Obtener peso final de la pregunta"""
        return self.peso_personalizado or self.pregunta.peso

