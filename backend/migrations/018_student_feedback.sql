-- Phase 12: 学习反馈系统 + 智能报告系统

-- 1. 综合学习反馈表（存储个性化反馈记录）
CREATE TABLE IF NOT EXISTS student_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    feedback_type VARCHAR(30) NOT NULL,
    subject_id INTEGER REFERENCES subjects(id),
    progress_summary JSON DEFAULT '{}',
    emotion_summary JSON DEFAULT '{}',
    suggestions JSON DEFAULT '[]',
    difficulty_adjustment JSON DEFAULT '{}',
    encouragement TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sf_user ON student_feedback(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_sf_type ON student_feedback(user_id, feedback_type);
