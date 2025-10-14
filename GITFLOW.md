# 🌳 Git Flow - Guía de Uso para C4A

## 📋 Tabla de Contenidos
1. [¿Qué es Git Flow?](#qué-es-git-flow)
2. [Estructura de Ramas](#estructura-de-ramas)
3. [Flujo de Trabajo](#flujo-de-trabajo)
4. [Comandos Comunes](#comandos-comunes)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Reglas y Mejores Prácticas](#reglas-y-mejores-prácticas)

---

## 🎯 ¿Qué es Git Flow?

Git Flow es una estrategia de branching que nos ayuda a:
- ✅ Mantener el código organizado y estable
- ✅ Trabajar en múltiples features simultáneamente
- ✅ Facilitar la colaboración en equipo
- ✅ Tener control sobre las versiones de producción
- ✅ Gestionar hotfixes de emergencia sin afectar el desarrollo

---

## 🌿 Estructura de Ramas

### Ramas Principales (Permanentes)

#### 🔴 `main` (Producción)
- **Propósito**: Código en producción
- **Estabilidad**: 100% estable y probado
- **Protección**: ⛔ No se puede hacer commit directo
- **Deploy**: Automático a producción
- **Acceso**: Solo mediante merge de `release/*` o `hotfix/*`

#### 🟢 `develop` (Desarrollo)
- **Propósito**: Rama de integración de desarrollo
- **Estabilidad**: Debe ser funcional, pero puede tener bugs menores
- **Protección**: ⚠️ Solo merge desde features, releases, hotfixes
- **Deploy**: Automático a entorno de staging/desarrollo
- **Acceso**: Mediante Pull Requests aprobados

---

### Ramas Temporales (Se eliminan después de merge)

#### 🔵 `feature/*` - Nuevas Funcionalidades
- **Nomenclatura**: `feature/nombre-descriptivo`
- **Origen**: Se crea desde `develop`
- **Destino**: Se mergea a `develop`
- **Duración**: Días o semanas
- **Ejemplos**:
  - `feature/login-sso`
  - `feature/dashboard-analytics`
  - `feature/stripe-integration`

#### 🟡 `release/*` - Preparación de Versión
- **Nomenclatura**: `release/v1.2.0`
- **Origen**: Se crea desde `develop`
- **Destino**: Se mergea a `main` Y `develop`
- **Duración**: Días
- **Propósito**: Preparar release, últimas pruebas, actualizar versión

#### 🔴 `hotfix/*` - Correcciones Urgentes
- **Nomenclatura**: `hotfix/nombre-del-bug`
- **Origen**: Se crea desde `main`
- **Destino**: Se mergea a `main` Y `develop`
- **Duración**: Horas
- **Propósito**: Corregir bugs críticos en producción

#### 🟣 `bugfix/*` - Corrección de Bugs (Opcional)
- **Nomenclatura**: `bugfix/nombre-del-bug`
- **Origen**: Se crea desde `develop`
- **Destino**: Se mergea a `develop`
- **Duración**: Horas/días
- **Propósito**: Corregir bugs no críticos durante desarrollo

---

## 🔄 Flujo de Trabajo

### 1. Desarrollo de Nueva Funcionalidad

```bash
# 1. Actualizar develop
git checkout develop
git pull origin develop

# 2. Crear feature branch
git checkout -b feature/nombre-descriptivo

# 3. Trabajar en la feature
git add .
git commit -m "feat: descripción del cambio"
git push origin feature/nombre-descriptivo

# 4. Crear Pull Request en GitHub/GitLab
# → De feature/nombre-descriptivo a develop

# 5. Después del merge, eliminar rama
git checkout develop
git pull origin develop
git branch -d feature/nombre-descriptivo
```

### 2. Preparar un Release

```bash
# 1. Crear rama de release desde develop
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. Actualizar versión en archivos
# - package.json
# - backend/version.py
# - etc.

# 3. Commit de versión
git add .
git commit -m "chore: preparar release v1.2.0"
git push origin release/v1.2.0

# 4. Crear PR a main (producción)
# → De release/v1.2.0 a main

# 5. Después del merge a main, mergear a develop también
git checkout develop
git merge release/v1.2.0
git push origin develop

# 6. Crear tag en main
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0

# 7. Eliminar rama de release
git branch -d release/v1.2.0
```

### 3. Hotfix de Emergencia

```bash
# 1. Crear hotfix desde main
git checkout main
git pull origin main
git checkout -b hotfix/corregir-login

# 2. Hacer la corrección
git add .
git commit -m "fix: corregir error crítico en login"
git push origin hotfix/corregir-login

# 3. Crear PR a main
# → De hotfix/corregir-login a main

# 4. Después del merge, también mergear a develop
git checkout develop
git merge hotfix/corregir-login
git push origin develop

# 5. Crear tag si es necesario
git checkout main
git tag -a v1.2.1 -m "Hotfix v1.2.1"
git push origin v1.2.1

# 6. Eliminar rama de hotfix
git branch -d hotfix/corregir-login
```

---

## 💻 Comandos Comunes

### Ver el estado de las ramas

```bash
# Ver todas las ramas
git branch -a

# Ver rama actual
git branch --show-current

# Ver ramas remotas
git branch -r
```

### Actualizar tu rama local

```bash
# Actualizar develop
git checkout develop
git pull origin develop

# Actualizar tu feature con los últimos cambios de develop
git checkout feature/mi-feature
git merge develop
# o usar rebase para historial más limpio
git rebase develop
```

### Limpiar ramas

```bash
# Eliminar rama local
git branch -d nombre-rama

# Eliminar rama remota
git push origin --delete nombre-rama

# Ver ramas que ya fueron mergeadas
git branch --merged

# Limpiar referencias a ramas remotas eliminadas
git fetch --prune
```

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Implementar Login con SSO

```bash
# Paso 1: Crear feature
git checkout develop
git pull origin develop
git checkout -b feature/sso-login

# Paso 2: Desarrollar
# ... trabajar en los archivos ...
git add aplicaciones/frontend/src/componentes/auth/SSOLogin.tsx
git commit -m "feat: implementar componente SSOLogin"

git add aplicaciones/backend/app/api/v1/endpoints/auth.py
git commit -m "feat: agregar endpoint para autenticación SSO"

# Paso 3: Subir y crear PR
git push origin feature/sso-login
# Crear Pull Request en GitHub

# Paso 4: Después del code review y merge
git checkout develop
git pull origin develop
git branch -d feature/sso-login
```

### Ejemplo 2: Preparar Release 1.5.0

```bash
# Paso 1: Crear release branch
git checkout develop
git pull origin develop
git checkout -b release/v1.5.0

# Paso 2: Actualizar versiones
# Editar package.json, cambiar version a "1.5.0"
git add package.json aplicaciones/frontend/package.json
git commit -m "chore: bump version to 1.5.0"

# Paso 3: Actualizar CHANGELOG
# Editar CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: actualizar CHANGELOG para v1.5.0"

# Paso 4: Push y crear PRs
git push origin release/v1.5.0
# Crear PR a main
# Crear PR a develop

# Paso 5: Después del merge, crear tag
git checkout main
git pull origin main
git tag -a v1.5.0 -m "Release v1.5.0 - Nuevas funcionalidades de dashboard"
git push origin v1.5.0
```

### Ejemplo 3: Hotfix Urgente

```bash
# Bug crítico en producción: usuarios no pueden hacer login
git checkout main
git pull origin main
git checkout -b hotfix/fix-login-validation

# Corregir el bug
git add aplicaciones/backend/app/core/seguridad.py
git commit -m "fix: corregir validación de token en login"

git push origin hotfix/fix-login-validation
# Crear PR a main (urgente)

# Después del merge a main
git checkout develop
git merge hotfix/fix-login-validation
git push origin develop

# Tag de hotfix
git checkout main
git tag -a v1.4.1 -m "Hotfix v1.4.1 - Corregir validación de login"
git push origin v1.4.1
```

---

## 📏 Reglas y Mejores Prácticas

### ✅ DO - Hacer

1. **Siempre crear features desde develop actualizado**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/mi-feature
   ```

2. **Usar nombres descriptivos para las ramas**
   - ✅ `feature/stripe-payment-integration`
   - ✅ `bugfix/corregir-validacion-email`
   - ❌ `feature/cambios`
   - ❌ `fix`

3. **Hacer commits pequeños y descriptivos**
   ```bash
   git commit -m "feat: agregar botón de pago con Stripe"
   git commit -m "test: agregar tests para componente Payment"
   git commit -m "docs: actualizar README con instrucciones de Stripe"
   ```

4. **Usar Conventional Commits**
   - `feat:` - Nueva funcionalidad
   - `fix:` - Corrección de bug
   - `docs:` - Documentación
   - `style:` - Formato, punto y coma faltantes, etc.
   - `refactor:` - Refactorización de código
   - `test:` - Agregar tests
   - `chore:` - Cambios en build, dependencias, etc.

5. **Crear Pull Requests con descripción clara**
   - Descripción del cambio
   - Screenshots (si aplica)
   - Tests realizados
   - Notas para el reviewer

6. **Mantener develop y main protegidas**
   - Requerir code review antes de merge
   - Ejecutar CI/CD antes de merge
   - No permitir force push

7. **Eliminar ramas después del merge**
   ```bash
   git branch -d feature/mi-feature
   git push origin --delete feature/mi-feature
   ```

8. **Actualizar tu feature con develop regularmente**
   ```bash
   git checkout feature/mi-feature
   git fetch origin
   git merge origin/develop
   ```

### ❌ DON'T - No Hacer

1. **❌ NO hacer commit directo a main o develop**
   ```bash
   # NUNCA hagas esto:
   git checkout main
   git commit -m "cambio rápido"  # ❌ MAL
   ```

2. **❌ NO usar force push en ramas compartidas**
   ```bash
   # EVITAR en ramas públicas:
   git push --force origin develop  # ❌ MAL
   ```

3. **❌ NO crear features desde main**
   ```bash
   # INCORRECTO:
   git checkout main
   git checkout -b feature/nueva  # ❌ MAL
   
   # CORRECTO:
   git checkout develop
   git checkout -b feature/nueva  # ✅ BIEN
   ```

4. **❌ NO dejar ramas muertas en el repositorio**
   - Eliminar ramas después de merge
   - Usar `git fetch --prune` regularmente

5. **❌ NO hacer merge de develop a main directamente**
   - Siempre usar release branches
   - main solo recibe merges de release/* o hotfix/*

6. **❌ NO mezclar múltiples features en una sola rama**
   - Una feature = una rama
   - Mantener cambios aislados y fáciles de revisar

7. **❌ NO olvidar actualizar develop después de un hotfix**
   ```bash
   # Después de mergear hotfix a main:
   git checkout develop
   git merge hotfix/mi-fix  # ✅ IMPORTANTE
   ```

---

## 🔧 Configuración de GitHub

### Protección de Ramas

Configurar en GitHub: Settings → Branches → Branch protection rules

#### Para `main`:
- ✅ Require a pull request before merging
- ✅ Require approvals: 2
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators
- ✅ Restrict who can push to matching branches

#### Para `develop`:
- ✅ Require a pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

---

## 🎓 Recursos Adicionales

- [Git Flow Original](https://nvie.com/posts/a-successful-git-branching-model/)
- [Atlassian Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📞 Contacto y Soporte

Si tienes dudas sobre Git Flow o necesitas ayuda:
- Consulta con el Tech Lead del proyecto
- Revisa esta documentación
- Pregunta en el canal de #desarrollo del equipo

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0.0  
**Mantenedor**: Equipo C4A

