# Documentación: Sistema de Bienvenida y Onboarding

## Estado Actual

**Fecha de documentación:** Noviembre 2025

### Resumen

El sistema de bienvenida y onboarding en C4A Autodiagnóstico combina un componente centralizado reutilizable con vistas específicas por plan. Los usuarios sin evaluaciones acceden al flujo guiado `OnboardingEvaluaciones`, mientras que las páginas de planes (`PlanGratuitoPage`, `PlanProPage`, `PlanEmpresarialPage`) mantienen mensajes personalizados por nivel de suscripción.

---

## Componentes y Ubicación

### Componente centralizado: `OnboardingEvaluaciones`

- **Ubicación:** `aplicaciones/frontend/src/components/onboarding/OnboardingEvaluaciones.tsx`
- **Renderizado en:** `aplicaciones/frontend/src/pages/evaluaciones/EvaluacionesPage.tsx`
- **Activación:** aparece automáticamente como estado vacío cuando la API devuelve cero evaluaciones para el usuario autenticado.
- **Estructura:** tres tarjetas de pasos que guían al usuario por (1) explorar el dashboard, (2) crear su primera evaluación y (3) gestionar invitaciones/planes.
- **Acciones clave:**
  - `Ir al dashboard` (`/app/dashboard`)
  - `Crear evaluación` (callback que abre `/app/evaluaciones/crear`)
  - `Gestionar invitaciones` (`/app/suscripciones`)
- **Estilos:** tarjetas con borde `c4a-blue` y encabezado con número de paso, manteniendo consistencia visual con el resto del layout.

### Páginas de Planes (Onboarding por Nivel de Suscripción)

Las páginas de planes continúan actuando como la primera pantalla de bienvenida tras el login, según el nivel de suscripción del usuario. Cada una muestra un mensaje personalizado y orientación específica.

#### 1. **PlanGratuitoPage.tsx**
- **Ubicación:** `aplicaciones/frontend/src/pages/planes/PlanGratuitoPage.tsx`
- **Mensaje de bienvenida:** `¡Bienvenido, {usuario?.nombres}!`
- **Descripción:** "Estás usando el plan gratuito de {usuario?.organizacion?.nombre}."
- **Características mostradas:**
  - Evaluación básica NIST CSF 2.0
  - 1 evaluación por mes
  - Reporte básico en PDF
- **Acciones disponibles:**
  - Botón primario: "Comenzar Evaluación" (navega a `/app/diagnosticos/{id}/responder`)
  - Botón secundario: "Actualizar Plan" (navega a `/app/suscripciones`)
- **Estilo:** Gradiente azul (`from-blue-50 to-indigo-100`), tarjeta blanca con sombra

#### 2. **PlanProPage.tsx**
- **Ubicación:** `aplicaciones/frontend/src/pages/planes/PlanProPage.tsx`
- **Mensaje de bienvenida:** `¡Excelente elección, {usuario?.nombres}!`
- **Descripción:** "Tienes acceso a todas las funciones Pro de {usuario?.organizacion?.nombre}."
- **Características mostradas:**
  - Evaluación completa NIST CSF 2.0
  - Cuestionarios COBIT 2019
  - 10 evaluaciones por mes
  - Reportes avanzados con gráficos
- **Acciones disponibles:**
  - Botón primario: "Comenzar Evaluación" (navega a `/app/diagnosticos/{id}/responder`)
  - Botón secundario: "Gestionar Usuarios" (navega a `/app/usuarios`)
- **Estilo:** Gradiente púrpura (`from-purple-50 to-indigo-100`), tarjeta blanca con sombra

#### 3. **PlanEmpresarialPage.tsx**
- **Ubicación:** `aplicaciones/frontend/src/pages/planes/PlanEmpresarialPage.tsx`
- **Mensaje de bienvenida:** `¡Acceso completo, {usuario?.nombres}!`
- **Descripción:** "Tienes acceso a todas las funciones empresariales de {usuario?.organizacion?.nombre}."
- **Características mostradas:**
  - Evaluaciones ilimitadas
  - Usuarios ilimitados
  - Analytics avanzado
  - Soporte 24/7
- **Acciones disponibles:**
  - Botón primario: "Comenzar Evaluación" (navega a `/app/diagnosticos/{id}/responder`)
  - Botón secundario: "Gestionar Equipo" (navega a `/app/usuarios`)
- **Estilo:** Gradiente ámbar/naranja (`from-amber-50 to-orange-100`), tarjeta blanca con sombra

---

## Flujo de Onboarding

### Flujo de Redirección Post-Login

