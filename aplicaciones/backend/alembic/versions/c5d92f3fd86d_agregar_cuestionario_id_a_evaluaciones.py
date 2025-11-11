"""agregar_cuestionario_id_a_evaluaciones

Revision ID: c5d92f3fd86d
Revises: 002_crear_cuestionarios
Create Date: 2025-10-23 22:03:03.329154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5d92f3fd86d'
down_revision = '002_crear_cuestionarios'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna cuestionario_id a la tabla evaluaciones
    op.add_column('evaluaciones', sa.Column('cuestionario_id', sa.UUID(as_uuid=True), nullable=True))
    
    # Agregar foreign key constraint
    op.create_foreign_key(
        'fk_evaluaciones_cuestionario_id',
        'evaluaciones', 'cuestionarios',
        ['cuestionario_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Remover foreign key constraint
    op.drop_constraint('fk_evaluaciones_cuestionario_id', 'evaluaciones', type_='foreignkey')
    
    # Remover columna cuestionario_id
    op.drop_column('evaluaciones', 'cuestionario_id')