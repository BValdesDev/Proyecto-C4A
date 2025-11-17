# app/api/v1/endpoints/cuestionarios.py
"""
Endpoints para gestión de cuestionarios/diagnósticos
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ....modelos.base import obtener_sesion
from ....modelos.cuestionario import (
    Cuestionario, CuestionarioPregunta, 
    NivelCuestionario, TipoSeccion
)
from ....modelos.pregunta import Pregunta
from ....modelos.usuario import Usuario
from ....modelos.organizacion import Organizacion
from ....modelos.evaluacion import Evaluacion
from ....core.permissions import verificar_permisos
from ..dependencias import obtener_usuario_actual_dependencia, obtener_usuario_opcional
from ....servicios.calculo_madurez_service import CalculoMadurezService
from ....servicios.pdf_service import PDFService
from pydantic import BaseModel, Field
from fastapi.responses import Response

router = APIRouter()

# ============================================================================
# SCHEMAS/MODELS PYDANTIC
# ============================================================================

class CuestionarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    nivel: NivelCuestionario
    tiempo_estimado_minutos: int = Field(..., gt=0)
    texto_instrucciones: Optional[str] = None

class CuestionarioCreate(CuestionarioBase):
    framework_id: UUID
    estructura_secciones: List[dict]

class CuestionarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tiempo_estimado_minutos: Optional[int] = Field(None, gt=0)
    texto_instrucciones: Optional[str] = None
    esta_activo: Optional[bool] = None
    configuracion_formato: Optional[dict] = None
    escala_madurez: Optional[dict] = None
    niveles_resultado: Optional[dict] = None

class PreguntaAsignar(BaseModel):
    pregunta_id: UUID
    seccion: str
    tipo_seccion: TipoSeccion
    orden_seccion: int
    orden_pregunta: int
    es_obligatoria: bool = True
    peso_personalizado: Optional[int] = None
    texto_pregunta_personalizado: Optional[str] = None
    texto_ayuda_personalizado: Optional[str] = None

class CuestionarioResponse(BaseModel):
    id: UUID
    nombre: str
    codigo: str
    descripcion: Optional[str]
    nivel: str
    total_items: int
    tiempo_estimado_minutos: int
    version: str
    esta_activo: bool
    es_editable_por_admin: bool
    framework_id: UUID
    total_evaluaciones: int = 0
    
    class Config:
        from_attributes = True

class CuestionarioDetalleResponse(CuestionarioResponse):
    texto_instrucciones: Optional[str]
    configuracion_formato: dict
    escala_madurez: dict
    niveles_resultado: dict
    estructura_secciones: List[dict]
    total_preguntas_asignadas: int
    
    class Config:
        from_attributes = True

class PreguntaAsignadaResponse(BaseModel):
    id: UUID
    pregunta_id: UUID
    codigo_pregunta: str
    texto_pregunta: str
    texto_ayuda: Optional[str]
    seccion: str
    tipo_seccion: str
    orden_seccion: int
    orden_pregunta: int
    es_obligatoria: bool
    peso: int
    
    class Config:
        from_attributes = True

# ============================================================================
# ENDPOINTS - LISTAR Y OBTENER
# ============================================================================

@router.get("/principal", response_model=CuestionarioResponse)
async def obtener_cuestionario_principal(
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia),
    db: Session = Depends(obtener_sesion)
):
    """
    Obtener el cuestionario principal según el nivel de suscripción del usuario
    """
    # Obtener organización del usuario
    organizacion = db.query(Organizacion).filter(
        Organizacion.id == usuario_actual.organizacion_id
    ).first()
    
    if not organizacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organización no encontrada"
        )
    
    nivel_suscripcion = organizacion.nivel_suscripcion.value
    
    # Determinar el nivel de cuestionario según la suscripción
    if nivel_suscripcion == "gratuito":
        nivel_cuestionario = "basico"
    elif nivel_suscripcion == "pro":
        nivel_cuestionario = "intermedio"
    elif nivel_suscripcion == "empresarial":
        nivel_cuestionario = "avanzado"
    else:
        nivel_cuestionario = "basico"
    
    # Buscar el cuestionario principal para ese nivel
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.nivel == nivel_cuestionario,
        Cuestionario.esta_activo == True,
        Cuestionario.fecha_eliminacion.is_(None)
    ).order_by(Cuestionario.fecha_creacion.desc()).first()
    
    if not cuestionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay cuestionarios disponibles para el nivel {nivel_suscripcion}"
        )
    
    return CuestionarioResponse.from_orm(cuestionario)

@router.get("/", response_model=List[CuestionarioResponse])
async def listar_cuestionarios(
    nivel: Optional[NivelCuestionario] = None,
    activos_solo: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(obtener_sesion),
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional)
):
    """
    Listar cuestionarios disponibles.
    
    - Usuarios normales: solo cuestionarios activos
    - Administradores: todos los cuestionarios
    - Sin autenticación: solo cuestionarios activos
    """
    query = db.query(Cuestionario).filter(Cuestionario.fecha_eliminacion.is_(None))
    
    # Filtro por nivel
    if nivel:
        query = query.filter(Cuestionario.nivel == nivel)
    
    # Filtro por activos (excepto admins)
    es_admin = False
    if usuario_actual:
        try:
            es_admin = verificar_permisos(usuario_actual, ["cuestionarios:admin"], raise_exception=False)
        except:
            es_admin = False
    
    if activos_solo or not es_admin:
        query = query.filter(Cuestionario.esta_activo == True)
    
    # Filtro por nivel de suscripción del usuario
    if usuario_actual and not es_admin:
        # Obtener nivel de suscripción del usuario
        from ....modelos.organizacion import Organizacion
        organizacion = db.query(Organizacion).filter(
            Organizacion.id == usuario_actual.organizacion_id
        ).first()
        
        if organizacion:
            nivel_suscripcion = organizacion.nivel_suscripcion.value
            
            # Mapear niveles de suscripción a niveles de cuestionarios permitidos
            if nivel_suscripcion == "gratuito":
                # Solo cuestionarios básicos
                query = query.filter(Cuestionario.nivel == "basico")
            elif nivel_suscripcion == "pro":
                # Cuestionarios básicos e intermedios
                query = query.filter(Cuestionario.nivel.in_(["basico", "intermedio"]))
            # Para niveles premium/enterprise, no hay restricciones
    
    cuestionarios = query.order_by(
        Cuestionario.nivel,
        Cuestionario.total_items
    ).offset(skip).limit(limit).all()
    
    # Agregar estadísticas
    resultado = []
    for cuest in cuestionarios:
        cuest_dict = {
            "id": cuest.id,
            "nombre": cuest.nombre,
            "codigo": cuest.codigo,
            "descripcion": cuest.descripcion,
            "nivel": cuest.nivel.value,
            "total_items": cuest.total_items,
            "tiempo_estimado_minutos": cuest.tiempo_estimado_minutos,
            "version": cuest.version,
            "esta_activo": cuest.esta_activo,
            "es_editable_por_admin": cuest.es_editable_por_admin,
            "framework_id": cuest.framework_id,
            "total_evaluaciones": len(cuest.evaluaciones) if cuest.evaluaciones else 0
        }
        resultado.append(CuestionarioResponse(**cuest_dict))
    
    return resultado

@router.get("/{cuestionario_id}", response_model=CuestionarioDetalleResponse)
async def obtener_cuestionario(
    cuestionario_id: UUID,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional)
):
    """Obtener detalles completos de un cuestionario"""
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    # Verificar permisos si no está activo
    if not cuestionario.esta_activo:
        verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    return CuestionarioDetalleResponse(
        id=cuestionario.id,
        nombre=cuestionario.nombre,
        codigo=cuestionario.codigo,
        descripcion=cuestionario.descripcion,
        nivel=cuestionario.nivel.value,
        total_items=cuestionario.total_items,
        tiempo_estimado_minutos=cuestionario.tiempo_estimado_minutos,
        version=cuestionario.version,
        esta_activo=cuestionario.esta_activo,
        es_editable_por_admin=cuestionario.es_editable_por_admin,
        framework_id=cuestionario.framework_id,
        total_evaluaciones=len(cuestionario.evaluaciones) if cuestionario.evaluaciones else 0,
        texto_instrucciones=cuestionario.texto_instrucciones,
        configuracion_formato=cuestionario.configuracion_formato,
        escala_madurez=cuestionario.escala_madurez,
        niveles_resultado=cuestionario.niveles_resultado,
        estructura_secciones=cuestionario.estructura_secciones,
        total_preguntas_asignadas=len(cuestionario.preguntas_asignadas) if cuestionario.preguntas_asignadas else 0
    )

@router.get("/{cuestionario_id}/preguntas", response_model=List[PreguntaAsignadaResponse])
async def obtener_preguntas_cuestionario(
    cuestionario_id: UUID,
    seccion: Optional[str] = None,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional)
):
    """Obtener todas las preguntas asignadas a un cuestionario"""
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    # Obtener preguntas ordenadas
    query = db.query(CuestionarioPregunta).filter(
        CuestionarioPregunta.cuestionario_id == cuestionario_id
    )
    
    if seccion:
        query = query.filter(CuestionarioPregunta.seccion == seccion)
    
    preguntas_asignadas = query.order_by(
        CuestionarioPregunta.orden_seccion,
        CuestionarioPregunta.orden_pregunta
    ).all()
    
    resultado = []
    for pa in preguntas_asignadas:
        resultado.append(PreguntaAsignadaResponse(
            id=pa.id,
            pregunta_id=pa.pregunta_id,
            codigo_pregunta=pa.pregunta.codigo if pa.pregunta else "N/A",
            texto_pregunta=pa.texto_final,
            texto_ayuda=pa.texto_ayuda_final,
            seccion=pa.seccion,
            tipo_seccion=pa.tipo_seccion.value,
            orden_seccion=pa.orden_seccion,
            orden_pregunta=pa.orden_pregunta,
            es_obligatoria=pa.es_obligatoria,
            peso=pa.peso_final
        ))
    
    return resultado

@router.get("/nivel/{nivel_suscripcion}")
async def obtener_preguntas_por_nivel(
    nivel_suscripcion: str,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Optional[Usuario] = Depends(obtener_usuario_opcional)
):
    """
    Obtener preguntas según el nivel de suscripción
    Mapea: gratuito -> basico, pro -> intermedio, empresarial -> avanzado
    """
    # Mapear nivel de suscripción a nivel de cuestionario
    mapeo_niveles = {
        "gratuito": NivelCuestionario.basico,
        "pro": NivelCuestionario.intermedio,
        "empresarial": NivelCuestionario.avanzado
    }
    
    nivel_cuestionario = mapeo_niveles.get(nivel_suscripcion.lower())
    if not nivel_cuestionario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nivel de suscripción inválido: {nivel_suscripcion}. Debe ser: gratuito, pro o empresarial"
        )
    
    # Buscar el cuestionario activo para ese nivel
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.nivel == nivel_cuestionario,
        Cuestionario.esta_activo == True,
        Cuestionario.fecha_eliminacion.is_(None)
    ).order_by(Cuestionario.fecha_creacion.desc()).first()
    
    if not cuestionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay cuestionarios disponibles para el nivel {nivel_suscripcion}"
        )
    
    # Obtener todas las preguntas asignadas al cuestionario
    preguntas_asignadas = db.query(CuestionarioPregunta).filter(
        CuestionarioPregunta.cuestionario_id == cuestionario.id
    ).order_by(
        CuestionarioPregunta.orden_seccion,
        CuestionarioPregunta.orden_pregunta
    ).all()
    
    # Formatear respuesta
    preguntas_formateadas = []
    for pa in preguntas_asignadas:
        pregunta_data = {
            "id": str(pa.pregunta_id),
            "codigo": pa.pregunta.codigo if pa.pregunta else "N/A",
            "texto": pa.texto_final,
            "texto_ayuda": pa.texto_ayuda_final,
            "categoria": pa.pregunta.categoria if pa.pregunta else None,
            "subcategoria": pa.pregunta.subcategoria if pa.pregunta else None,
            "seccion": pa.seccion,
            "tipo_seccion": pa.tipo_seccion.value,
            "orden": pa.orden_pregunta,
            "es_obligatoria": pa.es_obligatoria,
            "peso": pa.peso_final,
            "tipo_respuesta": pa.pregunta.tipo_respuesta if pa.pregunta else "likert_5"
        }
        preguntas_formateadas.append(pregunta_data)
    
    return {
        "nivel_suscripcion": nivel_suscripcion,
        "nivel_cuestionario": nivel_cuestionario.value,
        "cuestionario_id": str(cuestionario.id),
        "cuestionario_nombre": cuestionario.nombre,
        "total_preguntas": len(preguntas_formateadas),
        "preguntas": preguntas_formateadas
    }

# ============================================================================
# ENDPOINTS - ADMINISTRACIÓN (Solo Admins)
# ============================================================================

@router.post("/", response_model=CuestionarioResponse)
async def crear_cuestionario(
    data: CuestionarioCreate,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Crear un nuevo cuestionario (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    # Generar código único
    codigo_base = f"DIAG_{data.nivel.value.upper()}_{data.nombre[:10].upper().replace(' ', '_')}"
    codigo = codigo_base
    contador = 1
    while db.query(Cuestionario).filter(Cuestionario.codigo == codigo).first():
        codigo = f"{codigo_base}_{contador}"
        contador += 1
    
    cuestionario = Cuestionario(
        nombre=data.nombre,
        codigo=codigo,
        descripcion=data.descripcion,
        nivel=data.nivel,
        framework_id=data.framework_id,
        total_items=sum(s.get("items", 0) for s in data.estructura_secciones),
        tiempo_estimado_minutos=data.tiempo_estimado_minutos,
        texto_instrucciones=data.texto_instrucciones,
        estructura_secciones=data.estructura_secciones,
        esta_activo=True,
        es_editable_por_admin=True,
        es_plantilla=False,
        version="1.0"
    )
    
    db.add(cuestionario)
    db.commit()
    db.refresh(cuestionario)
    
    return CuestionarioResponse(
        id=cuestionario.id,
        nombre=cuestionario.nombre,
        codigo=cuestionario.codigo,
        descripcion=cuestionario.descripcion,
        nivel=cuestionario.nivel.value,
        total_items=cuestionario.total_items,
        tiempo_estimado_minutos=cuestionario.tiempo_estimado_minutos,
        version=cuestionario.version,
        esta_activo=cuestionario.esta_activo,
        es_editable_por_admin=cuestionario.es_editable_por_admin,
        framework_id=cuestionario.framework_id,
        total_evaluaciones=0
    )

@router.put("/{cuestionario_id}", response_model=CuestionarioResponse)
async def actualizar_cuestionario(
    cuestionario_id: UUID,
    data: CuestionarioUpdate,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Actualizar un cuestionario (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    if not cuestionario.es_editable_por_admin:
        raise HTTPException(status_code=403, detail="Este cuestionario no es editable")
    
    # Actualizar campos
    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(cuestionario, campo, valor)
    
    db.commit()
    db.refresh(cuestionario)
    
    return CuestionarioResponse(
        id=cuestionario.id,
        nombre=cuestionario.nombre,
        codigo=cuestionario.codigo,
        descripcion=cuestionario.descripcion,
        nivel=cuestionario.nivel.value,
        total_items=cuestionario.total_items,
        tiempo_estimado_minutos=cuestionario.tiempo_estimado_minutos,
        version=cuestionario.version,
        esta_activo=cuestionario.esta_activo,
        es_editable_por_admin=cuestionario.es_editable_por_admin,
        framework_id=cuestionario.framework_id,
        total_evaluaciones=len(cuestionario.evaluaciones) if cuestionario.evaluaciones else 0
    )

@router.delete("/{cuestionario_id}")
async def eliminar_cuestionario(
    cuestionario_id: UUID,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Eliminar un cuestionario (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    if cuestionario.es_plantilla:
        raise HTTPException(status_code=403, detail="No se puede eliminar una plantilla del sistema")
    
    # Eliminación lógica
    from datetime import datetime
    cuestionario.fecha_eliminacion = datetime.utcnow()
    
    db.commit()
    
    return {"mensaje": "Cuestionario eliminado exitosamente"}

@router.post("/{cuestionario_id}/preguntas", response_model=PreguntaAsignadaResponse)
async def asignar_pregunta_a_cuestionario(
    cuestionario_id: UUID,
    data: PreguntaAsignar,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Asignar una pregunta a un cuestionario (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    if not cuestionario.es_editable_por_admin:
        raise HTTPException(status_code=403, detail="Este cuestionario no es editable")
    
    # Verificar que la pregunta existe
    pregunta = db.query(Pregunta).filter(Pregunta.id == data.pregunta_id).first()
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    # Crear asignación
    asignacion = CuestionarioPregunta(
        cuestionario_id=cuestionario_id,
        pregunta_id=data.pregunta_id,
        seccion=data.seccion,
        tipo_seccion=data.tipo_seccion,
        orden_seccion=data.orden_seccion,
        orden_pregunta=data.orden_pregunta,
        es_obligatoria=data.es_obligatoria,
        peso_personalizado=data.peso_personalizado,
        texto_pregunta_personalizado=data.texto_pregunta_personalizado,
        texto_ayuda_personalizado=data.texto_ayuda_personalizado
    )
    
    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)
    
    return PreguntaAsignadaResponse(
        id=asignacion.id,
        pregunta_id=asignacion.pregunta_id,
        codigo_pregunta=pregunta.codigo,
        texto_pregunta=asignacion.texto_final,
        texto_ayuda=asignacion.texto_ayuda_final,
        seccion=asignacion.seccion,
        tipo_seccion=asignacion.tipo_seccion.value,
        orden_seccion=asignacion.orden_seccion,
        orden_pregunta=asignacion.orden_pregunta,
        es_obligatoria=asignacion.es_obligatoria,
        peso=asignacion.peso_final
    )

@router.put("/{cuestionario_id}/preguntas/{pregunta_asignada_id}")
async def actualizar_pregunta_asignada(
    cuestionario_id: UUID,
    pregunta_asignada_id: UUID,
    data: PreguntaAsignar,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Actualizar una pregunta asignada (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    asignacion = db.query(CuestionarioPregunta).filter(
        CuestionarioPregunta.id == pregunta_asignada_id,
        CuestionarioPregunta.cuestionario_id == cuestionario_id
    ).first()
    
    if not asignacion:
        raise HTTPException(status_code=404, detail="Pregunta asignada no encontrada")
    
    # Actualizar campos
    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(asignacion, campo, valor)
    
    db.commit()
    
    return {"mensaje": "Pregunta actualizada exitosamente"}

@router.delete("/{cuestionario_id}/preguntas/{pregunta_asignada_id}")
async def eliminar_pregunta_asignada(
    cuestionario_id: UUID,
    pregunta_asignada_id: UUID,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Eliminar una pregunta de un cuestionario (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    asignacion = db.query(CuestionarioPregunta).filter(
        CuestionarioPregunta.id == pregunta_asignada_id,
        CuestionarioPregunta.cuestionario_id == cuestionario_id
    ).first()
    
    if not asignacion:
        raise HTTPException(status_code=404, detail="Pregunta asignada no encontrada")
    
    db.delete(asignacion)
    db.commit()
    
    return {"mensaje": "Pregunta eliminada del cuestionario"}

@router.post("/{cuestionario_id}/clonar", response_model=CuestionarioResponse)
async def clonar_cuestionario(
    cuestionario_id: UUID,
    nuevo_nombre: str,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """Clonar un cuestionario existente (Solo administradores)"""
    verificar_permisos(usuario_actual, ["cuestionarios:admin"])
    
    cuestionario_original = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario_original:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    # Generar código único
    codigo_base = f"DIAG_{cuestionario_original.nivel.value.upper()}_{nuevo_nombre[:10].upper().replace(' ', '_')}"
    codigo = codigo_base
    contador = 1
    while db.query(Cuestionario).filter(Cuestionario.codigo == codigo).first():
        codigo = f"{codigo_base}_{contador}"
        contador += 1
    
    # Clonar cuestionario
    nuevo_cuestionario = cuestionario_original.clonar_cuestionario(nuevo_nombre, codigo)
    db.add(nuevo_cuestionario)
    db.flush()
    
    # Clonar preguntas asignadas
    for pa_original in cuestionario_original.preguntas_asignadas:
        nueva_asignacion = CuestionarioPregunta(
            cuestionario_id=nuevo_cuestionario.id,
            pregunta_id=pa_original.pregunta_id,
            seccion=pa_original.seccion,
            tipo_seccion=pa_original.tipo_seccion,
            orden_seccion=pa_original.orden_seccion,
            orden_pregunta=pa_original.orden_pregunta,
            es_obligatoria=pa_original.es_obligatoria,
            peso_personalizado=pa_original.peso_personalizado,
            texto_pregunta_personalizado=pa_original.texto_pregunta_personalizado,
            texto_ayuda_personalizado=pa_original.texto_ayuda_personalizado
        )
        db.add(nueva_asignacion)
    
    db.commit()
    db.refresh(nuevo_cuestionario)
    
    return CuestionarioResponse(
        id=nuevo_cuestionario.id,
        nombre=nuevo_cuestionario.nombre,
        codigo=nuevo_cuestionario.codigo,
        descripcion=nuevo_cuestionario.descripcion,
        nivel=nuevo_cuestionario.nivel.value,
        total_items=nuevo_cuestionario.total_items,
        tiempo_estimado_minutos=nuevo_cuestionario.tiempo_estimado_minutos,
        version=nuevo_cuestionario.version,
        esta_activo=nuevo_cuestionario.esta_activo,
        es_editable_por_admin=nuevo_cuestionario.es_editable_por_admin,
        framework_id=nuevo_cuestionario.framework_id,
        total_evaluaciones=0
    )

# ============================================================================
# ENDPOINTS - CÁLCULO DE RESULTADOS
# ============================================================================

@router.get("/{cuestionario_id}/calcular-resultado")
async def calcular_resultado_cuestionario(
    cuestionario_id: UUID,
    evaluacion_id: UUID,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Calcular resultados de madurez para una evaluación de un cuestionario.
    """
    # Verificar que el cuestionario existe
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    # Verificar que la evaluación existe y pertenece al usuario
    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id,
        Evaluacion.cuestionario_id == cuestionario_id,
        Evaluacion.fecha_eliminacion.is_(None)
    ).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    # Verificar permisos: solo el creador o un admin puede ver resultados
    try:
        es_admin = verificar_permisos(usuario_actual, ["evaluaciones:admin"], raise_exception=False)
    except:
        es_admin = False
    
    if not es_admin and str(evaluacion.creado_por) != str(usuario_actual.id):
        raise HTTPException(status_code=403, detail="No tiene permisos para ver estos resultados")
    
    # Calcular resultados
    servicio = CalculoMadurezService(db)
    analisis = servicio.generar_analisis_completo(evaluacion, cuestionario)
    
    return analisis

