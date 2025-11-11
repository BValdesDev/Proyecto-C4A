# Implementación del Sistema de Diagnósticos C4A

## Resumen Ejecutivo

Se ha implementado un sistema completo de diagnósticos de ciberseguridad con tres niveles de complejidad (Básico, Intermedio y Avanzado) basados en NIST CSF 2.0 y COBIT 2019.

**Fecha**: 21 de Octubre de 2025  
**Estado**: Backend completado - Frontend pendiente  
**Versión**: 1.0.0

---

## 🎯 Características Principales

### 1. Sistema de Cuestionarios Jerárquicos

✅ **Tres Niveles de Diagnóstico**:
- **Básico**: 10 ítems - 15 minutos (Introductorio / Pequeñas empresas)
- **Intermedio**: 50 ítems - 45 minutos (Departamentos TI / Medianas empresas)
- **Avanzado**: 100 ítems - 90 minutos (Diagnóstico organizacional completo)

✅ **Integración de Frameworks**:
- NIST Cybersecurity Framework 2.0 (5 funciones: Identify, Protect, Detect, Respond, Recover)
- COBIT 2019 (Gobernanza y Gestión)
- GRC (Governance, Risk & Compliance)

✅ **Escala de Madurez Estandarizada**:
1. **No implementado** - La práctica no existe en la organización
2. **Parcialmente implementado** - Iniciativas aisladas sin coordinación
3. **En desarrollo** - Procesos en implementación activa
4. **Implementado** - Práctica establecida y operativa
5. **Optimizado** - Mejora continua y medición regular

### 2. Gestión Administrativa Completa

✅ **Capacidades de Administración**:
- Crear cuestionarios personalizados
- Editar cuestionarios existentes
- Clonar cuestionarios como plantillas
- Asignar y ordenar preguntas
- Personalizar textos e instrucciones
- Configurar formato y diseño
- Definir niveles de resultado

✅ **Control de Acceso**:
- Solo administradores pueden crear/editar cuestionarios
- Cuestionarios activos visibles para todos los usuarios
- Cuestionarios inactivos solo para administradores
- Protección de plantillas del sistema

### 3. Estructura de Datos Robusta

✅ **Modelos de Base de Datos**:
- `Cuestionario`: Definición principal del diagnóstico
- `CuestionarioPregunta`: Relación con preguntas y configuración
- `Pregunta`: Banco de preguntas reutilizables
- `Respuesta`: Respuestas de usuarios a evaluaciones
- `Evaluacion`: Instancias de evaluaciones completadas

---

## 📊 Estructura de los Cuestionarios

### Diagnóstico Básico (10 items)

**Secciones**:
1. Identificación de Activos Críticos
2. Evaluación de Riesgos Básicos
3. Protección de Contraseñas y Accesos
4. Copias de Seguridad
5. Actualización de Software
6. Gestión de Incidentes
7. Roles y Responsabilidades
8. Políticas de Uso Aceptable
9. Sensibilización y Capacitación
10. Cumplimiento Legal Básico

**Resultado**: Nivel de madurez (Inicial, Repetible, Definido, Gestionado, Optimizado)

### Evaluación Intermedia (50 items)

**Estructura NIST CSF - 10 preguntas por función**:

**Identify** (10):
- Gestión de Activos (5)
- Evaluación de Riesgos (5)

**Protect** (10):
- Control de Acceso (5)
- Protección de Datos (5)

**Detect** (10):
- Monitoreo Continuo (5)
- Análisis de Anomalías (5)

**Respond** (10):
- Planificación de Respuesta (5)
- Comunicaciones (5)

**Recover** (10):
- Planificación de Recuperación (5)
- Mejoras Post-Incidente (5)

**Resultado**: Gráfico o tabla de madurez por función y nivel global

### Evaluación Avanzada (100 items)

**Estructura Integrada NIST + COBIT**:

**Gobernanza (COBIT 2019)** - 20 preguntas:
- Marco Estratégico (10)
- Gestión de Riesgos (10)

**Gestión (COBIT 2019)** - 20 preguntas:
- Recursos y Capacidades (10)
- Evaluación del Desempeño (10)

**Funciones NIST CSF** - 40 preguntas:
- Identify (8)
- Protect (8)
- Detect (8)
- Respond (8)
- Recover (8)

**Cultura y Mejora Continua** - 10 preguntas

**GRC (Governance, Risk & Compliance)** - 10 preguntas

**Resultado**: Evaluación exhaustiva con análisis multidimensional

---

## 🔧 Implementación Técnica

### Backend (✅ Completado)

#### 1. Modelos de Datos

**Archivo**: `app/modelos/cuestionario.py`

