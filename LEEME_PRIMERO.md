# Bienvenido a C4A - Plataforma de Autodiagnóstico de Ciberseguridad

## Inicio Rápido en 3 Pasos

### 1. Abrir una terminal en este directorio

```bash
cd "c4a-autodiagnostico"
```

### 2. Iniciar el proyecto con Docker

```bash
docker-compose up -d
```

### 3. Acceder a la aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

---

## Credenciales de Prueba

### Administrador del Sistema
```
Email: admin@c4a.cl
Password: Admin123!
Redirige a: /admin/dashboard
```

### Usuario Empresarial
```
Email: empresa@c4a.cl
Password: empresarial123
Redirige a: /admin/dashboard
```

---

## Qué Incluye Este Proyecto

### Sistema de Autenticación
- Login seguro con JWT
- Autenticación multifactor (MFA)
- Detección de bots
- Protección contra ataques de fuerza bruta

### Panel de Administración
- Dashboard con analytics en tiempo real
- Gestión de usuarios y organizaciones
- Monitoreo de seguridad
- Gestión de pagos y suscripciones
- Configuración del sistema

### Evaluaciones de Ciberseguridad
- Cuestionarios basados en NIST CSF 2.0
- Cuestionarios basados en COBIT 2019
- Generación de reportes en PDF
- Benchmarking sectorial
- Recomendaciones personalizadas

### Sistema de Suscripciones
- **Gratuito**: Cuestionarios NIST CSF básicos
- **Pro**: NIST CSF + COBIT 2019
- **Empresarial**: Todo lo anterior + características avanzadas

---

## Documentación Disponible

### Para Empezar
1. **[INDICE_DOCUMENTACION.md](./INDICE_DOCUMENTACION.md)** - Índice completo de toda la documentación
2. **[CREDENCIALES.md](./CREDENCIALES.md)** - Todas las credenciales de usuarios de prueba
3. **[README.md](./README.md)** - Documentación técnica principal

### Para Desarrolladores
- **[GITFLOW.md](./GITFLOW.md)** - Guía de Git Flow y convenciones
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Cómo contribuir al proyecto
- **[DASHBOARD_API_DOCS.md](./aplicaciones/backend/DASHBOARD_API_DOCS.md)** - Documentación de la API
- **[MCP_CHROME_DEVTOOLS.md](./MCP_CHROME_DEVTOOLS.md)** - Testing E2E con Chrome DevTools MCP

### Para Administradores
- **[GUIA_IMPLEMENTACION_ADMIN_PANEL.md](./GUIA_IMPLEMENTACION_ADMIN_PANEL.md)** - Guía del panel de administración
- **[INSTRUCCIONES_RAPIDAS.md](./INSTRUCCIONES_RAPIDAS.md)** - Instrucciones rápidas de uso

---

## Estructura del Proyecto

```
c4a-autodiagnostico/
├── aplicaciones/
│   ├── backend/              # API FastAPI
│   │   ├── app/
│   │   │   ├── api/          # Endpoints de la API
│   │   │   ├── core/         # Configuración y seguridad
│   │   │   ├── modelos/      # Modelos de base de datos
│   │   │   ├── servicios/    # Lógica de negocio
│   │   │   └── main.py       # Entry point
│   │   ├── alembic/          # Migraciones de BD
│   │   └── scripts/          # Scripts de utilidad
│   │
│   └── frontend/             # Aplicación React
│       ├── src/
│       │   ├── componentes/  # Componentes React
│       │   ├── pages/        # Páginas
│       │   ├── hooks/        # Custom hooks
│       │   └── utilidades/   # Utilidades
│       └── package.json
│
├── scripts/                  # Scripts de ayuda
├── docker-compose.yml        # Configuración Docker
└── README.md                 # Este archivo
```

---

## Comandos Útiles

### Docker

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Ver estado de servicios
docker-compose ps

# Reconstruir todo desde cero
docker-compose down -v
docker-compose up -d --build
```

### Acceso a Contenedores

```bash
# Acceder al backend
docker exec -it c4a_backend bash

