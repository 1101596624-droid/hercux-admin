"""
Add Studio tables migration

Run this script to add studio_processors and studio_packages tables
"""

import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'hercu_dev.db')

# SQL statements to create Studio tables
CREATE_STUDIO_PROCESSORS = """
CREATE TABLE IF NOT EXISTS studio_processors (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0.0',
    author VARCHAR(255),
    tags JSON,
    color VARCHAR(50) DEFAULT '#3B82F6',
    icon VARCHAR(50) DEFAULT 'Sparkles',
    system_prompt TEXT,
    enabled INTEGER DEFAULT 1,
    display_order INTEGER DEFAULT 0,
    is_official INTEGER DEFAULT 0,
    is_custom INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
"""

CREATE_STUDIO_PACKAGES = """
CREATE TABLE IF NOT EXISTS studio_packages (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source_info TEXT,
    style VARCHAR(100),
    status VARCHAR(20) DEFAULT 'draft',
    meta JSON,
    lessons JSON,
    edges JSON,
    global_ai_config JSON,
    total_lessons INTEGER DEFAULT 0,
    estimated_hours REAL DEFAULT 0,
    processor_id VARCHAR(100) REFERENCES studio_processors(id),
    course_id INTEGER REFERENCES courses(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
"""

# Create indexes
CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_studio_packages_status ON studio_packages(status);
CREATE INDEX IF NOT EXISTS idx_studio_packages_processor ON studio_packages(processor_id);
CREATE INDEX IF NOT EXISTS idx_studio_packages_course ON studio_packages(course_id);
CREATE INDEX IF NOT EXISTS idx_studio_processors_enabled ON studio_processors(enabled);
"""


def run_migration():
    """Run the migration"""
    print(f"Running migration on: {DB_PATH}")

    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create studio_processors table
        print("Creating studio_processors table...")
        cursor.execute(CREATE_STUDIO_PROCESSORS)

        # Create studio_packages table
        print("Creating studio_packages table...")
        cursor.execute(CREATE_STUDIO_PACKAGES)

        # Create indexes
        print("Creating indexes...")
        for stmt in CREATE_INDEXES.strip().split(';'):
            if stmt.strip():
                cursor.execute(stmt)

        conn.commit()
        print("Migration completed successfully!")

        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'studio_%'")
        tables = cursor.fetchall()
        print(f"Studio tables created: {[t[0] for t in tables]}")

        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
