-- Phase 9: 学科知识图谱 — 学科间关系表

CREATE TABLE IF NOT EXISTS subject_relations (
    id SERIAL PRIMARY KEY,
    source_subject_id INTEGER NOT NULL REFERENCES subjects(id),
    target_subject_id INTEGER NOT NULL REFERENCES subjects(id),
    relation_type VARCHAR(30) NOT NULL,  -- prerequisite/extension/cross_discipline/complementary
    weight FLOAT DEFAULT 1.0,            -- 关联强度 0~1
    description TEXT,                    -- 关系描述（如"数学建模是物理的基础"）
    shared_concepts JSONB DEFAULT '[]'::jsonb,  -- 共享概念列表
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sr_source ON subject_relations(source_subject_id);
CREATE INDEX IF NOT EXISTS idx_sr_target ON subject_relations(target_subject_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_subject_rel
    ON subject_relations(source_subject_id, target_subject_id, relation_type);
