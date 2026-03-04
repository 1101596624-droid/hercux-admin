-- Phase 8: 多任务学习与多目标优化

CREATE TABLE IF NOT EXISTS student_multi_task_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    -- 目标权重配置
    objective_weights JSONB DEFAULT '{"mastery":0.35,"retention":0.25,"emotion":0.2,"efficiency":0.2}'::jsonb,
    -- 学生状态快照
    student_snapshot JSONB DEFAULT '{}'::jsonb,
    -- 生成的任务列表
    tasks JSONB DEFAULT '[]'::jsonb,
    -- 优化结果摘要
    optimization_summary JSONB DEFAULT '{}'::jsonb,
    -- 计划状态
    status VARCHAR(20) DEFAULT 'active',
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    session_minutes INTEGER DEFAULT 30,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_mtp_user ON student_multi_task_plans(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_mtp_status ON student_multi_task_plans(user_id, status);
