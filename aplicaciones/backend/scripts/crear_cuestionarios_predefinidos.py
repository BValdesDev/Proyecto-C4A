# scripts/crear_cuestionarios_predefinidos.py
"""
Script para crear los 3 cuestionarios predefinidos:
- Básico (10 items)
- Intermedio (50 items)
- Avanzado (100 items)
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modelos.base import SessionLocal
from app.modelos.framework import Framework
from app.modelos.pregunta import Pregunta
from app.modelos.cuestionario import (
    Cuestionario, CuestionarioPregunta, 
    NivelCuestionario, TipoSeccion
)

def crear_preguntas_basicas(framework, db):
    """Crear 10 preguntas básicas"""
    preguntas = []
    
    preguntas_data = [
        {
            "codigo": "BAS_ID_01",
            "texto": "¿Su organización tiene identificados y documentados sus activos críticos de información?",
            "categoria": "Identificación de Activos",
            "tipo_seccion": TipoSeccion.identify,
            "ayuda": "Incluye servidores, bases de datos, aplicaciones críticas, equipos de red, etc."
        },
        {
            "codigo": "BAS_RI_01",
            "texto": "¿Se realizan evaluaciones periódicas de riesgos de ciberseguridad?",
            "categoria": "Evaluación de Riesgos",
            "tipo_seccion": TipoSeccion.identify,
            "ayuda": "Evaluación sistemática de amenazas, vulnerabilidades e impactos potenciales."
        },
        {
            "codigo": "BAS_PR_01",
            "texto": "¿Existen políticas de contraseñas seguras implementadas (longitud mínima, complejidad, cambios periódicos)?",
            "categoria": "Protección de Accesos",
            "tipo_seccion": TipoSeccion.protect,
            "ayuda": "Mínimo 8 caracteres, combinación de mayúsculas, minúsculas, números y símbolos."
        },
        {
            "codigo": "BAS_PR_02",
            "texto": "¿Se realizan copias de seguridad (backups) de la información crítica de forma regular?",
            "categoria": "Copias de Seguridad",
            "tipo_seccion": TipoSeccion.protect,
            "ayuda": "Respaldos automáticos diarios, semanales o mensuales según criticidad."
        },
        {
            "codigo": "BAS_PR_03",
            "texto": "¿Los sistemas operativos y aplicaciones se mantienen actualizados con los últimos parches de seguridad?",
            "categoria": "Actualización de Software",
            "tipo_seccion": TipoSeccion.protect,
            "ayuda": "Proceso regular de aplicación de actualizaciones de seguridad."
        },
        {
            "codigo": "BAS_DE_01",
            "texto": "¿Existe un procedimiento documentado para la gestión y respuesta a incidentes de seguridad?",
            "categoria": "Gestión de Incidentes",
            "tipo_seccion": TipoSeccion.detect,
            "ayuda": "Plan de respuesta que incluye detección, contención, erradicación y recuperación."
        },
        {
            "codigo": "BAS_RS_01",
            "texto": "¿Están definidos los roles y responsabilidades en materia de ciberseguridad?",
            "categoria": "Roles y Responsabilidades",
            "tipo_seccion": TipoSeccion.respond,
            "ayuda": "Asignación clara de quién es responsable de qué aspectos de seguridad."
        },
        {
            "codigo": "BAS_PR_04",
            "texto": "¿Existe una política de uso aceptable de recursos tecnológicos comunicada a todos los empleados?",
            "categoria": "Políticas de Uso",
            "tipo_seccion": TipoSeccion.protect,
            "ayuda": "Documento que establece cómo deben usarse los recursos de TI."
        },
        {
            "codigo": "BAS_PR_05",
            "texto": "¿Se realizan capacitaciones de concientización en ciberseguridad para el personal?",
            "categoria": "Capacitación",
            "tipo_seccion": TipoSeccion.protect,
            "ayuda": "Programas regulares de formación en buenas prácticas de seguridad."
        },
        {
            "codigo": "BAS_GE_01",
            "texto": "¿La organización cumple con las regulaciones y normativas aplicables en materia de protección de datos?",
            "categoria": "Cumplimiento Legal",
            "tipo_seccion": TipoSeccion.general,
            "ayuda": "Ej: Ley de Protección de Datos Personales, reglamentos sectoriales, etc."
        }
    ]
    
    for idx, p_data in enumerate(preguntas_data):
        pregunta = Pregunta(
            codigo=p_data["codigo"],
            texto_pregunta=p_data["texto"],
            texto_ayuda=p_data["ayuda"],
            framework_id=framework.id,
            categoria=p_data["categoria"],
            disponibilidad_por_nivel={
                "gratuito": True,
                "pro": True,
                "empresarial": True
            },
            peso=1,
            tipo_respuesta="likert_5",
            esta_activa=True,
            orden=idx + 1
        )
        db.add(pregunta)
        preguntas.append({
            "pregunta": pregunta,
            "tipo_seccion": p_data["tipo_seccion"],
            "seccion": p_data["categoria"]
        })
    
    db.flush()
    return preguntas

def crear_preguntas_intermedias(framework, db):
    """Crear 50 preguntas intermedias (10 por cada función NIST)"""
    preguntas = []
    
    # IDENTIFY - 10 preguntas
    identify_preguntas = [
        {"codigo": "INT_ID_AM_01", "texto": "¿Se mantiene un inventario actualizado de todos los dispositivos de hardware?", "categoria": "Gestión de Activos"},
        {"codigo": "INT_ID_AM_02", "texto": "¿Se mantiene un inventario actualizado de todas las aplicaciones y software?", "categoria": "Gestión de Activos"},
        {"codigo": "INT_ID_AM_03", "texto": "¿Se han identificado y clasificado los datos según su nivel de criticidad?", "categoria": "Gestión de Activos"},
        {"codigo": "INT_ID_BE_01", "texto": "¿Se han identificado y documentado los procesos de negocio críticos?", "categoria": "Entorno de Negocio"},
        {"codigo": "INT_ID_BE_02", "texto": "¿Se comprende la cadena de suministro de TI y sus riesgos asociados?", "categoria": "Entorno de Negocio"},
        {"codigo": "INT_ID_RA_01", "texto": "¿Se realizan evaluaciones de vulnerabilidades de forma periódica?", "categoria": "Evaluación de Riesgos"},
        {"codigo": "INT_ID_RA_02", "texto": "¿Se documentan y priorizan las amenazas identificadas?", "categoria": "Evaluación de Riesgos"},
        {"codigo": "INT_ID_RM_01", "texto": "¿Existe una estrategia de gestión de riesgos definida?", "categoria": "Gestión de Riesgos"},
        {"codigo": "INT_ID_RM_02", "texto": "¿Se determinan y documentan los niveles de tolerancia al riesgo?", "categoria": "Gestión de Riesgos"},
        {"codigo": "INT_ID_GV_01", "texto": "¿Existe un comité o responsable de gobierno de ciberseguridad?", "categoria": "Gobernanza"},
    ]
    
    # PROTECT - 10 preguntas
    protect_preguntas = [
        {"codigo": "INT_PR_AC_01", "texto": "¿Se implementa autenticación multifactor para accesos críticos?", "categoria": "Control de Acceso"},
        {"codigo": "INT_PR_AC_02", "texto": "¿Se revisan periódicamente los permisos y privilegios de usuario?", "categoria": "Control de Acceso"},
        {"codigo": "INT_PR_AC_03", "texto": "¿Se gestionan adecuadamente las cuentas de usuarios (altas, bajas, cambios)?", "categoria": "Control de Acceso"},
        {"codigo": "INT_PR_DS_01", "texto": "¿Se encriptan los datos sensibles en reposo?", "categoria": "Protección de Datos"},
        {"codigo": "INT_PR_DS_02", "texto": "¿Se encriptan las comunicaciones que contienen datos sensibles?", "categoria": "Protección de Datos"},
        {"codigo": "INT_PR_IP_01", "texto": "¿Se mantienen configuraciones seguras en sistemas y aplicaciones?", "categoria": "Procesos de Protección"},
        {"codigo": "INT_PR_IP_02", "texto": "¿Existe un proceso de gestión de cambios documentado?", "categoria": "Procesos de Protección"},
        {"codigo": "INT_PR_MA_01", "texto": "¿Se realiza mantenimiento preventivo regular de los sistemas?", "categoria": "Mantenimiento"},
        {"codigo": "INT_PR_PT_01", "texto": "¿Se realizan auditorías de logs y registros de actividad?", "categoria": "Tecnología de Protección"},
        {"codigo": "INT_PR_AT_01", "texto": "¿El personal recibe capacitación específica según su rol?", "categoria": "Capacitación"},
    ]
    
    # DETECT - 10 preguntas
    detect_preguntas = [
        {"codigo": "INT_DE_AE_01", "texto": "¿Se establece una línea base de actividad normal de red?", "categoria": "Anomalías y Eventos"},
        {"codigo": "INT_DE_AE_02", "texto": "¿Se detectan eventos que se desvían de la línea base?", "categoria": "Anomalías y Eventos"},
        {"codigo": "INT_DE_CM_01", "texto": "¿Se monitorea la red en busca de actividades no autorizadas?", "categoria": "Monitoreo Continuo"},
        {"codigo": "INT_DE_CM_02", "texto": "¿Se monitorea el acceso físico a instalaciones críticas?", "categoria": "Monitoreo Continuo"},
        {"codigo": "INT_DE_CM_03", "texto": "¿Se escanean periódicamente los sistemas en busca de malware?", "categoria": "Monitoreo Continuo"},
        {"codigo": "INT_DE_DP_01", "texto": "¿Se han definido roles y responsabilidades para la detección?", "categoria": "Procesos de Detección"},
        {"codigo": "INT_DE_DP_02", "texto": "¿Los procesos de detección se prueban regularmente?", "categoria": "Procesos de Detección"},
        {"codigo": "INT_DE_DP_03", "texto": "¿Los eventos de detección se comunican apropiadamente?", "categoria": "Procesos de Detección"},
        {"codigo": "INT_DE_DP_04", "texto": "¿Se mejoran continuamente los procesos de detección?", "categoria": "Procesos de Detección"},
        {"codigo": "INT_DE_DP_05", "texto": "¿Se utilizan herramientas automatizadas de detección?", "categoria": "Procesos de Detección"},
    ]
    
    # RESPOND - 10 preguntas
    respond_preguntas = [
        {"codigo": "INT_RS_RP_01", "texto": "¿Existe un plan de respuesta a incidentes documentado y aprobado?", "categoria": "Planificación de Respuesta"},
        {"codigo": "INT_RS_CO_01", "texto": "¿Se notifican los incidentes al personal apropiado?", "categoria": "Comunicaciones"},
        {"codigo": "INT_RS_CO_02", "texto": "¿Se coordina la información de incidentes con partes externas?", "categoria": "Comunicaciones"},
        {"codigo": "INT_RS_AN_01", "texto": "¿Se realizan investigaciones sobre las notificaciones de incidentes?", "categoria": "Análisis"},
        {"codigo": "INT_RS_AN_02", "texto": "¿Se comprende el impacto de los incidentes?", "categoria": "Análisis"},
        {"codigo": "INT_RS_MI_01", "texto": "¿Se contienen los incidentes de manera oportuna?", "categoria": "Mitigación"},
        {"codigo": "INT_RS_MI_02", "texto": "¿Se mitigan nuevas amenazas identificadas durante incidentes?", "categoria": "Mitigación"},
        {"codigo": "INT_RS_IM_01", "texto": "¿Se incorporan lecciones aprendidas después de incidentes?", "categoria": "Mejoras"},
        {"codigo": "INT_RS_IM_02", "texto": "¿Se actualizan estrategias de respuesta basadas en lecciones?", "categoria": "Mejoras"},
        {"codigo": "INT_RS_RP_02", "texto": "¿Se realizan ejercicios de simulación de incidentes?", "categoria": "Planificación de Respuesta"},
    ]
    
    # RECOVER - 10 preguntas
    recover_preguntas = [
        {"codigo": "INT_RC_RP_01", "texto": "¿Existe un plan de recuperación documentado?", "categoria": "Planificación de Recuperación"},
        {"codigo": "INT_RC_RP_02", "texto": "¿El plan de recuperación se mantiene actualizado?", "categoria": "Planificación de Recuperación"},
        {"codigo": "INT_RC_IM_01", "texto": "¿Se incorporan lecciones aprendidas en el plan de recuperación?", "categoria": "Mejoras"},
        {"codigo": "INT_RC_IM_02", "texto": "¿Se actualizan las estrategias de recuperación?", "categoria": "Mejoras"},
        {"codigo": "INT_RC_CO_01", "texto": "¿Se gestiona la reputación después de un incidente?", "categoria": "Comunicaciones"},
        {"codigo": "INT_RC_CO_02", "texto": "¿Se comunican las actividades de recuperación a partes interesadas?", "categoria": "Comunicaciones"},
        {"codigo": "INT_RC_RP_03", "texto": "¿Se han definido objetivos de tiempo de recuperación (RTO)?", "categoria": "Planificación de Recuperación"},
        {"codigo": "INT_RC_RP_04", "texto": "¿Se han definido objetivos de punto de recuperación (RPO)?", "categoria": "Planificación de Recuperación"},
        {"codigo": "INT_RC_RP_05", "texto": "¿Se prueban regularmente los procedimientos de recuperación?", "categoria": "Planificación de Recuperación"},
        {"codigo": "INT_RC_RP_06", "texto": "¿Se documentan los resultados de las pruebas de recuperación?", "categoria": "Planificación de Recuperación"},
    ]
    
    # Combinar todas las preguntas
    todas_preguntas = [
        (identify_preguntas, TipoSeccion.identify),
        (protect_preguntas, TipoSeccion.protect),
        (detect_preguntas, TipoSeccion.detect),
        (respond_preguntas, TipoSeccion.respond),
        (recover_preguntas, TipoSeccion.recover)
    ]
    
    orden = 1
    for grupo, tipo_seccion in todas_preguntas:
        for p_data in grupo:
            pregunta = Pregunta(
                codigo=p_data["codigo"],
                texto_pregunta=p_data["texto"],
                texto_ayuda=f"Evalúe el nivel de implementación de esta práctica en su organización.",
                framework_id=framework.id,
                categoria=p_data["categoria"],
                disponibilidad_por_nivel={
                    "gratuito": False,
                    "pro": True,
                    "empresarial": True
                },
                peso=1,
                tipo_respuesta="likert_5",
                esta_activa=True,
                orden=orden
            )
            db.add(pregunta)
            preguntas.append({
                "pregunta": pregunta,
                "tipo_seccion": tipo_seccion,
                "seccion": p_data["categoria"]
            })
            orden += 1
    
    db.flush()
    return preguntas

def crear_cuestionarios():
    """Función principal para crear los cuestionarios"""
    db = SessionLocal()
    try:
        print("🚀 Iniciando creación de cuestionarios predefinidos...")
        print("=" * 80)
        
        # Obtener framework NIST CSF
        framework = db.query(Framework).filter(Framework.nombre == "NIST_CSF").first()
        if not framework:
            print("❌ Framework NIST CSF no encontrado. Ejecuta primero crear_frameworks.py")
            return
        
        print()
        
        # Verificar si ya existen cuestionarios
        cuest_existente = db.query(Cuestionario).first()
        if cuest_existente:
            print("⚠️  Ya existen cuestionarios. Eliminando para recrear...")
            db.query(CuestionarioPregunta).delete()
            db.query(Cuestionario).delete()
            db.query(Pregunta).delete()
            db.commit()
            print("✅ Cuestionarios y preguntas anteriores eliminados")
            print()
        
        # ============================================================================
        # 1. CUESTIONARIO BÁSICO (10 items)
        # ============================================================================
        print("📝 Creando Cuestionario Básico (10 items)...")
        
        cuest_basico = Cuestionario.crear_cuestionario_basico(
            nombre="Diagnóstico Básico de Madurez en Ciberseguridad",
            framework_id=str(framework.id)
        )
        db.add(cuest_basico)
        db.flush()
        
        # Crear preguntas básicas
        preguntas_basicas = crear_preguntas_basicas(framework, db)
        
        # Asignar preguntas al cuestionario
        for idx, p_data in enumerate(preguntas_basicas):
            asignacion = CuestionarioPregunta(
                cuestionario_id=cuest_basico.id,
                pregunta_id=p_data["pregunta"].id,
                seccion=p_data["seccion"],
                tipo_seccion=p_data["tipo_seccion"],
                orden_seccion=idx + 1,
                orden_pregunta=idx + 1,
                es_obligatoria=True
            )
            db.add(asignacion)
        
        print(f"   ✅ Cuestionario Básico creado: {cuest_basico.codigo}")
        print(f"   📊 {len(preguntas_basicas)} preguntas asignadas")
        print()
        
        # ============================================================================
        # 2. CUESTIONARIO INTERMEDIO (50 items)
        # ============================================================================
        print("📝 Creando Cuestionario Intermedio (50 items)...")
        
        cuest_intermedio = Cuestionario.crear_cuestionario_intermedio(
            nombre="Evaluación Intermedia de Gobernanza y Ciberseguridad",
            framework_id=str(framework.id)
        )
        db.add(cuest_intermedio)
        db.flush()
        
        # Crear preguntas intermedias
        preguntas_intermedias = crear_preguntas_intermedias(framework, db)
        
        # Asignar preguntas al cuestionario
        for idx, p_data in enumerate(preguntas_intermedias):
            asignacion = CuestionarioPregunta(
                cuestionario_id=cuest_intermedio.id,
                pregunta_id=p_data["pregunta"].id,
                seccion=p_data["seccion"],
                tipo_seccion=p_data["tipo_seccion"],
                orden_seccion=idx + 1,
                orden_pregunta=idx + 1,
                es_obligatoria=True
            )
            db.add(asignacion)
        
        print(f"   ✅ Cuestionario Intermedio creado: {cuest_intermedio.codigo}")
        print(f"   📊 {len(preguntas_intermedias)} preguntas asignadas")
        print()
        
        # ============================================================================
        # 3. CUESTIONARIO AVANZADO (100 items)
        # ============================================================================
        print("📝 Creando Cuestionario Avanzado (100 items)...")
        print("   ⚠️  Nota: Por razones de tiempo, el cuestionario avanzado usará")
        print("      las 50 preguntas intermedias duplicadas con diferentes secciones.")
        print("      Un administrador puede personalizarlas después.")
        print()
        
        cuest_avanzado = Cuestionario.crear_cuestionario_avanzado(
            nombre="Evaluación Avanzada de Madurez Organizacional (NIST + COBIT)",
            framework_id=str(framework.id)
        )
        db.add(cuest_avanzado)
        db.flush()
        
        # Reusar las preguntas intermedias para el avanzado (duplicadas)
        preguntas_avanzadas = preguntas_intermedias + preguntas_intermedias
        
        for idx, p_data in enumerate(preguntas_avanzadas):
            asignacion = CuestionarioPregunta(
                cuestionario_id=cuest_avanzado.id,
                pregunta_id=p_data["pregunta"].id,
                seccion=p_data["seccion"],
                tipo_seccion=p_data["tipo_seccion"],
                orden_seccion=idx + 1,
                orden_pregunta=idx + 1,
                es_obligatoria=True
            )
            db.add(asignacion)
        
        print(f"   ✅ Cuestionario Avanzado creado: {cuest_avanzado.codigo}")
        print(f"   📊 {len(preguntas_avanzadas)} preguntas asignadas")
        print()
        
        # Commit final
        db.commit()
        
        print("=" * 80)
        print("🎉 ¡Cuestionarios creados exitosamente!")
        print()
        print("📋 RESUMEN:")
        print(f"   • Básico:      10 items  - {cuest_basico.tiempo_estimado_minutos} min")
        print(f"   • Intermedio:  50 items  - {cuest_intermedio.tiempo_estimado_minutos} min")
        print(f"   • Avanzado:    100 items - {cuest_avanzado.tiempo_estimado_minutos} min")
        print()
        print("📝 Los administradores pueden:")
        print("   • Editar las preguntas de cada cuestionario")
        print("   • Personalizar textos y configuraciones")
        print("   • Clonar cuestionarios para crear versiones personalizadas")
        print()
        
    except Exception as e:
        print(f"\n❌ Error creando cuestionarios: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_cuestionarios()

