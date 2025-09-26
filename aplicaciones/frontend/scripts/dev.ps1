# Script de desarrollo para el frontend
# Uso: .\scripts\dev.ps1 [opciones]

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "test", "build", "deploy", "clean")]
    [string]$Action = "start",
    
    [switch]$Watch,
    [switch]$Coverage,
    [switch]$UI,
    [switch]$Help
)

# Colores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Función para imprimir mensajes
function Write-DevMessage {
    param([string]$Message)
    Write-Host "[DEV] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Función para mostrar ayuda
function Show-Help {
    Write-Host "Script de desarrollo para el frontend" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Uso: .\scripts\dev.ps1 [opciones]" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Acciones:" -ForegroundColor $Blue
    Write-Host "  start             Iniciar servidor de desarrollo"
    Write-Host "  test              Ejecutar tests"
    Write-Host "  build             Construir aplicación"
    Write-Host "  deploy            Desplegar aplicación"
    Write-Host "  clean             Limpiar archivos temporales"
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor $Blue
    Write-Host "  -Watch            Ejecutar en modo watch"
    Write-Host "  -Coverage         Incluir cobertura de código"
    Write-Host "  -UI               Ejecutar con interfaz visual"
    Write-Host "  -Help             Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor $Blue
    Write-Host "  .\scripts\dev.ps1 start                    # Iniciar desarrollo"
    Write-Host "  .\scripts\dev.ps1 test -Coverage           # Tests con cobertura"
    Write-Host "  .\scripts\dev.ps1 build -Watch            # Build en modo watch"
    Write-Host "  .\scripts\dev.ps1 clean                    # Limpiar archivos"
}

# Mostrar ayuda si se solicita
if ($Help) {
    Show-Help
    exit 0
}

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "package.json")) {
    Write-Error "No se encontró package.json. Ejecuta este script desde el directorio del frontend."
    exit 1
}

# Función para verificar estado del proyecto
function Test-ProjectStatus {
    Write-DevMessage "Verificando estado del proyecto..."
    
    # Verificar node_modules
    if (-not (Test-Path "node_modules")) {
        Write-Warning "node_modules no encontrado. Instalando dependencias..."
        npm install
    }
    
    # Verificar package-lock.json
    if (-not (Test-Path "package-lock.json")) {
        Write-Warning "package-lock.json no encontrado. Generando..."
        npm install
    }
    
    # Verificar configuración
    $configFiles = @("vite.config.ts", "tsconfig.json", "tailwind.config.js")
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Write-Success "Archivo de configuración encontrado: $file"
        } else {
            Write-Warning "Archivo de configuración no encontrado: $file"
        }
    }
    
    Write-Success "Estado del proyecto verificado"
}

# Función para iniciar desarrollo
function Start-Development {
    Write-DevMessage "Iniciando servidor de desarrollo..."
    
    # Verificar que el puerto 3000 esté disponible
    $port = 3000
    $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    
    if ($portInUse) {
        Write-Warning "Puerto $port está en uso. Intentando con puerto alternativo..."
        $env:PORT = "3001"
    }
    
    Write-DevMessage "Servidor disponible en: http://localhost:$($env:PORT ?? '3000')"
    Write-DevMessage "Presiona Ctrl+C para detener el servidor"
    
    npm run dev
}

# Función para ejecutar tests
function Invoke-Tests {
    Write-DevMessage "Ejecutando tests..."
    
    if ($Watch) {
        Write-DevMessage "Ejecutando en modo watch..."
        npm run test:watch
    } elseif ($UI) {
        Write-DevMessage "Ejecutando con interfaz visual..."
        npm run test:ui
    } elseif ($Coverage) {
        Write-DevMessage "Ejecutando con cobertura..."
        npm run test:coverage
    } else {
        npm run test
    }
}

# Función para construir aplicación
function Invoke-Build {
    Write-DevMessage "Construyendo aplicación..."
    
    if ($Watch) {
        Write-DevMessage "Ejecutando build en modo watch..."
        npm run build:watch
    } else {
        npm run build
    }
}

# Función para desplegar aplicación
function Invoke-Deploy {
    Write-DevMessage "Desplegando aplicación..."
    
    # Verificar que el build existe
    if (-not (Test-Path "dist")) {
        Write-Warning "Build no encontrado. Construyendo aplicación..."
        Invoke-Build
    }
    
    # Aquí iría la lógica de deployment
    # Por ahora solo mostramos un mensaje
    Write-DevMessage "Deployment configurado para Railway"
    Write-DevMessage "Para desplegar, ejecuta: npm run deploy"
}

# Función para limpiar archivos
function Clear-Project {
    Write-DevMessage "Limpiando archivos temporales..."
    
    # Limpiar dist
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist"
        Write-Success "Directorio dist eliminado"
    }
    
    # Limpiar node_modules/.vite
    if (Test-Path "node_modules/.vite") {
        Remove-Item -Recurse -Force "node_modules/.vite"
        Write-Success "Cache de Vite eliminado"
    }
    
    # Limpiar archivos de test
    if (Test-Path "coverage") {
        Remove-Item -Recurse -Force "coverage"
        Write-Success "Directorio coverage eliminado"
    }
    
    Write-Success "Limpieza completada"
}

# Ejecutar acción solicitada
Write-DevMessage "Iniciando proceso de desarrollo..."
Write-DevMessage "Acción: $Action"
Write-DevMessage "Watch: $Watch"
Write-DevMessage "Coverage: $Coverage"
Write-DevMessage "UI: $UI"

# Verificar estado del proyecto
Test-ProjectStatus

# Ejecutar acción
switch ($Action) {
    "start" {
        Start-Development
    }
    "test" {
        Invoke-Tests
    }
    "build" {
        Invoke-Build
    }
    "deploy" {
        Invoke-Deploy
    }
    "clean" {
        Clear-Project
    }
    default {
        Write-Error "Acción no válida: $Action"
        Show-Help
        exit 1
    }
}

Write-Success "Proceso completado exitosamente!"

