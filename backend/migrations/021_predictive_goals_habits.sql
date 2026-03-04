-- Phase 15: 智能反馈与预测分析系统
-- 新增: student_goals (目标管理) + learning_habits (学习习惯追踪)

-- 1. 学习目标表
CREATE TABLE IF NOT EXISTS student_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    goal_type VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    subject_id INTEGER REFERENCES subjects(id),
    node_id INTEGER REFERENCES knowledge_nodes(id),
    target_value FLOAT NOT NULL,
    current_value FLOAT DEFAULT 0,
    deadline TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sg_user_status ON student_goals(user_id, status);
CREATE INDEX IF NOT EXISTS idx_sg_user_deadline ON student_goals(user_id, deadline);

-- 2. 学习习惯每日快照表
CREATE TABLE IF NOT EXISTS learning_habits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    events_count INTEGER DEFAULT 0,
    study_minutes INTEGER DEFAULT 0,
    subjects_touched INTEGER DEFAULT 0,
    accuracy FLOAT,
    dominant_emotion VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_lh_user_date ON learning_habits(user_id, date);
