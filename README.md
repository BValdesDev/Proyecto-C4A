# 🚀 C4A SaaS - Plataforma de Evaluación de Ciberseguridad

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

## 📋 **Descripción**

**C4A SaaS** es una plataforma de autodiagnóstico de madurez en seguridad de la información y ciberseguridad, con modelo de suscripción escalonado (Gratuito/Pro/Empresarial), específicamente diseñada para PyMEs chilenas.

### **🎯 Problema que Resuelve**
Las PyMEs enfrentan barreras significativas para acceder a consultorías especializadas en ciberseguridad (costos $15K-50K USD), dejándolas vulnerables ante riesgos cibernéticos que pueden impactar su operación, reputación y viabilidad financiera.

### **💡 Solución Diferenciada**
Plataforma web que democratiza el acceso a evaluaciones de ciberseguridad mediante modelo escalonado, permitiendo progresión natural desde evaluaciones básicas gratuitas hasta servicios empresariales listos para auditorías.

---

## 🏗️ **Arquitectura**

### **Stack Tecnológico**

**Frontend:**
- React 18+ con TypeScript 5.0+
- Tailwind CSS 3.3+ para estilos
- shadcn/ui para componentes
- Recharts para visualizaciones
- React Router para navegación
- Axios para comunicación con API
- Sonner para notificaciones
- Zustand para gestión de estado

**Backend:**
- FastAPI 0.104+ (Python 3.11+)
- PostgreSQL 15+ con extensiones UUID
- Redis 7+ para caché y sesiones
- SQLAlchemy 2.0 con Alembic
- JWT RS256 para autenticación
- Argon2id para hash de contraseñas
- Pydantic v2 para validación
- AES-256-GCM para cifrado

**Infraestructura:**
- Docker y Docker Compose
- Railway para deployment
- OpenTelemetry para monitoreo
- Nginx como proxy reverso

---

## 🎨 **Características Principales**

### **Modelo de Negocio por Niveles**

#### **🆓 Nivel Gratuito**
- 1 evaluación por mes
- 1 reporte básico por mes
- Hasta 3 usuarios
- Framework NIST CSF 2.0
- Reportes con marca de agua

#### **💼 Nivel Pro (CLP $29.990/mes)**
- 10 evaluaciones por mes
- 10 reportes por mes
- Hasta 25 usuarios
- Frameworks NIST CSF 2.0 y COBIT 2019
- Reportes avanzados en PDF y Excel
- Benchmarks del sector
- Soporte por email

#### **🏢 Nivel Empresarial (CLP $99.990/mes)**
- 100 evaluaciones por mes
- 100 reportes por mes
- Hasta 100 usuarios
- Todos los frameworks (NIST, COBIT, ISO 27001)
- Reportes personalizados
- Exportación de datos
- API completa
- Soporte prioritario

---

## 🚀 **Instalación y Configuración**

### **Requisitos Previos**
- Node.js 18+
- Python 3.11+
- Docker y Docker Compose
- Git

### **Instalación Rápida**

```bash
# Clonar el repositorio
git clone https://github.com/cherrera0001/c4a-autodiagnostico.git
cd c4a-autodiagnostico

# Instalar dependencias
npm run install:all

# Configurar variables de entorno
cp .env.example .env

# Levantar servicios con Docker
npm run dev

# Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### **Configuración Manual**

#### **Frontend:**
```bash
cd aplicaciones/frontend
npm install
npm run dev
```

#### **Backend:**
```bash
cd aplicaciones/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### **Base de Datos:**
```bash
# Migraciones
npm run db:migrate

# Datos iniciales
npm run db:seed
```

---

## 🛠️ **Desarrollo**

### **Comandos Disponibles**

```bash
# Desarrollo
npm run dev              # Levantar todos los servicios
npm run dev:frontend     # Solo frontend
npm run dev:backend      # Solo backend

# Testing
npm run test             # Tests unitarios
npm run test:e2e         # Tests E2E
npm run lint             # Linting
npm run type-check       # Type checking

# Base de datos
npm run db:migrate       # Ejecutar migraciones
npm run db:seed          # Cargar datos iniciales
npm run db:reset         # Resetear base de datos

# Docker
npm run logs             # Ver logs
npm run stop             # Parar servicios
npm run restart          # Reiniciar servicios
```

### **Estructura del Proyecto**

```
c4a-autodiagnostico/
├── aplicaciones/
│   ├── frontend/                 # React + TypeScript
│   │   ├── src/
│   │   │   ├── componentes/      # Componentes reutilizables
│   │   │   ├── paginas/          # Páginas principales
│   │   │   ├── hooks/            # Hooks personalizados
│   │   │   ├── tipos/            # Interfaces TypeScript
│   │   │   └── utilidades/       # Utilidades y helpers
│   │   └── package.json
│   └── backend/                  # FastAPI + Python
│       ├── app/
│       │   ├── api/              # Endpoints REST
│       │   ├── core/             # Configuración
│       │   ├── modelos/          # Modelos SQLAlchemy
│       │   ├── servicios/        # Lógica de negocio
│       │   └── utilidades/       # Utilidades
│       └── requirements.txt
├── docker-compose.yml            # Configuración Docker
├── README.md                     # Este archivo
├── CONTRIBUTING.md               # Guía de contribución
├── CHANGELOG.md                  # Historial de cambios
└── LICENSE                       # Licencia MIT
```

