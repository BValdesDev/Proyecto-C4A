#!/bin/bash
# Script para configurar el entorno local de desarrollo
# Uso: ./scripts/setup-env.sh

set -e

echo "🔧 Configurando entorno local para C4A Backend..."
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Este script debe ejecutarse desde el directorio aplicaciones/backend"
    exit 1
fi

# 1. Copiar .env.example a .env si no existe
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "📋 Copiando env.example a .env..."
        cp env.example .env
        echo "✅ Archivo .env creado"
    else
        echo "❌ Error: No se encontró env.example"
        exit 1
    fi
else
    echo "⚠️  El archivo .env ya existe, no se sobrescribirá"
fi

# 2. Generar claves RSA si no existen
if [ ! -f "jwt_private.pem" ] || [ ! -f "jwt_public.pem" ]; then
    echo ""
    echo "🔑 Generando claves RSA para JWT..."
    
    if [ -f "scripts/generar_claves_rsa.py" ]; then
        python scripts/generar_claves_rsa.py
    else
        echo "⚠️  Script generar_claves_rsa.py no encontrado, usando openssl..."
        openssl genrsa -out jwt_private.pem 2048
        openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
        echo "✅ Claves RSA generadas"
    fi
    
    # Convertir claves a formato de una línea para .env
    echo ""
    echo "📝 Convirtiendo claves a formato de una línea..."
    
    # Clave pública
    PUBLIC_KEY=$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_public.pem)
    # Clave privada
    PRIVATE_KEY=$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_private.pem)
    
    # Actualizar .env con las claves
    if [ -f ".env" ]; then
        # Usar sed para actualizar las claves en .env
        # Nota: Esto requiere que las variables ya existan en .env
        echo "⚠️  Por favor, actualiza manualmente CLAVE_PUBLICA_JWT y CLAVE_PRIVADA_JWT en .env"
        echo "   con el contenido de jwt_public.pem y jwt_private.pem"
    fi
else
    echo "✅ Las claves RSA ya existen"
fi

# 3. Verificar que .env está en .gitignore
if [ -f "../../.gitignore" ]; then
    if grep -q "^\.env$" ../../.gitignore || grep -q "^aplicaciones/backend/\.env$" ../../.gitignore; then
        echo "✅ .env está en .gitignore"
    else
        echo "⚠️  Advertencia: .env no está en .gitignore, agregándolo..."
        echo ".env" >> ../../.gitignore
        echo "✅ .env agregado a .gitignore"
    fi
fi

# 4. Verificar que jwt_*.pem está en .gitignore
if [ -f "../../.gitignore" ]; then
    if grep -q "jwt_.*\.pem" ../../.gitignore; then
        echo "✅ jwt_*.pem está en .gitignore"
    else
        echo "⚠️  Advertencia: jwt_*.pem no está en .gitignore, agregándolo..."
        echo "jwt_*.pem" >> ../../.gitignore
        echo "✅ jwt_*.pem agregado a .gitignore"
    fi
fi

echo ""
echo "✅ Configuración del entorno local completada"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Edita .env y configura las siguientes variables:"
echo "      - URL_BASE_DATOS (con tus credenciales de PostgreSQL)"
echo "      - CLAVE_PUBLICA_JWT (con el contenido de jwt_public.pem)"
echo "      - CLAVE_PRIVADA_JWT (con el contenido de jwt_private.pem)"
echo "      - CLAVE_MAESTRA_CIFRADO (genera una clave segura)"
echo "      - EMAIL_USER y EMAIL_PASSWORD"
echo "      - STRIPE_CLAVE_PUBLICA y STRIPE_CLAVE_SECRETA"
echo ""
echo "   2. Para generar una clave maestra de cifrado:"
echo "      openssl rand -hex 32"
echo ""
echo "   3. Valida la configuración:"
echo "      python -c 'from app.core.config import config; print(\"✅ Configuración válida\")'"
echo ""



