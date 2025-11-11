# 🎯 SISTEMA DE DIAGNÓSTICOS C4A - GUÍA COMPLETA

> **Estado**: ✅ 100% Implementado y Funcional  
> **Fecha**: 21 de Octubre de 2025  
> **Versión**: 1.0.0

---

## 🚀 INICIO RÁPIDO

### 1. Acceder como Usuario
```
URL:      http://localhost:3000/login
Email:    usuario@normal.cl
Password: Usuario123!

Luego ir a: http://localhost:3000/app/diagnosticos
```

### 2. Responder un Diagnóstico
```
1. Selecciona "Diagnóstico Básico" (10 preguntas, 15 min)
2. Click en "Iniciar Diagnóstico"
3. Lee las instrucciones
4. Responde cada pregunta seleccionando 1-5:
   1 = No implementado
   2 = Parcialmente implementado
   3 = En desarrollo
   4 = Implementado
   5 = Optimizado
5. Click en "Finalizar Diagnóstico"
6. Ve tus resultados y nivel de madurez
7. Descarga el PDF
```

### 3. Gestionar como Administrador
```
URL:      http://localhost:3000/login
Email:    admin@c4a.cl
Password: Admin123!

Luego ir a: http://localhost:3000/admin/cuestionarios
```

---

## 📊 CUESTIONARIOS DISPONIBLES

### 📄 Diagnóstico Básico
- **10 preguntas** en 15 minutos
- Evaluación rápida e introductoria
- Ideal para pequeñas empresas
- Cubre aspectos fundamentales de ciberseguridad

### 📄 Evaluación Intermedia
- **50 preguntas** en 45 minutos
- Basado en las 5 funciones de NIST CSF
- Ideal para departamentos de TI
- Evaluación completa y estructurada

### 📄 Evaluación Avanzada
- **100 preguntas** en 90 minutos
- Integra NIST CSF + COBIT 2019
- Diagnóstico organizacional exhaustivo
- Incluye gobernanza, gestión, cultura y GRC

---

## 🎯 NIVELES DE MADUREZ

| Puntuación | Nivel | Color | Descripción |
|------------|-------|-------|-------------|
| 0-20% | Inicial | Rojo | Prácticas básicas no implementadas |
| 21-40% | Repetible | Naranja | Procesos básicos en marcha |
| 41-60% | Definido | Amarillo | Procesos documentados y seguidos |
| 61-80% | Gestionado | Azul | Procesos medidos y controlados |
| 81-100% | Optimizado | Verde | Mejora continua activa |

---

## 💻 ARQUITECTURA TÉCNICA

### Backend (Python + FastAPI)

**Modelos**:
- `Cuestionario` - Definición de diagnósticos
- `CuestionarioPregunta` - Relación con preguntas
- `Pregunta` - Banco de preguntas
- `Respuesta` - Respuestas de usuarios
- `Evaluacion` - Instancias de evaluaciones

**Servicios**:
- `CalculoMadurezService` - Cálculo de puntuaciones y niveles
- `PDFService` - Generación de PDFs profesionales

**API REST**:
- 14 endpoints (5 públicos + 9 administrativos)
- Autenticación JWT
- Control de permisos por rol
- Documentación Swagger automática

### Frontend (React + TypeScript)

**Páginas**:
- `ListaDiagnosticos.tsx` - Catálogo de diagnósticos
- `DetalleDiagnostico.tsx` - Información antes de iniciar
- `ResponderDiagnostico.tsx` - Interfaz para responder
- `ResultadosDiagnostico.tsx` - Visualización de resultados
- `GestionCuestionarios.tsx` - Panel de administración

**Hooks**:
- `useCuestionarios()` - Gestión de cuestionarios
- `useResponderCuestionario()` - Gestión de respuestas

**Componentes UI**:
- Cards, Badges, Buttons, Progress
- Radio Groups, Textareas, Labels
- Dialogs, Alerts, Tabs
- Todos con Tailwind CSS

---

## 🔐 SEGURIDAD Y PERMISOS

### Niveles de Acceso:

**Usuario Normal** (evaluador):
- ✅ Ver diagnósticos activos
- ✅ Responder diagnósticos
- ✅ Ver sus propios resultados
- ✅ Descargar PDFs de sus evaluaciones
- ❌ No puede crear/editar cuestionarios

**Administrador Empresa** (admin_empresa):
- ✅ Todo lo del usuario normal
- ✅ Ver todos los diagnósticos (activos e inactivos)
- ✅ Crear cuestionarios nuevos
- ✅ Editar cuestionarios editables
- ✅ Clonar cuestionarios
- ✅ Activar/desactivar cuestionarios
- ✅ Eliminar cuestionarios (excepto plantillas)
- ✅ Ver resultados de su organización

