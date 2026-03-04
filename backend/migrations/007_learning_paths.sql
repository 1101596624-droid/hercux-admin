-- 自适应学习路径表 (Phase 2)
-- 执行: PGPASSWORD='Hercu2026Secure' psql -h localhost -U hercu -d hercu_db -f /tmp/007_learning_paths.sql

CREATE TABLE IF NOT EXISTS student_learning_paths (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    status VARCHAR(20) DEFAULT 'active',
    session_duration INTEGER DEFAULT 30,
    path_items JSONB DEFAULT '[]'::jsonb,
    emotion_snapshot VARCHAR(50),
    total_nodes INTEGER DEFAULT 0,
    completed_nodes INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_slp_user ON student_learning_paths(user_id);
CREATE INDEX IF NOT EXISTS idx_slp_subject ON student_learning_paths(subject_id);
CREATE INDEX IF NOT EXISTS idx_slp_user_status ON student_learning_paths(user_id, status);
CREATE INDEX IF NOT EXISTS idx_slp_created ON student_learning_paths(created_at DESC);
