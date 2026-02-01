"""Initial schema with unlock system and progress tracking

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE difficultylevel AS ENUM ('beginner', 'intermediate', 'advanced', 'expert')")
    op.execute("CREATE TYPE nodetype AS ENUM ('video', 'simulator', 'quiz', 'reading', 'practice')")
    op.execute("CREATE TYPE nodestatus AS ENUM ('locked', 'unlocked', 'in_progress', 'completed')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_premium', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create courses table
    op.create_table(
        'courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.Enum('beginner', 'intermediate', 'advanced', 'expert', name='difficultylevel'), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('instructor', sa.String(length=255), nullable=True),
        sa.Column('duration_hours', sa.Float(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('is_published', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)

    # Create course_nodes table with tree structure and unlock system
    op.create_table(
        'course_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('node_id', sa.String(length=100), nullable=False),
        sa.Column('type', sa.Enum('video', 'simulator', 'quiz', 'reading', 'practice', name='nodetype'), nullable=False),
        sa.Column('component_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('timeline_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('unlock_condition', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['course_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_nodes_id'), 'course_nodes', ['id'], unique=False)
    op.create_index(op.f('ix_course_nodes_node_id'), 'course_nodes', ['node_id'], unique=True)

    # Create learning_progress table
    op.create_table(
        'learning_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('locked', 'unlocked', 'in_progress', 'completed', name='nodestatus'), nullable=True, server_default='locked'),
        sa.Column('completion_percentage', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['node_id'], ['course_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_progress_id'), 'learning_progress', ['id'], unique=False)
    op.create_index('ix_learning_progress_user_node', 'learning_progress', ['user_id', 'node_id'], unique=True)

    # Create training_plans table
    op.create_table(
        'training_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('plan_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_plans_id'), 'training_plans', ['id'], unique=False)

    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.String(length=100), nullable=False),
        sa.Column('badge_name', sa.String(length=255), nullable=False),
        sa.Column('badge_description', sa.Text(), nullable=True),
        sa.Column('rarity', sa.String(length=50), nullable=True),
        sa.Column('icon_url', sa.String(length=500), nullable=True),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_achievements_id'), 'achievements', ['id'], unique=False)

    # Create user_courses table
    op.create_table(
        'user_courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_favorite', sa.Integer(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_courses_id'), 'user_courses', ['id'], unique=False)
    op.create_index('ix_user_courses_user_course', 'user_courses', ['user_id', 'course_id'], unique=True)

    # Create chat_history table
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['node_id'], ['course_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_history_id'), 'chat_history', ['id'], unique=False)

    # Create learning_statistics table
    op.create_table(
        'learning_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_time_seconds', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('nodes_completed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('streak_days', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_statistics_id'), 'learning_statistics', ['id'], unique=False)
    op.create_index('ix_learning_statistics_user_date', 'learning_statistics', ['user_id', 'date'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_learning_statistics_user_date', table_name='learning_statistics')
    op.drop_index(op.f('ix_learning_statistics_id'), table_name='learning_statistics')
    op.drop_table('learning_statistics')

    op.drop_index(op.f('ix_chat_history_id'), table_name='chat_history')
    op.drop_table('chat_history')

    op.drop_index('ix_user_courses_user_course', table_name='user_courses')
    op.drop_index(op.f('ix_user_courses_id'), table_name='user_courses')
    op.drop_table('user_courses')

    op.drop_index(op.f('ix_achievements_id'), table_name='achievements')
    op.drop_table('achievements')

    op.drop_index(op.f('ix_training_plans_id'), table_name='training_plans')
    op.drop_table('training_plans')

    op.drop_index('ix_learning_progress_user_node', table_name='learning_progress')
    op.drop_index(op.f('ix_learning_progress_id'), table_name='learning_progress')
    op.drop_table('learning_progress')

    op.drop_index(op.f('ix_course_nodes_node_id'), table_name='course_nodes')
    op.drop_index(op.f('ix_course_nodes_id'), table_name='course_nodes')
    op.drop_table('course_nodes')

    op.drop_index(op.f('ix_courses_id'), table_name='courses')
    op.drop_table('courses')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    # Drop enum types
    op.execute("DROP TYPE nodestatus")
    op.execute("DROP TYPE nodetype")
    op.execute("DROP TYPE difficultylevel")
