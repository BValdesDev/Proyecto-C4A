# Script para ver el estado del proyecto C4A
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "                        ESTADO DEL PROYECTO C4A                                " -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

# Verificar estado de contenedores
Write-Host "Verificando contenedores..." -ForegroundColor Yellow
$containers = docker-compose ps --format json 2>$null | ConvertFrom-Json

if ($containers) {
    Write-Host ""
    Write-Host "SERVICIOS:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($container in $containers) {
        $status = if ($container.State -eq "running") { "CORRIENDO" } else { "DETENIDO" }
        $color = if ($container.State -eq "running") { "Green" } else { "Red" }
        $icon = if ($container.State -eq "running") { "[OK]" } else { "[X]" }
        
        Write-Host "   $icon $($container.Service.PadRight(15)) - $status" -ForegroundColor $color
    }
    
    Write-Host ""
    Write-Host "URLS DE ACCESO:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Frontend:          http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API:       http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs:          http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    
    Write-Host "CREDENCIALES:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Admin:    admin@c4a.cl / Admin123!" -ForegroundColor White
    Write-Host "   Empresa:  empresa@c4a.cl / empresarial123" -ForegroundColor White
    Write-Host ""
    
    Write-Host "COMANDOS UTILES:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Ver logs:       docker-compose logs -f" -ForegroundColor Gray
    Write-Host "   Detener:        docker-compose down" -ForegroundColor Gray
    Write-Host "   Reiniciar:      docker-compose restart" -ForegroundColor Gray
    Write-Host "   Ver este menu:  .\ver-estado.ps1" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "   [!] No hay contenedores corriendo" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Para iniciar el proyecto:" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d" -ForegroundColor White
    Write-Host ""
}

Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""




