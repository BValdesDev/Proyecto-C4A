# 🚀 GUÍA RÁPIDA - SISTEMA DE DIAGNÓSTICOS C4A

**Estado**: ✅ Sistema 100% funcional y listo para usar  
**Fecha**: 21 de Octubre de 2025  
**Versión**: 1.0.0

---

## 📊 ¿QUÉ SE HA IMPLEMENTADO?

Un **sistema completo de diagnósticos de madurez en ciberseguridad** con:

- ✅ **3 niveles de diagnóstico** (Básico 10, Intermedio 50, Avanzado 100 preguntas)
- ✅ **Interfaz de usuario completa** (4 páginas React)
- ✅ **API REST funcional** (14 endpoints)
- ✅ **Cálculo automático** de niveles de madurez
- ✅ **Generación de PDFs** profesionales
- ✅ **Panel de administración** para gestionar cuestionarios

---

## 🎯 ACCESO RÁPIDO

### URLs Principales:

```
Frontend:           http://localhost:3000
Backend API:        http://localhost:8000
Swagger Docs:       http://localhost:8000/docs
Diagnósticos:       http://localhost:3000/app/diagnosticos
Admin Panel:        http://localhost:3000/admin/cuestionarios
```

### Credenciales de Prueba:

**Usuario Normal** (para responder diagnósticos):
```
Email:    usuario@normal.cl
Password: Usuario123!
Acceso:   http://localhost:3000/app/diagnosticos
```

**Administrador** (para gestionar cuestionarios):
```
Email:    admin@c4a.cl
Password: Admin123!
Acceso:   http://localhost:3000/admin/cuestionarios
```

---

## 🎮 GUÍA DE USO RÁPIDA

### PARA USUARIOS:

#### 1. Acceder al Sistema
```
1. Ir a http://localhost:3000/login
2. Ingresar: usuario@normal.cl / Usuario123!
3. Click en "Iniciar Sesión"
4. Serás redirigido a /app/dashboard
```

#### 2. Iniciar un Diagnóstico
```
1. Click en "Diagnósticos" en el menú lateral (icono de clipboard)
2. Verás 3 diagnósticos disponibles:
   - Básico (10 preguntas, 15 min)
   - Intermedio (50 preguntas, 45 min)
   - Avanzado (100 preguntas, 90 min)
3. Click en "Iniciar Diagnóstico" en el que desees
4. Lee las instrucciones
5. Click en "Iniciar Diagnóstico"
```

#### 3. Responder Preguntas
```
1. Para cada pregunta, selecciona el nivel de madurez (1-5):
   1 = No implementado
   2 = Parcialmente implementado
   3 = En desarrollo
   4 = Implementado
   5 = Optimizado
   
2. Opcionalmente agrega:
   - Evidencia que respalde tu respuesta
   - Comentarios adicionales
   
3. Usa botones "Siguiente" y "Anterior" para navegar
4. El progreso se muestra en la barra superior
5. Click en "Finalizar Diagnóstico" al completar todas
```

#### 4. Ver Resultados
```
Automáticamente verás:
- Puntuación global (0-100%)
- Nivel de madurez:
  * Inicial (0-20%)
  * Repetible (21-40%)
  * Definido (41-60%)
  * Gestionado (61-80%)
  * Optimizado (81-100%)
- Distribución de respuestas
- Recomendaciones personalizadas

Acciones disponibles:
- Descargar PDF
- Compartir resultados
- Iniciar nuevo diagnóstico
```

### PARA ADMINISTRADORES:

#### 1. Acceder al Panel de Administración
```
1. Ir a http://localhost:3000/login
2. Ingresar: admin@c4a.cl / Admin123!
3. Serás redirigido a /admin/dashboard
4. Click en "Diagnostics" en el menú lateral
```

#### 2. Ver y Gestionar Cuestionarios
```
1. Verás lista de todos los cuestionarios
2. Información mostrada:
   - Nombre y código
   - Nivel (básico/intermedio/avanzado)
   - Total de preguntas
   - Tiempo estimado
   - Estado (activo/inactivo)
   - Total de evaluaciones realizadas
   
3. Acciones disponibles:
   - Ver (icono de ojo)
   - Editar (icono de lápiz)
   - Clonar (icono de copiar)
   - Eliminar (icono de basura)
```

