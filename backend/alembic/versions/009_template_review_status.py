"""Add status column to simulator_templates for review workflow

Revision ID: 009_template_review_status
Revises: 008_simulator_templates
Create Date: 2026-02-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009_template_review_status'
down_revision = '008_simulator_templates'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'simulator_templates',
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
    )
    op.create_index('ix_simulator_templates_status', 'simulator_templates', ['status'])
    # Mark existing templates as approved
    op.execute("UPDATE simulator_templates SET status = 'approved'")


def downgrade() -> None:
    op.drop_index('ix_simulator_templates_status', table_name='simulator_templates')
    op.drop_column('simulator_templates', 'status')
