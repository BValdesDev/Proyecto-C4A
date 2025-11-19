# INSTRUCCIÓN ÚNICA: AUDITORÍA Y LIMPIEZA DEL PROYECTO C4A AUTODIAGNÓSTICO

## OBJETIVO
Realizar una auditoría completa del código y eliminar archivos, scripts de test y archivos adicionales fuera del scope del proyecto de producción.

---

## FASE 1: AUDITORÍA COMPLETA DEL CÓDIGO

### 1.1 Auditoría de Seguridad Backend
**Ubicación**: `aplicaciones/backend/`

**Tareas**:
1. Revisar `app/core/config.py`:
   - Identificar claves hardcodeadas (RSA, Stripe, DB, Redis)
   - Verificar que todas las claves estén en variables de entorno
   - Documentar variables de entorno requeridas

2. Revisar autenticación JWT:
   - Verificar implementación RS256 en `app/core/seguridad.py`
   - Revisar blacklist de tokens
   - Verificar rate limiting

3. Revisar validación de inputs:
   - Verificar modelos Pydantic en todos los endpoints
   - Confirmar validación de UUIDs (el proyecto usa UUIDs, NO IDs numéricos)
   - Verificar sanitización de strings

4. Revisar protección CORS/CSRF:
   - Verificar configuración en `app/main.py`
   - Revisar headers de seguridad en middleware

5. Analizar dependencias vulnerables:
   - Revisar `requirements.txt`
   - Identificar versiones con vulnerabilidades conocidas

**Entregable**: Crear `AUDITORIA_SEGURIDAD_BACKEND.md` con hallazgos y recomendaciones

### 1.2 Auditoría de Seguridad Frontend
**Ubicación**: `aplicaciones/frontend/`

**Tareas**:
1. Revisar almacenamiento de tokens:
   - Analizar `src/hooks/useAuth.tsx`
   - Verificar uso de localStorage vs httpOnly cookies
   - Evaluar seguridad actual

2. Revisar vulnerabilidades XSS:
   - Buscar uso de `dangerouslySetInnerHTML`
   - Verificar sanitización de contenido de usuario

3. Revisar validación de inputs:
   - Verificar validación en formularios
   - Confirmar validación de UUIDs, emails, teléfonos

4. Analizar dependencias vulnerables:
   - Revisar `package.json`
   - Identificar vulnerabilidades con `npm audit`

**Entregable**: Crear `AUDITORIA_SEGURIDAD_FRONTEND.md` con hallazgos y recomendaciones

### 1.3 Auditoría de Código Duplicado
**Tareas**:
1. **CRÍTICO**: Analizar duplicación entre:
   - `aplicaciones/frontend/src/utilidades/apiClient.ts` (versión activa con `c4a_token`)
   - `aplicaciones/frontend/src/utilidades/api.ts` (versión duplicada con `access_token`)
   
2. Comparar funcionalidades:
   - Identificar qué funcionalidades tiene cada archivo
   - Determinar cuál es la versión correcta a mantener
   - Documentar diferencias

3. Buscar otras duplicaciones:
   - Lógica de autenticación duplicada
   - Validaciones repetidas
   - Utilidades duplicadas

**Entregable**: Crear `AUDITORIA_CODIGO_DUPLICADO.md` con análisis y plan de consolidación

### 1.4 Auditoría de Integración Backend-Frontend
**Tareas**:
1. Comparar tipos:
   - Modelos Pydantic en `app/modelos/*.py`
   - Tipos TypeScript en `src/tipos/index.ts`
   - Identificar discrepancias

2. Verificar endpoints:
   - Mapear todos los endpoints del backend
   - Verificar que frontend llame correctamente
   - Identificar endpoints no utilizados

3. Verificar sincronización de autenticación:
   - Nombres de tokens consistentes
   - Flujo de login/logout/refresh sincronizado

**Entregable**: Crear `AUDITORIA_INTEGRACION.md` con hallazgos

---

