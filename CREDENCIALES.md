# Credenciales de Usuarios de Prueba

Este archivo centraliza todas las credenciales de usuarios de prueba del sistema C4A.

---

## Usuarios Principales

### 1. Administrador del Sistema

```
Email: admin@c4a.cl
Password: Admin123!
Rol: admin_sistema
Organización: C4A Admin
Nivel de suscripción: N/A (acceso total)
Redirige a: /admin/dashboard
```

**Permisos**:
- Acceso completo al panel de administración
- Gestión de todos los usuarios y organizaciones
- Configuración del sistema
- Monitoreo de seguridad
- Analytics avanzado
- Gestión de pagos y suscripciones

**Uso**:
```bash
# Login en el frontend
http://localhost:3000/login
Email: admin@c4a.cl
Password: Admin123!

# Luego serás redirigido a: /admin/dashboard
```

---

### 2. Usuario Empresarial

```
Email: empresa@c4a.cl
Password: empresarial123
Rol: admin_empresa
Organización: Empresa Demo
Nivel de suscripción: empresarial
Redirige a: /admin/dashboard (también es admin)
```

**Permisos**:
- Crear y gestionar evaluaciones
- Acceso a cuestionarios NIST CSF 2.0
- Acceso a cuestionarios COBIT 2019
- Generar reportes en PDF
- Gestionar usuarios de su organización
- Ver analytics de su organización

**Uso**:
```bash
# Login en el frontend
http://localhost:3000/login
Email: empresa@c4a.cl
Password: empresarial123

# Luego serás redirigido a: /admin/dashboard (porque es admin_empresa)
```

---

### 3. Usuario Normal (Evaluador)

```
Email: usuario@normal.cl
Password: Usuario123!
Rol: evaluador
Organización: Empresa Usuario Normal
Nivel de suscripción: pro
Redirige a: /app/dashboard
```

**Permisos**:
- Crear y responder evaluaciones
- Acceso a cuestionarios NIST CSF 2.0
- Acceso a cuestionarios COBIT 2019
- Generar reportes en PDF
- Ver analytics de sus evaluaciones

**Uso**:
```bash
# Login en el frontend
http://localhost:3000/login
Email: usuario@normal.cl
Password: Usuario123!

# Luego serás redirigido a: /app/dashboard
```

---

## Usuarios Adicionales (Si fueron creados)

### 3. Usuario Pro

```
Email: pro@c4a.cl
Password: pro123
Rol: evaluador
Organización: Empresa Pro
Nivel de suscripción: pro
Redirige a: /app/dashboard
```

**Permisos**:
- Crear evaluaciones limitadas
- Acceso a cuestionarios NIST CSF 2.0
- Acceso a cuestionarios COBIT 2019
- Generar reportes en PDF
- Límite de evaluaciones por mes

---

### 4. Usuario Gratuito

```
Email: gratuito@c4a.cl
Password: Gratuito123!
Rol: usuario_basico
Organización: Usuario Gratuito
Nivel de suscripción: gratuito
Redirige a: /app/dashboard
```

**Permisos**:
- Crear evaluaciones muy limitadas
- Solo cuestionarios NIST CSF 2.0 (básicos)
- Reportes básicos
- Límite muy bajo de evaluaciones por mes

---

## Roles del Sistema

### admin_sistema
- Acceso total al sistema
- Panel de administración completo
- Configuración del sistema
- Gestión de todos los usuarios y organizaciones

### admin_empresa
- Administrador de una organización específica
- Gestión de usuarios de su organización
- Acceso completo a evaluaciones y reportes de su organización

### evaluador
- Crear y responder evaluaciones
- Ver reportes de sus propias evaluaciones
- Acceso según nivel de suscripción

### usuario_basico
- Solo lectura de evaluaciones
- No puede crear evaluaciones
- Acceso muy limitado

### auditor
- Solo lectura de todo
- No puede modificar nada
- Acceso de auditoría

---

## Niveles de Suscripción

### Gratuito
- 10 preguntas NIST CSF 2.0
- 1 evaluación por mes
- Reportes básicos
- Sin soporte prioritario

### Pro
- 20 preguntas (10 NIST + 10 COBIT)
- 10 evaluaciones por mes
- Reportes completos con gráficos
- Soporte por email

### Empresarial
- 20 preguntas (10 NIST + 10 COBIT)
- Evaluaciones ilimitadas
- Reportes premium con benchmarking
- Soporte prioritario
- Múltiples usuarios
- Analytics avanzado

---

## Flujo de Redirección por Rol

```
Usuario hace login
    │
    ├── ¿Es admin_sistema o admin_empresa?
    │   │
    │   ├── Sí → Redirige a /admin/dashboard
    │   │
    │   └── No → Redirige a /app/dashboard
```

---

## Cómo Resetear Contraseñas

Si olvidaste una contraseña o necesitas resetearla:

### Opción 1: Resetear admin y empresa

```bash
docker exec -it c4a_backend python scripts/resetear_passwords.py
```

Esto reseteará:
- `admin@c4a.cl` → `Admin123!`
- `empresa@c4a.cl` → `empresarial123`

### Opción 2: Resetear TODAS las contraseñas

```bash
docker exec -it c4a_backend python scripts/resetear_passwords.py all
```

Esto reseteará todos los usuarios con contraseña: `{NombreUsuario}123!`

