#!/usr/bin/env python3
"""
通过Python直接导入模板到数据库
"""
import sys

try:
    import psycopg2
    print("[INFO] psycopg2 module found")
except ImportError:
    print("[ERROR] psycopg2 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    print("[INFO] psycopg2 installed successfully")

# 数据库连接配置
DB_CONFIG = {
    "host": "106.14.180.66",
    "database": "hercu_db",
    "user": "hercu",
    "password": "Hercu2026Secure"
}

def import_sql_file():
    """读取并执行SQL文件"""
    sql_file = "F:/9/hercux-admin/backend/import_templates.sql"

    print("="*50)
    print("HERCU HTML Simulator Templates Import")
    print("="*50)
    print(f"Target Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print(f"SQL File: {sql_file}")
    print()

    try:
        # 连接数据库
        print("[1/3] Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("[SUCCESS] Connected to database")

        # 读取SQL文件
        print(f"[2/3] Reading SQL file...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"[SUCCESS] SQL file loaded ({len(sql_content)} characters)")

        # 执行SQL
        print("[2/3] Executing SQL import...")
        cursor.execute(sql_content)
        conn.commit()
        print("[SUCCESS] SQL executed successfully")

        # 验证导入
        print("[3/3] Verifying import...")
        cursor.execute("""
            SELECT subject, COUNT(*) as count, AVG(quality_score) as avg_score
            FROM simulator_templates
            WHERE quality_score = 75
            GROUP BY subject
            ORDER BY subject;
        """)

        results = cursor.fetchall()
        print("\nImport Results:")
        print("-" * 50)
        print(f"{'Subject':<20} {'Count':<10} {'Avg Score':<10}")
        print("-" * 50)
        for subject, count, avg_score in results:
            print(f"{subject:<20} {count:<10} {avg_score:<10.1f}")
        print("-" * 50)
        print(f"Total templates: {sum(r[1] for r in results)}")

        cursor.close()
        conn.close()

        print()
        print("="*50)
        print("Import SUCCESSFUL!")
        print("="*50)

    except Exception as e:
        print()
        print("="*50)
        print(f"Import FAILED! Error: {e}")
        print("="*50)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(import_sql_file())
