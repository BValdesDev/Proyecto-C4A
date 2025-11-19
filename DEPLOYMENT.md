# 🚀 GUÍA DE DESPLIEGUE - C4A AUTODIAGNÓSTICO

Esta guía proporciona un checklist completo para el despliegue seguro de la plataforma C4A Autodiagnóstico.

---

## 📋 CHECKLIST PRE-DESPLIEGUE DE SEGURIDAD

### ✅ Configuración de Entorno

- [ ] **Variables de Entorno Configuradas**
  - [ ] `.env` creado desde `env.example`
  - [ ] Todas las variables críticas configuradas:
    - [ ] `CLAVE_PUBLICA_JWT` y `CLAVE_PRIVADA_JWT` (claves RSA generadas)
    - [ ] `URL_BASE_DATOS` (con credenciales reales)
    - [ ] `CLAVE_MAESTRA_CIFRADO` (clave segura generada)
    - [ ] `EMAIL_USER` y `EMAIL_PASSWORD`
    - [ ] `STRIPE_CLAVE_PUBLICA` y `STRIPE_CLAVE_SECRETA`
    - [ ] `CORS_ORIGINS` (solo orígenes permitidos en producción)
  - [ ] `ENTORNO=produccion`
  - [ ] `DEBUG=false`
  - [ ] `SALTAR_VERIFICACION_EMAIL=false`
  - [ ] `SALTAR_WEBHOOKS_STRIPE=false`
  - [ ] `SIMULAR_SERVICIOS_EXTERNOS=false`

- [ ] **Claves RSA Generadas**
  - [ ] Claves RSA generadas con `scripts/generar_claves_rsa.py` o `openssl`
  - [ ] Claves convertidas a formato de una línea para `.env`
  - [ ] Claves almacenadas de forma segura (no en repositorio)
  - [ ] Claves agregadas a `.gitignore`

- [ ] **Archivos de Configuración**
  - [ ] `.env` en `.gitignore`
  - [ ] `jwt_*.pem` en `.gitignore`
  - [ ] No hay valores hardcodeados en `config.py`

### ✅ Seguridad

- [ ] **Validación de Secretos**
  - [ ] Ejecutado `scripts/validate-no-secrets.py` - ✅ Sin errores
  - [ ] No hay claves hardcodeadas en código
  - [ ] No hay contraseñas en código fuente

- [ ] **Dependencias Auditadas**
  - [ ] Backend: `pip-audit` o `safety check` ejecutado - ✅ Sin vulnerabilidades críticas
  - [ ] Frontend: `npm audit` ejecutado - ✅ Sin vulnerabilidades críticas
  - [ ] Dependencias actualizadas a versiones seguras

- [ ] **Análisis de Seguridad**
  - [ ] `bandit` ejecutado en backend - ✅ Sin vulnerabilidades HIGH
  - [ ] `gitleaks` ejecutado - ✅ Sin secretos detectados
  - [ ] Pipeline de seguridad en GitHub Actions - ✅ Todos los jobs pasan

### ✅ Base de Datos

- [ ] **PostgreSQL Configurado**
  - [ ] Base de datos creada
  - [ ] Usuario y contraseña configurados
  - [ ] Migraciones ejecutadas: `alembic upgrade head`
  - [ ] Datos de prueba eliminados (si aplica)
  - [ ] Backups configurados

- [ ] **Redis Configurado**
  - [ ] Redis instalado y corriendo
  - [ ] URL de conexión configurada
  - [ ] Persistencia configurada (si aplica)

### ✅ Infraestructura

- [ ] **Servidor Web**
  - [ ] HTTPS configurado con certificados válidos
  - [ ] CORS configurado correctamente (solo orígenes permitidos)
  - [ ] Headers de seguridad configurados
  - [ ] Rate limiting configurado

- [ ] **Monitoreo y Logging**
  - [ ] Logging configurado
  - [ ] Monitoreo de errores configurado (Sentry, etc.)
  - [ ] Alertas configuradas

### ✅ Aplicación

- [ ] **Backend**
  - [ ] Aplicación inicia correctamente
  - [ ] Endpoint `/health` responde correctamente
  - [ ] Autenticación JWT funciona
  - [ ] Conexión a base de datos funciona
  - [ ] Conexión a Redis funciona

- [ ] **Frontend**
  - [ ] Build de producción generado: `npm run build`
  - [ ] Frontend conecta correctamente con backend
  - [ ] Variables de entorno configuradas (`VITE_API_URL`, etc.)
  - [ ] No hay errores en consola

### ✅ Integraciones

- [ ] **Stripe**
  - [ ] Claves de producción configuradas
  - [ ] Webhooks configurados y verificados
  - [ ] URLs de webhook correctas

- [ ] **Email**
  - [ ] Servidor SMTP configurado
  - [ ] Credenciales de email configuradas
  - [ ] Envío de emails probado

---

## 🔧 CONFIGURACIÓN INICIAL

### 1. Configurar Entorno Local

