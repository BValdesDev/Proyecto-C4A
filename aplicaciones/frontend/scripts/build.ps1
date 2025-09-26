# Script de build y deployment para el frontend
# Uso: .\scripts\build.ps1 [opciones]

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "staging", "production")]
    [string]$Environment = "dev",
    
    [switch]$Clean,
    [switch]$Analyze,
    [switch]$Help
)

# Colores para output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Función para imprimir mensajes
function Write-BuildMessage {
    param([string]$Message)
    Write-Host "[BUILD] $Message" -ForegroundColor $Blue
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
    Write-Host "Script de build y deployment para el frontend" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Uso: .\scripts\build.ps1 [opciones]" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor $Blue
    Write-Host "  -Environment ENV   Entorno (dev, staging, production)"
    Write-Host "  -Clean             Limpiar build anterior"
    Write-Host "  -Analyze           Analizar bundle"
    Write-Host "  -Help              Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor $Blue
    Write-Host "  .\scripts\build.ps1 -Environment dev              # Build desarrollo"
    Write-Host "  .\scripts\build.ps1 -Environment production -Clean # Build producción limpio"
    Write-Host "  .\scripts\build.ps1 -Environment staging -Analyze  # Build staging con análisis"
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

# Función para limpiar build anterior
function Clear-Build {
    Write-BuildMessage "Limpiando build anterior..."
    
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force "dist"
        Write-Success "Directorio dist eliminado"
    }
    
    if (Test-Path "node_modules/.vite") {
        Remove-Item -Recurse -Force "node_modules/.vite"
        Write-Success "Cache de Vite eliminado"
    }
}

# Función para verificar dependencias
function Test-Dependencies {
    Write-BuildMessage "Verificando dependencias..."
    
    if (-not (Test-Path "node_modules")) {
        Write-Warning "node_modules no encontrado. Instalando dependencias..."
        npm install
    }
    
    # Verificar que todas las dependencias están instaladas
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    $missingDeps = @()
    
    foreach ($dep in $packageJson.dependencies.PSObject.Properties.Name) {
        if (-not (Test-Path "node_modules/$dep")) {
            $missingDeps += $dep
        }
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-Warning "Dependencias faltantes: $($missingDeps -join ', ')"
        Write-BuildMessage "Instalando dependencias faltantes..."
        npm install
    }
    
    Write-Success "Dependencias verificadas"
}

# Función para ejecutar linting
function Invoke-Linting {
    Write-BuildMessage "Ejecutando linting..."
    
    try {
        npm run lint
        Write-Success "Linting completado sin errores"
    } catch {
        Write-Error "Errores de linting encontrados"
        exit 1
    }
}

# Función para ejecutar tests
function Invoke-Tests {
    Write-BuildMessage "Ejecutando tests..."
    
    try {
        npm run test
        Write-Success "Tests completados exitosamente"
    } catch {
        Write-Error "Tests fallaron"
        exit 1
    }
}

# Función para ejecutar type checking
function Invoke-TypeCheck {
    Write-BuildMessage "Ejecutando verificación de tipos..."
    
    try {
        npm run type-check
        Write-Success "Verificación de tipos completada"
    } catch {
        Write-Error "Errores de tipos encontrados"
        exit 1
    }
}

# Función para ejecutar build
function Invoke-Build {
    param([string]$Env)
    
    Write-BuildMessage "Ejecutando build para entorno: $Env"
    
    # Configurar variables de entorno
    $env:NODE_ENV = $Env
    
    switch ($Env) {
        "dev" {
            Write-BuildMessage "Iniciando servidor de desarrollo..."
            npm run dev
        }
        "staging" {
            Write-BuildMessage "Construyendo para staging..."
            npm run build:staging
        }
        "production" {
            Write-BuildMessage "Construyendo para producción..."
            npm run build:production
        }
    }
}

# Función para analizar bundle
function Invoke-BundleAnalysis {
    Write-BuildMessage "Analizando bundle..."
    
    try {
        npm run analyze
        Write-Success "Análisis de bundle completado"
    } catch {
        Write-Warning "Análisis de bundle no disponible"
    }
}

# Función para verificar build
function Test-Build {
    Write-BuildMessage "Verificando build..."
    
    if (Test-Path "dist") {
        $distSize = (Get-ChildItem -Recurse "dist" | Measure-Object -Property Length -Sum).Sum
        $distSizeMB = [math]::Round($distSize / 1MB, 2)
        Write-Success "Build completado. Tamaño: $distSizeMB MB"
        
        # Verificar archivos principales
        $requiredFiles = @("index.html", "assets")
        foreach ($file in $requiredFiles) {
            if (Test-Path "dist/$file") {
                Write-Success "Archivo requerido encontrado: $file"
            } else {
                Write-Error "Archivo requerido no encontrado: $file"
                exit 1
            }
        }
    } else {
        Write-Error "Directorio dist no encontrado"
        exit 1
    }
}

# Ejecutar proceso de build
Write-BuildMessage "Iniciando proceso de build..."
Write-BuildMessage "Entorno: $Environment"
Write-BuildMessage "Limpiar: $Clean"
Write-BuildMessage "Analizar: $Analyze"

# Limpiar si se solicita
if ($Clean) {
    Clear-Build
}

# Verificar dependencias
Test-Dependencies

# Ejecutar linting
Invoke-Linting

# Ejecutar tests
Invoke-Tests

# Ejecutar type checking
Invoke-TypeCheck

# Ejecutar build
Invoke-Build -Env $Environment

# Verificar build
Test-Build

# Analizar bundle si se solicita
if ($Analyze) {
    Invoke-BundleAnalysis
}

Write-Success "Build completado exitosamente!"
Write-BuildMessage "Entorno: $Environment"
Write-BuildMessage "Directorio de salida: dist/"

