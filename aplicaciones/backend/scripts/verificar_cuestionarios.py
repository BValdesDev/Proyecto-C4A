#!/usr/bin/env python3
"""
Script para verificar que existan los cuestionarios necesarios
y que tengan el número correcto de preguntas
"""

import os
import sys

# Ajustar path para imports
sys.path.insert(0, '/app')

from app.modelos.base import SessionLocal
from app.modelos.cuestionario import Cuestionario, CuestionarioPregunta, NivelCuestionario

def verificar_cuestionarios():
    """Verificar que existan los cuestionarios necesarios"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Verificación de Cuestionarios")
        print("=" * 60)
        print()
        
        niveles_requeridos = {
            NivelCuestionario.basico: 10,
            NivelCuestionario.intermedio: 50,
            NivelCuestionario.avanzado: 100
        }
        
        todos_ok = True
        
        for nivel, preguntas_esperadas in niveles_requeridos.items():
            print(f"📋 Verificando cuestionario {nivel.value.upper()}...")
            
            cuestionario = db.query(Cuestionario).filter(
                Cuestionario.nivel == nivel,
                Cuestionario.esta_activo == True,
                Cuestionario.fecha_eliminacion.is_(None)
            ).order_by(Cuestionario.fecha_creacion.desc()).first()
            
            if not cuestionario:
                print(f"   ❌ No existe cuestionario {nivel.value} activo")
                print(f"   💡 Ejecuta: python scripts/crear_cuestionarios_predefinidos.py")
                todos_ok = False
                print()
                continue
            
            # Contar preguntas asignadas
            total_preguntas = db.query(CuestionarioPregunta).filter(
                CuestionarioPregunta.cuestionario_id == cuestionario.id
            ).count()
            
            print(f"   ✅ Cuestionario encontrado: {cuestionario.nombre}")
            print(f"   📊 Preguntas asignadas: {total_preguntas}")
            print(f"   📊 Preguntas esperadas: {preguntas_esperadas}")
            
            if total_preguntas < preguntas_esperadas:
                print(f"   ⚠️  ADVERTENCIA: Tiene menos preguntas de las esperadas")
                print(f"      Diferencia: {preguntas_esperadas - total_preguntas} preguntas faltantes")
            elif total_preguntas == preguntas_esperadas:
                print(f"   ✅ Número de preguntas correcto")
            else:
                print(f"   ℹ️  Tiene más preguntas de las esperadas (esto está bien)")
            
            print()
        
        print("=" * 60)
        if todos_ok:
            print("✅ Todos los cuestionarios están configurados correctamente")
        else:
            print("⚠️  Algunos cuestionarios necesitan configuración")
        print("=" * 60)
        
        return todos_ok
        
    except Exception as e:
        import traceback
        print(f"❌ Error: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verificar_cuestionarios()
    sys.exit(0 if success else 1)




