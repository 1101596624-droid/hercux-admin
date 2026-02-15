"""Add simulator_templates table

Revision ID: 008_simulator_templates
Revises: 007_add_processor_constraints
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '008_simulator_templates'
down_revision = '007_add_processor_constraints'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create simulator_templates table
    op.create_table(
        'simulator_templates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('subject', sa.String(100), nullable=False, index=True),
        sa.Column('topic', sa.String(255), nullable=False, index=True),

        # Core content
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False, index=True),

        # Code metrics
        sa.Column('line_count', sa.Integer(), nullable=False),
        sa.Column('variable_count', sa.Integer(), server_default='0'),
        sa.Column('has_setup_update', sa.Boolean(), server_default='false'),

        # Visual and interaction features
        sa.Column('visual_elements', JSONB(), nullable=True),

        # Template metadata for learning
        sa.Column('template_metadata', JSONB(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )

    # Create indexes
    op.create_index('ix_simulator_templates_id', 'simulator_templates', ['id'])
    op.create_index('ix_simulator_templates_subject', 'simulator_templates', ['subject'])
    op.create_index('ix_simulator_templates_quality_score', 'simulator_templates', ['quality_score'])


def downgrade() -> None:
    op.drop_index('ix_simulator_templates_quality_score', table_name='simulator_templates')
    op.drop_index('ix_simulator_templates_subject', table_name='simulator_templates')
    op.drop_index('ix_simulator_templates_id', table_name='simulator_templates')
    op.drop_table('simulator_templates')
