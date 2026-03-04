-- Optimized SQL queries for hot paths
-- Run with:
--   psql -h localhost -U hercu -d hercu_db -f scripts/optimized_queries.sql
-- Replace :user_id / :subject_id / :threshold with actual values.

-- =============================
-- 1) Weak nodes (BKT)
-- Uses: idx_sks_user_mastery_updated + idx_sks_user_node + PK on knowledge_nodes
-- =============================
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    sks.knowledge_node_id,
    sks.mastery,
    sks.stability,
    sks.practice_count,
    sks.streak,
    kn.name AS node_name,
    kn.code AS node_code
FROM student_knowledge_state sks
JOIN knowledge_nodes kn ON kn.id = sks.knowledge_node_id
WHERE sks.user_id = :user_id
  AND sks.mastery < :threshold
ORDER BY sks.mastery ASC
LIMIT 100;

-- =============================
-- 2) Latest emotion state
-- Uses: idx_ses_user_created_desc
-- =============================
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id, emotion_type, intensity, confidence, trigger_type, context, created_at
FROM student_emotion_states
WHERE user_id = :user_id
ORDER BY created_at DESC
LIMIT 1;

-- =============================
-- 3) Student events timeline (paged)
-- Uses: idx_se_user_created_desc / idx_se_user_event_created_desc
-- =============================
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    id, knowledge_node_id, event_type, is_correct, response_time_ms, created_at
FROM student_events
WHERE user_id = :user_id
ORDER BY created_at DESC
LIMIT 50 OFFSET 0;

-- =============================
-- 4) Recommendation context query (consolidation nodes)
-- Uses: idx_sks_user_mastery_updated
-- =============================
EXPLAIN (ANALYZE, BUFFERS)
SELECT
    knowledge_node_id, mastery, stability, last_practice_at
FROM student_knowledge_state
WHERE user_id = :user_id
  AND mastery >= 0.4
  AND mastery < 0.7
ORDER BY mastery ASC, stability ASC
LIMIT 50;

-- =============================
-- 5) Admin overview aggregate (single query)
-- =============================
EXPLAIN (ANALYZE, BUFFERS)
WITH node_stats AS (
    SELECT subject_id, COUNT(id) AS total_nodes
    FROM knowledge_nodes
    GROUP BY subject_id
),
mastery_stats AS (
    SELECT
        kn.subject_id AS subject_id,
        AVG(sks.mastery) AS avg_mastery,
        COUNT(DISTINCT sks.user_id) AS active_students,
        COUNT(DISTINCT CASE WHEN sks.mastery < 0.4 THEN sks.knowledge_node_id END) AS weak_node_count
    FROM student_knowledge_state sks
    JOIN knowledge_nodes kn ON kn.id = sks.knowledge_node_id
    GROUP BY kn.subject_id
)
SELECT
    s.id AS subject_id,
    s.name AS subject_name,
    COALESCE(ns.total_nodes, 0) AS total_nodes,
    COALESCE(ms.avg_mastery, 0.0) AS avg_mastery,
    COALESCE(ms.active_students, 0) AS active_students,
    COALESCE(ms.weak_node_count, 0) AS weak_node_count
FROM subjects s
LEFT JOIN node_stats ns ON ns.subject_id = s.id
LEFT JOIN mastery_stats ms ON ms.subject_id = s.id
ORDER BY s.id;

