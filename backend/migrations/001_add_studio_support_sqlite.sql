-- SQLite 版本的数据库迁移脚本
-- 添加 Studio 课程包支持

-- 1. 创建课程包表
CREATE TABLE IF NOT EXISTS course_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    studio_package_id TEXT UNIQUE NOT NULL,
    course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
    version TEXT DEFAULT '1.0.0',
    style TEXT,
    package_data TEXT NOT NULL,  -- SQLite 使用 TEXT 存储 JSON
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported_by INTEGER REFERENCES users(id)
);

-- 2. 扩展 courses 表
ALTER TABLE courses ADD COLUMN IF NOT EXISTS studio_package_id TEXT;
ALTER TABLE courses ADD COLUMN IF NOT EXISTS source_info TEXT;

-- 3. 扩展 course_nodes 表
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS studio_node_id TEXT;
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS learning_objectives TEXT;  -- JSON
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS content_l1 TEXT;  -- JSON
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS content_l2 TEXT;  -- JSON
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS content_l3 TEXT;  -- JSON
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS ai_tutor_config TEXT;  -- JSON
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS quiz_data TEXT;  -- JSON
ALTER TABLE course_nodes ADD COLUMN IF NOT EXISTS timeline_config TEXT;  -- JSON

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS idx_course_packages_studio_id ON course_packages(studio_package_id);
CREATE INDEX IF NOT EXISTS idx_course_packages_course_id ON course_packages(course_id);
CREATE INDEX IF NOT EXISTS idx_courses_studio_package_id ON courses(studio_package_id);
CREATE INDEX IF NOT EXISTS idx_course_nodes_studio_node_id ON course_nodes(studio_node_id);
