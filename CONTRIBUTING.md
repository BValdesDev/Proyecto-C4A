# 🤝 Guía de Contribución - C4A SaaS

## 📋 **Bienvenido al Proyecto C4A SaaS**

Este documento describe cómo contribuir al proyecto C4A SaaS, una plataforma de evaluación de ciberseguridad para PyMEs chilenas.

---

## 🎯 **Sobre el Proyecto**

**C4A SaaS** es una plataforma de autodiagnóstico de madurez en seguridad de la información y ciberseguridad, con modelo de suscripción escalonado (Gratuito/Pro/Empresarial), específicamente diseñada para PyMEs en Chile.

### **Características Principales:**
- ✅ Cuestionarios adaptativos por nivel (10/50/100 preguntas)
- ✅ Dashboards diferenciados con gráficos
- ✅ Generación de reportes PDF/Excel
- ✅ Gestión de pagos con Stripe (CLP)
- ✅ Benchmarking sectorial
- ✅ Analytics avanzado
- ✅ Gestión multi-usuario

---

## 🚀 **Configuración del Entorno**

### **Requisitos Previos:**
- Node.js 18+ 
- npm o yarn
- Git
- Docker (opcional)

### **Instalación:**
```bash
# Clonar el repositorio
git clone https://github.com/cherrera0001/c4a-autodiagnostico.git
cd c4a-autodiagnostico

# Instalar dependencias del frontend
cd aplicaciones/frontend
npm install

# Instalar dependencias del backend
cd ../backend
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

### **Variables de Entorno Requeridas:**
```env
# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_GOOGLE_CLIENT_ID=...

# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/c4a_saas
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_...
```

---

## 🛠️ **Desarrollo**

### **Comandos Disponibles:**

#### **Frontend:**
```bash
cd aplicaciones/frontend

# Desarrollo
npm run dev

# Build
npm run build

# Testing
npm run test
npm run test:e2e

# Linting
npm run lint
npm run lint:fix
```

#### **Backend:**
```bash
cd aplicaciones/backend

# Desarrollo
uvicorn app.main:app --reload

# Testing
pytest

# Migraciones
alembic upgrade head
```

#### **Docker:**
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down
```

---

## 📝 **Guías de Contribución**

### **1. Flujo de Trabajo:**
1. **Fork** del repositorio
2. **Clone** tu fork localmente
3. **Crea** una rama para tu feature
4. **Desarrolla** tu contribución
5. **Testea** tu código
6. **Commit** con mensajes descriptivos
7. **Push** a tu fork
8. **Crea** un Pull Request

### **2. Convenciones de Código:**

#### **TypeScript:**
```typescript
// Interfaces con PascalCase
interface PropiedadesComponente {
  nivel: 'gratuito' | 'pro' | 'empresarial'
  organizacion: Organizacion
}

// Componentes con PascalCase
export const MiComponente: React.FC<PropiedadesComponente> = ({ nivel, organizacion }) => {
  // Hooks al inicio
  const [estado, setEstado] = useState<string>('')
  
  // Funciones con camelCase
  const manejarEvento = () => {
    // Lógica aquí
  }
  
  return (
    <div className="mi-componente">
      {/* JSX aquí */}
    </div>
  )
}
```

#### **CSS/Tailwind:**
```css
/* Usar clases de Tailwind */
.mi-componente {
  @apply flex items-center justify-center p-4 bg-white rounded-lg shadow-md;
}

/* Colores personalizados C4A */
.c4a-button-primary {
  @apply bg-c4a-blue-600 hover:bg-c4a-blue-700 text-white;
}
```

#### **Commits:**
```bash
# Formato: tipo(scope): descripción
feat(frontend): agregar componente CuestionarioNivel
fix(backend): corregir validación de email
docs(readme): actualizar documentación
test(frontend): agregar tests para DashboardNivel
```

### **3. Estructura de Ramas:**
- `main` - Rama principal estable
- `develop` - Rama de desarrollo
- `feature/nombre-feature` - Nuevas funcionalidades
- `fix/nombre-fix` - Correcciones de bugs
- `docs/nombre-docs` - Documentación

