# Chrome DevTools MCP - Guía de Implementación

Esta guía explica cómo usar las herramientas MCP (Model Context Protocol) de Chrome DevTools en el proyecto C4A para automatización de testing y debugging.

## ¿Qué es Chrome DevTools MCP?

Chrome DevTools MCP es un servidor que expone las capacidades de Chrome DevTools a través del protocolo MCP, permitiendo a agentes de IA y herramientas automatizadas controlar y monitorear Chrome programáticamente.

**Repositorio**: https://github.com/ChromeDevTools/chrome-devtools-mcp

## Herramientas Disponibles

### 1. Automatización de Entrada (7 herramientas)
- `click` - Hacer click en elementos
- `drag` - Arrastrar elementos
- `fill` - Llenar campos de texto
- `fill_form` - Llenar formularios completos
- `handle_dialog` - Manejar diálogos (alerts, confirms)
- `hover` - Hacer hover sobre elementos
- `upload_file` - Subir archivos

### 2. Automatización de Navegación (7 herramientas)
- `close_page` - Cerrar página
- `list_pages` - Listar páginas abiertas
- `navigate_page` - Navegar a URL
- `navigate_page_history` - Navegar historial (atrás/adelante)
- `new_page` - Crear nueva página
- `select_page` - Seleccionar página activa
- `wait_for` - Esperar condiciones

### 3. Emulación (3 herramientas)
- `emulate_cpu` - Emular CPU lenta
- `emulate_network` - Emular condiciones de red
- `resize_page` - Cambiar tamaño de viewport

### 4. Performance (3 herramientas)
- `performance_analyze_insight` - Análisis de performance
- `performance_start_trace` - Iniciar captura de performance
- `performance_stop_trace` - Detener captura de performance

### 5. Network (2 herramientas)
- `get_network_request` - Obtener request específico
- `list_network_requests` - Listar todos los requests

### 6. Debugging (5 herramientas)
- `evaluate_script` - Ejecutar JavaScript
- `get_console_message` - Obtener mensaje de consola
- `list_console_messages` - Listar mensajes de consola
- `take_screenshot` - Capturar screenshot
- `take_snapshot` - Capturar snapshot del DOM

---

## Instalación

El paquete chrome-devtools-mcp se instala automáticamente con npx cuando se ejecuta:

```bash
npx chrome-devtools-mcp@latest
```

No requiere instalación previa.

---

## Configuraciones Disponibles

El proyecto incluye 3 configuraciones MCP en `.mcp-config.json`:

### 1. chrome-devtools (Desarrollo)
Configuración para desarrollo con interfaz visible:
```json
{
  "command": "npx",
  "args": [
    "chrome-devtools-mcp@latest",
    "--headless=false",
    "--isolated=false",
    "--channel=stable"
  ]
}
```

**Uso**: Desarrollo manual, debugging visual

### 2. chrome-devtools-testing (Testing Automatizado)
Configuración para testing sin interfaz:
```json
{
  "command": "npx",
  "args": [
    "chrome-devtools-mcp@latest",
    "--headless=true",
    "--isolated=true",
    "--channel=stable",
    "--viewport=1920x1080"
  ]
}
```

**Uso**: CI/CD, tests automatizados

### 3. chrome-devtools-remote (Instancia Remota)
Configuración para conectarse a Chrome ya corriendo:
```json
{
  "command": "npx",
  "args": [
    "chrome-devtools-mcp@latest",
    "--browser-url=http://127.0.0.1:9222"
  ]
}
```

**Uso**: Debugging de Chrome existente

---

## Uso con Claude Desktop

Si usas Claude Desktop, agrega esto a tu configuración (`claude_desktop_config.json`):

**macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "chrome-devtools-c4a": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--headless=false",
        "--channel=stable"
      ]
    }
  }
}
```

Luego reinicia Claude Desktop.

---

## Ejecutar Tests E2E

### En Windows (PowerShell)

```powershell
# Asegurarse que los servidores estén corriendo
docker-compose up -d

# Ejecutar tests E2E
.\aplicaciones\frontend\scripts\test-e2e-mcp.ps1
```

### En Linux/Mac (Bash)

```bash
# Asegurarse que los servidores estén corriendo
docker-compose up -d

