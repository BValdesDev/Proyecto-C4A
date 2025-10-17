#!/bin/bash
# Script de implementación automatizada del Panel de Administración C4A SaaS
# Autor: C4A Development Team
# Fecha: 16 Octubre 2025

echo "=================================================="
echo "  IMPLEMENTACION PANEL DE ADMINISTRACION C4A"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Paso 1: Verificar que estamos en el directorio correcto
echo -e "${YELLOW}[1/7] Verificando directorio...${NC}"
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: No se encontró docker-compose.yml${NC}"
    echo "Por favor ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi
echo -e "${GREEN}✓ Directorio correcto${NC}"
echo ""

# Paso 2: Obtener últimos cambios
echo -e "${YELLOW}[2/7] Obteniendo cambios desde GitHub...${NC}"
git checkout develop
git pull origin develop
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Cambios obtenidos exitosamente${NC}"
else
    echo -e "${RED}Error al obtener cambios${NC}"
    exit 1
fi
echo ""

# Paso 3: Detener contenedores
echo -e "${YELLOW}[3/7] Deteniendo contenedores...${NC}"
docker-compose down
echo -e "${GREEN}✓ Contenedores detenidos${NC}"
echo ""

# Paso 4: Reconstruir imágenes
echo -e "${YELLOW}[4/7] Reconstruyendo imágenes Docker...${NC}"
echo "Esto puede tomar varios minutos..."
docker-compose build backend
docker-compose build frontend
echo -e "${GREEN}✓ Imágenes reconstruidas${NC}"
echo ""

# Paso 5: Iniciar contenedores
echo -e "${YELLOW}[5/7] Iniciando contenedores...${NC}"
docker-compose up -d
echo "Esperando que los servicios estén listos..."
sleep 10
echo -e "${GREEN}✓ Contenedores iniciados${NC}"
echo ""

# Paso 6: Verificar estado
echo -e "${YELLOW}[6/7] Verificando estado de servicios...${NC}"
docker-compose ps
echo ""

# Paso 7: Actualizar datos (opcional)
echo -e "${YELLOW}[7/7] ¿Deseas actualizar los datos de prueba? (s/n)${NC}"
read -r respuesta
if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
    echo "Actualizando datos de prueba..."
    docker-compose exec -T backend python scripts/crear_usuarios_prueba.py
    echo "Actualizando montos de suscripciones..."
    docker-compose exec -T backend python scripts/actualizar_montos.py
    echo -e "${GREEN}✓ Datos actualizados${NC}"
else
    echo "Datos no actualizados"
fi
echo ""

# Resumen final
echo "=================================================="
echo -e "${GREEN}  IMPLEMENTACION COMPLETADA${NC}"
echo "=================================================="
echo ""
echo "El panel de administración ha sido implementado exitosamente."
echo ""
echo "Próximos pasos:"
echo "1. Abre tu navegador en: http://localhost:3000/login"
echo "2. Inicia sesión con:"
echo "   Email: frankbailey440@gmail.com"
echo "   Password: Fr@nk15481548"
echo ""
echo "3. Navega a las nuevas páginas:"
echo "   - Pagos: http://localhost:3000/admin/payments"
echo "   - Analytics: http://localhost:3000/admin/analytics"
echo "   - Seguridad: http://localhost:3000/admin/security"
echo "   - Notificaciones: http://localhost:3000/admin/notifications"
echo ""
echo "Para ver los logs:"
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend"
echo ""
echo "Para más información, revisa: GUIA_IMPLEMENTACION_ADMIN_PANEL.md"
echo "=================================================="

