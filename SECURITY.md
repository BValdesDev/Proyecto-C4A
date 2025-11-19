# Política de Seguridad

## Versión Soportada

Actualmente, solo la última versión del proyecto recibe actualizaciones de seguridad. Por favor, asegúrate de estar ejecutando la versión más reciente.

## Divulgación Responsable

La seguridad es una prioridad para el equipo de C4A. Si descubres una vulnerabilidad de seguridad, apreciamos tu ayuda para divulgarla de manera responsable.

### Cómo Reportar una Vulnerabilidad

1. **No** divulgues la vulnerabilidad públicamente ni crees un issue público en GitHub.
2. Envía un email a: **security@c4a.cl** con el asunto: `[CVE-Report] - Descripción breve de la vulnerabilidad`
3. Incluye los siguientes detalles:
   - Tipo de vulnerabilidad (ej: XSS, SQL Injection, autenticación, etc.)
   - Componente afectado (backend, frontend, API, etc.)
   - Pasos para reproducir la vulnerabilidad
   - Impacto potencial de la vulnerabilidad
   - Sugerencias de mitigación (si las tienes)
   - Tu información de contacto (opcional)

### Proceso de Respuesta

1. **Confirmación**: Recibirás una confirmación de recepción dentro de 48 horas.
2. **Evaluación**: Evaluaremos el reporte y te informaremos de nuestro análisis inicial dentro de 5 días hábiles.
3. **Resolución**: Trabajaremos contigo para entender y validar la vulnerabilidad.
4. **Corrección**: Desarrollaremos y probaremos un fix.
5. **Divulgación**: Coordinaremos la divulgación pública después de que se haya publicado una corrección.

### Lo que NO Reportar

- Problemas de configuración de servidores (no relacionados con el código)
- Vulnerabilidades en dependencias obsoletas (en su lugar, usa Dependabot)
- Problemas de spam o phishing
- Denegación de servicio (DoS)
- Vulnerabilidades que requieren acceso físico al dispositivo
- Vulnerabilidades que requieren acceso a la red local (MITM)

## Buenas Prácticas de Seguridad

### Para Desarrolladores

1. **Nunca commitees credenciales**: Usa variables de entorno o secretos de gestión.
2. **Revisa dependencias**: Mantén las dependencias actualizadas usando `npm audit` y `safety check`.
3. **Valida inputs**: Siempre valida y sanitiza los inputs del usuario.
4. **Usa HTTPS**: Nunca envíes información sensible sobre conexiones HTTP.
5. **Principio de menor privilegio**: Otorga solo los permisos mínimos necesarios.

### Para Usuarios

1. **Mantén actualizado**: Instala las actualizaciones de seguridad tan pronto como estén disponibles.
2. **Usa contraseñas fuertes**: Usa contraseñas únicas y complejas.
3. **Habilita 2FA**: Activa la autenticación de dos factores cuando esté disponible.
4. **Revisa permisos**: Revisa regularmente los permisos y accesos de tu cuenta.

## Programa de Recompensas

Actualmente, no operamos un programa formal de recompensas por errores (bug bounty). Sin embargo, agradecemos públicamente a los investigadores de seguridad que reporten vulnerabilidades de manera responsable y pueden ser reconocidos en nuestros agradecimientos de seguridad.

## Historial de Divulgaciones

Las vulnerabilidades corregidas y divulgadas se listarán aquí después de que se haya publicado un fix:

### 2024

- No hay divulgaciones públicas hasta la fecha.

## Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [MITRE ATT&CK](https://attack.mitre.org/)

## Contacto

Para preguntas sobre seguridad que no sean vulnerabilidades:
- Email: **info@c4a.cl**
- Website: **https://c4a.cl**

---

**Última actualización**: Diciembre 2024




