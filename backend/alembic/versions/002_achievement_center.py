"""Add achievement center tables

Revision ID: 002_achievement_center
Revises: 001_initial_schema
Create Date: 2026-01-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_achievement_center'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create badge_configs table
    op.create_table(
        'badge_configs',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('icon', sa.String(10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(20), nullable=False),
        sa.Column('rarity', sa.String(20), nullable=True, server_default='common'),
        sa.Column('points', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('condition', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
    )

    # Create skill_tree_configs table
    op.create_table(
        'skill_tree_configs',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('icon', sa.String(10), nullable=False),
        sa.Column('color', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('match_rules', sa.JSON(), nullable=False),
        sa.Column('level_thresholds', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('unlocks', sa.JSON(), nullable=True),
        sa.Column('is_advanced', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create skill_achievement_configs table
    op.create_table(
        'skill_achievement_configs',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('icon', sa.String(10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('points', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('condition', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('sort_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Create tag_dictionary table
    op.create_table(
        'tag_dictionary',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('icon', sa.String(10), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('parent_id', sa.String(50), sa.ForeignKey('tag_dictionary.id'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_registered', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )

    # Create pending_domains table
    op.create_table(
        'pending_domains',
        sa.Column('domain', sa.String(50), primary_key=True),
        sa.Column('node_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completed_users', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('first_seen', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, server_default='pending'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.String(50), nullable=True),
        sa.Column('reject_reason', sa.Text(), nullable=True),
    )

    # Create user_badges table
    op.create_table(
        'user_badges',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('badge_id', sa.String(50), sa.ForeignKey('badge_configs.id'), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_user_badges_id', 'user_badges', ['id'])
    op.create_index('ix_user_badges_user_badge', 'user_badges', ['user_id', 'badge_id'], unique=True)

    # Create user_skill_progress table
    op.create_table(
        'user_skill_progress',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('skill_tree_id', sa.String(50), sa.ForeignKey('skill_tree_configs.id'), nullable=False),
        sa.Column('current_points', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_level', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('sub_skills', sa.JSON(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_user_skill_progress_id', 'user_skill_progress', ['id'])
    op.create_index('ix_user_skill_progress_user_tree', 'user_skill_progress', ['user_id', 'skill_tree_id'], unique=True)

    # Create user_skill_achievements table
    op.create_table(
        'user_skill_achievements',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('achievement_id', sa.String(50), sa.ForeignKey('skill_achievement_configs.id'), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )
    op.create_index('ix_user_skill_achievements_id', 'user_skill_achievements', ['id'])
    op.create_index('ix_user_skill_achievements_user_ach', 'user_skill_achievements', ['user_id', 'achievement_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_user_skill_achievements_user_ach', table_name='user_skill_achievements')
    op.drop_index('ix_user_skill_achievements_id', table_name='user_skill_achievements')
    op.drop_table('user_skill_achievements')

    op.drop_index('ix_user_skill_progress_user_tree', table_name='user_skill_progress')
    op.drop_index('ix_user_skill_progress_id', table_name='user_skill_progress')
    op.drop_table('user_skill_progress')

    op.drop_index('ix_user_badges_user_badge', table_name='user_badges')
    op.drop_index('ix_user_badges_id', table_name='user_badges')
    op.drop_table('user_badges')

    op.drop_table('pending_domains')
    op.drop_table('tag_dictionary')
    op.drop_table('skill_achievement_configs')
    op.drop_table('skill_tree_configs')
    op.drop_table('badge_configs')
