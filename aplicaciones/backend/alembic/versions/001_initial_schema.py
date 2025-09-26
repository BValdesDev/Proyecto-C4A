"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    
    # Create roles table
    op.create_table('roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('nombre', sa.String(50), nullable=False),
        sa.Column('nombre_mostrar', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('permisos', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('niveles_disponibles', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )
    
    # Create frameworks table
    op.create_table('frameworks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('nombre', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('nombre_mostrar', sa.String(100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('niveles_disponibles', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre', 'version')
    )
    
    # Create organizaciones table
    op.create_table('organizaciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('rut', sa.String(12), nullable=True),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('tamaño', sa.String(50), nullable=True),
        sa.Column('nivel_suscripcion', sa.String(20), nullable=False, server_default='gratuito'),
        sa.Column('stripe_customer_id', sa.String(100), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(100), nullable=True),
        sa.Column('fecha_vencimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rut')
    )
    
    # Create usuarios table
    op.create_table('usuarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hash_contraseña', sa.String(255), nullable=False),
        sa.Column('nombre', sa.String(100), nullable=True),
        sa.Column('apellido', sa.String(100), nullable=True),
        sa.Column('organizacion_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rol_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('mfa_habilitado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mfa_secreto', sa.String(255), nullable=True),
        sa.Column('ultimo_acceso', sa.DateTime(timezone=True), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['organizacion_id'], ['organizaciones.id'], ),
        sa.ForeignKeyConstraint(['rol_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create sesiones table
    op.create_table('sesiones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('jti', sa.String(255), nullable=False),
        sa.Column('hash_token_refresco', sa.String(255), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('expira_en', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revocado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti')
    )
    
    # Create suscripciones table
    op.create_table('suscripciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('organizacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(100), nullable=True),
        sa.Column('stripe_price_id', sa.String(100), nullable=True),
        sa.Column('nivel', sa.String(20), nullable=False),
        sa.Column('estado', sa.String(20), nullable=False),
        sa.Column('monto_centavos', sa.Integer(), nullable=False),
        sa.Column('moneda', sa.String(3), nullable=False, server_default='CLP'),
        sa.Column('ciclo_facturacion', sa.String(20), nullable=False),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('evaluaciones_usadas', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reportes_usados', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['organizacion_id'], ['organizaciones.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    
    # Create evaluaciones table
    op.create_table('evaluaciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('organizacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('framework_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nivel_usado', sa.String(20), nullable=False),
        sa.Column('total_preguntas', sa.Integer(), nullable=False),
        sa.Column('preguntas_respondidas', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('estado', sa.String(20), nullable=False, server_default='borrador'),
        sa.Column('puntuacion_global', sa.Float(), nullable=True),
        sa.Column('puntuaciones_dominio', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_completado', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['creado_por'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['framework_id'], ['frameworks.id'], ),
        sa.ForeignKeyConstraint(['organizacion_id'], ['organizaciones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create preguntas table
    op.create_table('preguntas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('codigo', sa.String(50), nullable=False),
        sa.Column('texto_pregunta', sa.Text(), nullable=False),
        sa.Column('texto_ayuda', sa.Text(), nullable=True),
        sa.Column('framework_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('categoria', sa.String(100), nullable=False),
        sa.Column('disponibilidad_por_nivel', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('peso', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('tipo_respuesta', sa.String(20), nullable=False, server_default='escala'),
        sa.Column('opciones_respuesta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['framework_id'], ['frameworks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('codigo', 'framework_id')
    )
    
    # Create respuestas table
    op.create_table('respuestas',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('evaluacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pregunta_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('respondido_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('texto_evidencia', sa.Text(), nullable=True),
        sa.Column('comentarios', sa.Text(), nullable=True),
        sa.Column('nivel_confianza', sa.Float(), nullable=True),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['evaluacion_id'], ['evaluaciones.id'], ),
        sa.ForeignKeyConstraint(['pregunta_id'], ['preguntas.id'], ),
        sa.ForeignKeyConstraint(['respondido_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('evaluacion_id', 'pregunta_id')
    )
    
    # Create reportes table
    op.create_table('reportes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('evaluacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organizacion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('generado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_reporte', sa.String(20), nullable=False),
        sa.Column('nivel_generado', sa.String(20), nullable=False),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('puntuacion_global', sa.Float(), nullable=False),
        sa.Column('fortalezas', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('debilidades', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recomendaciones', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('url_pdf', sa.String(500), nullable=True),
        sa.Column('tiene_marca_agua', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['evaluacion_id'], ['evaluaciones.id'], ),
        sa.ForeignKeyConstraint(['generado_por'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['organizacion_id'], ['organizaciones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create logs_auditoria table
    op.create_table('logs_auditoria',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organizacion_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tipo_evento', sa.String(50), nullable=False),
        sa.Column('accion', sa.String(100), nullable=False),
        sa.Column('tipo_recurso', sa.String(50), nullable=True),
        sa.Column('id_recurso', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('exitoso', sa.Boolean(), nullable=False),
        sa.Column('mensaje_error', sa.Text(), nullable=True),
        sa.Column('metadatos', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('suma_verificacion', sa.String(64), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['organizacion_id'], ['organizaciones.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_usuarios_email', 'usuarios', ['email'])
    op.create_index('idx_usuarios_organizacion', 'usuarios', ['organizacion_id'])
    op.create_index('idx_sesiones_usuario', 'sesiones', ['usuario_id'])
    op.create_index('idx_sesiones_jti', 'sesiones', ['jti'])
    op.create_index('idx_evaluaciones_organizacion', 'evaluaciones', ['organizacion_id'])
    op.create_index('idx_evaluaciones_framework', 'evaluaciones', ['framework_id'])
    op.create_index('idx_respuestas_evaluacion', 'respuestas', ['evaluacion_id'])
    op.create_index('idx_respuestas_pregunta', 'respuestas', ['pregunta_id'])
    op.create_index('idx_reportes_evaluacion', 'reportes', ['evaluacion_id'])
    op.create_index('idx_reportes_organizacion', 'reportes', ['organizacion_id'])
    op.create_index('idx_logs_auditoria_usuario', 'logs_auditoria', ['usuario_id'])
    op.create_index('idx_logs_auditoria_organizacion', 'logs_auditoria', ['organizacion_id'])
    op.create_index('idx_logs_auditoria_fecha', 'logs_auditoria', ['creado_en'])
    op.create_index('idx_suscripciones_organizacion', 'suscripciones', ['organizacion_id'])
    op.create_index('idx_suscripciones_stripe', 'suscripciones', ['stripe_subscription_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_suscripciones_stripe', table_name='suscripciones')
    op.drop_index('idx_suscripciones_organizacion', table_name='suscripciones')
    op.drop_index('idx_logs_auditoria_fecha', table_name='logs_auditoria')
    op.drop_index('idx_logs_auditoria_organizacion', table_name='logs_auditoria')
    op.drop_index('idx_logs_auditoria_usuario', table_name='logs_auditoria')
    op.drop_index('idx_reportes_organizacion', table_name='reportes')
    op.drop_index('idx_reportes_evaluacion', table_name='reportes')
    op.drop_index('idx_respuestas_pregunta', table_name='respuestas')
    op.drop_index('idx_respuestas_evaluacion', table_name='respuestas')
    op.drop_index('idx_evaluaciones_framework', table_name='evaluaciones')
    op.drop_index('idx_evaluaciones_organizacion', table_name='evaluaciones')
    op.drop_index('idx_sesiones_jti', table_name='sesiones')
    op.drop_index('idx_sesiones_usuario', table_name='sesiones')
    op.drop_index('idx_usuarios_organizacion', table_name='usuarios')
    op.drop_index('idx_usuarios_email', table_name='usuarios')
    
    # Drop tables
    op.drop_table('logs_auditoria')
    op.drop_table('reportes')
    op.drop_table('respuestas')
    op.drop_table('preguntas')
    op.drop_table('evaluaciones')
    op.drop_table('suscripciones')
    op.drop_table('sesiones')
    op.drop_table('usuarios')
    op.drop_table('organizaciones')
    op.drop_table('frameworks')
    op.drop_table('roles')















