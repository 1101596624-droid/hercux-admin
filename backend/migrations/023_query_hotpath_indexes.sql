-- Phase 16+ 性能强化：高并发与大数据量下的查询热路径索引
-- 目标：
-- 1) 降低 student_knowledge_state / student_events / student_emotion_states 全表扫描概率
-- 2) 优化学习路径、误解查询、推荐上下文的排序与过滤
-- 3) 与现有 020_performance_indexes.sql 互补（不重复）

-- =============================
-- 1. BKT / 知识状态热路径
-- =============================

-- 高频点查: user_id + knowledge_node_id
CREATE INDEX IF NOT EXISTS idx_sks_user_node
    ON student_knowledge_state(user_id, knowledge_node_id);

-- 学科维度汇总时，常按 mastery 区间筛选
CREATE INDEX IF NOT EXISTS idx_sks_user_mastery_updated
    ON student_knowledge_state(user_id, mastery, updated_at);


-- =============================
-- 2. 学习事件热路径
-- =============================

-- 最近事件时间线（按用户）
CREATE INDEX IF NOT EXISTS idx_se_user_created_desc
    ON student_events(user_id, created_at DESC);

-- 情感推断与节点级事件回放：user_id + knowledge_node_id + created_at DESC
CREATE INDEX IF NOT EXISTS idx_se_user_node_created_desc
    ON student_events(user_id, knowledge_node_id, created_at DESC);

-- 事件类型过滤（answer/hint/skip）常见场景
CREATE INDEX IF NOT EXISTS idx_se_user_event_created_desc
    ON student_events(user_id, event_type, created_at DESC);


-- =============================
-- 3. 情感状态热路径
-- =============================

-- 当前情感读取（latest by user）
CREATE INDEX IF NOT EXISTS idx_ses_user_created_desc
    ON student_emotion_states(user_id, created_at DESC);

-- 历史情感过滤（按情感类型）
CREATE INDEX IF NOT EXISTS idx_ses_user_emotion_created_desc
    ON student_emotion_states(user_id, emotion_type, created_at DESC);


-- =============================
-- 4. 误解与复习热路径
-- =============================

-- 未解决误解查询 + 最近出现排序
CREATE INDEX IF NOT EXISTS idx_sm_user_resolved_seen_desc
    ON student_misconceptions(user_id, resolved, last_seen_at DESC);

-- 复习到期查询（已有 idx_review_user_due，这里补充覆盖最近复习排序）
CREATE INDEX IF NOT EXISTS idx_rs_user_last_review_desc
    ON review_schedule(user_id, last_review_at DESC);


-- =============================
-- 5. 学习路径热路径
-- =============================

-- 取活跃路径（含学科过滤）+ 按 created_at 倒序
CREATE INDEX IF NOT EXISTS idx_slp_user_status_subject_created_desc
    ON student_learning_paths(user_id, status, subject_id, created_at DESC);

-- 历史路径列表
CREATE INDEX IF NOT EXISTS idx_slp_user_created_desc
    ON student_learning_paths(user_id, created_at DESC);


-- =============================
-- 6. 关联表与节点排序
-- =============================

-- 学习进度去重/课程推荐链路
CREATE INDEX IF NOT EXISTS idx_lp_user_node
    ON learning_progress(user_id, node_id);

-- 管理端节点列表：subject_id + code 排序
CREATE INDEX IF NOT EXISTS idx_kn_subject_code
    ON knowledge_nodes(subject_id, code);

