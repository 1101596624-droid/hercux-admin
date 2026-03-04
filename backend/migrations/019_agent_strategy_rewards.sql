-- Phase 13: Agent 强化学习与自适应任务生成

-- 1. Agent 策略奖惩记录表
CREATE TABLE IF NOT EXISTS agent_strategy_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    strategy_type VARCHAR(50) NOT NULL,
    action_taken JSON DEFAULT '{}',
    student_state_before JSON DEFAULT '{}',
    student_state_after JSON DEFAULT '{}',
    reward_signal FLOAT DEFAULT 0.0,
    reward_components JSON DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_asr_user ON agent_strategy_rewards(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_asr_strategy ON agent_strategy_rewards(strategy_type, reward_signal);

-- 2. Agent 策略权重表（自我优化的权重存储）
CREATE TABLE IF NOT EXISTS agent_strategy_weights (
    id SERIAL PRIMARY KEY,
    strategy_type VARCHAR(50) NOT NULL UNIQUE,
    weights JSON DEFAULT '{}',
    total_episodes INTEGER DEFAULT 0,
    avg_reward FLOAT DEFAULT 0.0,
    last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 初始化默认策略权重
INSERT INTO agent_strategy_weights (strategy_type, weights) VALUES
    ('task_generation', '{"learn":0.25,"review":0.2,"practice":0.2,"remediate":0.15,"challenge":0.1,"recover":0.1}'),
    ('difficulty_selection', '{"easy":0.3,"medium":0.4,"hard":0.2,"challenge":0.1}'),
    ('content_type', '{"lecture":0.25,"simulator":0.25,"grinder":0.25,"tutor":0.25}')
ON CONFLICT (strategy_type) DO NOTHING;
