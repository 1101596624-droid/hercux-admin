-- Phase 7: 智能评估与自适应反馈

CREATE TABLE IF NOT EXISTS student_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    knowledge_node_id INTEGER REFERENCES knowledge_nodes(id),
    mastery FLOAT,
    stability FLOAT,
    frustration_level FLOAT DEFAULT 0.0,
    anxiety_level FLOAT DEFAULT 0.0,
    focus_level FLOAT DEFAULT 0.5,
    assessment_type VARCHAR(30) DEFAULT 'auto',
    feedback TEXT,
    strategy_suggestions JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assess_user ON student_assessments(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_assess_node ON student_assessments(knowledge_node_id);
