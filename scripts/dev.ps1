# Script para desarrollo de C4A SaaS
# Comandos útiles para desarrollo

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "C4A SaaS - Comandos de Desarrollo" -ForegroundColor Blue
    Write-Host "=================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Uso: .\dev.ps1 [comando]"
    Write-Host ""
    Write-Host "Comandos disponibles:"
    Write-Host "  start        Iniciar todos los servicios"
    Write-Host "  stop         Parar todos los servicios"
    Write-Host "  restart      Reiniciar todos los servicios"
    Write-Host "  logs         Ver logs de todos los servicios"
    Write-Host "  logs-backend Ver logs del backend"
    Write-Host "  logs-frontend Ver logs del frontend"
    Write-Host "  logs-db      Ver logs de la base de datos"
    Write-Host "  shell-backend Acceder al shell del backend"
    Write-Host "  shell-db     Acceder a la base de datos"
    Write-Host "  shell-redis  Acceder a Redis"
    Write-Host "  migrate      Ejecutar migraciones"
    Write-Host "  seed         Ejecutar seeds"
    Write-Host "  reset-db     Resetear base de datos"
    Write-Host "  test         Ejecutar tests"
    Write-Host "  build        Construir imágenes"
    Write-Host "  clean        Limpiar contenedores y volúmenes"
    Write-Host "  status       Ver estado de servicios"
    Write-Host "  help         Mostrar esta ayuda"
}

function Start-Services {
    Write-Host "🚀 Iniciando servicios..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "✅ Servicios iniciados" -ForegroundColor Green
}

function Stop-Services {
    Write-Host "🛑 Parando servicios..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Servicios parados" -ForegroundColor Green
}

function Restart-Services {
    Write-Host "🔄 Reiniciando servicios..." -ForegroundColor Yellow
    docker-compose restart
    Write-Host "✅ Servicios reiniciados" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "📋 Mostrando logs..." -ForegroundColor Cyan
    docker-compose logs -f
}

function Show-BackendLogs {
    Write-Host "📋 Mostrando logs del backend..." -ForegroundColor Cyan
    docker-compose logs -f backend
}

function Show-FrontendLogs {
    Write-Host "📋 Mostrando logs del frontend..." -ForegroundColor Cyan
    docker-compose logs -f frontend
}

function Show-DbLogs {
    Write-Host "📋 Mostrando logs de la base de datos..." -ForegroundColor Cyan
    docker-compose logs -f db
}

function Enter-BackendShell {
    Write-Host "🐚 Accediendo al shell del backend..." -ForegroundColor Cyan
    docker-compose exec backend bash
}

function Enter-DbShell {
    Write-Host "🐚 Accediendo a la base de datos..." -ForegroundColor Cyan
    docker-compose exec db psql -U c4a_user -d c4a_saas
}

function Enter-RedisShell {
    Write-Host "🐚 Accediendo a Redis..." -ForegroundColor Cyan
    docker-compose exec redis redis-cli
}

function Invoke-Migrations {
    Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor Yellow
    docker-compose exec backend python scripts/init_db.py
    Write-Host "✅ Migraciones ejecutadas" -ForegroundColor Green
}

function Invoke-Seeds {
    Write-Host "🌱 Ejecutando seeds..." -ForegroundColor Yellow
    docker-compose exec backend python scripts/run_seeds.py
    Write-Host "✅ Seeds ejecutados" -ForegroundColor Green
}

function Reset-Database {
    Write-Host "⚠️  Reseteando base de datos..." -ForegroundColor Red
    $confirm = Read-Host "¿Estás seguro? Esto eliminará todos los datos (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        docker-compose exec backend python scripts/reset_db.py
        Write-Host "✅ Base de datos reseteada" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

function Invoke-Tests {
    Write-Host "🧪 Ejecutando tests..." -ForegroundColor Yellow
    docker-compose exec backend python -m pytest
    Write-Host "✅ Tests completados" -ForegroundColor Green
}

function Build-Images {
    Write-Host "🔨 Construyendo imágenes..." -ForegroundColor Yellow
    docker-compose build
    Write-Host "✅ Imágenes construidas" -ForegroundColor Green
}

function Clean-Environment {
    Write-Host "🧹 Limpiando entorno..." -ForegroundColor Yellow
    $confirm = Read-Host "¿Estás seguro? Esto eliminará contenedores y volúmenes (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        docker-compose down -v --remove-orphans
        docker system prune -f
        Write-Host "✅ Entorno limpiado" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
}

function Show-Status {
    Write-Host "📊 Estado de servicios:" -ForegroundColor Cyan
    docker-compose ps
}

# Ejecutar comando
switch ($Command.ToLower()) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { Restart-Services }
    "logs" { Show-Logs }
    "logs-backend" { Show-BackendLogs }
    "logs-frontend" { Show-FrontendLogs }
    "logs-db" { Show-DbLogs }
    "shell-backend" { Enter-BackendShell }
    "shell-db" { Enter-DbShell }
    "shell-redis" { Enter-RedisShell }
    "migrate" { Invoke-Migrations }
    "seed" { Invoke-Seeds }
    "reset-db" { Reset-Database }
    "test" { Invoke-Tests }
    "build" { Build-Images }
    "clean" { Clean-Environment }
    "status" { Show-Status }
    "help" { Show-Help }
    default { 
        Write-Host "❌ Comando no reconocido: $Command" -ForegroundColor Red
        Show-Help
    }
}
















