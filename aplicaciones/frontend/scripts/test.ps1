# Script de testing para el frontend
# Uso: .\scripts\test.ps1 [opciones]

param(
    [Parameter(Position=0)]
    [ValidateSet("unit", "integration", "e2e", "all")]
    [string]$Type = "unit",
    
    [switch]$Coverage,
    [switch]$Watch,
    [switch]$UI,
    [switch]$Help
)

# Colores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Función para imprimir mensajes
function Write-TestMessage {
    param([string]$Message)
    Write-Host "[TEST] $Message" -ForegroundColor $Blue
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
    Write-Host "Script de testing para el frontend" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Uso: .\scripts\test.ps1 [opciones]" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor $Blue
    Write-Host "  -Type TYPE        Tipo de test (unit, integration, e2e, all)"
    Write-Host "  -Coverage         Incluir cobertura de código"
    Write-Host "  -Watch            Ejecutar en modo watch"
    Write-Host "  -UI               Ejecutar con interfaz visual"
    Write-Host "  -Help             Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor $Blue
    Write-Host "  .\scripts\test.ps1 -Type unit                    # Tests unitarios"
    Write-Host "  .\scripts\test.ps1 -Type unit -Coverage          # Tests unitarios con cobertura"
    Write-Host "  .\scripts\test.ps1 -Type all -Watch              # Todos los tests en modo watch"
    Write-Host "  .\scripts\test.ps1 -Type unit -UI                # Tests unitarios con UI"
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

# Verificar que node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Warning "node_modules no encontrado. Instalando dependencias..."
    npm install
}

# Función para ejecutar tests
function Invoke-Tests {
    param(
        [string]$TestType,
        [bool]$IncludeCoverage
    )
    
    Write-TestMessage "Ejecutando tests de tipo: $TestType"
    
    switch ($TestType) {
        "unit" {
            if ($IncludeCoverage) {
                Write-TestMessage "Ejecutando tests unitarios con cobertura..."
                npm run test:coverage
            } else {
                Write-TestMessage "Ejecutando tests unitarios..."
                npm run test
            }
        }
        "integration" {
            Write-TestMessage "Ejecutando tests de integración..."
            npm run test:integration
        }
        "e2e" {
            Write-TestMessage "Ejecutando tests end-to-end..."
            npm run test:e2e
        }
        "all" {
            Write-TestMessage "Ejecutando todos los tests..."
            npm run test:all
        }
        default {
            Write-Error "Tipo de test no válido: $TestType"
            Show-Help
            exit 1
        }
    }
}

# Ejecutar tests
Write-TestMessage "Iniciando proceso de testing..."
Write-TestMessage "Tipo: $Type"
Write-TestMessage "Cobertura: $Coverage"
Write-TestMessage "Watch: $Watch"
Write-TestMessage "UI: $UI"

# Ejecutar tests según las opciones
if ($Watch) {
    Write-TestMessage "Ejecutando en modo watch..."
    npm run test:watch
} elseif ($UI) {
    Write-TestMessage "Ejecutando con interfaz visual..."
    npm run test:ui
} else {
    Invoke-Tests -TestType $Type -IncludeCoverage $Coverage
}

Write-Success "Tests completados exitosamente!"

