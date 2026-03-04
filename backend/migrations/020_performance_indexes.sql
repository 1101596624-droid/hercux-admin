-- Phase 14: 性能优化 — 高频查询复合索引
-- 针对 student_events, student_knowledge_state, student_emotion_states, student_learning_paths
-- 这些表在推荐/反馈/Agent服务中被高频查询

-- student_knowledge_state: 推荐系统按user_id+mastery筛选薄弱点
CREATE INDEX IF NOT EXISTS idx_sks_user_mastery
    ON student_knowledge_state(user_id, mastery);

-- student_events: 反馈/报告按user_id+created_at范围查询
CREATE INDEX IF NOT EXISTS idx_se_user_created
    ON student_events(user_id, created_at);

-- student_emotion_states: Agent/反馈按user_id+created_at取最新情感
CREATE INDEX IF NOT EXISTS idx_ses_user_created
    ON student_emotion_states(user_id, created_at);

-- student_learning_paths: 反馈按user_id+status筛选活跃路径
CREATE INDEX IF NOT EXISTS idx_slp_user_status
    ON student_learning_paths(user_id, status);

-- student_feedback: 历史查询按user_id+feedback_type+created_at
CREATE INDEX IF NOT EXISTS idx_sfb_user_type_created
    ON student_feedback(user_id, feedback_type, created_at);

-- agent_strategy_rewards: 奖惩历史按user_id+strategy_type+created_at
CREATE INDEX IF NOT EXISTS idx_asr_user_strategy_created
    ON agent_strategy_rewards(user_id, strategy_type, created_at);

-- review_schedule: 到期复习按user_id+next_review_at
CREATE INDEX IF NOT EXISTS idx_rs_user_next_review
    ON review_schedule(user_id, next_review_at);