Ejemplo:
- `admin@c4a.cl` → `Admin123!`
- `empresa@c4a.cl` → `empresarial123`
- `juan@empresa.cl` → `Juan123!`

### Opción 3: Verificar usuarios

```bash
docker exec -it c4a_backend python scripts/verificar_usuarios.py
```

Esto mostrará todos los usuarios y sus datos, y corregirá las contraseñas de admin y empresa.

---

## Crear Nuevos Usuarios de Prueba

### Método 1: Script automatizado

```bash
docker exec -it c4a_backend python scripts/crear_usuarios_prueba.py
```

Este script creará usuarios de prueba con diferentes roles y niveles de suscripción.

### Método 2: Registro desde el frontend

1. Ve a `http://localhost:3000/registro`
2. Completa el formulario de registro
3. El usuario será creado con nivel `gratuito` por defecto
4. Un admin puede cambiar el rol y nivel desde el panel de administración

### Método 3: Desde la API

```bash
curl -X POST "http://localhost:8000/api/v1/auth/registro" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@ejemplo.cl",
    "password": "Password123!",
    "nombres": "Nuevo",
    "apellidos": "Usuario",
    "nombre_organizacion": "Mi Organización"
  }'
```

---

## Testing de Autenticación

### Test 1: Login como Admin

```bash
curl -X POST "http://localhost:8000/api/v1/auth/iniciar-sesion" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@c4a.cl",
    "password": "Admin123!"
  }'
```

Debería devolver:
- `access_token`
- `refresh_token`
- `usuario.rol.nombre` = "admin_sistema"

### Test 2: Login como Empresa

```bash
curl -X POST "http://localhost:8000/api/v1/auth/iniciar-sesion" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "empresa@c4a.cl",
    "password": "empresarial123"
  }'
```

Debería devolver:
- `access_token`
- `refresh_token`
- `usuario.organizacion.nivel_suscripcion` = "empresarial"

---

## Seguridad de Contraseñas

### Requisitos de contraseñas

Las contraseñas deben cumplir:
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Al menos un carácter especial (!@#$%^&*)

### Ejemplos válidos
- `Admin123!`
- `empresarial123`
- `pro123`
- `MiPassword@2024`
- `Segura#123`

### Ejemplos NO válidos
- `admin123` (sin mayúscula ni especial)
- `ADMIN123!` (sin minúscula)
- `Admin!` (muy corto)
- `Administrador` (sin número ni especial)

---

## Protección de Cuenta

El sistema incluye protección contra ataques de fuerza bruta:

- **3 intentos fallidos**: Advertencia
- **5 intentos fallidos**: Cuenta bloqueada por 15 minutos
- **10 intentos fallidos**: Cuenta bloqueada por 1 hora

Para desbloquear una cuenta:

```bash
docker exec -it c4a_backend python scripts/resetear_passwords.py
```

Esto desbloqueará y reseteará las contraseñas.

---

## Acceso a la Base de Datos

Si necesitas acceder directamente a la base de datos:

```bash
# Acceder a PostgreSQL
docker exec -it c4a_db psql -U c4a_user -d c4a_saas

# Ver usuarios
SELECT email, nombres, apellidos FROM usuarios;

# Ver organizaciones
SELECT nombre, nivel_suscripcion FROM organizaciones;

# Salir
\q
```

---

## Endpoints de Autenticación

### Login
```
POST /api/v1/auth/iniciar-sesion
Body: { "email": "string", "password": "string" }
```

### Registro
```
POST /api/v1/auth/registro
Body: {
  "email": "string",
  "password": "string",
  "nombres": "string",
  "apellidos": "string",
  "nombre_organizacion": "string"
}
```

### Mi Perfil
```
GET /api/v1/auth/mi-perfil
Headers: { "Authorization": "Bearer {token}" }
```

### Renovar Token
```
POST /api/v1/auth/renovar-token
Body: { "refresh_token": "string" }
```

### Cerrar Sesión
```
POST /api/v1/auth/cerrar-sesion
Headers: { "Authorization": "Bearer {token}" }
```

---

## Notas Importantes

1. **Nunca uses estas credenciales en producción**
   - Estas son solo para desarrollo y testing
   - En producción, usa contraseñas seguras únicas

2. **Las contraseñas están hasheadas en la BD**
   - Usando Argon2id (muy seguro)
   - No se pueden recuperar, solo resetear

3. **Los tokens JWT expiran**
   - Access token: 30 minutos
   - Refresh token: 7 días
   - Usa el refresh token para renovar

4. **Sesiones en Redis**
   - Las sesiones se guardan en Redis
   - Persisten entre reinicios (con volumen)

---

## Solución de Problemas

### No puedo hacer login
```bash
# Verifica que los servicios estén corriendo
docker-compose ps

# Verifica los logs del backend
docker-compose logs backend

# Resetea las contraseñas
docker exec -it c4a_backend python scripts/resetear_passwords.py
```

### Token inválido o expirado
```bash
# Vuelve a hacer login para obtener un nuevo token
# O usa el refresh token para renovar
```

### Usuario no existe
```bash
# Verifica los usuarios existentes
docker exec -it c4a_backend python scripts/verificar_usuarios.py

# O crea usuarios de prueba
docker exec -it c4a_backend python scripts/crear_usuarios_prueba.py
```

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0.0

Para más información, consulta el [INDICE_DOCUMENTACION.md](./INDICE_DOCUMENTACION.md)

