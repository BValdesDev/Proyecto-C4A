# Usuarios Reales en la Base de Datos

Este documento muestra todos los usuarios REALES que están actualmente en la base de datos del sistema C4A.

---

## 👑 Administradores del Sistema (2 usuarios)

### 1. Admin Principal
- **Email**: `admin@c4a.cl`
- **Nombre**: Admin Sistema
- **Rol**: `ADMIN_SISTEMA` (Administrador Sistema)
- **Organización**: C4A Admin
- **Nivel Suscripción**: GRATUITO
- **Password**: `Admin123!`
- **Redirige a**: `/admin/dashboard`
- **Permisos**: `["*:*"]` (Acceso total al sistema)

### 2. Admin Secundario
- **Email**: `frankbailey440@gmail.com`
- **Nombre**: Frank Bailey
- **Rol**: `ADMIN_SISTEMA` (Administrador Sistema)
- **Organización**: Empresa Ghost
- **Nivel Suscripción**: GRATUITO
- **Password**: `Password123!`
- **Redirige a**: `/admin/dashboard`
- **Permisos**: `["*:*"]` (Acceso total al sistema)

---

## 🏢 Administradores de Empresa (2 usuarios)

### 1. Admin Empresa Principal
- **Email**: `empresa@c4a.cl`
- **Nombre**: Usuario Empresarial
- **Rol**: `ADMIN_EMPRESA` (Administrador Empresa)
- **Organización**: Empresa Demo
- **Nivel Suscripción**: EMPRESARIAL
- **Password**: `empresarial123`
- **Redirige a**: `/admin/dashboard`
- **Permisos**: `["organizaciones:*", "usuarios:*", "evaluaciones:*", "reportes:*", "suscripciones:*"]`

### 2. Admin Empresa Secundario
- **Email**: `mantenedor@c4a.cl`
- **Nombre**: Admin Mantenedor
- **Rol**: `ADMIN_EMPRESA` (Administrador Empresa)
- **Organización**: C4A Administración
- **Nivel Suscripción**: GRATUITO
- **Password**: `Password123!`
- **Redirige a**: `/admin/dashboard`
- **Permisos**: `["organizaciones:*", "usuarios:*", "evaluaciones:*", "reportes:*", "suscripciones:*"]`

---

## 👨‍💼 Evaluadores/Usuarios Normales (7 usuarios)

### 1. Usuario Normal (Recién Creado)
- **Email**: `usuario@normal.cl`
- **Nombre**: Usuario Normal
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: Empresa Usuario Normal
- **Nivel Suscripción**: PRO
- **Password**: `Usuario123!`
- **Redirige a**: `/app/dashboard`
- **Permisos**: `["evaluaciones:crear", "evaluaciones:responder", "evaluaciones:ver", "reportes:ver"]`

### 2. Patricia Morales
- **Email**: `patricia@retailsolutions.cl`
- **Nombre**: Patricia Morales
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: Retail Solutions
- **Nivel Suscripción**: PRO
- **Password**: `Password123!`
- **Redirige a**: `/app/dashboard`

### 3. Juan Pérez
- **Email**: `juan@empresaabc.cl`
- **Nombre**: Juan Pérez
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: Empresa ABC
- **Nivel Suscripción**: PRO
- **Password**: `Password123!`
- **Redirige a**: `/app/dashboard`

### 4. Carlos Silva
- **Email**: `carlos@startup.cl`
- **Nombre**: Carlos Silva
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: Startup Innovadora
- **Nivel Suscripción**: GRATUITO
- **Password**: `Password123!`
- **Redirige a**: `/app/dashboard`

### 5. Ana Martínez
- **Email**: `ana@consultora.cl`
- **Nombre**: Ana Martínez
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: Consultora Digital
- **Nivel Suscripción**: PRO
- **Password**: `Password123!`
- **Redirige a**: `/app/dashboard`

### 6. Roberto Silva
- **Email**: `roberto@mineranorte.cl`
- **Nombre**: Roberto Silva
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: Minera del Norte
- **Nivel Suscripción**: GRATUITO
- **Password**: `Password123!`
- **Redirige a**: `/app/dashboard`

### 7. María González
- **Email**: `maria@techcorp.cl`
- **Nombre**: María González
- **Rol**: `EVALUADOR` (Evaluador)
- **Organización**: TechCorp Chile
- **Nivel Suscripción**: EMPRESARIAL
- **Password**: `Password123!`
- **Redirige a**: `/app/dashboard`

---

## 📊 Resumen Estadístico

| Categoría | Cantidad | Porcentaje |
|-----------|----------|------------|
| **Total Usuarios** | 11 | 100% |
| **Administradores Sistema** | 2 | 18.2% |
| **Administradores Empresa** | 2 | 18.2% |
| **Evaluadores** | 7 | 63.6% |

### Por Nivel de Suscripción:
- **GRATUITO**: 4 usuarios (36.4%)
- **PRO**: 4 usuarios (36.4%)
- **EMPRESARIAL**: 3 usuarios (27.3%)

### Por Organización:
- **Empresas con múltiples usuarios**: 0
- **Empresas con un usuario**: 11
- **Total organizaciones**: 11

---

## 🔐 Credenciales para Testing

### Para Panel de Administración:
```bash
# Admin Sistema Principal
Email: admin@c4a.cl
Password: Admin123!

# Admin Empresa Principal  
Email: empresa@c4a.cl
Password: empresarial123
```

### Para Dashboard de Usuario:
```bash
# Usuario Normal (Recién creado)
Email: usuario@normal.cl
Password: Usuario123!

# Cualquier otro evaluador
Email: patricia@retailsolutions.cl
Password: Password123!
```

### Para Testing de Diferentes Niveles:
```bash
# Nivel GRATUITO
Email: carlos@startup.cl
Password: Password123!

# Nivel PRO
Email: juan@empresaabc.cl
Password: Password123!

# Nivel EMPRESARIAL
Email: maria@techcorp.cl
Password: Password123!
```

---

## 🎯 Lógica de Redirección

```javascript
if (usuario.rol.nombre === 'admin_sistema' || usuario.rol.nombre === 'admin_empresa') {
    // Redirige a panel de administración
    navigate('/admin/dashboard')
} else {
    // Redirige a dashboard de usuario
    navigate('/app/dashboard')
}
```

**Resultado**:
- ✅ **4 usuarios** van a `/admin/dashboard` (todos los admins)
- ✅ **7 usuarios** van a `/app/dashboard` (todos los evaluadores)

---

## 🔄 Comandos para Gestión

### Ver todos los usuarios:
```bash
docker exec c4a_backend python scripts/verificar_roles_usuarios.py
```

### Resetear contraseñas principales:
```bash
docker exec c4a_backend python scripts/resetear_passwords.py
```

### Crear más usuarios de prueba:
```bash
docker exec c4a_backend python scripts/crear_usuarios_prueba.py
```

### Verificar usuarios específicos:
```bash
docker exec c4a_backend python scripts/verificar_usuarios.py
```

---

**Última actualización**: 21 de Octubre de 2025  
**Total usuarios activos**: 11  
**Estado**: Todos los usuarios están activos y funcionando correctamente