## FASE 2: IDENTIFICACIÓN Y ELIMINACIÓN DE ARCHIVOS FUERA DEL SCOPE

### 2.1 Scripts de Test y Verificación (ELIMINAR)

**Backend - Scripts de Test**:
- `aplicaciones/backend/tests/e2e-mcp-tests.js` - Test E2E con MCP (fuera del scope)
- `aplicaciones/backend/tests/test_dashboard_api.py` - Test manual (mantener si es parte de suite de tests oficial)

**Scripts Raíz - Tests y Verificaciones**:
- `scripts/test_analytics_endpoints.py` - Script de test manual (ELIMINAR)
- `scripts/test_diagnostics_endpoint.py` - Script de test manual (ELIMINAR)
- `scripts/verificar_api_admin_simple.py` - Script de verificación temporal (ELIMINAR)
- `scripts/verificar_api_admin.py` - Script de verificación temporal (ELIMINAR)
- `scripts/verificar_datos_admin.py` - Script de verificación temporal (ELIMINAR)
- `scripts/verificar_estadisticas_diagnosticos.py` - Script de verificación temporal (ELIMINAR)

**Frontend - Scripts de Test**:
- `aplicaciones/frontend/scripts/test-e2e-mcp.ps1` - Script de test MCP (ELIMINAR si no es parte de suite oficial)

### 2.2 Archivos MCP y Desarrollo Temporal (EVALUAR PARA ELIMINAR)

- `MCP_CHROME_DEVTOOLS.md` - Documentación MCP (evaluar si es necesario para producción)
- `aplicaciones/backend/tests/e2e-mcp-tests.js` - Tests MCP (ELIMINAR)

### 2.3 Scripts de Utilidad Backend (MANTENER - Son necesarios para setup)

**MANTENER estos scripts en `aplicaciones/backend/scripts/`** (son necesarios para configuración inicial):
- `crear_frameworks.py` - Crear frameworks iniciales
- `crear_cuestionarios_predefinidos.py` - Crear cuestionarios
- `crear_usuario_gratuito.py` - Crear usuarios de prueba
- `crear_usuario_normal.py` - Crear usuarios de prueba
- `crear_usuarios_prueba.py` - Crear usuarios de prueba
- `generar_claves_rsa.py` - Generar claves JWT
- `rotar_claves_jwt.py` - Rotar claves JWT
- `configurar_usuario_empresarial.py` - Configurar usuarios empresariales
- `actualizar_montos.py` - Actualizar montos de suscripciones
- `sincronizar_suscripciones.py` - Sincronizar suscripciones
- `resetear_passwords.py` - Resetear contraseñas (útil para desarrollo)

**EVALUAR estos scripts** (podrían ser temporales):
- `debug_organizacion.py` - Script de debug (evaluar si es necesario)
- `verificar_cuestionarios.py` - Script de verificación (evaluar si es necesario)
- `verificar_datos_admin.py` - Script de verificación (evaluar si es necesario)
- `verificar_roles_usuarios.py` - Script de verificación (evaluar si es necesario)

**Scripts Raíz - Evaluar**:
- `scripts/arreglar_suscripciones_empresariales.py` - Script de corrección (evaluar si es necesario)
- `scripts/arreglar_suscripciones.py` - Script de corrección (evaluar si es necesario)
- `scripts/obtener_usuarios_completos.py` - Script de utilidad (evaluar si es necesario)
- `scripts/gitflow-helper.ps1` y `.sh` - Helpers de git (MANTENER si son útiles)
- `scripts/implementar-admin-panel.ps1` y `.sh` - Scripts de implementación (MANTENER si son útiles)

### 2.4 Código Duplicado (CONSOLIDAR)

**ELIMINAR después de consolidar**:
- `aplicaciones/frontend/src/utilidades/api.ts` - Duplicado de apiClient.ts
  - **ACCIÓN**: Consolidar funcionalidades en `apiClient.ts` y eliminar `api.ts`
  - **NOTA**: `apiClient.ts` usa `c4a_token` (correcto), `api.ts` usa `access_token` (incorrecto)