# Ejecutar tests E2E
node aplicaciones/backend/tests/e2e-mcp-tests.js
```

---

## Conectarse a Chrome Manualmente

Si quieres usar tu instancia de Chrome existente:

### Paso 1: Iniciar Chrome con puerto de debugging

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile-mcp
```

**Linux:**
```bash
/usr/bin/google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-profile-mcp
```

**Windows:**
```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$env:TEMP\chrome-profile-mcp"
```

### Paso 2: Conectar MCP

```bash
npx chrome-devtools-mcp@latest --browser-url=http://127.0.0.1:9222
```

---

## Ejemplos de Uso

### Ejemplo 1: Testing de Login

```javascript
// Navegar a login
await mcp.navigatePage('http://localhost:3000/login');

// Llenar formulario
await mcp.fill('input[name="email"]', 'admin@c4a.cl');
await mcp.fill('input[name="password"]', 'Admin123!');

// Capturar screenshot antes de submit
await mcp.takeScreenshot('before-login');

// Hacer click en submit
await mcp.click('button[type="submit"]');

// Esperar navegación
await mcp.waitFor('navigation');

// Capturar screenshot después
await mcp.takeScreenshot('after-login');
```

### Ejemplo 2: Análisis de Performance

```javascript
// Navegar a la página
await mcp.navigatePage('http://localhost:3000');

// Iniciar trace
await mcp.performanceStartTrace();

// Realizar acciones
await mcp.click('#some-button');
await mcp.waitFor('networkIdle');

// Detener trace y analizar
const trace = await mcp.performanceStopTrace();
const insights = await mcp.performanceAnalyzeInsight();

console.log('Métricas:', insights.metrics);
```

### Ejemplo 3: Debugging de Errores

```javascript
// Navegar a la app
await mcp.navigatePage('http://localhost:3000');

// Ejecutar acciones
await mcp.click('#trigger-error');

// Obtener mensajes de consola
const messages = await mcp.listConsoleMessages();

// Filtrar errores
const errors = messages.filter(m => m.level === 'error');

// Capturar screenshot si hay errores
if (errors.length > 0) {
  await mcp.takeScreenshot('error-state');
  console.log('Errores encontrados:', errors);
}
```

### Ejemplo 4: Testing de Responsive

```javascript
// Desktop
await mcp.resizePage({ width: 1920, height: 1080 });
await mcp.takeScreenshot('desktop-view');

// Tablet
await mcp.resizePage({ width: 768, height: 1024 });
await mcp.takeScreenshot('tablet-view');

// Mobile
await mcp.resizePage({ width: 375, height: 667 });
await mcp.takeScreenshot('mobile-view');
```

---

## Casos de Uso en C4A

### 1. Testing de Autenticación
- Verificar login de admin
- Verificar login de usuario empresarial
- Verificar redirección según rol
- Verificar manejo de credenciales inválidas

### 2. Testing de Dashboard
- Verificar carga de métricas
- Verificar gráficos
- Verificar acciones rápidas
- Verificar navegación

### 3. Testing de Evaluaciones
- Crear nueva evaluación
- Responder cuestionario
- Verificar guardado de respuestas
- Generar reporte PDF

### 4. Performance Monitoring
- Medir tiempo de carga inicial
- Medir tiempo de navegación
- Identificar recursos lentos
- Verificar optimizaciones

### 5. Debugging Visual
- Capturar screenshots de errores
- Grabar videos de flujos
- Inspeccionar estado de componentes
- Verificar estilos y layout

---

## Opciones de Configuración

### Opciones Disponibles

- `--browserUrl` o `-u` - URL del browser (para port forwarding)
- `--wsEndpoint` o `-w` - WebSocket endpoint
- `--wsHeaders` - Headers personalizados para WebSocket
- `--headless` - Modo sin interfaz (default: false)
- `--executablePath` o `-e` - Ruta a Chrome custom
- `--isolated` - Usar perfil temporal (default: false)
- `--channel` - Canal de Chrome (stable, canary, beta, dev)
- `--logFile` - Archivo para logs de debug
- `--viewport` - Tamaño inicial de viewport (ej: 1920x1080)
- `--proxyServer` - Configuración de proxy
- `--acceptInsecureCerts` - Ignorar errores de certificados
- `--chromeArg` - Argumentos adicionales para Chrome