```python
class Cuestionario(ModeloConEliminacionLogica):
    - nombre: str
    - codigo: str (único)
    - nivel: NivelCuestionario (basico|intermedio|avanzado)
    - framework_id: UUID
    - total_items: int
    - tiempo_estimado_minutos: int
    - configuracion_formato: JSONB
    - texto_instrucciones: Text
    - escala_madurez: JSONB
    - niveles_resultado: JSONB
    - estructura_secciones: JSONB
    - esta_activo: bool
    - es_editable_por_admin: bool
    - version: str

class CuestionarioPregunta(ModeloConUUID):
    - cuestionario_id: UUID
    - pregunta_id: UUID
    - seccion: str
    - tipo_seccion: TipoSeccion
    - orden_seccion: int
    - orden_pregunta: int
    - es_obligatoria: bool
    - peso_personalizado: int (opcional)
    - texto_pregunta_personalizado: Text (opcional)
    - texto_ayuda_personalizado: Text (opcional)
```

#### 2. Migraciones de Base de Datos

**Archivo**: `alembic/versions/002_crear_cuestionarios.py`

- Crea tablas `cuestionarios` y `cuestionario_preguntas`
- Define enums `NivelCuestionario` y `TipoSeccion`
- Agrega relación con `evaluaciones`

#### 3. API REST Endpoints

**Archivo**: `app/api/v1/endpoints/cuestionarios.py`

**Endpoints Públicos** (Todos los usuarios autenticados):
```
GET    /api/v1/cuestionarios/                    # Listar cuestionarios
GET    /api/v1/cuestionarios/{id}                # Obtener detalle
GET    /api/v1/cuestionarios/{id}/preguntas      # Obtener preguntas
```

**Endpoints Administrativos** (Solo admins):
```
POST   /api/v1/cuestionarios/                    # Crear cuestionario
PUT    /api/v1/cuestionarios/{id}                # Actualizar cuestionario
DELETE /api/v1/cuestionarios/{id}                # Eliminar cuestionario
POST   /api/v1/cuestionarios/{id}/preguntas      # Asignar pregunta
PUT    /api/v1/cuestionarios/{id}/preguntas/{pid} # Actualizar pregunta asignada
DELETE /api/v1/cuestionarios/{id}/preguntas/{pid} # Eliminar pregunta asignada
POST   /api/v1/cuestionarios/{id}/clonar         # Clonar cuestionario
```

#### 4. Scripts de Inicialización

**Archivo**: `scripts/crear_cuestionarios_predefinidos.py`

- Crea los 3 cuestionarios predefinidos con sus preguntas
- Genera 10 preguntas para el nivel Básico
- Genera 50 preguntas para el nivel Intermedio
- Genera 100 preguntas para el nivel Avanzado (reutilizando las intermedias)
- Asigna preguntas a cada cuestionario con orden y secciones

---

## 📋 Tareas Completadas

- [✅] Diseño de modelos de base de datos
- [✅] Creación de modelos SQLAlchemy
- [✅] Migración de Alembic
- [✅] Endpoints API REST completos
- [✅] Sistema de permisos y autorizaci\u00f3n
- [✅] Script de inicialización de cuestionarios
- [✅] Banco de preguntas predefinidas
- [✅] Sistema de clonación de cuestionarios
- [✅] Configuración de formato y diseño
- [✅] Escala de madurez configurable
- [✅] Integración con frameworks existentes

---

## 🚧 Tareas Pendientes

### Frontend (Prioridad Alta)

1. **Componentes de Visualización**:
   - [ ] `VisualizadorCuestionario.tsx` - Vista de cuestionario para responder
   - [ ] `TarjetaPregunta.tsx` - Componente individual de pregunta
   - [ ] `EscalaMadurez.tsx` - Selector de nivel de madurez
   - [ ] `ProgressoCuestionario.tsx` - Barra de progreso
   - [ ] `ResumenResultados.tsx` - Vista de resultados

2. **Panel de Administración**:
   - [ ] `GestionCuestionarios.tsx` - Lista y gestión de cuestionarios
   - [ ] `EditorCuestionario.tsx` - Editor de cuestionarios
   - [ ] `AsignadorPreguntas.tsx` - Asignar preguntas a cuestionarios
   - [ ] `ConfiguradorFormato.tsx` - Configuración de formato y diseño

3. **Hooks y Utilidades**:
   - [ ] `useCuestionarios.ts` - Hook para gestión de cuestionarios
   - [ ] `useRespuestasCuestionario.ts` - Hook para respuestas
   - [ ] `calculadorMadurez.ts` - Utilidad para cálculo de madurez

### Backend (Prioridad Media)

4. **Cálculo de Madurez**:
   - [ ] Algoritmo de cálculo de puntuación global
   - [ ] Cálculo de puntuación por sección
   - [ ] Determinación de nivel de madurez
   - [ ] Generación de recomendaciones

5. **Generación de PDFs**:
   - [ ] Plantilla PDF para Básico
   - [ ] Plantilla PDF para Intermedio
   - [ ] Plantilla PDF para Avanzado
   - [ ] Portada profesional
   - [ ] Gráficos y tablas de resultados
   - [ ] Integración con librería de PDF (ReportLab/WeasyPrint)

### Testing y Documentación (Prioridad Media)

6. **Testing**:
   - [ ] Tests unitarios para modelos
   - [ ] Tests de integración para API
   - [ ] Tests E2E para flujo completo

