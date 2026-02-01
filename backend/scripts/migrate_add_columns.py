"""
数据库迁移脚本：添加 learning_progress 表缺失的列
运行方式：python scripts/migrate_add_columns.py
"""
import sqlite3
import os

# 服务器数据库路径
DB_PATH = os.environ.get("DB_PATH", "/www/wwwroot/hercu-backend/hercu.db")

def migrate():
    print(f"连接数据库: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 检查现有列
    cursor.execute("PRAGMA table_info(learning_progress)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"现有列: {existing_columns}")

    # 需要添加的列
    columns_to_add = []

    if "completion_percentage" not in existing_columns:
        columns_to_add.append(("completion_percentage", "FLOAT DEFAULT 0.0"))

    if "last_accessed" not in existing_columns:
        columns_to_add.append(("last_accessed", "DATETIME"))

    if "current_step" not in existing_columns:
        columns_to_add.append(("current_step", "INTEGER DEFAULT 0"))

    if "score" not in existing_columns:
        columns_to_add.append(("score", "FLOAT DEFAULT 0.0"))

    if "attempts" not in existing_columns:
        columns_to_add.append(("attempts", "INTEGER DEFAULT 0"))

    if not columns_to_add:
        print("所有列已存在，无需迁移")
        conn.close()
        return

    # 执行迁移
    for col_name, col_def in columns_to_add:
        sql = f"ALTER TABLE learning_progress ADD COLUMN {col_name} {col_def}"
        print(f"执行: {sql}")
        try:
            cursor.execute(sql)
            print(f"  -> 成功添加列: {col_name}")
        except sqlite3.OperationalError as e:
            print(f"  -> 跳过 (可能已存在): {e}")

    conn.commit()

    # 验证
    cursor.execute("PRAGMA table_info(learning_progress)")
    final_columns = {row[1] for row in cursor.fetchall()}
    print(f"\n迁移后的列: {final_columns}")

    conn.close()
    print("\n迁移完成!")

if __name__ == "__main__":
    migrate()