### 2.5 Archivos de Documentación (MANTENER)

**MANTENER** (son documentación del proyecto):
- Todos los archivos `.md` en la raíz
- `aplicaciones/backend/DASHBOARD_API_DOCS.md`
- `aplicaciones/backend/SECURITY_JWT_UPGRADE.md`

---

## FASE 3: CONSOLIDACIÓN Y LIMPIEZA

### 3.1 Consolidar Cliente API Frontend

**Tareas**:
1. Analizar ambos archivos:
   - `src/utilidades/apiClient.ts` (versión activa - mantener)
   - `src/utilidades/api.ts` (versión duplicada - eliminar)

2. Verificar que `apiClient.ts` tenga todas las funcionalidades necesarias:
   - Interceptores de request/response
   - Manejo de tokens (`c4a_token`, `c4a_refresh_token`)
   - Renovación automática de tokens
   - Manejo de errores 401

3. Buscar todas las referencias a `api.ts`:
   - Buscar imports de `api.ts` en todo el código
   - Actualizar a usar `apiClient.ts` o las funciones helper de `apiClient.ts`

4. Eliminar `api.ts` después de actualizar todas las referencias

**Entregable**: Código consolidado, archivo `api.ts` eliminado

### 3.2 Actualizar Referencias

**Tareas**:
1. Buscar en todo el código frontend:
   - Imports de `./utilidades/api` o `../utilidades/api`
   - Uso de funciones de `api.ts` (authAPI, userAPI, etc.)
   
2. Actualizar a usar:
   - `apiClient` directamente, o
   - Funciones helper exportadas desde `apiClient.ts`

3. Verificar que no se rompa funcionalidad

---

## FASE 4: VERIFICACIÓN FINAL

### 4.1 Verificar Funcionalidad

**Tareas**:
1. Verificar que el proyecto compile sin errores:
   - Backend: Verificar imports y sintaxis
   - Frontend: Verificar que TypeScript compile

2. Verificar que no haya referencias rotas:
   - Buscar imports de archivos eliminados
   - Verificar que todas las referencias estén actualizadas

3. Verificar estructura del proyecto:
   - Confirmar que estructura sea limpia
   - Verificar que solo queden archivos necesarios

### 4.2 Crear Resumen Final

**Entregable**: Crear `RESUMEN_AUDITORIA_LIMPIEZA.md` con:
1. Archivos eliminados (lista completa)
2. Archivos consolidados (cambios realizados)
3. Hallazgos de seguridad (resumen)
4. Recomendaciones pendientes
5. Estado final del proyecto

---

## ORDEN DE EJECUCIÓN

1. ✅ **FASE 1**: Realizar todas las auditorías (solo análisis, sin cambios)
2. ✅ **FASE 2**: Identificar archivos a eliminar (crear lista)
3. ✅ **FASE 3**: Consolidar código duplicado (hacer cambios)
4. ✅ **FASE 4**: Eliminar archivos identificados
5. ✅ **FASE 5**: Verificar que todo funcione
6. ✅ **FASE 6**: Crear resumen final

---

## CRITERIOS DE ÉXITO

- [ ] Todas las auditorías completadas con reportes
- [ ] Archivos de test fuera del scope eliminados
- [ ] Código duplicado consolidado
- [ ] Referencias actualizadas correctamente
- [ ] Proyecto compila sin errores
- [ ] Resumen final creado
- [ ] Proyecto limpio y listo para producción

---

## NOTAS IMPORTANTES

1. **Backup**: Hacer commit o backup antes de eliminar archivos
2. **Verificar antes de eliminar**: Confirmar que archivos no sean necesarios
3. **Tests oficiales**: Mantener tests que sean parte de la suite oficial (pytest, vitest)
4. **Scripts de setup**: Mantener scripts necesarios para configuración inicial
5. **Documentación**: Mantener toda la documentación del proyecto

