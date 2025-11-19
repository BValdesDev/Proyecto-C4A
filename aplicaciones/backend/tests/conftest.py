"""
Configuración global de pytest para las pruebas del backend.
Este archivo asegura que el módulo 'app' pueda ser importado correctamente.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz del backend al PYTHONPATH
backend_root = Path(__file__).parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