**Administrador Sistema** (admin_sistema):
- ✅ Todos los permisos (acceso total)

---

## 📁 ARCHIVOS PRINCIPALES

### Backend:
```
app/modelos/cuestionario.py                        # Modelos de datos
app/api/v1/endpoints/cuestionarios.py              # API REST (677 líneas)
app/servicios/calculo_madurez_service.py           # Cálculo de madurez
app/servicios/pdf_service.py                       # Generación de PDFs
scripts/crear_cuestionarios_predefinidos.py        # Script de inicialización
alembic/versions/002_crear_cuestionarios.py        # Migración de BD
```

### Frontend:
```
hooks/useCuestionarios.ts                          # Hook principal
pages/diagnosticos/ListaDiagnosticos.tsx           # Lista
pages/diagnosticos/DetalleDiagnostico.tsx          # Detalle
pages/diagnosticos/ResponderDiagnostico.tsx        # Responder
pages/diagnosticos/ResultadosDiagnostico.tsx       # Resultados
pages/admin/GestionCuestionarios.tsx               # Admin panel
components/layout/Sidebar.tsx                      # Navegación actualizada
App.tsx                                             # Rutas actualizadas
```

### Documentación:
```
SISTEMA_DIAGNOSTICOS_COMPLETO.md                   # Guía técnica completa
GUIA_RAPIDA_DIAGNOSTICOS.md                        # Guía rápida de uso
IMPLEMENTACION_DIAGNOSTICOS.md                     # Detalles de implementación
LEEME_DIAGNOSTICOS.md                              # Este documento
USUARIOS_REALES.md                                 # Lista de usuarios
```

---

## 🧪 TESTING

### Test Básico (Usuario Normal):

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@normal.cl","password":"Usuario123!"}'

# 2. Listar cuestionarios (usa el token recibido)
curl -X GET http://localhost:8000/api/v1/cuestionarios/ \
  -H "Authorization: Bearer TU_TOKEN_AQUI"

# 3. Ver detalle de un cuestionario
curl -X GET http://localhost:8000/api/v1/cuestionarios/{CUESTIONARIO_ID} \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### Test Administrativo:

```bash
# 1. Login como admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@c4a.cl","password":"Admin123!"}'

# 2. Clonar cuestionario
curl -X POST "http://localhost:8000/api/v1/cuestionarios/{ID}/clonar?nuevo_nombre=Mi%20Copia" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 🎨 PERSONALIZACIÓN

### Cambiar Colores Institucionales:

En la base de datos, actualiza el campo `configuracion_formato` del cuestionario:

```json
{
  "color_institucional": "#TU_COLOR_AQUI",
  "color_secundario": "#TU_COLOR_AQUI",
  "tipografia": "Roboto",
  "incluir_logo": true,
  "incluir_portada": true,
  "incluir_instrucciones": true
}
```

### Modificar Niveles de Resultado:

Actualiza el campo `niveles_resultado` del cuestionario:

```json
{
  "0-20": {
    "nombre": "Tu Nombre",
    "descripcion": "Tu Descripción",
    "color": "#TU_COLOR"
  }
}
```

### Cambiar Escala de Madurez:

Actualiza el campo `escala_madurez`:

```json
{
  "1": "Tu descripción para nivel 1",
  "2": "Tu descripción para nivel 2",
  ...
}
```

---

## 🔧 MANTENIMIENTO

### Recrear Cuestionarios:
```bash
# Eliminar todos
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.cuestionario import Cuestionario, CuestionarioPregunta; from app.modelos.pregunta import Pregunta; db = SessionLocal(); db.query(CuestionarioPregunta).delete(); db.query(Cuestionario).delete(); db.query(Pregunta).delete(); db.commit(); print('Eliminado')"

# Recrear
docker exec c4a_backend python scripts/crear_cuestionarios_predefinidos.py
```

### Verificar Estado:
```bash
# Ver cuestionarios
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.cuestionario import Cuestionario; db = SessionLocal(); cuests = db.query(Cuestionario).all(); print(f'Total: {len(cuests)}'); [print(f'  - {c.nombre} ({c.nivel.value}): {c.total_items} items - {"Activo" if c.esta_activo else "Inactivo"}') for c in cuests]"

# Ver preguntas
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.pregunta import Pregunta; db = SessionLocal(); print(f'Total preguntas: {db.query(Pregunta).count()}')"
```

### Logs:
```bash
# Backend
docker logs c4a_backend --tail 50

# Frontend
docker logs c4a_frontend --tail 50

