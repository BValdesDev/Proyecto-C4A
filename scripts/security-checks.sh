#!/bin/bash

# Script de validación de seguridad para el proyecto C4A
# Valida que no existan valores hardcodeados, console.log con información sensible, etc.

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "🔒 Iniciando validaciones de seguridad personalizadas..."

# Función para reportar errores
report_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    ERRORS=$((ERRORS + 1))
}

# Función para reportar warnings
report_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

# Función para reportar éxito
report_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 1. Validar que no existan valores hardcodeados en config.py
echo ""
echo "1. Verificando valores hardcodeados en config.py..."

CONFIG_FILE="aplicaciones/backend/app/core/config.py"

if [ ! -f "$CONFIG_FILE" ]; then
    report_error "No se encontró el archivo config.py en $CONFIG_FILE"
    exit 1
fi

# Patrones a buscar que indican valores hardcodeados
HARDCODED_PATTERNS=(
    "password.*=.*['\"][^'\"]{8,}['\"]"
    "secret.*=.*['\"][^'\"]{16,}['\"]"
    "key.*=.*['\"][^'\"]{32,}['\"]"
    "token.*=.*['\"][^'\"]{16,}['\"]"
    "api_key.*=.*['\"][^'\"]{16,}['\"]"
    "CLAVE_PUBLICA_JWT.*=.*['\"][^'\"]{64,}['\"]"
    "CLAVE_PRIVADA_JWT.*=.*['\"][^'\"]{64,}['\"]"
    "CLAVE_MAESTRA_CIFRADO.*=.*['\"][^'\"]{32,}['\"]"
    "email_password.*=.*['\"][^'\"]{8,}['\"]"
    "email_user.*=.*['\"][^'\"]+@[^'\"]+['\"]"
    "url_base_datos.*=.*postgresql.*://[^'\"]+:[^'\"]+@"
)

HARDCODED_FOUND=false

for pattern in "${HARDCODED_PATTERNS[@]}"; do
    if grep -E "$pattern" "$CONFIG_FILE" | grep -v "# " | grep -v "Requerido desde" | grep -v "RSA " | grep -v "BEGIN\|END"; then
        report_error "Se encontraron valores hardcodeados en config.py que coinciden con: $pattern"
        grep -E "$pattern" "$CONFIG_FILE" | grep -v "# " | grep -v "Requerido desde" | head -5
        HARDCODED_FOUND=true
    fi
done

# Verificar que los valores críticos estén vacíos por defecto
CRITICAL_VARS=(
    "clave_publica_jwt.*=.*['\"]['\"]"
    "clave_privada_jwt.*=.*['\"]['\"]"
    "clave_maestra_cifrado.*=.*['\"]['\"]"
    "email_user.*=.*['\"]['\"]"
    "email_password.*=.*['\"]['\"]"
    "url_base_datos.*=.*['\"]['\"]"
)

MISSING_EMPTY_DEFAULTS=false

for pattern in "${CRITICAL_VARS[@]}"; do
    if ! grep -E "$pattern" "$CONFIG_FILE" > /dev/null 2>&1; then
        report_warning "Variable crítica puede no tener valor vacío por defecto: $pattern"
        MISSING_EMPTY_DEFAULTS=true
    fi
done

if [ "$HARDCODED_FOUND" = false ] && [ "$MISSING_EMPTY_DEFAULTS" = false ]; then
    report_success "No se encontraron valores hardcodeados en config.py"
fi

# 2. Validar que las variables de entorno estén documentadas en .env.example
echo ""
echo "2. Verificando documentación de variables de entorno en .env.example..."

ENV_EXAMPLE="env.example"

if [ ! -f "$ENV_EXAMPLE" ]; then
    report_error "No se encontró el archivo .env.example en $ENV_EXAMPLE"
else
    # Variables críticas que deben estar documentadas
    REQUIRED_VARS=(
        "POSTGRES"
        "REDIS"
        "JWT"
        "CORS"
        "STRIPE"
        "EMAIL"
    )
    
    MISSING_VARS=false
    
    for var in "${REQUIRED_VARS[@]}"; do
        if ! grep -qi "$var" "$ENV_EXAMPLE"; then
            report_warning "Variable de entorno relacionada con '$var' no encontrada en .env.example"
            MISSING_VARS=true
        fi
    done
    
    if [ "$MISSING_VARS" = false ]; then
        report_success "Variables de entorno están documentadas en .env.example"
    fi
