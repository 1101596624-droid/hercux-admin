"""Add simulator icon library tables

Revision ID: 003_simulator_icons
Revises: 002_achievement_center
Create Date: 2026-01-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_simulator_icons'
down_revision = '002_achievement_center'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create simulator_icons table
    op.create_table(
        'simulator_icons',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('category', sa.String(30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('default_color', sa.String(20), nullable=True, server_default='#3B82F6'),
        sa.Column('default_scale', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('recommended_scenes', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create index on category for faster filtering
    op.create_index('ix_simulator_icons_category', 'simulator_icons', ['category'])
    
    # Create simulator_icon_presets table
    op.create_table(
        'simulator_icon_presets',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icons', sa.JSON(), nullable=False),
        sa.Column('canvas_config', sa.JSON(), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_official', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('usage_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_index('ix_simulator_icons_category', table_name='simulator_icons')
    op.drop_table('simulator_icon_presets')
    op.drop_table('simulator_icons')
