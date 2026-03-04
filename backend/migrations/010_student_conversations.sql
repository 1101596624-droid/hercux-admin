-- Phase 3: 诊断式AI Tutor - 对话记录表
-- student_emotion_states 已在 Phase 2 创建，此处仅创建 student_conversations

CREATE TABLE IF NOT EXISTS student_conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    knowledge_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    session_id VARCHAR(64) NOT NULL,
    tutor_phase VARCHAR(20) DEFAULT 'understand',
    messages JSONB DEFAULT '[]'::jsonb,
    diagnosis JSONB DEFAULT '{}'::jsonb,
    emotion_snapshot VARCHAR(50),
    mastery_before FLOAT,
    mastery_after FLOAT,
    mode VARCHAR(20) DEFAULT 'adaptive',
    turn_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_conv_user_session ON student_conversations(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_conv_user_node ON student_conversations(user_id, knowledge_node_id);
CREATE INDEX IF NOT EXISTS idx_conv_session_id ON student_conversations(session_id);