fi

# 3. Validar console.log con información sensible en el frontend
echo ""
echo "3. Verificando console.log con información sensible en el frontend..."

FRONTEND_DIR="aplicaciones/frontend/src"

if [ ! -d "$FRONTEND_DIR" ]; then
    report_warning "No se encontró el directorio frontend en $FRONTEND_DIR"
else
    SENSITIVE_CONSOLE_FOUND=false
    
    # Buscar console.log con patrones sensibles
    while IFS= read -r line; do
        # Ignorar comentarios y console.log vacíos
        if echo "$line" | grep -qiE "console\.(log|debug|info|warn|error)" && \
           echo "$line" | grep -qiE "(password|secret|token|key|api[_-]?key|auth|credential|jwt|bearer)" && \
           ! echo "$line" | grep -qiE "^(//|/\*|\*)" && \
           ! echo "$line" | grep -qiE "console\.(log|debug|info).*['\"]['\"]"; then
            report_error "console.log con posible información sensible encontrado:"
            echo "  $line"
            SENSITIVE_CONSOLE_FOUND=true
        fi
    done < <(find "$FRONTEND_DIR" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -exec grep -Hn "console\." {} \;)
    
    if [ "$SENSITIVE_CONSOLE_FOUND" = false ]; then
        report_success "No se encontraron console.log con información sensible"
    fi
fi

# 4. Validar que los tokens sigan el patrón c4a_*
echo ""
echo "4. Verificando que los tokens sigan el patrón c4a_*..."

TOKEN_PATTERN="c4a_[a-zA-Z0-9_]+"

# Buscar tokens que no sigan el patrón
INVALID_TOKENS_FOUND=false

# Buscar en archivos de configuración y código
for file in $(find aplicaciones -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.json" \) ! -path "*/node_modules/*" ! -path "*/__pycache__/*" ! -path "*/.pytest_cache/*" ! -name "*.test.*"); do
    # Buscar tokens que no sigan el patrón pero parezcan ser de C4A
    if grep -qiE "(token|key|secret).*=.*['\"][^'\"]*token[^'\"]*['\"]" "$file" 2>/dev/null; then
        if grep -qiE "(token|key|secret).*=.*['\"][^'\"]*token[^'\"]*['\"]" "$file" | grep -vE "$TOKEN_PATTERN" | grep -qi "c4a\|C4A"; then
            report_warning "Posible token que no sigue el patrón c4a_* en: $file"
            grep -iE "(token|key|secret).*=.*['\"][^'\"]*token[^'\"]*['\"]" "$file" | grep -vE "$TOKEN_PATTERN" | head -3
            INVALID_TOKENS_FOUND=true
        fi
    fi
done

if [ "$INVALID_TOKENS_FOUND" = false ]; then
    report_success "Los tokens encontrados siguen el patrón c4a_* o son válidos"
fi

# 5. Validar que no existan comentarios con información sensible
echo ""
echo "5. Verificando comentarios con información sensible..."

SENSITIVE_COMMENTS_FOUND=false

SENSITIVE_COMMENT_PATTERNS=(
    "# password.*:"
    "# secret.*:"
    "# key.*:"
    "# token.*:"
    "// password.*:"
    "// secret.*:"
    "// key.*:"
    "// token.*:"
)

for pattern in "${SENSITIVE_COMMENT_PATTERNS[@]}"; do
    while IFS= read -r line; do
        # Ignorar ejemplos y documentación
        if ! echo "$line" | grep -qiE "(example|ejemplo|placeholder|test|TODO|FIXME|XXX)"; then
            report_warning "Posible comentario con información sensible: $line"
            SENSITIVE_COMMENTS_FOUND=true
        fi
    done < <(find aplicaciones -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) ! -path "*/node_modules/*" ! -path "*/__pycache__/*" ! -path "*/tests/*" -exec grep -HniE "$pattern" {} \; 2>/dev/null | head -10)
done

if [ "$SENSITIVE_COMMENTS_FOUND" = false ]; then
    report_success "No se encontraron comentarios con información sensible"
fi

# Resumen final
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Resumen de validaciones de seguridad:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Errores: $ERRORS"
echo "⚠️  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ La validación de seguridad falló con $ERRORS error(es)${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  La validación pasó con $WARNINGS advertencia(s)${NC}"
    exit 0
else
    echo -e "${GREEN}✅ Todas las validaciones de seguridad pasaron correctamente${NC}"
    exit 0
fi




