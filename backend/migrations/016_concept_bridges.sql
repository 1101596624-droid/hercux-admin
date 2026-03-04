-- Phase 10: 跨学科推荐与知识推理

-- 1. 知识节点级跨学科概念桥接表
CREATE TABLE IF NOT EXISTS concept_bridges (
    id SERIAL PRIMARY KEY,
    source_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    target_node_id INTEGER NOT NULL REFERENCES knowledge_nodes(id),
    concept_name VARCHAR(200) NOT NULL,
    transfer_weight FLOAT DEFAULT 0.5,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cb_source ON concept_bridges(source_node_id);
CREATE INDEX IF NOT EXISTS idx_cb_target ON concept_bridges(target_node_id);
CREATE INDEX IF NOT EXISTS idx_cb_concept ON concept_bridges(concept_name);
CREATE UNIQUE INDEX IF NOT EXISTS uq_concept_bridge
    ON concept_bridges(source_node_id, target_node_id, concept_name);

-- 2. subject_relations 增加学习迁移系数
ALTER TABLE subject_relations
    ADD COLUMN IF NOT EXISTS transfer_coefficient FLOAT DEFAULT 0.3;