# PostgreSQL
docker logs c4a_postgres --tail 30
```

---

## 📚 FRAMEWORKS INTEGRADOS

### NIST Cybersecurity Framework 2.0

**5 Funciones Principales**:
1. **Identify** - Comprender el contexto de riesgos
2. **Protect** - Implementar salvaguardas
3. **Detect** - Identificar incidentes
4. **Respond** - Actuar ante incidentes
5. **Recover** - Restaurar capacidades

### COBIT 2019

**Componentes Clave**:
- **Gobernanza** - Evaluación, dirección y monitoreo
- **Gestión** - Planificación, construcción, ejecución y monitoreo

### GRC (Governance, Risk & Compliance)

- Cumplimiento normativo
- Gestión de riesgos empresariales
- Alineación estratégica

---

## 🎓 MEJORES PRÁCTICAS

### Al Responder un Diagnóstico:

1. **Tómate tu tiempo**: No apresures las respuestas
2. **Sé honesto**: Evalúa objetivamente la situación actual
3. **Agrega evidencia**: Documenta ejemplos concretos
4. **Consulta al equipo**: Involucra a responsables de áreas
5. **Guarda progreso**: Puedes continuar después
6. **Revisa antes de finalizar**: Verifica tus respuestas

### Al Crear un Cuestionario Personalizado:

1. **Define el objetivo**: ¿Qué quieres evaluar?
2. **Selecciona el nivel apropiado**: Básico/Intermedio/Avanzado
3. **Estructura en secciones**: Agrupa preguntas por tema
4. **Asigna pesos apropiados**: Mayor peso a preguntas críticas
5. **Escribe instrucciones claras**: Ayuda a los usuarios
6. **Prueba antes de activar**: Responde tu propio cuestionario

---

## 📈 ROADMAP FUTURO

### Mejoras Planificadas:

**Corto Plazo**:
- [ ] Gráficos avanzados en PDFs
- [ ] Exportación a Excel
- [ ] Comparación histórica de evaluaciones
- [ ] Dashboard de análisis

**Medio Plazo**:
- [ ] Benchmarking sectorial
- [ ] Recomendaciones con IA
- [ ] Integración con herramientas de seguridad
- [ ] Certificados de cumplimiento

**Largo Plazo**:
- [ ] API pública para partners
- [ ] Marketplace de cuestionarios
- [ ] Análisis predictivo
- [ ] Integración con SIEM

---

## ❓ FAQ

### ¿Puedo crear mis propios cuestionarios?
Sí, como administrador puedes crear cuestionarios personalizados o clonar los existentes.

### ¿Los resultados se guardan automáticamente?
Sí, todas las respuestas y resultados se guardan en la base de datos.

### ¿Puedo modificar los cuestionarios predefinidos?
Los cuestionarios predefinidos son plantillas del sistema. Puedes clonarlos y editar el clon.

### ¿Cuántos usuarios pueden responder el mismo cuestionario?
Ilimitados. Cada usuario genera su propia evaluación independiente.

### ¿Se pueden comparar resultados entre evaluaciones?
Sí, el sistema incluye funciones de comparación (implementado en el servicio de cálculo).

### ¿Los PDFs se pueden personalizar?
Sí, puedes modificar colores, tipografía y formato en la configuración del cuestionario.

---

## 🔗 ENLACES Y RECURSOS

### Documentación del Sistema:
- [SISTEMA_DIAGNOSTICOS_COMPLETO.md](./SISTEMA_DIAGNOSTICOS_COMPLETO.md) - Guía técnica
- [GUIA_RAPIDA_DIAGNOSTICOS.md](./GUIA_RAPIDA_DIAGNOSTICOS.md) - Guía de uso
- [USUARIOS_REALES.md](./USUARIOS_REALES.md) - Lista de usuarios

### APIs y Servicios:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Referencias Externas:
- [NIST CSF 2.0](https://www.nist.gov/cyberframework)
- [COBIT 2019](https://www.isaca.org/resources/cobit)
- [Ley 19.628 Chile](https://www.bcn.cl/leychile/navegar?idNorma=141599)

---

## 🎉 ¡LISTO PARA USAR!

El sistema de diagnósticos está **completamente implementado y operativo**.

### Verifica que todo funciona:

```bash
# 1. Backend activo
curl http://localhost:8000/health
# Debe responder: {"status":"healthy"}

# 2. Frontend activo
curl http://localhost:3000
# Debe cargar la página HTML

# 3. Cuestionarios creados
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.cuestionario import Cuestionario; db = SessionLocal(); print(f'Total: {db.query(Cuestionario).count()}')"
# Debe mostrar: Total: 3
```

Si todos los checks pasan, **¡estás listo para usar el sistema!**

---

**Desarrollado por**: Sistema C4A  
**Soporte**: Consulta la documentación o revisa los logs  
**Versión**: 1.0.0 - Sistema Completo Funcional