7. **Documentación**:
   - [ ] Guía de usuario para cuestionarios
   - [ ] Guía de administrador
   - [ ] Documentación API (Swagger/OpenAPI)
   - [ ] Ejemplos de uso

---

## 🔄 Flujo de Uso

### Para Usuarios

1. Usuario accede a la sección de "Diagnósticos"
2. Selecciona el nivel de diagnóstico deseado (Básico/Intermedio/Avanzado)
3. Sistema muestra información del cuestionario:
   - Descripción
   - Tiempo estimado
   - Total de preguntas
   - Instrucciones
4. Usuario inicia el cuestionario
5. Responde cada pregunta seleccionando el nivel de madurez (1-5)
6. Puede agregar evidencias y comentarios (opcional)
7. Sistema muestra progreso en tiempo real
8. Al completar, sistema calcula:
   - Puntuación global
   - Puntuación por sección
   - Nivel de madurez
9. Usuario puede:
   - Ver resultados detallados
   - Descargar PDF
   - Compartir resultados
   - Comparar con evaluaciones anteriores

### Para Administradores

1. Admin accede al panel de administración de cuestionarios
2. Puede:
   - Ver todos los cuestionarios (activos e inactivos)
   - Crear un nuevo cuestionario desde cero
   - Clonar un cuestionario existente como plantilla
   - Editar cuestionarios existentes
3. Al crear/editar:
   - Define información básica (nombre, nivel, descripción)
   - Configura estructura de secciones
   - Asigna preguntas existentes o crea nuevas
   - Ordena preguntas dentro de secciones
   - Personaliza textos y ayudas
   - Configura formato y diseño
   - Define escala de madurez
   - Establece niveles de resultado
4. Puede activar/desactivar cuestionarios
5. Ve estadísticas de uso

---

## 💡 Notas Técnicas

### Configuración de Formato (JSONB)

```json
{
  "color_institucional": "#1E3A8A",
  "color_secundario": "#6B7280",
  "tipografia": "Roboto",
  "incluir_logo": true,
  "incluir_portada": true,
  "incluir_instrucciones": true
}
```

### Escala de Madurez (JSONB)

```json
{
  "1": "No implementado",
  "2": "Parcialmente implementado",
  "3": "En desarrollo",
  "4": "Implementado",
  "5": "Optimizado/Mejorado continuamente"
}
```

### Niveles de Resultado (JSONB)

```json
{
  "0-20": {
    "nombre": "Inicial",
    "descripcion": "Prácticas básicas no implementadas",
    "color": "#EF4444"
  },
  "21-40": {
    "nombre": "Repetible",
    "descripcion": "Procesos básicos en marcha",
    "color": "#F59E0B"
  },
  "41-60": {
    "nombre": "Definido",
    "descripcion": "Procesos documentados y seguidos",
    "color": "#EAB308"
  },
  "61-80": {
    "nombre": "Gestionado",
    "descripcion": "Procesos medidos y controlados",
    "color": "#3B82F6"
  },
  "81-100": {
    "nombre": "Optimizado",
    "descripcion": "Mejora continua activa",
    "color": "#10B981"
  }
}
```

---

## 🚀 Próximos Pasos

### Inmediatos (Esta sesión)

1. ✅ Ejecutar migración de base de datos
2. ✅ Ejecutar script de creación de cuestionarios
3. ✅ Verificar que los endpoints funcionan
4. 🔲 Crear componentes frontend básicos
5. 🔲 Implementar visualización de cuestionarios
6. 🔲 Implementar sistema de respuestas

### Corto Plazo (Siguiente sesión)

1. Completar panel de administración
2. Implementar cálculo de madurez
3. Generar reportes PDF
4. Tests básicos

### Medio Plazo

1. Mejoras en UI/UX
2. Análisis avanzado de resultados
3. Comparación entre evaluaciones
4. Benchmarking sectorial

---

## 📚 Referencias

- **NIST CSF 2.0**: https://www.nist.gov/cyberframework
- **COBIT 2019**: https://www.isaca.org/resources/cobit
- **Ley de Protección de Datos Personales (Chile)**: Ley 19.628
- **ISO 27001**: Sistemas de Gestión de Seguridad de la Información

---

## 🎨 Diseño Visual

### Colores Institucionales

- **Azul Marino**: `#1E3A8A` (Color principal)
- **Gris**: `#6B7280` (Color secundario)
- **Verde**: `#10B981` (Éxito/Optimizado)
- **Azul**: `#3B82F6` (Gestionado)
- **Amarillo**: `#EAB308` (Definido)
- **Naranja**: `#F59E0B` (Repetible)
- **Rojo**: `#EF4444` (Inicial)

### Tipografía

- **Principal**: Roboto / Lato
- **Tamaño Base**: 14px
- **Encabezados**: 18px-24px
- **Subtítulos**: 16px

---

**Documento actualizado**: 21 de Octubre de 2025  
**Autor**: Sistema C4A  
**Versión**: 1.0.0




