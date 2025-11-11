"""Crear tablas de cuestionarios

Revision ID: 002_crear_cuestionarios
Revises: 001_initial_schema
Create Date: 2025-10-21 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_crear_cuestionarios'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tipo enum para nivel de cuestionario
    nivel_cuestionario_enum = postgresql.ENUM(
        'basico', 'intermedio', 'avanzado',
        name='nivelcuestionario',
        create_type=True
    )
    nivel_cuestionario_enum.create(op.get_bind(), checkfirst=True)
    
    # Crear tipo enum para tipo de sección
    tipo_seccion_enum = postgresql.ENUM(
        'identify', 'protect', 'detect', 'respond', 'recover',
        'gobernanza', 'gestion', 'cultura', 'grc', 'general',
        name='tiposeccion',
        create_type=True
    )
    tipo_seccion_enum.create(op.get_bind(), checkfirst=True)
    
    # Crear tabla cuestionarios
    op.create_table(
        'cuestionarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('nivel', nivel_cuestionario_enum, nullable=False),
        sa.Column('framework_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False),
        sa.Column('tiempo_estimado_minutos', sa.Integer(), nullable=False),
        sa.Column('configuracion_formato', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('texto_instrucciones', sa.Text(), nullable=True),
        sa.Column('escala_madurez', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('niveles_resultado', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('estructura_secciones', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('es_editable_por_admin', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('es_plantilla', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('version', sa.String(length=20), nullable=False, server_default='1.0'),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('fecha_eliminacion', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['framework_id'], ['frameworks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo')
    )
    op.create_index(op.f('ix_cuestionarios_nivel'), 'cuestionarios', ['nivel'], unique=False)
    op.create_index(op.f('ix_cuestionarios_framework_id'), 'cuestionarios', ['framework_id'], unique=False)
    
    # Crear tabla cuestionario_preguntas (relación muchos a muchos)
    op.create_table(
        'cuestionario_preguntas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cuestionario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pregunta_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('seccion', sa.String(length=100), nullable=False),
        sa.Column('tipo_seccion', tipo_seccion_enum, nullable=False),
        sa.Column('orden_seccion', sa.Integer(), nullable=False),
        sa.Column('orden_pregunta', sa.Integer(), nullable=False),
        sa.Column('es_obligatoria', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('peso_personalizado', sa.Integer(), nullable=True),
        sa.Column('texto_pregunta_personalizado', sa.Text(), nullable=True),
        sa.Column('texto_ayuda_personalizado', sa.Text(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['cuestionario_id'], ['cuestionarios.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pregunta_id'], ['preguntas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cuestionario_preguntas_cuestionario_id'), 'cuestionario_preguntas', ['cuestionario_id'], unique=False)
    op.create_index(op.f('ix_cuestionario_preguntas_pregunta_id'), 'cuestionario_preguntas', ['pregunta_id'], unique=False)
    
    # Agregar columna cuestionario_id a evaluaciones
    op.add_column('evaluaciones', sa.Column('cuestionario_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_evaluaciones_cuestionario', 'evaluaciones', 'cuestionarios', ['cuestionario_id'], ['id'])
    op.create_index(op.f('ix_evaluaciones_cuestionario_id'), 'evaluaciones', ['cuestionario_id'], unique=False)


def downgrade():
    # Eliminar índice y columna de evaluaciones
    op.drop_index(op.f('ix_evaluaciones_cuestionario_id'), table_name='evaluaciones')
    op.drop_constraint('fk_evaluaciones_cuestionario', 'evaluaciones', type_='foreignkey')
    op.drop_column('evaluaciones', 'cuestionario_id')
    
    # Eliminar tabla cuestionario_preguntas
    op.drop_index(op.f('ix_cuestionario_preguntas_pregunta_id'), table_name='cuestionario_preguntas')
    op.drop_index(op.f('ix_cuestionario_preguntas_cuestionario_id'), table_name='cuestionario_preguntas')
    op.drop_table('cuestionario_preguntas')
    
    # Eliminar tabla cuestionarios
    op.drop_index(op.f('ix_cuestionarios_framework_id'), table_name='cuestionarios')
    op.drop_index(op.f('ix_cuestionarios_nivel'), table_name='cuestionarios')
    op.drop_table('cuestionarios')
    
    # Eliminar enums
    sa.Enum(name='tiposeccion').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='nivelcuestionario').drop(op.get_bind(), checkfirst=True)