### Ejemplo de Configuración Avanzada

```json
{
  "mcpServers": {
    "chrome-devtools-advanced": {
      "command": "npx",
      "args": [
        "chrome-devtools-mcp@latest",
        "--headless=true",
        "--isolated=true",
        "--viewport=1920x1080",
        "--logFile=./logs/mcp-chrome.log",
        "--chromeArg=--disable-gpu",
        "--chromeArg=--no-sandbox"
      ]
    }
  }
}
```

---

## Directorio de Datos de Usuario

El MCP usa estos directorios por defecto:

- **Linux/macOS**: `$HOME/.cache/chrome-devtools-mcp/chrome-profile-$CHANNEL`
- **Windows**: `%HOMEPATH%/.cache/chrome-devtools-mcp/chrome-profile-$CHANNEL`

Con `--isolated=true`, usa un directorio temporal que se limpia automáticamente.

---

## Limitaciones Conocidas

### 1. Sandboxes del Sistema Operativo
Si el cliente MCP usa sandboxes (macOS Seatbelt, Linux containers), puede que no pueda iniciar Chrome. 

**Solución**: Usar `--browser-url` para conectarse a Chrome iniciado manualmente.

### 2. Port Forwarding VM-Host
Si usas VMs, puede haber problemas de port forwarding.

**Solución**: Ver `docs/troubleshooting.md` en el repositorio oficial.

---

## Troubleshooting

### Chrome no inicia

**Problema**: El MCP no puede iniciar Chrome

**Soluciones**:
1. Verificar que Chrome está instalado
2. Usar `--executablePath` para especificar ruta
3. Usar `--browser-url` para conectar a Chrome existente

### Port 9222 ya en uso

**Problema**: El puerto de debugging ya está ocupado

**Soluciones**:
1. Cerrar todas las instancias de Chrome
2. Usar un puerto diferente
3. Conectarse a la instancia existente con `--browser-url`

### Permisos denegados

**Problema**: Error de permisos al crear directorios

**Soluciones**:
1. Usar `--isolated=true` para usar directorio temporal
2. Verificar permisos en el directorio de usuario
3. Ejecutar con permisos adecuados

### Screenshots no se guardan

**Problema**: Los screenshots no aparecen

**Soluciones**:
1. Verificar que el directorio de screenshots existe
2. Verificar permisos de escritura
3. Especificar ruta absoluta

---

## Recursos

- **Repositorio oficial**: https://github.com/ChromeDevTools/chrome-devtools-mcp
- **NPM Package**: https://npmjs.org/package/chrome-devtools-mcp
- **Documentación MCP**: https://modelcontextprotocol.io/
- **Chrome DevTools Protocol**: https://chromedevtools.github.io/devtools-protocol/

---

## Scripts Disponibles

### Windows
```powershell
# Testing E2E completo
.\aplicaciones\frontend\scripts\test-e2e-mcp.ps1
```

### Linux/Mac
```bash
# Testing E2E completo
node aplicaciones/backend/tests/e2e-mcp-tests.js
```

---

## Próximos Pasos

1. **Implementar tests reales**: El script actual es una simulación, integrar con el SDK MCP real
2. **Agregar más tests**: Cubrir más flujos de la aplicación
3. **CI/CD Integration**: Integrar en pipeline de GitHub Actions
4. **Visual Regression**: Comparar screenshots automáticamente
5. **Performance Monitoring**: Alertas automáticas de degradación

---

## Soporte

Para problemas o preguntas:
- Issues del proyecto: https://github.com/ChromeDevTools/chrome-devtools-mcp/issues
- Documentación: Ver este archivo y el repositorio oficial

---

**Última actualización**: Octubre 2025  
**Versión Chrome DevTools MCP**: 0.8.1+  
**Compatible con**: C4A v1.0.0




