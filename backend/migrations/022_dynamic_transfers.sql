-- Phase 16: 动态迁移系数学习
-- 个性化跨学科迁移系数（贝叶斯更新）

CREATE TABLE IF NOT EXISTS student_subject_transfers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    source_subject_id INTEGER NOT NULL REFERENCES subjects(id),
    target_subject_id INTEGER NOT NULL REFERENCES subjects(id),
    observed_transfer FLOAT DEFAULT 0.5,
    confidence FLOAT DEFAULT 0.1,
    sample_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, source_subject_id, target_subject_id)
);

CREATE INDEX IF NOT EXISTS idx_sst_user ON student_subject_transfers(user_id);
CREATE INDEX IF NOT EXISTS idx_sst_user_source ON student_subject_transfers(user_id, source_subject_id);
