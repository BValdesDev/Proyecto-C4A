# Script de inicio para C4A SaaS con Docker Desktop
# Ejecuta este script para levantar todos los servicios

Write-Host "=== C4A SaaS - Iniciando servicios con Docker Desktop ===" -ForegroundColor Green

# Verificar que Docker Desktop esté ejecutándose
Write-Host "Verificando Docker Desktop..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "Docker Desktop está ejecutándose" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker Desktop no está ejecutándose. Por favor inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Limpiar contenedores anteriores si existen
Write-Host "Limpiando contenedores anteriores..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# Construir las imágenes
Write-Host "Construyendo imágenes Docker..." -ForegroundColor Yellow
docker-compose build --no-cache

# Levantar los servicios
Write-Host "Iniciando servicios..." -ForegroundColor Yellow
docker-compose up -d

# Esperar a que los servicios estén listos
Write-Host "Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar el estado de los servicios
Write-Host "Verificando estado de los servicios..." -ForegroundColor Yellow
docker-compose ps

Write-Host "=== Servicios iniciados ===" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Base de datos: localhost:5432" -ForegroundColor Cyan
Write-Host "Redis: localhost:6379" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver los logs: docker-compose logs -f" -ForegroundColor Yellow
Write-Host "Para detener: docker-compose down" -ForegroundColor Yellow

