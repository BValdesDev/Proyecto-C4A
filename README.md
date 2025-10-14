# 🛡️ C4A - Plataforma de Autodiagnóstico de Ciberseguridad

Plataforma SaaS de evaluación de ciberseguridad para PyMEs chilenas basada en frameworks internacionales (NIST, COBIT, ISO).

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Instalación](#instalación)
- [Uso](#uso)
- [Git Flow](#git-flow)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Soporte](#soporte)

## ✨ Características

- 🔐 **Autenticación Segura**: Sistema de autenticación con JWT, MFA y detección de bots
- 📊 **Dashboard Analytics**: Visualización de métricas de ciberseguridad
- 📝 **Cuestionarios Personalizados**: Evaluaciones basadas en NIST, COBIT e ISO
- 📈 **Reportes Detallados**: Generación de reportes en PDF con gráficos y recomendaciones
- 💳 **Sistema de Suscripciones**: Integración con Stripe para pagos
- 🌐 **Multiidioma**: Soporte para español chileno
- 🎨 **UI/UX Moderna**: Interfaz construida con React y Tailwind CSS
- 📱 **Responsive**: Diseño adaptable a dispositivos móviles

## 🚀 Tecnologías

### Frontend
- **React 18** + **TypeScript**
- **Vite** - Build tool
- **Tailwind CSS** - Estilos
- **Radix UI** - Componentes accesibles
- **Zustand** - Estado global
- **React Router** - Navegación
- **Recharts** - Gráficos

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Alembic** - Migraciones
- **PostgreSQL** - Base de datos
- **Redis** - Cache y sesiones
- **JWT** - Autenticación

### DevOps
- **Docker** + **Docker Compose**
- **GitHub Actions** - CI/CD
- **Nginx** - Reverse proxy (producción)

## 📦 Instalación

### Prerrequisitos

- Node.js >= 18.0.0
- Python >= 3.11
- Docker y Docker Compose
- Git

### Clonar el Repositorio

```bash
git clone https://github.com/cherrera0001/c4a-autodiagnostico.git
cd c4a-autodiagnostico
```

### Configuración con Docker (Recomendado)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Configuración Manual

#### Backend

```bash
cd aplicaciones/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd aplicaciones/frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar servidor de desarrollo
npm run dev
```

## 🎯 Uso

### Acceso a la Aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Base de Datos**: localhost:5432

### Credenciales de Prueba

```
Email: admin@c4a.cl
Password: Admin123!
```

## 🌳 Git Flow

Este proyecto utiliza **Git Flow** para mantener un desarrollo organizado y estable.

### Ramas Principales

- **`main`**: Código en producción (protegida)
- **`develop`**: Rama de desarrollo e integración

### Ramas Temporales

- **`feature/*`**: Nuevas funcionalidades
- **`bugfix/*`**: Corrección de bugs
- **`hotfix/*`**: Correcciones urgentes en producción
- **`release/*`**: Preparación de releases

### Guía Rápida

#### Crear una nueva feature

```bash
# Opción 1: Usando el helper script (Recomendado)
.\scripts\gitflow-helper.ps1 -Action feature -Name nombre-feature

# Opción 2: Manual
git checkout develop
git pull origin develop
git checkout -b feature/nombre-feature

# Trabajar en tu feature
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nombre-feature

# Crear Pull Request en GitHub a develop
```

#### Crear un hotfix urgente

```bash
# Opción 1: Usando el helper script
.\scripts\gitflow-helper.ps1 -Action hotfix -Name corregir-bug

# Opción 2: Manual
git checkout main
git pull origin main
git checkout -b hotfix/corregir-bug

# Hacer la corrección
git add .
git commit -m "fix: descripción de la corrección"
git push origin hotfix/corregir-bug

# Crear Pull Request a main
# Después del merge, también mergear a develop
```

#### Finalizar una rama

```bash
# Usando el helper script
.\scripts\gitflow-helper.ps1 -Action finish

# Esto te guiará en los pasos finales
```

### Scripts Helper

Hemos creado scripts para facilitar el uso de Git Flow:

**Windows (PowerShell)**:
```powershell
.\scripts\gitflow-helper.ps1 -Action feature -Name mi-feature
.\scripts\gitflow-helper.ps1 -Action bugfix -Name fix-login
.\scripts\gitflow-helper.ps1 -Action release -Name v1.2.0
.\scripts\gitflow-helper.ps1 -Action hotfix -Name critical-fix
.\scripts\gitflow-helper.ps1 -Action finish
```

**Linux/Mac (Bash)**:
```bash
chmod +x scripts/gitflow-helper.sh
./scripts/gitflow-helper.sh feature mi-feature
./scripts/gitflow-helper.sh bugfix fix-login
./scripts/gitflow-helper.sh release v1.2.0
./scripts/gitflow-helper.sh hotfix critical-fix
./scripts/gitflow-helper.sh finish
```

### Convenciones de Commits

Usamos **Conventional Commits** para mantener un historial limpio:

```
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: formato, punto y coma, etc.
refactor: refactorización de código
test: agregar o modificar tests
chore: cambios en build, dependencias, etc.
perf: mejoras de rendimiento
ci: cambios en CI/CD
```

**Ejemplos**:
```bash
git commit -m "feat: implementar login con SSO"
git commit -m "fix: corregir validación de email"
git commit -m "docs: actualizar README con instrucciones de Git Flow"
git commit -m "refactor: mejorar estructura de componentes"
```

### Documentación Completa

Para más detalles sobre Git Flow, consulta:
- 📖 [GITFLOW.md](./GITFLOW.md) - Guía completa de Git Flow
- 📋 [CONTRIBUTING.md](./CONTRIBUTING.md) - Guía de contribución

## 📁 Estructura del Proyecto

```
c4a-autodiagnostico/
├── aplicaciones/
│   ├── backend/              # API FastAPI
│   │   ├── app/
│   │   │   ├── api/          # Endpoints
│   │   │   ├── core/         # Configuración y seguridad
│   │   │   ├── modelos/      # Modelos SQLAlchemy
│   │   │   ├── servicios/    # Lógica de negocio
│   │   │   └── main.py       # Entry point
│   │   ├── alembic/          # Migraciones
│   │   └── requirements.txt  # Dependencias Python
│   │
│   └── frontend/             # Aplicación React
│       ├── src/
│       │   ├── componentes/  # Componentes React
│       │   ├── pages/        # Páginas
│       │   ├── hooks/        # Custom hooks
│       │   ├── utilidades/   # Utilidades
│       │   └── main.tsx      # Entry point
│       └── package.json      # Dependencias Node
│
├── scripts/                  # Scripts de ayuda
│   ├── gitflow-helper.ps1    # Helper de Git Flow (Windows)
│   └── gitflow-helper.sh     # Helper de Git Flow (Linux/Mac)
│
├── .github/                  # GitHub Actions y templates
│   ├── workflows/            # CI/CD workflows
│   └── pull_request_template.md
│
├── docker-compose.yml        # Configuración Docker
├── .gitflow                  # Configuración Git Flow
├── GITFLOW.md               # Documentación Git Flow
├── CONTRIBUTING.md          # Guía de contribución
└── README.md                # Este archivo
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Lee [CONTRIBUTING.md](./CONTRIBUTING.md)
2. Revisa [GITFLOW.md](./GITFLOW.md)
3. Crea una rama siguiendo Git Flow
4. Haz tus cambios
5. Escribe tests si es necesario
6. Crea un Pull Request

### Proceso de Code Review

- Todos los PRs requieren al menos 1 aprobación
- Los PRs a `main` requieren 2 aprobaciones
- Los tests de CI/CD deben pasar
- El código debe seguir las convenciones del proyecto

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](./LICENSE) para más detalles.

## 📞 Soporte

- **Issues**: https://github.com/cherrera0001/c4a-autodiagnostico/issues
- **Documentación**: Ver carpeta `docs/`
- **Email**: contacto@c4a.cl

## 🙏 Agradecimientos

- Frameworks de referencia: NIST, COBIT, ISO 27001
- Comunidad open source

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0.0  
**Estado**: En desarrollo activo 🚀
