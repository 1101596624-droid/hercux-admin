"""Add learning patterns system with pgvector support

Revision ID: 006_learning_patterns
Revises: 005_unified_learning
Create Date: 2026-02-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '006_learning_patterns'
down_revision = '005_unified_learning'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Install pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # 2. Add embedding column to content_templates table
    op.execute("""
        ALTER TABLE content_templates
        ADD COLUMN IF NOT EXISTS embedding vector(384)
    """)

    # 3. Create generation_patterns table
    op.create_table(
        'generation_patterns',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('pattern_type', sa.String(50), nullable=False, index=True),  # 'failure_recovery', 'optimization', 'best_practice'
        sa.Column('step_type', sa.String(50), nullable=False, index=True),  # 'text_content', 'illustrated_content', 'assessment', 'ai_tutor'
        sa.Column('subject', sa.String(100), nullable=False, index=True),
        sa.Column('pattern_name', sa.String(255), nullable=False),
        sa.Column('pattern_description', sa.Text(), nullable=False),
        sa.Column('trigger_conditions', JSONB(), nullable=False),  # 触发条件
        sa.Column('solution_strategy', sa.Text(), nullable=False),  # 解决策略
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.8'),  # 置信度
        sa.Column('use_count', sa.Integer(), nullable=False, server_default='0'),  # 使用次数
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),  # 成功次数
        sa.Column('embedding', sa.Text(), nullable=False),  # vector(384) - stored as TEXT for SQLAlchemy compatibility
        sa.Column('source_templates', JSONB(), nullable=True),  # 来源模板IDs
        sa.Column('created_from_count', sa.Integer(), nullable=False, server_default='1'),  # 蒸馏样本数
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_generation_patterns_id', 'generation_patterns', ['id'])

    # Convert embedding column to vector type
    op.execute("""
        ALTER TABLE generation_patterns
        ALTER COLUMN embedding TYPE vector(384) USING embedding::vector
    """)

    # 4. Create ivfflat index on generation_patterns.embedding
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_generation_patterns_embedding
        ON generation_patterns
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # 5. Create ivfflat index on content_templates.embedding
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_templates_embedding
        ON content_templates
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)

    # 6. Create pattern_applications table
    op.create_table(
        'pattern_applications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('pattern_id', sa.Integer(), sa.ForeignKey('generation_patterns.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('step_type', sa.String(50), nullable=False, index=True),
        sa.Column('subject', sa.String(100), nullable=False, index=True),
        sa.Column('topic', sa.String(255), nullable=False, index=True),
        sa.Column('original_input', JSONB(), nullable=False),  # 原始输入
        sa.Column('applied_strategy', sa.Text(), nullable=False),  # 应用的策略
        sa.Column('result_quality', sa.Float(), nullable=True),  # 结果质量评分
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),  # 应用是否成功
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), index=True),
    )
    op.create_index('ix_pattern_applications_id', 'pattern_applications', ['id'])


def downgrade() -> None:
    # Drop pattern_applications table
    op.drop_index('ix_pattern_applications_id', table_name='pattern_applications')
    op.drop_table('pattern_applications')

    # Drop indexes on embeddings
    op.execute('DROP INDEX IF EXISTS idx_content_templates_embedding')
    op.execute('DROP INDEX IF EXISTS idx_generation_patterns_embedding')

    # Drop generation_patterns table
    op.drop_index('ix_generation_patterns_id', table_name='generation_patterns')
    op.drop_table('generation_patterns')

    # Remove embedding column from content_templates
    op.execute('ALTER TABLE content_templates DROP COLUMN IF EXISTS embedding')

    # Drop pgvector extension (optional - might be used by other tables)
    # op.execute('DROP EXTENSION IF EXISTS vector')
