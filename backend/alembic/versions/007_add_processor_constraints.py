"""Add structure_constraints to studio_processors

Revision ID: 007_add_processor_constraints
Revises: 006_learning_patterns
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '007_add_processor_constraints'
down_revision = '006_learning_patterns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add structure_constraints column to studio_processors table
    op.add_column(
        'studio_processors',
        sa.Column('structure_constraints', JSON(), nullable=True)
    )


def downgrade() -> None:
    # Remove structure_constraints column
    op.drop_column('studio_processors', 'structure_constraints')