#### 3. Clonar un Cuestionario
```
1. Click en icono de "Copiar" del cuestionario deseado
2. Ingresa un nombre para el clon (ej: "Mi Diagnóstico Personalizado")
3. Click en "Clonar"
4. Sistema crea una copia exacta que puedes editar
```

#### 4. Editar un Cuestionario
```
1. Click en icono de "Editar"
2. Modifica los campos que necesites:
   - Nombre
   - Descripción
   - Tiempo estimado
   - Instrucciones
   - Estado (activo/inactivo)
3. Puedes también:
   - Agregar nuevas preguntas
   - Reordenar preguntas existentes
   - Personalizar textos de ayuda
   - Cambiar pesos de preguntas
```

---

## 📋 LOS 3 DIAGNÓSTICOS DISPONIBLES

### 1. Diagnóstico Básico

**Ideal para**: Pequeñas empresas, evaluación rápida  
**Preguntas**: 10  
**Tiempo**: 15 minutos  
**Código**: DIAG_BASICO_DIAGNÓSTIC

**Temas**:
- Identificación de activos críticos
- Evaluación de riesgos básicos
- Protección de contraseñas
- Copias de seguridad
- Actualización de software
- Gestión de incidentes
- Roles y responsabilidades
- Políticas de uso
- Capacitación
- Cumplimiento legal

### 2. Evaluación Intermedia

**Ideal para**: Departamentos TI, medianas empresas  
**Preguntas**: 50  
**Tiempo**: 45 minutos  
**Código**: DIAG_INTERMEDIO_EVALUACIÓN

**Estructura** (NIST CSF - 10 preguntas por función):
- **Identify**: Gestión de activos + Evaluación de riesgos
- **Protect**: Control de acceso + Protección de datos
- **Detect**: Monitoreo continuo + Análisis de anomalías
- **Respond**: Planificación de respuesta + Comunicaciones
- **Recover**: Planificación de recuperación + Mejoras

### 3. Evaluación Avanzada

**Ideal para**: Evaluación organizacional completa  
**Preguntas**: 100  
**Tiempo**: 90 minutos  
**Código**: DIAG_AVANZADO_EVALUACIÓN

**Estructura** (NIST + COBIT integrado):
- **Gobernanza** (COBIT) - 20 preguntas
- **Gestión** (COBIT) - 20 preguntas
- **Funciones NIST** - 40 preguntas
- **Cultura y Mejora Continua** - 10 preguntas
- **GRC** - 10 preguntas

---

## 🔧 COMANDOS ÚTILES

### Verificar que todo funciona:
```bash
# Ver cuestionarios en la BD
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.cuestionario import Cuestionario; db = SessionLocal(); cuests = db.query(Cuestionario).all(); print(f'Total: {len(cuests)}'); [print(f'  - {c.nombre} ({c.nivel.value}): {c.total_items} items') for c in cuests]"

# Probar API
curl http://localhost:8000/api/v1/cuestionarios/

# Ver documentación Swagger
# Abrir en navegador: http://localhost:8000/docs
```

### Si necesitas recrear los cuestionarios:
```bash
# Eliminar y recrear
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.cuestionario import Cuestionario, CuestionarioPregunta; from app.modelos.pregunta import Pregunta; db = SessionLocal(); db.query(CuestionarioPregunta).delete(); db.query(Cuestionario).delete(); db.query(Pregunta).delete(); db.commit(); print('Limpiado')"

docker exec c4a_backend python scripts/crear_cuestionarios_predefinidos.py
```

### Reiniciar servicios:
```bash
# Reiniciar solo backend
docker restart c4a_backend

# Reiniciar todo
docker-compose restart

# Ver logs
docker logs c4a_backend --tail 50
docker logs c4a_frontend --tail 50
```

---

## 🎨 DISEÑO Y UX

### Colores del Sistema:
- **Nivel Inicial** (0-20%): Rojo `#EF4444`
- **Nivel Repetible** (21-40%): Naranja `#F59E0B`
- **Nivel Definido** (41-60%): Amarillo `#EAB308`
- **Nivel Gestionado** (61-80%): Azul `#3B82F6`
- **Nivel Optimizado** (81-100%): Verde `#10B981`