# Acceder al frontend
docker exec -it c4a_frontend sh

# Acceder a la base de datos
docker exec -it c4a_db psql -U c4a_user -d c4a_saas
```

### Scripts de Utilidad

```bash
# Resetear contraseñas de admin y empresa
docker exec -it c4a_backend python scripts/resetear_passwords.py

# Resetear TODAS las contraseñas
docker exec -it c4a_backend python scripts/resetear_passwords.py all

# Verificar usuarios y credenciales
docker exec -it c4a_backend python scripts/verificar_usuarios.py

# Debug de organización
docker exec -it c4a_backend python scripts/debug_organizacion.py

# Crear frameworks NIST y COBIT
docker exec -it c4a_backend python scripts/crear_frameworks.py

# Crear usuarios de prueba
docker exec -it c4a_backend python scripts/crear_usuarios_prueba.py
```

---

## Endpoints Principales de la API

### Autenticación
- `POST /api/v1/auth/iniciar-sesion` - Login
- `POST /api/v1/auth/registro` - Registro de usuarios
- `POST /api/v1/auth/renovar-token` - Renovar token
- `GET /api/v1/auth/mi-perfil` - Perfil del usuario actual

### Administración (Solo Admins)
- `GET /api/v1/admin/dashboard` - Dashboard de administración
- `GET /api/v1/admin/usuarios` - Listar usuarios
- `GET /api/v1/admin/analytics` - Analytics del sistema
- `GET /api/v1/admin/security` - Métricas de seguridad

### Evaluaciones
- `GET /api/v1/evaluaciones` - Mis evaluaciones
- `POST /api/v1/evaluaciones` - Crear evaluación
- `GET /api/v1/evaluaciones/{id}` - Ver evaluación
- `POST /api/v1/evaluaciones/{id}/responder` - Responder evaluación

### Reportes
- `POST /api/v1/reportes/generar` - Generar reporte PDF
- `GET /api/v1/reportes/{id}` - Descargar reporte

### Cuestionarios
- `GET /api/v1/cuestionarios/nivel/{nivel}` - Obtener cuestionario
  - Niveles: gratuito, pro, empresarial

---

## Solución de Problemas

### El frontend no carga
```bash
docker-compose logs frontend
docker-compose restart frontend
```

### Error de base de datos
```bash
docker-compose logs db
docker-compose restart db
```

### Error de autenticación
```bash
# Resetear contraseñas
docker exec -it c4a_backend python scripts/resetear_passwords.py
```

### Reconstruir todo
```bash
docker-compose down -v
docker-compose up -d --build
```

---

## Tecnologías Utilizadas

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL 15
- Redis 7
- Alembic (migraciones)

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Radix UI
- Zustand (estado global)
- Recharts (gráficos)

### DevOps
- Docker & Docker Compose
- Nginx (producción)
- GitHub Actions (CI/CD)

---

## Características de Seguridad

- Hashing de contraseñas con Argon2id
- Tokens JWT con acceso y refresco
- Rate limiting en endpoints sensibles
- Logs de auditoría completos
- Detección de bots y ataques
- Bloqueo de cuenta tras intentos fallidos
- Protección CSRF
- Headers de seguridad

---

## Próximos Pasos

1. Iniciar el proyecto con Docker
2. Probar el login con las credenciales de prueba
3. Explorar el panel de administración (login como admin)
4. Crear una evaluación (login como empresa)
5. Generar un reporte PDF
6. Revisar la documentación completa en [INDICE_DOCUMENTACION.md](./INDICE_DOCUMENTACION.md)

---

## Soporte

- **Issues**: https://github.com/cherrera0001/c4a-autodiagnostico/issues
- **Email**: contacto@c4a.cl
- **Documentación**: Ver [INDICE_DOCUMENTACION.md](./INDICE_DOCUMENTACION.md)

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Estado**: En desarrollo activo

A trabajar!