#### Opción A: Script Automático (Linux/Mac)
```bash
cd aplicaciones/backend
chmod +x scripts/setup-env.sh
./scripts/setup-env.sh
```

#### Opción B: Script Automático (Windows)
```powershell
cd aplicaciones\backend
.\scripts\setup-env.ps1
```

#### Opción C: Manual
```bash
# 1. Copiar env.example a .env
cd aplicaciones/backend
cp env.example .env

# 2. Generar claves RSA
python scripts/generar_claves_rsa.py
# O con openssl:
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem

# 3. Convertir claves a formato de una línea
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_public.pem
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_private.pem

# 4. Generar clave maestra de cifrado
openssl rand -hex 32
```

### 2. Configurar Variables de Entorno

Edita `.env` y configura:

```env
# Entorno
ENTORNO=produccion
DEBUG=false

# Base de datos
URL_BASE_DATOS=postgresql+asyncpg://usuario:contraseña@host:puerto/c4a_saas

# JWT (claves en formato de una línea)
CLAVE_PUBLICA_JWT=-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----
CLAVE_PRIVADA_JWT=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQD...\n-----END PRIVATE KEY-----

# Cifrado
CLAVE_MAESTRA_CIFRADO=tu-clave-generada-con-openssl-rand-hex-32

# Email
EMAIL_USER=tu-email@gmail.com
EMAIL_PASSWORD=tu-app-password

# Stripe
STRIPE_CLAVE_PUBLICA=pk_live_tu_clave_publica
STRIPE_CLAVE_SECRETA=sk_live_tu_clave_secreta

# CORS (solo orígenes permitidos en producción)
CORS_ORIGINS=https://c4a.cl,https://app.c4a.cl
```

### 3. Validar Configuración

```bash
cd aplicaciones/backend

# Validar que no hay secretos hardcodeados
python scripts/validate-no-secrets.py

# Validar que la configuración carga correctamente
python -c "from app.core.config import config; print('✅ Configuración válida')"

# Probar endpoint de health
curl http://localhost:8000/health
```

---

## 🐳 DESPLIEGUE CON DOCKER

### 1. Configurar Variables de Entorno en Docker

Crea un archivo `.env` en la raíz del proyecto o usa variables de entorno del sistema.

### 2. Construir y Ejecutar

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar salud
curl http://localhost:8000/health
```

### 3. Ejecutar Migraciones

```bash
docker-compose exec backend alembic upgrade head
```

---

## ☁️ DESPLIEGUE EN PRODUCCIÓN

### Opciones de Despliegue

1. **Azure App Service**
   - Configurar variables de entorno en Azure Portal
   - Usar Azure Key Vault para secretos
   - Configurar Application Insights

2. **AWS Elastic Beanstalk / ECS**
   - Configurar variables de entorno en AWS Systems Manager Parameter Store
   - Usar AWS Secrets Manager para secretos
   - Configurar CloudWatch

3. **Google Cloud Run**
   - Configurar variables de entorno en Cloud Run
   - Usar Google Secret Manager para secretos
   - Configurar Cloud Monitoring

### Gestión de Secretos en Producción

**NUNCA** almacenes secretos en:
- Código fuente
- Variables de entorno en archivos
- Repositorios Git

**SÍ** usa:
- Azure Key Vault
- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- Otras soluciones de gestión de secretos

---

## 🔍 VERIFICACIÓN POST-DESPLIEGUE

### 1. Verificar Endpoints

```bash
# Health check
curl https://api.c4a.cl/health

# Verificar que no expone información sensible
curl https://api.c4a.cl/
```

### 2. Verificar Seguridad

- [ ] HTTPS funciona correctamente
- [ ] Headers de seguridad presentes
- [ ] CORS configurado correctamente
- [ ] No hay información sensible en respuestas
- [ ] Rate limiting funciona

### 3. Verificar Funcionalidad

- [ ] Login funciona
- [ ] Registro funciona
- [ ] Creación de evaluaciones funciona
- [ ] Generación de reportes funciona
- [ ] Integración con Stripe funciona

---

## 🚨 ROLLBACK

Si algo sale mal:

1. **Detener servicios**
   ```bash
   docker-compose down
   # O detener servicios en la plataforma cloud
   ```

2. **Restaurar base de datos** (si aplica)
   ```bash
   # Restaurar desde backup
   ```

3. **Revertir código**
   ```bash
   git revert <commit-hash>
   # O desplegar versión anterior
   ```

---

## 📞 SOPORTE

Si encuentras problemas durante el despliegue:

1. Revisa los logs: `docker-compose logs` o logs de la plataforma cloud
2. Verifica las variables de entorno
3. Consulta la documentación de troubleshooting
4. Contacta al equipo de desarrollo

---

## 📚 RECURSOS ADICIONALES

- [Documentación de FastAPI](https://fastapi.tiangolo.com/)
- [Documentación de React](https://react.dev/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Guía de Seguridad de Python](https://python.readthedocs.io/en/stable/library/security.html)

---

**Última actualización**: 2024



