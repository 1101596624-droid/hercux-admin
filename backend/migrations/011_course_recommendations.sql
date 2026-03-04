-- Phase 6: 推荐系统 - 课程推荐关联表

CREATE TABLE IF NOT EXISTS course_recommendations (
    id SERIAL PRIMARY KEY,
    source_course_id INTEGER NOT NULL REFERENCES courses(id),
    target_course_id INTEGER NOT NULL REFERENCES courses(id),
    relation_type VARCHAR(30) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    reason VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rec_source ON course_recommendations(source_course_id);
CREATE INDEX IF NOT EXISTS idx_rec_target ON course_recommendations(target_course_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_course_rec ON course_recommendations(source_course_id, target_course_id, relation_type);