### Iconos:
- **Diagnósticos**: Clipboard con lista
- **Básico**: Check verde
- **Intermedio**: Gráfico de barras azul
- **Avanzado**: Tendencia púrpura

---

## ⚙️ ENDPOINTS API DISPONIBLES

### Endpoints Públicos (Autenticado):
```
GET  /api/v1/cuestionarios/                     # Listar todos
GET  /api/v1/cuestionarios/{id}                 # Ver detalle
GET  /api/v1/cuestionarios/{id}/preguntas       # Ver preguntas
GET  /api/v1/cuestionarios/{id}/calcular-resultado?evaluacion_id=...  # Calcular
GET  /api/v1/cuestionarios/{id}/descargar-pdf/{evaluacion_id}  # PDF
```

### Endpoints Admin:
```
POST   /api/v1/cuestionarios/                   # Crear
PUT    /api/v1/cuestionarios/{id}               # Actualizar
DELETE /api/v1/cuestionarios/{id}               # Eliminar
POST   /api/v1/cuestionarios/{id}/clonar        # Clonar
POST   /api/v1/cuestionarios/{id}/preguntas     # Asignar pregunta
PUT    /api/v1/cuestionarios/{id}/preguntas/{pid}  # Actualizar pregunta
DELETE /api/v1/cuestionarios/{id}/preguntas/{pid}  # Eliminar pregunta
```

---

## 🐛 TROUBLESHOOTING

### Si el backend no inicia:
```bash
docker logs c4a_backend --tail 50
# Revisar errores de importación o sintaxis
```

### Si los cuestionarios no aparecen:
```bash
# Verificar que existen en la BD
docker exec c4a_backend python -c "from app.modelos.base import SessionLocal; from app.modelos.cuestionario import Cuestionario; db = SessionLocal(); print(f'Total: {db.query(Cuestionario).count()}')"

# Si es 0, recrear:
docker exec c4a_backend python scripts/crear_cuestionarios_predefinidos.py
```

### Si hay errores de permisos:
```bash
# Verificar rol del usuario
docker exec c4a_backend python scripts/verificar_roles_usuarios.py
```

### Si el frontend no carga:
```bash
docker logs c4a_frontend --tail 50
docker restart c4a_frontend
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

Para información más detallada, consulta:

- **SISTEMA_DIAGNOSTICOS_COMPLETO.md** - Documentación técnica completa
- **IMPLEMENTACION_DIAGNOSTICOS.md** - Guía de implementación
- **USUARIOS_REALES.md** - Lista de todos los usuarios del sistema
- **CREDENCIALES.md** - Credenciales de acceso

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de usar el sistema, verifica que todo esté funcionando:

- [ ] Backend corriendo: http://localhost:8000/health (debe responder "healthy")
- [ ] Frontend corriendo: http://localhost:3000 (debe cargar la página)
- [ ] Swagger accesible: http://localhost:8000/docs
- [ ] Puedes hacer login como usuario normal
- [ ] Puedes hacer login como administrador
- [ ] Menú muestra opción "Diagnósticos"
- [ ] Aparecen los 3 cuestionarios en la lista
- [ ] Puedes iniciar un diagnóstico
- [ ] Puedes responder preguntas
- [ ] Se calculan los resultados
- [ ] Se puede descargar PDF

---

## 🎉 ¡TODO LISTO!

El sistema de diagnósticos está **completamente implementado y funcional**. 

### Próximos pasos sugeridos:

1. **Probar el sistema**:
   - Responder un diagnóstico básico completo
   - Ver los resultados
   - Descargar el PDF

2. **Como administrador**:
   - Clonar un cuestionario
   - Editarlo
   - Ver las estadísticas

3. **Personalizar**:
   - Ajustar colores institucionales
   - Modificar textos de instrucciones
   - Agregar/modificar preguntas

---

**¡Disfruta del sistema de diagnósticos C4A!**

Para cualquier duda, consulta la documentación completa en:
- `SISTEMA_DIAGNOSTICOS_COMPLETO.md`
- `http://localhost:8000/docs` (Swagger)

---

**Última actualización**: 21 de Octubre de 2025, 21:25 hrs  
**Estado**: ✅ Sistema Operativo y Funcional