El sistema de autenticación (`useAuth.tsx`) continúa redirigiendo automáticamente a los usuarios según su nivel de suscripción después del login:

```typescript
// Lógica en useAuth.tsx (líneas 177-189)
switch (nivelSuscripcion) {
  case 'gratuito':
    navigate('/app/plan-gratuito')
    break
  case 'pro':
    navigate('/app/plan-pro')
    break
  case 'empresarial':
    navigate('/app/plan-empresarial')
    break
  default:
    navigate('/app/dashboard')
}
```

### Flujo de Usuario

1. **Usuario inicia sesión** → `useAuth.login()`
2. **Sistema identifica nivel de suscripción** → `usuarioData.organizacion?.nivel_suscripcion`
3. **Redirección automática** → Página de plan correspondiente
4. **Pantalla de bienvenida** → Muestra mensaje personalizado, características del plan y acciones rápidas
5. **Usuario interactúa** → Puede comenzar evaluación o gestionar usuarios/equipo
6. **Vista de evaluaciones vacía** → Si no existen evaluaciones, se muestra `OnboardingEvaluaciones` con pasos guiados

---

## Características del Sistema Actual

### Ventajas

- **Personalización por plan:** Cada nivel tiene un mensaje y características específicas
- **Orientación clara:** Muestra qué puede hacer el usuario según su plan
- **Acciones rápidas:** Botones directos para comenzar a usar la plataforma
- **Estilos diferenciados:** Colores distintos por plan (azul, púrpura, ámbar)

### Limitaciones

- **Código duplicado:** La estructura de bienvenida está repetida en 3 archivos
- **Código duplicado:** La estructura de bienvenida está repetida en 3 archivos (uno por plan)
- **Onboarding progresivo limitado:** `OnboardingEvaluaciones` cubre el primer acceso a evaluaciones, pero no persiste estados avanzados
- **Sin estado de "primer uso":** No se persiste si el usuario completó el recorrido inicial

---

## Estructura de Código Actual

### Patrón Utilizado

Cada página de plan sigue esta estructura:

```typescript
1. Hook useAuth() para obtener datos del usuario
2. Hook useNavigate() para navegación
3. Función handleComenzarEvaluacion() que:
   - Obtiene el cuestionario principal vía API
   - Navega a la página de responder diagnóstico
4. JSX con:
   - Header con título del plan
   - Tarjeta de bienvenida con mensaje personalizado
   - Lista de características con checkmarks
   - Botones de acción
```

### Funcionalidad Común

Todas las páginas comparten:
- Obtención del cuestionario principal: `api.get('/api/v1/cuestionarios/principal')`
- Navegación a responder diagnóstico: `/app/diagnosticos/${response.id}/responder`
- Manejo de errores con `toast.error()`
- Estructura visual similar (tarjeta blanca sobre gradiente)

---

## Recomendaciones para Mejora

### Opción 1: Componente Reutilizable

Crear un componente `WelcomePlanCard.tsx` que reciba props:
- `nivel`: 'gratuito' | 'pro' | 'empresarial'
- `usuario`: Objeto usuario
- `caracteristicas`: Array de características
- `onComenzarEvaluacion`: Callback
- `accionSecundaria`: Configuración del botón secundario

### Opción 2: Onboarding Progresivo

Implementar un sistema de pasos guiados para nuevos usuarios:
- Paso 1: Bienvenida y presentación del plan
- Paso 2: Tour por el dashboard
- Paso 3: Crear primera evaluación
- Paso 4: Explicación de reportes

### Opción 3: Empty State Pattern

Para usuarios sin evaluaciones, mostrar un estado vacío con:
- Mensaje de bienvenida más prominente
- Tutorial interactivo
- Ejemplos de uso
- Call-to-action destacado

---

## Referencias

- **Páginas de planes:** `aplicaciones/frontend/src/pages/planes/`
- **Hook de autenticación:** `aplicaciones/frontend/src/hooks/useAuth.tsx`
- **Cliente API:** `aplicaciones/frontend/src/utilidades/apiClient.ts`

---

## Notas Técnicas

- El sistema NO utiliza un componente `WelcomeDashboard.tsx`
- El mensaje "Excelente elección" aparece solo en `PlanProPage.tsx` (línea 48)
- El mensaje "Bienvenido" aparece en `PlanGratuitoPage.tsx` (línea 48)
- El mensaje "Acceso completo" aparece en `PlanEmpresarialPage.tsx` (línea 48)
- Todos los componentes utilizan Tailwind CSS para estilos
- No hay persistencia de estado de onboarding (no se marca como "completado")



