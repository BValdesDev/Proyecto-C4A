# Script para ejecutar tests E2E con Chrome DevTools MCP
# Requiere tener el servidor MCP corriendo

Write-Host "🚀 Iniciando tests E2E con Chrome DevTools MCP" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Verificar que Node.js está instalado
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Node.js no está instalado" -ForegroundColor Red
    exit 1
}

# Verificar que el backend está corriendo
Write-Host "`n📡 Verificando que el backend está corriendo..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend está corriendo" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error: El backend no está corriendo en http://localhost:8000" -ForegroundColor Red
    Write-Host "   Por favor inicia el backend con: docker-compose up -d backend" -ForegroundColor Yellow
    exit 1
}

# Verificar que el frontend está corriendo
Write-Host "`n📡 Verificando que el frontend está corriendo..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend está corriendo" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error: El frontend no está corriendo en http://localhost:3000" -ForegroundColor Red
    Write-Host "   Por favor inicia el frontend con: docker-compose up -d frontend" -ForegroundColor Yellow
    exit 1
}

# Instalar chrome-devtools-mcp si no está instalado
Write-Host "`n📦 Verificando instalación de chrome-devtools-mcp..." -ForegroundColor Yellow
npx chrome-devtools-mcp@latest --help | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ chrome-devtools-mcp está disponible" -ForegroundColor Green
} else {
    Write-Host "❌ Error: No se pudo instalar chrome-devtools-mcp" -ForegroundColor Red
    exit 1
}

Write-Host "`n🎯 Ejecutando tests E2E..." -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Green

# Ejecutar el script de testing Node.js
node ../backend/tests/e2e-mcp-tests.js

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Tests E2E completados exitosamente" -ForegroundColor Green
} else {
    Write-Host "`n❌ Tests E2E fallaron" -ForegroundColor Red
    exit 1
}




