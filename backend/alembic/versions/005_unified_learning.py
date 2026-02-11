"""Add unified learning system tables: content_templates and quality_evaluations

Revision ID: 005_unified_learning
Revises: 004_missing_tables
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_unified_learning'
down_revision = '004_missing_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create content_templates table (统一模板表)
    op.create_table(
        'content_templates',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('template_type', sa.String(50), nullable=False, index=True),  # 'simulator', 'tutor_dialogue', 'chapter_content', 'quiz_question'
        sa.Column('subject', sa.String(100), nullable=False, index=True),
        sa.Column('topic', sa.String(255), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),  # JSON格式内容
        sa.Column('quality_score', sa.Float(), nullable=False, index=True),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),  # 评分细分
        sa.Column('template_metadata', sa.JSON(), nullable=True),  # 学习元数据

        # 类型特定字段
        sa.Column('difficulty_level', sa.String(50), nullable=True),  # 用于quiz/chapter
        sa.Column('content_hash', sa.String(64), nullable=True, index=True),  # 去重用

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('usage_count', sa.Integer(), server_default='0'),
    )
    op.create_index('ix_content_templates_id', 'content_templates', ['id'])

    # 2. Create quality_evaluations table (质量评估记录表)
    op.create_table(
        'quality_evaluations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('content_type', sa.String(50), nullable=False, index=True),  # 'simulator', 'tutor_dialogue', 'chapter_content', 'quiz_question'
        sa.Column('content_id', sa.String(255), nullable=False, index=True),  # 内容唯一标识
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),  # 评分细分
        sa.Column('saved_as_template', sa.Integer(), server_default='0'),  # 是否保存为模板
        sa.Column('evaluated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), index=True),
    )
    op.create_index('ix_quality_evaluations_id', 'quality_evaluations', ['id'])


def downgrade() -> None:
    op.drop_index('ix_quality_evaluations_id', table_name='quality_evaluations')
    op.drop_table('quality_evaluations')

    op.drop_index('ix_content_templates_id', table_name='content_templates')
    op.drop_table('content_templates')
