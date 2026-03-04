-- Phase 11: 课程关系与学生课程进度

-- 1. 课程间结构关系表（前置/扩展/并行）
CREATE TABLE IF NOT EXISTS course_relations (
    id SERIAL PRIMARY KEY,
    source_course_id INTEGER NOT NULL REFERENCES courses(id),
    target_course_id INTEGER NOT NULL REFERENCES courses(id),
    relation_type VARCHAR(30) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cr_source ON course_relations(source_course_id);
CREATE INDEX IF NOT EXISTS idx_cr_target ON course_relations(target_course_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_course_rel
    ON course_relations(source_course_id, target_course_id, relation_type);

-- 2. 学生课程级进度聚合表
CREATE TABLE IF NOT EXISTS student_course_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    total_nodes INTEGER DEFAULT 0,
    completed_nodes INTEGER DEFAULT 0,
    completion_pct FLOAT DEFAULT 0.0,
    avg_mastery FLOAT DEFAULT 0.0,
    total_time_seconds INTEGER DEFAULT 0,
    last_activity_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'in_progress',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_scp_user_course
    ON student_course_progress(user_id, course_id);
CREATE INDEX IF NOT EXISTS idx_scp_user ON student_course_progress(user_id, status);
