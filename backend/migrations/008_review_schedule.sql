-- Phase 4: 间隔复习系统 (FSRS)
-- 执行: PGPASSWORD='Hercu2026Secure' psql -h localhost -U hercu -d hercu_db -f /tmp/008_review_schedule.sql

-- 1. 创建 review_schedule 表
CREATE TABLE IF NOT EXISTS review_schedule (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    knowledge_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    fsrs_stability FLOAT DEFAULT 1.0,
    fsrs_difficulty FLOAT DEFAULT 5.0,
    next_review_at TIMESTAMPTZ NOT NULL,
    last_review_at TIMESTAMPTZ,
    last_review_type VARCHAR(30),
    last_rating INTEGER,
    review_count INTEGER DEFAULT 0,
    interval_days FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, knowledge_node_id)
);

CREATE INDEX IF NOT EXISTS idx_review_user_due ON review_schedule(user_id, next_review_at);
CREATE INDEX IF NOT EXISTS idx_review_node ON review_schedule(knowledge_node_id);
