# Git Flow Helper Script para C4A
# Este script facilita el uso de Git Flow en Windows

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('feature', 'bugfix', 'release', 'hotfix', 'finish')]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Name
)

# Colores para output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }

# Banner
Write-Host @"

╔═══════════════════════════════════════╗
║     Git Flow Helper - C4A SaaS        ║
╚═══════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Verificar que estamos en un repositorio git
if (!(Test-Path .git)) {
    Write-Error "❌ Error: Este directorio no es un repositorio Git"
    exit 1
}

# Función para crear una nueva rama
function New-GitFlowBranch {
    param($Type, $Name)
    
    if ([string]::IsNullOrEmpty($Name)) {
        Write-Error "❌ Error: Debes proporcionar un nombre para la rama"
        Write-Info "Uso: .\gitflow-helper.ps1 -Action $Type -Name nombre-descriptivo"
        exit 1
    }
    
    $baseBranch = if ($Type -eq 'hotfix' -or $Type -eq 'release') { 'main' } else { 'develop' }
    $branchName = "$Type/$Name"
    
    Write-Info "📋 Creando rama: $branchName"
    Write-Info "📍 Base: $baseBranch"
    
    # Actualizar rama base
    Write-Info "`n🔄 Actualizando $baseBranch..."
    git checkout $baseBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Error al hacer checkout a $baseBranch"
        exit 1
    }
    
    git pull origin $baseBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Error al actualizar $baseBranch"
        exit 1
    }
    
    # Crear nueva rama
    Write-Info "`n🌿 Creando nueva rama..."
    git checkout -b $branchName
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Error al crear la rama $branchName"
        exit 1
    }
    
    Write-Success "`n✅ ¡Rama creada exitosamente!"
    Write-Info "`n📝 Próximos pasos:"
    Write-Info "1. Desarrolla tu cambio"
    Write-Info "2. git add ."
    Write-Info "3. git commit -m 'tipo: descripción'"
    Write-Info "4. git push origin $branchName"
    Write-Info "5. Crea un Pull Request en GitHub"
    
    if ($Type -eq 'feature' -or $Type -eq 'bugfix') {
        Write-Info "`n🎯 Tu PR debe ir a: develop"
    } else {
        Write-Info "`n🎯 Tu PR debe ir a: main"
        if ($Type -eq 'release' -or $Type -eq 'hotfix') {
            Write-Warning "⚠️  Recuerda: después del merge a main, también debes mergear a develop"
        }
    }
}

# Función para finalizar una rama
function Complete-GitFlowBranch {
    $currentBranch = git rev-parse --abbrev-ref HEAD
    
    if ($currentBranch -eq 'main' -or $currentBranch -eq 'develop') {
        Write-Error "❌ Error: No puedes ejecutar 'finish' desde main o develop"
        Write-Info "Cambia a la rama que quieres finalizar primero"
        exit 1
    }
    
    Write-Info "🔍 Finalizando rama: $currentBranch"
    
    # Determinar rama destino
    if ($currentBranch -match '^(hotfix|release)/') {
        $targetBranch = 'main'
        $alsoMerge = 'develop'
    } else {
        $targetBranch = 'develop'
        $alsoMerge = $null
    }
    
    Write-Info "`n📝 Pasos para finalizar la rama:"
    Write-Info "1. Asegúrate de que todos los cambios estén commiteados"
    Write-Info "2. git push origin $currentBranch"
    Write-Info "3. Crea un Pull Request en GitHub: $currentBranch → $targetBranch"
    Write-Info "4. Espera aprobación y pasa los checks de CI/CD"
    Write-Info "5. Mergea el PR"
    
    if ($alsoMerge) {
        Write-Warning "`n⚠️  IMPORTANTE: Después del merge a $targetBranch, también debes mergear a $alsoMerge"
    }
    
    Write-Info "`n6. Después del merge, ejecuta:"
    Write-Host "   git checkout $targetBranch" -ForegroundColor Yellow
    Write-Host "   git pull origin $targetBranch" -ForegroundColor Yellow
    Write-Host "   git branch -d $currentBranch" -ForegroundColor Yellow
    Write-Host "   git push origin --delete $currentBranch" -ForegroundColor Yellow
    
    # Preguntar si quiere push automático
    $push = Read-Host "`n¿Quieres hacer push ahora? (s/n)"
    if ($push -eq 's' -or $push -eq 'S') {
        Write-Info "`n⬆️  Haciendo push..."
        git push origin $currentBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Push exitoso!"
            Write-Info "`n🌐 Crea tu Pull Request en:"
            Write-Info "https://github.com/cherrera0001/c4a-autodiagnostico/pull/new/$currentBranch"
        } else {
            Write-Error "❌ Error al hacer push"
        }
    }
}

# Ejecutar acción
switch ($Action) {
    'feature' { New-GitFlowBranch -Type 'feature' -Name $Name }
    'bugfix'  { New-GitFlowBranch -Type 'bugfix' -Name $Name }
    'release' { New-GitFlowBranch -Type 'release' -Name $Name }
    'hotfix'  { New-GitFlowBranch -Type 'hotfix' -Name $Name }
    'finish'  { Complete-GitFlowBranch }
}

Write-Host "`n" -NoNewline

