# Script PowerShell para configurar el entorno local de desarrollo
# Uso: .\scripts\setup-env.ps1

$ErrorActionPreference = "Stop"

Write-Host "🔧 Configurando entorno local para C4A Backend..." -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: Este script debe ejecutarse desde el directorio aplicaciones/backend" -ForegroundColor Red
    exit 1
}

# 1. Copiar env.example a .env si no existe
if (-not (Test-Path ".env")) {
    if (Test-Path "env.example") {
        Write-Host "📋 Copiando env.example a .env..." -ForegroundColor Yellow
        Copy-Item "env.example" ".env"
        Write-Host "✅ Archivo .env creado" -ForegroundColor Green
    } else {
        Write-Host "❌ Error: No se encontró env.example" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  El archivo .env ya existe, no se sobrescribirá" -ForegroundColor Yellow
}

# 2. Generar claves RSA si no existen
if (-not (Test-Path "jwt_private.pem") -or -not (Test-Path "jwt_public.pem")) {
    Write-Host ""
    Write-Host "🔑 Generando claves RSA para JWT..." -ForegroundColor Yellow
    
    if (Test-Path "scripts\generar_claves_rsa.py") {
        python scripts\generar_claves_rsa.py
    } else {
        Write-Host "⚠️  Script generar_claves_rsa.py no encontrado, usando openssl..." -ForegroundColor Yellow
        # Verificar si openssl está disponible
        $openssl = Get-Command openssl -ErrorAction SilentlyContinue
        if ($openssl) {
            openssl genrsa -out jwt_private.pem 2048
            openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
            Write-Host "✅ Claves RSA generadas" -ForegroundColor Green
        } else {
            Write-Host "❌ Error: openssl no está disponible. Por favor, instálalo o usa el script Python." -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "✅ Las claves RSA ya existen" -ForegroundColor Green
}

# 3. Verificar que .env está en .gitignore
$gitignorePath = "..\..\.gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
    if ($gitignoreContent -match "\.env" -or $gitignoreContent -match "aplicaciones/backend/\.env") {
        Write-Host "✅ .env está en .gitignore" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Advertencia: .env no está en .gitignore, agregándolo..." -ForegroundColor Yellow
        Add-Content $gitignorePath "`n.env"
        Write-Host "✅ .env agregado a .gitignore" -ForegroundColor Green
    }
}

# 4. Verificar que jwt_*.pem está en .gitignore
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
    if ($gitignoreContent -match "jwt_.*\.pem") {
        Write-Host "✅ jwt_*.pem está en .gitignore" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Advertencia: jwt_*.pem no está en .gitignore, agregándolo..." -ForegroundColor Yellow
        Add-Content $gitignorePath "`njwt_*.pem"
        Write-Host "✅ jwt_*.pem agregado a .gitignore" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Configuración del entorno local completada" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Edita .env y configura las siguientes variables:"
Write-Host "      - URL_BASE_DATOS (con tus credenciales de PostgreSQL)"
Write-Host "      - CLAVE_PUBLICA_JWT (con el contenido de jwt_public.pem)"
Write-Host "      - CLAVE_PRIVADA_JWT (con el contenido de jwt_private.pem)"
Write-Host "      - CLAVE_MAESTRA_CIFRADO (genera una clave segura)"
Write-Host "      - EMAIL_USER y EMAIL_PASSWORD"
Write-Host "      - STRIPE_CLAVE_PUBLICA y STRIPE_CLAVE_SECRETA"
Write-Host ""
Write-Host "   2. Para generar una clave maestra de cifrado:"
Write-Host "      openssl rand -hex 32"
Write-Host ""
Write-Host "   3. Valida la configuración:"
Write-Host "      python -c `"from app.core.config import config; print('✅ Configuración válida')`""
Write-Host ""



