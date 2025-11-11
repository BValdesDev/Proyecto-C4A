# Script para detener C4A SaaS con Docker Desktop

Write-Host "=== C4A SaaS - Deteniendo servicios ===" -ForegroundColor Yellow

# Detener y eliminar contenedores
Write-Host "Deteniendo contenedores..." -ForegroundColor Yellow
docker-compose down

# Limpiar volúmenes si se desea (descomenta la siguiente línea)
# docker-compose down -v

Write-Host "Servicios detenidos correctamente" -ForegroundColor Green

