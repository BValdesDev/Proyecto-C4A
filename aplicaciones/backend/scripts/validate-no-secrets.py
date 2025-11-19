#!/usr/bin/env python3
"""
Script para validar que config.py no contiene valores hardcodeados
Verifica que todas las variables sensibles se carguen desde variables de entorno
"""

import re
import sys
from pathlib import Path

# Patrones que NO deben aparecer en config.py
FORBIDDEN_PATTERNS = [
    # Claves RSA hardcodeadas
    (r'-----BEGIN\s+(RSA\s+)?(PRIVATE|PUBLIC)\s+KEY-----', 'Claves RSA hardcodeadas detectadas'),
    
    # Contraseñas hardcodeadas (más de 8 caracteres)
    (r'password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', 'Contraseñas hardcodeadas detectadas'),
    
    # URLs de base de datos con credenciales hardcodeadas
    (r'postgresql.*://[^:]+:[^@]+@', 'URL de base de datos con credenciales hardcodeadas'),
    
    # Claves de cifrado hardcodeadas
    (r'clave_maestra_cifrado\s*[:=]\s*["\'][^"\']{10,}["\']', 'Clave maestra de cifrado hardcodeada'),
    
    # Tokens JWT hardcodeados
    (r'jwt.*secret.*[:=]\s*["\'][^"\']{20,}["\']', 'Secreto JWT hardcodeado'),
    
    # Claves de Stripe hardcodeadas (excepto en comentarios)
    (r'(sk_live_|sk_test_|pk_live_)[a-zA-Z0-9]{24,}', 'Clave de Stripe hardcodeada'),
    
    # Credenciales de email hardcodeadas
    (r'email.*password["\']?\s*[:=]\s*["\'][^"\']{6,}["\']', 'Contraseña de email hardcodeada'),
]

# Patrones permitidos (valores vacíos o desde variables de entorno)
ALLOWED_PATTERNS = [
    r'= ""',  # Valores vacíos
    r'= os\.getenv\(',  # Variables de entorno con os.getenv
    r'BaseSettings',  # Pydantic BaseSettings
    r'Field\(',  # Pydantic Field
    r'# .*',  # Comentarios
]

def check_config_file(file_path: Path) -> tuple[bool, list[str]]:
    """
    Verifica que config.py no contenga valores hardcodeados
    Retorna (es_valido, lista_de_errores)
    """
    errors = []
    
    if not file_path.exists():
        return False, [f"Archivo no encontrado: {file_path}"]
    
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Verificar cada línea
    for line_num, line in enumerate(lines, 1):
        # Saltar comentarios
        if line.strip().startswith('#'):
            continue
        
        # Verificar patrones prohibidos
        for pattern, error_msg in FORBIDDEN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Verificar que no sea un comentario
                if '#' in line:
                    comment_start = line.index('#')
                    if re.search(pattern, line[:comment_start], re.IGNORECASE):
                        errors.append(f"Línea {line_num}: {error_msg}")
                        errors.append(f"  Contenido: {line.strip()}")
                else:
                    errors.append(f"Línea {line_num}: {error_msg}")
                    errors.append(f"  Contenido: {line.strip()}")
    
    # Verificar que las variables críticas usen valores vacíos o BaseSettings
    critical_vars = [
        'clave_publica_jwt',
        'clave_privada_jwt',
        'url_base_datos',
        'clave_maestra_cifrado',
        'email_user',
        'email_password',
    ]
    
    for var in critical_vars:
        # Buscar definiciones de estas variables
        pattern = rf'{var}\s*[:=]\s*["\']([^"\']+)["\']'
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            value = match.group(1)
            # Si el valor no está vacío y no es un placeholder, es un problema
            if value and value not in ['', 'TU_CLAVE_PUBLICA_RSA_AQUI', 'TU_CLAVE_PRIVADA_RSA_AQUI', 
                                      'tu-clave-maestra-segura-de-al-menos-32-caracteres-aqui',
                                      'tu-email@gmail.com', 'tu-app-password-aqui',
                                      'postgresql+asyncpg://usuario:contraseña@localhost:5432/c4a_saas']:
                # Verificar que no sea una clave real
                if len(value) > 20 and not value.startswith('TU_') and not value.startswith('tu-'):
                    line_num = content[:match.start()].count('\n') + 1
                    errors.append(f"Línea {line_num}: Variable {var} tiene un valor que parece real: {value[:50]}...")
    
    return len(errors) == 0, errors

def main():
    """Función principal"""
    # Ruta al archivo config.py
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    config_file = backend_dir / 'app' / 'core' / 'config.py'
    
    # Verificar que estamos en el directorio correcto
    if not config_file.exists():
        print(f"❌ Error: No se encontró {config_file}")
        print(f"   Directorio actual: {Path.cwd()}")
        print(f"   Script en: {script_dir}")
        return 1
    
    print("🔍 Validando que config.py no contiene valores hardcodeados...")
    print(f"📁 Archivo: {config_file}")
    print()
    
    is_valid, errors = check_config_file(config_file)
    
    if is_valid:
        print("✅ Validación exitosa: config.py no contiene valores hardcodeados")
        print()
        print("✅ Todas las variables sensibles se cargan desde variables de entorno")
        return 0
    else:
        print("❌ Validación fallida: Se encontraron valores hardcodeados en config.py")
        print()
        print("Errores encontrados:")
        print("-" * 80)
        for error in errors:
            print(error)
        print("-" * 80)
        print()
        print("💡 Solución:")
        print("  1. Elimina todos los valores hardcodeados de config.py")
        print("  2. Usa valores vacíos ('') como defaults")
        print("  3. Carga los valores desde variables de entorno usando BaseSettings")
        print("  4. Configura las variables en el archivo .env")
        return 1

if __name__ == "__main__":
    sys.exit(main())