---

## 🧪 **Testing**

### **Frontend Testing:**
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

### **Backend Testing:**
```bash
# Unit tests
pytest

# Coverage
pytest --cov=app

# Integration tests
pytest tests/integration/
```

### **Criterios de Testing:**
- ✅ **Cobertura mínima:** 80%
- ✅ **Tests unitarios** para todas las funciones
- ✅ **Tests de integración** para APIs
- ✅ **Tests E2E** para flujos críticos

---

## 📚 **Documentación**

### **Tipos de Documentación:**
1. **README.md** - Documentación principal
2. **CONTRIBUTING.md** - Esta guía
3. **DOCUMENTACION_COMPONENTES_FRONTEND.md** - Documentación técnica
4. **Comentarios en código** - Documentación inline
5. **Interfaces TypeScript** - Documentación de tipos

### **Estándares de Documentación:**
- ✅ **Comentarios JSDoc** para funciones públicas
- ✅ **Interfaces TypeScript** bien documentadas
- ✅ **README** actualizado con cada cambio
- ✅ **Ejemplos de uso** en la documentación

---

## 🐛 **Reporte de Bugs**

### **Template de Bug Report:**
```markdown
## 🐛 Descripción del Bug
Descripción clara del problema.

## 🔄 Pasos para Reproducir
1. Ir a '...'
2. Hacer clic en '...'
3. Ver error

## 🎯 Comportamiento Esperado
Lo que debería pasar.

## 📱 Entorno
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 91]
- Versión: [e.g. 1.0.0]

## 📷 Screenshots
Si aplica, agregar screenshots.

## 📋 Información Adicional
Cualquier información adicional relevante.
```

---

## ✨ **Solicitud de Features**

### **Template de Feature Request:**
```markdown
## 🚀 Descripción de la Feature
Descripción clara de la funcionalidad solicitada.

## 🎯 Problema que Resuelve
¿Qué problema resuelve esta feature?

## 💡 Solución Propuesta
Descripción de la solución propuesta.

## 🔄 Alternativas Consideradas
Otras soluciones consideradas.

## 📋 Información Adicional
Cualquier información adicional relevante.
```

---

## 🏷️ **Versionado**

### **Semantic Versioning:**
- **MAJOR** - Cambios incompatibles
- **MINOR** - Nuevas funcionalidades compatibles
- **PATCH** - Correcciones de bugs

### **Ejemplos:**
- `1.0.0` - Primera versión estable
- `1.1.0` - Nueva funcionalidad
- `1.1.1` - Corrección de bug

---

## 🔒 **Seguridad**

### **Reporte de Vulnerabilidades:**
- **NO** reportar vulnerabilidades en issues públicos
- **SÍ** contactar directamente a los maintainers
- **SÍ** usar el email de seguridad si está disponible

### **Buenas Prácticas:**
- ✅ **Validar inputs** en todos los formularios
- ✅ **Sanitizar datos** antes de procesar
- ✅ **Usar HTTPS** en producción
- ✅ **Mantener dependencias** actualizadas

---

## 📞 **Contacto y Soporte**

### **Canales de Comunicación:**
- **Issues** - Para bugs y features
- **Discussions** - Para preguntas generales
- **Email** - Para asuntos privados

### **Mantainers:**
- **Frontend:** Cursor AI Assistant
- **Backend:** Equipo de desarrollo
- **DevOps:** Equipo de infraestructura

---

## 🎉 **Reconocimientos**

### **Contribuidores:**
- Cursor AI Assistant - Implementación frontend
- Equipo de desarrollo - Backend y arquitectura
- Comunidad - Feedback y testing

### **Tecnologías Utilizadas:**
- React 18+ con TypeScript
- FastAPI con Python
- PostgreSQL y Redis
- Docker y Docker Compose
- Stripe para pagos
- Tailwind CSS y shadcn/ui

---

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**¡Gracias por contribuir a C4A SaaS! 🚀**

*Última actualización: Diciembre 2024*
