#!/bin/bash
# Git Flow Helper Script para C4A
# Este script facilita el uso de Git Flow en Linux/Mac

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones de output
success() { echo -e "${GREEN}$1${NC}"; }
error() { echo -e "${RED}$1${NC}"; }
info() { echo -e "${CYAN}$1${NC}"; }
warning() { echo -e "${YELLOW}$1${NC}"; }

# Banner
echo -e "${CYAN}"
cat << "EOF"

╔═══════════════════════════════════════╗
║     Git Flow Helper - C4A SaaS        ║
╚═══════════════════════════════════════╝

EOF
echo -e "${NC}"

# Verificar argumentos
if [ $# -lt 1 ]; then
    error "❌ Error: Debes proporcionar una acción"
    info "Uso: ./gitflow-helper.sh [feature|bugfix|release|hotfix|finish] [nombre]"
    exit 1
fi

ACTION=$1
NAME=$2

# Verificar que estamos en un repositorio git
if [ ! -d .git ]; then
    error "❌ Error: Este directorio no es un repositorio Git"
    exit 1
fi

# Función para crear una nueva rama
create_branch() {
    local type=$1
    local name=$2
    
    if [ -z "$name" ]; then
        error "❌ Error: Debes proporcionar un nombre para la rama"
        info "Uso: ./gitflow-helper.sh $type nombre-descriptivo"
        exit 1
    fi
    
    if [ "$type" = "hotfix" ] || [ "$type" = "release" ]; then
        base_branch="main"
    else
        base_branch="develop"
    fi
    
    branch_name="$type/$name"
    
    info "📋 Creando rama: $branch_name"
    info "📍 Base: $base_branch"
    
    # Actualizar rama base
    info "\n🔄 Actualizando $base_branch..."
    git checkout $base_branch || { error "❌ Error al hacer checkout a $base_branch"; exit 1; }
    git pull origin $base_branch || { error "❌ Error al actualizar $base_branch"; exit 1; }
    
    # Crear nueva rama
    info "\n🌿 Creando nueva rama..."
    git checkout -b $branch_name || { error "❌ Error al crear la rama $branch_name"; exit 1; }
    
    success "\n✅ ¡Rama creada exitosamente!"
    info "\n📝 Próximos pasos:"
    echo "1. Desarrolla tu cambio"
    echo "2. git add ."
    echo "3. git commit -m 'tipo: descripción'"
    echo "4. git push origin $branch_name"
    echo "5. Crea un Pull Request en GitHub"
    
    if [ "$type" = "feature" ] || [ "$type" = "bugfix" ]; then
        info "\n🎯 Tu PR debe ir a: develop"
    else
        info "\n🎯 Tu PR debe ir a: main"
        if [ "$type" = "release" ] || [ "$type" = "hotfix" ]; then
            warning "⚠️  Recuerda: después del merge a main, también debes mergear a develop"
        fi
    fi
}

# Función para finalizar una rama
finish_branch() {
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    if [ "$current_branch" = "main" ] || [ "$current_branch" = "develop" ]; then
        error "❌ Error: No puedes ejecutar 'finish' desde main o develop"
        info "Cambia a la rama que quieres finalizar primero"
        exit 1
    fi
    
    info "🔍 Finalizando rama: $current_branch"
    
    # Determinar rama destino
    if [[ $current_branch =~ ^(hotfix|release)/ ]]; then
        target_branch="main"
        also_merge="develop"
    else
        target_branch="develop"
        also_merge=""
    fi
    
    info "\n📝 Pasos para finalizar la rama:"
    echo "1. Asegúrate de que todos los cambios estén commiteados"
    echo "2. git push origin $current_branch"
    echo "3. Crea un Pull Request en GitHub: $current_branch → $target_branch"
    echo "4. Espera aprobación y pasa los checks de CI/CD"
    echo "5. Mergea el PR"
    
    if [ -n "$also_merge" ]; then
        warning "\n⚠️  IMPORTANTE: Después del merge a $target_branch, también debes mergear a $also_merge"
    fi
    
    info "\n6. Después del merge, ejecuta:"
    echo -e "${YELLOW}   git checkout $target_branch${NC}"
    echo -e "${YELLOW}   git pull origin $target_branch${NC}"
    echo -e "${YELLOW}   git branch -d $current_branch${NC}"
    echo -e "${YELLOW}   git push origin --delete $current_branch${NC}"
    
    # Preguntar si quiere push automático
    echo ""
    read -p "¿Quieres hacer push ahora? (s/n): " push_now
    if [ "$push_now" = "s" ] || [ "$push_now" = "S" ]; then
        info "\n⬆️  Haciendo push..."
        if git push origin $current_branch; then
            success "✅ Push exitoso!"
            info "\n🌐 Crea tu Pull Request en:"
            echo "https://github.com/cherrera0001/c4a-autodiagnostico/pull/new/$current_branch"
        else
            error "❌ Error al hacer push"
        fi
    fi
}

# Ejecutar acción
case $ACTION in
    feature|bugfix|release|hotfix)
        create_branch $ACTION $NAME
        ;;
    finish)
        finish_branch
        ;;
    *)
        error "❌ Error: Acción inválida: $ACTION"
        info "Acciones válidas: feature, bugfix, release, hotfix, finish"
        exit 1
        ;;
esac

echo ""


