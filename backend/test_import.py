#!/usr/bin/env python3
"""
简化的测试脚本：导入示例课程包
"""

import asyncio
import json
import httpx
from pathlib import Path


BASE_URL = "http://localhost:8000"


async def import_example_course():
    """导入示例课程包"""
    print("📦 正在导入示例课程包...")

    # 读取示例课程包
    example_file = Path(__file__).parent / "examples" / "example-package-physiology.json"

    if not example_file.exists():
        print(f"❌ 找不到示例文件: {example_file}")
        return None

    with open(example_file, "r", encoding="utf-8") as f:
        package_data = json.load(f)

    # 调用导入 API
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/internal/import-package",
                json={"package": package_data}
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 导入成功！")
                print(f"   课程 ID: {result['course_id']}")
                print(f"   创建节点数: {result['nodes_created']}")
                print(f"   创建边数: {result['edges_created']}")
                return result['course_id']
            else:
                print(f"❌ 导入失败: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ 导入失败: {str(e)}")
            return None


async def main():
    """主测试流程"""
    print("=" * 60)
    print("HERCU 学习模块测试")
    print("=" * 60)

    # 导入示例课程
    course_id = await import_example_course()

    if not course_id:
        print("\n❌ 导入失败，测试终止")
        return

    print("\n" + "=" * 60)
    print("✅ 导入完成！")
    print("=" * 60)
    print(f"\n🎓 现在可以访问前端开始学习：")
    print(f"   http://localhost:3000/course/{course_id}/learn")


if __name__ == "__main__":
    asyncio.run(main())