---

## 🧪 **Testing**

### **Frontend Testing**
```bash
cd aplicaciones/frontend
npm run test              # Unit tests
npm run test:e2e          # E2E tests
npm run test:coverage     # Coverage
```

### **Backend Testing**
```bash
cd aplicaciones/backend
pytest                    # Unit tests
pytest --cov=app         # Coverage
pytest tests/integration/ # Integration tests
```

### **Criterios de Testing**
- ✅ **Cobertura mínima:** 80%
- ✅ **Tests unitarios** para todas las funciones
- ✅ **Tests de integración** para APIs
- ✅ **Tests E2E** para flujos críticos

---

## 📚 **Documentación**

### **Documentación Técnica**
- [README_FRONTEND_C4A.md](README_FRONTEND_C4A.md) - Documentación del frontend
- [DOCUMENTACION_COMPONENTES_FRONTEND.md](DOCUMENTACION_COMPONENTES_FRONTEND.md) - Componentes implementados
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de contribución
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios

### **API Documentation**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## 🔒 **Seguridad**

### **Medidas de Seguridad Implementadas**
- ✅ **Validación de inputs** en todos los formularios
- ✅ **Sanitización de datos** antes de procesar
- ✅ **Headers de seguridad** configurados
- ✅ **Cifrado de datos sensibles** con AES-256-GCM
- ✅ **Autenticación JWT** con refresh tokens
- ✅ **Rate limiting** por nivel de suscripción
- ✅ **CORS** configurado correctamente

### **Cumplimiento Legal**
- ✅ **Ley 19.628** - Protección de datos personales
- ✅ **Residencia de datos** - Servidores en Chile
- ✅ **Retención de auditoría** - 7 años
- ✅ **Gestión de consentimiento** - Explícito e informado

---

## 🌍 **Localización**

### **Configuración Chile**
- **Idioma:** Español (es-CL)
- **Moneda:** CLP (Peso Chileno)
- **Zona horaria:** America/Santiago
- **Formato de fecha:** DD/MM/YYYY
- **Formato de número:** 1.234.567,89

---

## 📊 **Métricas del Proyecto**

### **Estadísticas de Código**
- **Componentes implementados:** 8/8 ✅
- **Líneas de código:** ~3,500 líneas
- **Interfaces TypeScript:** 24 interfaces
- **Funcionalidades:** 50+ características
- **Niveles soportados:** 3 (Gratuito/Pro/Empresarial)

### **Cobertura de Funcionalidades**
- ✅ **Autenticación:** Login, Registro, Google OAuth
- ✅ **Cuestionarios:** Adaptativos por nivel
- ✅ **Dashboards:** Diferenciados con gráficos
- ✅ **Reportes:** Generación PDF/Excel
- ✅ **Facturación:** Stripe CLP
- ✅ **Benchmarking:** Comparaciones sectoriales
- ✅ **Analytics:** Avanzado nivel empresarial
- ✅ **Usuarios:** Gestión multi-usuario

---

## 🚀 **Despliegue**

### **Despliegue Local**
```bash
# Desarrollo
npm run dev

# Producción
npm run build
docker-compose -f docker-compose.prod.yml up -d
```

### **Despliegue en Railway**
```bash
# Configurar Railway
railway login
railway link
railway up
```

### **Variables de Entorno**
```env
# Frontend
VITE_API_BASE_URL=https://api.c4a.cl
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
VITE_GOOGLE_CLIENT_ID=...

# Backend
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=...
STRIPE_SECRET_KEY=sk_live_...
```

---

## 🤝 **Contribución**

### **Cómo Contribuir**
1. **Fork** del repositorio
2. **Clone** tu fork localmente
3. **Crea** una rama para tu feature
4. **Desarrolla** tu contribución
5. **Testea** tu código
6. **Commit** con mensajes descriptivos
7. **Push** a tu fork
8. **Crea** un Pull Request

### **Convenciones de Código**
- **TypeScript** con modo estricto
- **ESLint** para linting
- **Prettier** para formateo
- **Commits** con formato convencional
- **Tests** para nuevas funcionalidades

---

## 📞 **Contacto y Soporte**

### **Canales de Comunicación**
- **Issues** - Para bugs y features
- **Discussions** - Para preguntas generales
- **Email** - Para asuntos privados

### **Mantainers**
- **Frontend:** Cursor AI Assistant
- **Backend:** Equipo de desarrollo
- **DevOps:** Equipo de infraestructura

---

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 🎉 **Reconocimientos**

### **Contribuidores**
- **Cursor AI Assistant** - Implementación frontend
- **Equipo de desarrollo** - Backend y arquitectura
- **Comunidad** - Feedback y testing

### **Tecnologías Utilizadas**
- React 18+ con TypeScript
- FastAPI con Python
- PostgreSQL y Redis
- Docker y Docker Compose
- Stripe para pagos
- Tailwind CSS y shadcn/ui

---

**¡Gracias por usar C4A SaaS! 🚀**

*Última actualización: Diciembre 2024*