-- Phase 6: 推荐记录持久化表

CREATE TABLE IF NOT EXISTS recommended_lessons (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    knowledge_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    course_node_id INTEGER REFERENCES course_nodes(id),
    reason VARCHAR(500),
    priority INTEGER DEFAULT 1,
    mastery_at_recommend FLOAT,
    emotion_at_recommend VARCHAR(50),
    is_viewed BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_rec_lesson_user ON recommended_lessons(user_id, created_at);

CREATE TABLE IF NOT EXISTS recommended_grinders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    knowledge_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    reason VARCHAR(500),
    priority INTEGER DEFAULT 1,
    suggested_difficulty FLOAT DEFAULT 0.5,
    mastery_at_recommend FLOAT,
    emotion_at_recommend VARCHAR(50),
    misconception_id INTEGER REFERENCES student_misconceptions(id),
    is_viewed BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_rec_grinder_user ON recommended_grinders(user_id, created_at);
