"""Add missing tables: simulator_results, studio_processors, studio_packages, token_usage, user_profiles

Revision ID: 004_missing_tables
Revises: 003_simulator_icons
Create Date: 2026-01-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_missing_tables'
down_revision = '003_simulator_icons'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create simulator_results table
    op.create_table(
        'simulator_results',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('node_id', sa.Integer(), sa.ForeignKey('course_nodes.id'), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('result_data', sa.JSON(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('time_spent_seconds', sa.Integer(), server_default='0'),
        sa.Column('completed', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_simulator_results_id', 'simulator_results', ['id'])
    op.create_index('ix_simulator_results_session_id', 'simulator_results', ['session_id'])

    # 2. Create studio_processors table
    op.create_table(
        'studio_processors',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(50), server_default='1.0.0'),
        sa.Column('author', sa.String(255), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('color', sa.String(50), server_default='#3B82F6'),
        sa.Column('icon', sa.String(50), server_default='Sparkles'),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Integer(), server_default='1'),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.Column('is_official', sa.Integer(), server_default='0'),
        sa.Column('is_custom', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 3. Create studio_packages table
    op.create_table(
        'studio_packages',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_info', sa.Text(), nullable=True),
        sa.Column('style', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.Column('lessons', sa.JSON(), nullable=True),
        sa.Column('edges', sa.JSON(), nullable=True),
        sa.Column('global_ai_config', sa.JSON(), nullable=True),
        sa.Column('total_lessons', sa.Integer(), server_default='0'),
        sa.Column('estimated_hours', sa.Float(), server_default='0'),
        sa.Column('processor_id', sa.String(100), sa.ForeignKey('studio_processors.id'), nullable=True),
        sa.Column('course_id', sa.Integer(), sa.ForeignKey('courses.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # 4. Create token_usage table
    op.create_table(
        'token_usage',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('feature', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('output_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('plan_id', sa.String(100), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_token_usage_id', 'token_usage', ['id'])
    op.create_index('ix_token_usage_feature', 'token_usage', ['feature'])
    op.create_index('ix_token_usage_created_at', 'token_usage', ['created_at'])

    # 5. Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('learning_style', sa.JSON(), nullable=True),
        sa.Column('knowledge_levels', sa.JSON(), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('communication_style', sa.String(50), nullable=True),
        sa.Column('engagement_level', sa.String(50), nullable=True),
        sa.Column('question_patterns', sa.JSON(), nullable=True),
        sa.Column('learning_pace', sa.String(50), nullable=True),
        sa.Column('personality_traits', sa.JSON(), nullable=True),
        sa.Column('recommended_approach', sa.Text(), nullable=True),
        sa.Column('analysis_summary', sa.Text(), nullable=True),
        sa.Column('messages_analyzed', sa.Integer(), server_default='0'),
        sa.Column('last_analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analysis_version', sa.String(20), server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_user_profiles_id', 'user_profiles', ['id'])

    # 6. Add completed_at column to user_courses if not exists
    # Note: SQLite doesn't support IF NOT EXISTS for columns, so we use try/except in the migration
    try:
        op.add_column('user_courses', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    except Exception:
        pass  # Column might already exist


def downgrade() -> None:
    # Remove completed_at column from user_courses
    try:
        op.drop_column('user_courses', 'completed_at')
    except Exception:
        pass

    op.drop_index('ix_user_profiles_id', table_name='user_profiles')
    op.drop_table('user_profiles')

    op.drop_index('ix_token_usage_created_at', table_name='token_usage')
    op.drop_index('ix_token_usage_feature', table_name='token_usage')
    op.drop_index('ix_token_usage_id', table_name='token_usage')
    op.drop_table('token_usage')

    op.drop_table('studio_packages')
    op.drop_table('studio_processors')

    op.drop_index('ix_simulator_results_session_id', table_name='simulator_results')
    op.drop_index('ix_simulator_results_id', table_name='simulator_results')
    op.drop_table('simulator_results')
