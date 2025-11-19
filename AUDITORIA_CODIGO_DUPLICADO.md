# AUDITORÍA DE CÓDIGO DUPLICADO - C4A AUTODIAGNÓSTICO

**Fecha**: 2024

## RESUMEN EJECUTIVO

### Duplicación Crítica Identificada

1. **CRÍTICO**: Dos clientes API en frontend
   - `src/utilidades/apiClient.ts` (versión activa - CORRECTA)
   - `src/utilidades/api.ts` (versión duplicada - OBSOLETA)

**Análisis**: El archivo `api.ts` NO se está usando en ningún lugar del código. Todos los imports son de `apiClient.ts`.

---

## DETALLE DE DUPLICACIÓN

### 1. Clientes API Duplicados

**Archivo 1**: `aplicaciones/frontend/src/utilidades/apiClient.ts`
- ✅ **VERSIÓN ACTIVA**
- Usa `c4a_token` y `c4a_refresh_token` (correcto)
- Usa `VITE_API_URL` (correcto)
- Tiene interceptores completos
- Tiene funciones helper `api.get/post/put/delete/patch`
- **Usado en**: 33 archivos del proyecto

**Archivo 2**: `aplicaciones/frontend/src/utilidades/api.ts`
- ❌ **VERSIÓN OBSOLETA**
- Usa `access_token` y `refresh_token` (incorrecto - no coincide con backend)
- Usa `VITE_API_BASE_URL` (diferente variable de entorno)
- Tiene funciones específicas (authAPI, userAPI, etc.) que no se usan
- **Usado en**: 0 archivos (NO se importa en ningún lugar)

**Diferencias clave**:
1. Nombres de tokens: `api.ts` usa `access_token`, `apiClient.ts` usa `c4a_token` (correcto)
2. Variables de entorno: `api.ts` usa `VITE_API_BASE_URL`, `apiClient.ts` usa `VITE_API_URL`
3. Funcionalidad: `apiClient.ts` tiene mejor manejo de renovación de tokens

---

## PLAN DE CONSOLIDACIÓN

### Paso 1: Verificar que api.ts no se usa
✅ **COMPLETADO**: Confirmado que `api.ts` no se importa en ningún archivo

### Paso 2: Eliminar api.ts
- Eliminar `aplicaciones/frontend/src/utilidades/api.ts`
- No requiere actualización de imports (no se usa)

### Paso 3: Verificar funcionalidad
- Verificar que `apiClient.ts` tenga todas las funcionalidades necesarias
- Confirmar que todas las llamadas API funcionen correctamente

---

## RECOMENDACIONES

1. **ELIMINAR** `api.ts` inmediatamente (no se usa)
2. **MANTENER** `apiClient.ts` como único cliente API
3. **DOCUMENTAR** que `apiClient.ts` es el cliente oficial
4. **VERIFICAR** que no haya otras duplicaciones similares

---

## ARCHIVOS AFECTADOS

### Archivos que usan apiClient.ts (33 archivos):
- `pages/evaluaciones/EvaluacionesPage.tsx`
- `hooks/useCuestionarios.ts`
- `pages/dashboard/DashboardPage.tsx`
- `pages/diagnosticos/ResultadosDiagnostico.tsx`
- `pages/evaluaciones/EvaluacionPage.tsx`
- `pages/planes/*.tsx` (3 archivos)
- `hooks/useAuth.tsx`
- `pages/admin/*.tsx` (7 archivos)
- `componentes/cuestionario/CuestionarioNivel.tsx`
- `hooks/useEvaluacion.ts`
- `pages/evaluaciones/CrearEvaluacionPage.tsx`
- `componentes/usuarios/GestionUsuarios.tsx`
- `componentes/facturacion/*.tsx` (2 archivos)
- `componentes/dashboard/DashboardNivel.tsx`
- `pages/auth/RegistroPage.tsx`
- `hooks/useSuscripcion.ts`
- `hooks/useReportes.ts`
- `componentes/reportes/*.tsx` (2 archivos)
- `componentes/auth/*.tsx` (4 archivos)
- `componentes/analytics/AnalyticsAvanzado.tsx`

### Archivos que NO usan api.ts:
- Ninguno (confirmado con búsqueda exhaustiva)

---

## CONCLUSIÓN

El archivo `api.ts` es código muerto que debe eliminarse. No hay riesgo en eliminarlo ya que no se usa en ningún lugar del proyecto.

