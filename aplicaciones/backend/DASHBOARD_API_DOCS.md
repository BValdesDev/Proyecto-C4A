# Dashboard API - Documentación

## Descripción
API del módulo Dashboard para C4A SaaS que proporciona estadísticas, evaluaciones recientes, acciones rápidas y funcionalidad para crear nuevas evaluaciones.

## Endpoints Disponibles

### 1. GET /api/v1/dashboard/summary
Obtiene el resumen completo del dashboard con estadísticas generales.

**Headers:**
```
Authorization: Bearer <token>
```

**Respuesta Exitosa (200):**
```json
{
  "total_evaluaciones": 15,
  "promedio_puntuacion": 78.5,
  "en_progreso": 3,
  "uso_mensual": 5,
  "nivel_suscripcion": "pro",
  "limite_mensual": 50,
  "porcentaje_uso": 10.0
}
```

**Respuesta de Error (403):**
```json
{
  "success": false,
  "message": "No tienes permisos para acceder al dashboard"
}
```

### 2. GET /api/v1/dashboard/evaluaciones-recientes
Obtiene las últimas 5 evaluaciones del usuario autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Respuesta Exitosa (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Evaluación Q4 2024",
    "fecha_creacion": "2024-10-01T10:30:00Z",
    "estado": "completada",
    "puntuacion": 85.5,
    "porcentaje_completado": 100.0
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "nombre": "Auditoría de Seguridad",
    "fecha_creacion": "2024-09-28T14:15:00Z",
    "estado": "en_progreso",
    "puntuacion": null,
    "porcentaje_completado": 65.0
  }
]
```

### 3. POST /api/v1/dashboard/evaluaciones
Crea una nueva evaluación inicial con estado "en progreso".

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "nombre": "Nueva Evaluación de Ciberseguridad",
  "framework_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**Respuesta Exitosa (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440003",
  "nombre": "Nueva Evaluación de Ciberseguridad",
  "estado": "en_progreso",
  "fecha_creacion": "2024-10-02T15:30:00Z",
  "mensaje": "Evaluación creada exitosamente"
}
```

**Respuesta de Error (403) - Límite Excedido:**
```json
{
  "success": false,
  "message": "Has alcanzado el límite de 5 evaluaciones por mes"
}
```

**Respuesta de Error (404) - Framework No Encontrado:**
```json
{
  "success": false,
  "message": "Framework no encontrado"
}
```

### 4. GET /api/v1/dashboard/acciones
Obtiene las acciones rápidas disponibles para el usuario según sus permisos.

**Headers:**
```
Authorization: Bearer <token>
```

**Respuesta Exitosa (200):**
```json
[
  {
    "id": "crear_nueva_evaluacion",
    "nombre": "Crear Nueva Evaluación",
    "descripcion": "Iniciar una nueva evaluación de ciberseguridad",
    "disponible": true,
    "icono": "plus-circle",
    "ruta": "/evaluaciones/nueva",
    "categoria": "evaluaciones"
  },
  {
    "id": "ver_reportes",
    "nombre": "Ver Reportes",
    "descripcion": "Acceder a reportes y análisis de evaluaciones",
    "disponible": true,
    "icono": "bar-chart",
    "ruta": "/reportes",
    "categoria": "reportes"
  },
  {
    "id": "gestionar_usuarios",
    "nombre": "Gestionar Usuarios",
    "descripcion": "Administrar usuarios de la organización",
    "disponible": false,
    "icono": "users",
    "ruta": "/usuarios",
    "categoria": "usuarios"
  },
  {
    "id": "actualizar_plan",
    "nombre": "Actualizar Plan",
    "descripcion": "Mejorar tu plan de suscripción",
    "disponible": true,
    "icono": "credit-card",
    "ruta": "/suscripciones",
    "categoria": "suscripciones"
  },
  {
    "id": "ver_dashboard",
    "nombre": "Ver Dashboard",
    "descripcion": "Acceder al panel principal",
    "disponible": true,
    "icono": "home",
    "ruta": "/dashboard",
    "categoria": "navegacion"
  }
]
```

