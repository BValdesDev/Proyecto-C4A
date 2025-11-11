# Script de implementación automatizada del Panel de Administración C4A SaaS
# Autor: C4A Development Team
# Fecha: 16 Octubre 2025

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  IMPLEMENTACION PANEL DE ADMINISTRACION C4A" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar que estamos en el directorio correcto
Write-Host "[1/7] Verificando directorio..." -ForegroundColor Yellow
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "Error: No se encontro docker-compose.yml" -ForegroundColor Red
    Write-Host "Por favor ejecuta este script desde el directorio raiz del proyecto" -ForegroundColor Red
    exit 1
}
Write-Host "OK Directorio correcto" -ForegroundColor Green
Write-Host ""

# Paso 2: Obtener últimos cambios
Write-Host "[2/7] Obteniendo cambios desde GitHub..." -ForegroundColor Yellow
git checkout develop
git pull origin develop
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Cambios obtenidos exitosamente" -ForegroundColor Green
} else {
    Write-Host "Error al obtener cambios" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Paso 3: Detener contenedores
Write-Host "[3/7] Deteniendo contenedores..." -ForegroundColor Yellow
docker-compose down
Write-Host "OK Contenedores detenidos" -ForegroundColor Green
Write-Host ""

# Paso 4: Reconstruir imágenes
Write-Host "[4/7] Reconstruyendo imagenes Docker..." -ForegroundColor Yellow
Write-Host "Esto puede tomar varios minutos..." -ForegroundColor Gray
docker-compose build backend
docker-compose build frontend
Write-Host "OK Imagenes reconstruidas" -ForegroundColor Green
Write-Host ""

# Paso 5: Iniciar contenedores
Write-Host "[5/7] Iniciando contenedores..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "Esperando que los servicios esten listos..." -ForegroundColor Gray
Start-Sleep -Seconds 10
Write-Host "OK Contenedores iniciados" -ForegroundColor Green
Write-Host ""

# Paso 6: Verificar estado
Write-Host "[6/7] Verificando estado de servicios..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Paso 7: Actualizar datos (opcional)
Write-Host "[7/7] Deseas actualizar los datos de prueba? (s/n)" -ForegroundColor Yellow
$respuesta = Read-Host
if ($respuesta -eq "s" -or $respuesta -eq "S") {
    Write-Host "Actualizando datos de prueba..." -ForegroundColor Gray
    docker-compose exec -T backend python scripts/crear_usuarios_prueba.py
    Write-Host "Actualizando montos de suscripciones..." -ForegroundColor Gray
    docker-compose exec -T backend python scripts/actualizar_montos.py
    Write-Host "OK Datos actualizados" -ForegroundColor Green
} else {
    Write-Host "Datos no actualizados" -ForegroundColor Gray
}
Write-Host ""

# Resumen final
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  IMPLEMENTACION COMPLETADA" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "El panel de administracion ha sido implementado exitosamente." -ForegroundColor Green
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Yellow
Write-Host "1. Abre tu navegador en: http://localhost:3000/login" -ForegroundColor White
Write-Host "2. Inicia sesion con:" -ForegroundColor White
Write-Host "   Email: frankbailey440@gmail.com" -ForegroundColor Cyan
Write-Host "   Password: Fr@nk15481548" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Navega a las nuevas paginas:" -ForegroundColor White
Write-Host "   - Pagos: http://localhost:3000/admin/payments" -ForegroundColor Cyan
Write-Host "   - Analytics: http://localhost:3000/admin/analytics" -ForegroundColor Cyan
Write-Host "   - Seguridad: http://localhost:3000/admin/security" -ForegroundColor Cyan
Write-Host "   - Notificaciones: http://localhost:3000/admin/notifications" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para ver los logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f backend" -ForegroundColor White
Write-Host "  docker-compose logs -f frontend" -ForegroundColor White
Write-Host ""
Write-Host "Para mas informacion, revisa: GUIA_IMPLEMENTACION_ADMIN_PANEL.md" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan









