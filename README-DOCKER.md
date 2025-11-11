# C4A SaaS - Guía de Docker Desktop

Esta guía te ayudará a levantar el proyecto C4A SaaS usando Docker Desktop.

## Requisitos Previos

1. **Docker Desktop** instalado y ejecutándose
2. **PowerShell** (incluido en Windows 10/11)
3. Al menos **4GB de RAM** disponibles para Docker

## Inicio Rápido

### 1. Preparar el entorno

```powershell
# Navegar al directorio del proyecto
cd "C:\Users\Brayatan\Desktop\c4a 23-10\c4a github\c4a-autodiagnostico"

# Verificar que Docker Desktop esté ejecutándose
docker version
```

### 2. Levantar los servicios

```powershell
# Opción 1: Usar el script automatizado
.\start-docker.ps1

# Opción 2: Comandos manuales
docker-compose up -d --build
```

### 3. Verificar que todo funcione

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Frontend | 3000 | Aplicación React con Vite |
| Backend | 8000 | API FastAPI |
| PostgreSQL | 5432 | Base de datos principal |
| Redis | 6379 | Caché y sesiones |

## Comandos Útiles

### Ver logs de todos los servicios
```powershell
docker-compose logs -f
```

### Ver logs de un servicio específico
```powershell
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Reiniciar un servicio
```powershell
docker-compose restart backend
```

### Detener todos los servicios
```powershell
.\stop-docker.ps1
# o
docker-compose down
```

### Limpiar todo (incluyendo volúmenes)
```powershell
docker-compose down -v
docker system prune -f
```

## Solución de Problemas

### Error: Puerto ya en uso
Si obtienes un error de puerto ocupado:
```powershell
# Verificar qué está usando el puerto
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Detener el proceso que usa el puerto
taskkill /PID <PID_NUMBER> /F
```

### Error: Docker Desktop no está ejecutándose
1. Abre Docker Desktop
2. Espera a que aparezca el ícono verde
3. Ejecuta nuevamente el script

### Error: Memoria insuficiente
1. Abre Docker Desktop
2. Ve a Settings > Resources
3. Aumenta la memoria asignada a 4GB o más

### Reconstruir desde cero
```powershell
# Detener todo
docker-compose down -v

# Limpiar imágenes
docker system prune -a -f

# Reconstruir
docker-compose up -d --build
```

## Configuración Avanzada

### Variables de Entorno
Copia `env.example` a `.env` y ajusta las variables según tu entorno:

```powershell
copy env.example .env
```

### Perfiles de Docker Compose

#### Desarrollo (por defecto)
```powershell
docker-compose up -d
```

#### Con monitoreo
```powershell
docker-compose --profile monitoring up -d
```

#### Producción
```powershell
docker-compose --profile production up -d
```

## Estructura del Proyecto

```
c4a-autodiagnostico/
├── aplicaciones/
│   ├── backend/          # API FastAPI
│   └── frontend/         # Aplicación React
├── docker-compose.yml    # Configuración de servicios
├── start-docker.ps1     # Script de inicio
├── stop-docker.ps1      # Script de parada
└── README-DOCKER.md     # Esta guía
```

## Soporte

Si encuentras problemas:
1. Verifica que Docker Desktop esté ejecutándose
2. Revisa los logs: `docker-compose logs -f`
3. Reinicia Docker Desktop si es necesario
4. Consulta la documentación del proyecto principal