### 5. GET /api/v1/dashboard/estadisticas-uso
Obtiene estadísticas detalladas de uso de la organización y usuario.

**Headers:**
```
Authorization: Bearer <token>
```

**Respuesta Exitosa (200):**
```json
{
  "organizacion": {
    "id": "550e8400-e29b-41d4-a716-446655440004",
    "nombre": "Empresa ABC Ltda.",
    "nivel_suscripcion": "pro",
    "sector": "tecnologia",
    "tamaño": "mediana",
    "uso_mensual": {
      "evaluaciones_usadas": 5,
      "evaluaciones_limite": 50,
      "usuarios_activos": 8,
      "usuarios_limite": 10,
      "porcentaje_uso_evaluaciones": 10.0,
      "porcentaje_uso_usuarios": 80.0
    }
  },
  "usuario": {
    "id": "550e8400-e29b-41d4-a716-446655440005",
    "nombre_completo": "Juan Pérez",
    "email": "juan.perez@empresa.com",
    "rol": "Administrador",
    "estadisticas": {
      "evaluaciones_completadas": 12,
      "evaluaciones_en_progreso": 2,
      "total_respuestas": 156,
      "fecha_ultimo_acceso": "2024-10-02T15:30:00Z",
      "dias_desde_ultimo_acceso": 0
    }
  },
  "evaluaciones": {
    "completada": 12,
    "en_progreso": 2,
    "borrador": 1
  },
  "tendencias": {
    "2024-09": 3,
    "2024-08": 5,
    "2024-07": 4,
    "2024-06": 2,
    "2024-05": 6,
    "2024-04": 4
  },
  "timestamp": "2024-10-02T15:30:00Z"
}
```

## Códigos de Estado HTTP

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Datos de entrada inválidos
- **401 Unauthorized**: Token de autenticación inválido o faltante
- **403 Forbidden**: Sin permisos para realizar la operación
- **404 Not Found**: Recurso no encontrado
- **422 Unprocessable Entity**: Error de validación
- **500 Internal Server Error**: Error interno del servidor

## Autenticación

Todos los endpoints requieren autenticación JWT. Incluir el token en el header:

```
Authorization: Bearer <tu_token_jwt>
```

## Límites por Plan

### Plan Gratuito
- Máximo 1 evaluación por mes
- Máximo 1 usuario
- Solo framework básico

### Plan Pro
- Máximo 50 evaluaciones por mes
- Máximo 10 usuarios
- Acceso a todos los frameworks

### Plan Empresarial
- Máximo 1000 evaluaciones por mes
- Máximo 100 usuarios
- Acceso completo a todas las funcionalidades

## Ejemplos de Uso con cURL

### Obtener Resumen del Dashboard
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/summary" \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json"
```

### Crear Nueva Evaluación
```bash
curl -X POST "http://localhost:8000/api/v1/dashboard/evaluaciones" \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Evaluación Q4 2024",
    "framework_id": "550e8400-e29b-41d4-a716-446655440002"
  }'
```

### Obtener Acciones Rápidas
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/acciones" \
  -H "Authorization: Bearer tu_token_jwt" \
  -H "Content-Type: application/json"
```

## Manejo de Errores

Todos los errores siguen el formato estándar:

```json
{
  "success": false,
  "message": "Descripción del error",
  "codigo_error": "CODIGO_ERROR_ESPECIFICO"
}
```

### Códigos de Error Comunes

- `DASHBOARD_ERROR`: Error general del dashboard
- `EVALUACIONES_RECIENTES_ERROR`: Error al obtener evaluaciones recientes
- `CREAR_EVALUACION_ERROR`: Error al crear evaluación
- `ACCIONES_RAPIDAS_ERROR`: Error al obtener acciones rápidas
- `ESTADISTICAS_DETALLADAS_ERROR`: Error al obtener estadísticas
- `TOKEN_INVALIDO`: Token JWT inválido o expirado
- `SIN_PERMISOS`: Usuario sin permisos para la operación
- `LIMITE_EXCEDIDO`: Límite de evaluaciones excedido

