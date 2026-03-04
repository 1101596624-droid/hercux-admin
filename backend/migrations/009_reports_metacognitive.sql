-- Phase 5: 学习报告 + 元认知日志
-- 执行: PGPASSWORD='Hercu2026Secure' psql -h localhost -U hercu -d hercu_db -f /tmp/009_reports_metacognitive.sql

CREATE TABLE IF NOT EXISTS learning_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    report_type VARCHAR(20) NOT NULL,
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    summary JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lr_user ON learning_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_lr_user_type ON learning_reports(user_id, report_type);

CREATE TABLE IF NOT EXISTS metacognitive_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    trigger VARCHAR(50) NOT NULL,
    prompt_text TEXT NOT NULL,
    student_response TEXT,
    knowledge_node_id INTEGER REFERENCES knowledge_nodes(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ml_user ON metacognitive_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ml_user_trigger ON metacognitive_logs(user_id, trigger);