@router.get("/{cuestionario_id}/descargar-pdf/{evaluacion_id}")
async def descargar_pdf_resultado(
    cuestionario_id: UUID,
    evaluacion_id: UUID,
    db: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(obtener_usuario_actual_dependencia)
):
    """
    Descargar PDF con los resultados del diagnóstico.
    """
    # Verificar que el cuestionario existe
    cuestionario = db.query(Cuestionario).filter(
        Cuestionario.id == cuestionario_id,
        Cuestionario.fecha_eliminacion.is_(None)
    ).first()
    
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    # Verificar que la evaluación existe
    evaluacion = db.query(Evaluacion).filter(
        Evaluacion.id == evaluacion_id,
        Evaluacion.cuestionario_id == cuestionario_id,
        Evaluacion.fecha_eliminacion.is_(None)
    ).first()
    
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    # Verificar permisos
    try:
        es_admin = verificar_permisos(usuario_actual, ["evaluaciones:admin"], raise_exception=False)
    except:
        es_admin = False
    
    if not es_admin and str(evaluacion.creado_por) != str(usuario_actual.id):
        raise HTTPException(status_code=403, detail="No tiene permisos para descargar este PDF")
    
    # Calcular resultados
    servicio_calculo = CalculoMadurezService(db)
    analisis = servicio_calculo.generar_analisis_completo(evaluacion, cuestionario)
    
    # Generar PDF
    servicio_pdf = PDFService()
    pdf_bytes = servicio_pdf.generar_pdf_diagnostico(evaluacion, cuestionario, analisis, db)
    
    # Nombre del archivo
    fecha_str = datetime.utcnow().strftime('%Y%m%d')
    filename = f"Diagnostico_{cuestionario.nivel.value}_{fecha_str}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

