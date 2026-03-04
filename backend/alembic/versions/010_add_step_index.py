"""Add current_step_index to learning_progress

Revision ID: 010_add_step_index
Revises: 009_template_review_status
Create Date: 2026-02-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '010_add_step_index'
down_revision = '009_template_review_status'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'learning_progress',
        sa.Column('current_step_index', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_column('learning_progress', 'current_step_index')
