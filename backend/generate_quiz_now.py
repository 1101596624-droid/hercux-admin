"""
为现有课程生成三难度题库
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.quiz_generator import generate_quiz_for_course

async def main():
    print("开始为课程 ID 4 (稀缺心理学) 生成三难度题库...")
    print("每个节点将生成 easy/medium/hard 各13道题，共39道题")
    print("-" * 50)

    result = await generate_quiz_for_course(4)

    print("-" * 50)
    print(f"生成结果: {result}")

    if result.get("success"):
        print(f"\n成功: {result.get('generated', 0)} 个节点")
        print(f"失败: {result.get('failed', 0)} 个节点")
        print(f"总计: {result.get('total', 0)} 个节点")
    else:
        print(f"\n错误: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
